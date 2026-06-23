"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import decimal
import math
from collections.abc import Iterable
from typing import Literal, Optional, Union
from tqdm.auto import tqdm
import numpy as np
import scipy.stats as scipy_st
import scipy.special as scipy_special

from vastorbit.connection.errors import QueryError

import vastorbit._config.config as conf
from vastorbit._typing import NoneType, PlottingObject, SQLColumns
from vastorbit._utils._gen import gen_name, gen_tmp_name
from vastorbit._utils._object import get_VAST_mllib, create_new_vdf
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit._utils._sql._vast_version import vast_version
from vastorbit.errors import EmptyParameter, VersionError

from vastorbit.core.tablesample.base import TableSample

from vastorbit.core.vastframe._encoding import vDFEncode, vDCEncode

from vastorbit.sql.drop import drop


class vDFCorr(vDFEncode):
    # System Methods.

    def _aggregate_matrix(
        self,
        method: str = "pearson",
        columns: Optional[SQLColumns] = None,
        mround: int = 3,
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        with_numbers: bool = True,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Global method used to compute the Correlation/Cov/Regr Matrix.
        """
        method_name = "Correlation"
        method_type = f" using the method = '{method}'"
        if method == "cov":
            method_name = "Covariance"
            method_type = ""
        columns = self.format_colnames(columns)
        if method != "cramer":
            for column in columns:
                assert self[column].isnum(), TypeError(
                    f"VastColumn {column} must be numerical to "
                    f"compute the {method_name} Matrix{method_type}."
                )
        if len(columns) == 1:
            if method in (
                "pearson",
                "spearman",
                "spearmand",
                "kendall",
                "biserial",
                "cramer",
            ):
                return 1.0
            elif method == "cov":
                return self[columns[0]].var()
        elif len(columns) == 2:
            pre_comp_val = self._get_catalog_value(method=method, columns=columns)
            if pre_comp_val != "VASTORBIT_NOT_PRECOMPUTED":
                return pre_comp_val
            cast_0_b = "CAST(" if (self[columns[0]].isbool()) else ""
            cast_0_e = " AS INT)" if (self[columns[0]].isbool()) else ""
            cast_1_b = ":CAST(" if (self[columns[1]].isbool()) else ""
            cast_1_e = " AS INT)" if (self[columns[1]].isbool()) else ""
            if method in (
                "pearson",
                "spearman",
                "spearmand",
            ):
                if columns[1] == columns[0]:
                    return 1
                if method == "pearson":
                    table = self._genSQL()
                else:
                    table = f"""
                        (SELECT 
                            RANK() OVER (ORDER BY {columns[0]}) AS {columns[0]}, 
                            RANK() OVER (ORDER BY {columns[1]}) AS {columns[1]} 
                        FROM {self}) rank_spearman_table
                    """
                query = f"""
                    SELECT 
                        /*+LABEL('VastFrame._aggregate_matrix')*/ 
                        CORR({cast_0_b}{columns[0]}{cast_0_e}, {cast_1_b}{columns[1]}{cast_1_e}) 
                    FROM {table}"""
                title = (
                    f"Computes the {method} correlation between "
                    f"{columns[0]} and {columns[1]}."
                )
            elif method == "biserial":
                if columns[1] == columns[0]:
                    return 1
                elif (self[columns[1]].category() != "int") and (
                    self[columns[0]].category() != "int"
                ):
                    return np.nan
                elif self[columns[1]].category() == "int":
                    if not self[columns[1]].isbool():
                        agg = (
                            self[columns[1]]
                            .aggregate(["approx_unique", "min", "max"])
                            .values[columns[1]]
                        )
                        if (agg[0] != 2) or (agg[1] != 0) or (agg[2] != 1):
                            return np.nan
                    column_b, column_n = columns[1], columns[0]
                    cast_b_b, cast_n_b = cast_1_b, cast_0_b
                    cast_b_e, cast_n_e = cast_1_e, cast_0_e
                elif self[columns[0]].category() == "int":
                    if not self[columns[0]].isbool():
                        agg = (
                            self[columns[0]]
                            .aggregate(["approx_unique", "min", "max"])
                            .values[columns[0]]
                        )
                        if (agg[0] != 2) or (agg[1] != 0) or (agg[2] != 1):
                            return np.nan
                    column_b, column_n = columns[0], columns[1]
                    cast_b_b, cast_n_b = cast_0_b, cast_1_b
                    cast_b_e, cast_n_e = cast_0_e, cast_1_e
                else:
                    return np.nan
                query = f"""
                    SELECT 
                        /*+LABEL('VastFrame._aggregate_matrix')*/
                       1.0000000 * ( 
                         AVG(1.0000000 * CASE {cast_b_b}{column_b}{cast_b_e} WHEN 1 THEN {cast_n_b}{column_n}{cast_n_e} END) 
                       - AVG(1.0000000 * CASE {cast_b_b}{column_b}{cast_b_e} WHEN 0 THEN {cast_n_b}{column_n}{cast_n_e} END)
                       ) 
                       / NULLIF(STDDEV({cast_n_b}{column_n}{cast_n_e}), 0)
                       * SQRT(1.0000000 * SUM({cast_b_b}{column_b}{cast_b_e}) 
                       * SUM(1 - {cast_b_b}{column_b}{cast_b_e}) 
                       / NULLIF(COUNT(*), 0) / NULLIF(COUNT(*), 0))
                    FROM {self} 
                    WHERE {column_b} IS NOT NULL 
                      AND {column_n} IS NOT NULL;"""
                title = (
                    "Computes the biserial correlation "
                    f"between {column_b} and {column_n}."
                )
            elif method == "cramer":
                if columns[1] == columns[0]:
                    return 1
                n, k, r = _executeSQL(
                    query=f"""
                        SELECT /*+LABEL('VastFrame._aggregate_matrix')*/
                            COUNT(*) AS n, 
                            COUNT(DISTINCT {columns[0]}) AS k, 
                            COUNT(DISTINCT {columns[1]}) AS r 
                         FROM {self} 
                         WHERE {columns[0]} IS NOT NULL 
                           AND {columns[1]} IS NOT NULL""",
                    title="Computing the columns cardinalities.",
                    method="fetchrow",
                )
                chi2_sql = f"""
                    WITH all_categories AS (
                        SELECT * FROM
                        (SELECT 
                            DISTINCT {columns[0]} 
                         FROM {self} WHERE {columns[0]} IS NOT NULL) table_0
                        CROSS JOIN
                        (SELECT 
                            DISTINCT {columns[1]}
                         FROM {self} WHERE {columns[1]} IS NOT NULL) table_1
                    ), categories_counts AS (
                        SELECT 
                            {columns[0]},
                            {columns[1]},
                            COUNT(*) AS _nij
                        FROM {self}
                        WHERE 
                            {columns[0]} IS NOT NULL
                        AND {columns[1]} IS NOT NULL
                        GROUP BY 1, 2
                    ), contingent_table AS (
                        SELECT 
                            all_categories.{columns[0]},
                            all_categories.{columns[1]},
                            COALESCE(_nij, 0) AS _nij
                        FROM all_categories 
                        LEFT JOIN categories_counts
                        ON  all_categories.{columns[0]} = categories_counts.{columns[0]}
                        AND all_categories.{columns[1]} = categories_counts.{columns[1]}
                    ), expected_values AS (
                        SELECT
                            _nij AS O,
                              SUM(_nij) OVER(PARTITION BY {columns[0]}) 
                            * SUM(_nij) OVER(PARTITION BY {columns[1]})
                            / NULLIF(SUM(_nij) OVER (), 0) AS E
                        FROM contingent_table
                    )
                    SELECT
                        SUM((POWER(O - E, 2) / NULLIF(E, 0))) 
                    FROM expected_values;"""
                chi2 = _executeSQL(
                    chi2_sql,
                    title=(
                        f"Computing the CramerV correlation between {columns[0]} "
                        f"and {columns[1]} (Chi2 Statistic)."
                    ),
                    method="fetchfirstelem",
                )
                if isinstance(chi2, NoneType):
                    return np.nan
                phi2 = chi2 / n
                phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
                rcorr = r - ((r - 1) ** 2) / (n - 1)
                kcorr = k - ((k - 1) ** 2) / (n - 1)
                div = min((kcorr - 1), (rcorr - 1))
                if div == 0:
                    return np.nan
                return np.sqrt(phi2corr / div)
            elif method == "kendall":
                if columns[1] == columns[0]:
                    return 1
                n_ = "SQRT(COUNT(*))"
                n_c = f"""
                    (SUM(CAST((({cast_0_b}x.{columns[0]}{cast_0_e} < {cast_0_b}y.{columns[0]}{cast_0_e} 
                       AND {cast_1_b}x.{columns[1]}{cast_1_e} < {cast_1_b}y.{columns[1]}{cast_1_e}) 
                       OR ({cast_0_b}x.{columns[0]}{cast_0_e} > {cast_0_b}y.{columns[0]}{cast_0_e} 
                       AND {cast_1_b}x.{columns[1]}{cast_1_e} > {cast_1_b}y.{columns[1]}{cast_1_e})) AS INT)))/2"""
                n_d = f"""
                    (SUM(CAST((({cast_0_b}x.{columns[0]}{cast_0_e} > {cast_0_b}y.{columns[0]}{cast_0_e} 
                       AND {cast_1_b}x.{columns[1]}{cast_1_e} < {cast_1_b}y.{columns[1]}{cast_1_e}) 
                       OR ({cast_0_b}x.{columns[0]}{cast_0_e} < {cast_0_b}y.{columns[0]}{cast_0_e}
                       AND {cast_1_b}x.{columns[1]}{cast_1_e} > {cast_1_b}y.{columns[1]}{cast_1_e})) AS INT)))/2"""
                n_1 = f"(SUM(CAST(({cast_0_b}x.{columns[0]}{cast_0_e} = {cast_0_b}y.{columns[0]}{cast_0_e}) AS INT))-{n_})/2"
                n_2 = f"(SUM(CAST(({cast_1_b}x.{columns[1]}{cast_1_e} = {cast_1_b}y.{columns[1]}{cast_1_e}) AS INT))-{n_})/2"
                n_0 = f"{n_} * ({n_} - 1)/2"
                tau_b = f"({n_c} - {n_d}) / sqrt(({n_0} - {n_1}) * ({n_0} - {n_2}))"
                query = f"""
                    SELECT /*+LABEL('VastFrame._aggregate_matrix')*/
                        {tau_b} 
                    FROM 
                        (SELECT 
                            {columns[0]}, 
                            {columns[1]} 
                         FROM {self}) x 
                        CROSS JOIN 
                        (SELECT 
                            {columns[0]}, 
                            {columns[1]} 
                         FROM {self}) y"""
                title = f"Computing the kendall correlation between {columns[0]} and {columns[1]}."
            elif method == "cov":
                query = f"""
                    SELECT /*+LABEL('VastFrame._aggregate_matrix')*/ 
                        COVAR_POP({cast_0_b}{columns[0]}{cast_0_e}, {cast_1_b}{columns[1]}{cast_1_e}) 
                    FROM {self}"""
                title = (
                    f"Computing the covariance between {columns[0]} and {columns[1]}."
                )
            try:
                result = _executeSQL(
                    query=query,
                    title=title,
                    method="fetchfirstelem",
                )
            except QueryError:
                result = np.nan
            self._update_catalog(
                values={columns[1]: result}, matrix=method, column=columns[0]
            )
            self._update_catalog(
                values={columns[0]: result}, matrix=method, column=columns[1]
            )
            if isinstance(result, decimal.Decimal):
                result = float(result)
            return result
        elif len(columns) > 2:
            nb_precomputed, n = 0, len(columns)
            for column1 in columns:
                for column2 in columns:
                    pre_comp_val = self._get_catalog_value(
                        method=method, columns=[column1, column2]
                    )
                    if pre_comp_val != "VASTORBIT_NOT_PRECOMPUTED":
                        nb_precomputed += 1

            if method in (
                "pearson",
                "spearman",
                "spearmand",
                "kendall",
                "biserial",
                "cramer",
            ):
                title = "Computing all Correlations in a single query"
                if method == "biserial":
                    i0, step = 0, 1
                else:
                    i0, step = 1, 0
            elif method == "cov":
                title = "Computing all covariances in a single query"
                i0, step = 0, 1
            n = len(columns)
            loop = tqdm(range(i0, n)) if conf.get_option("tqdm") else range(i0, n)
            try:
                all_list = []
                nb_precomputed = 0
                nb_loop = 0
                for i in loop:
                    for j in range(0, i + step):
                        nb_loop += 1
                        cast_i_b = "CAST(" if (self[columns[i]].isbool()) else ""
                        cast_i_e = " AS INT)" if (self[columns[i]].isbool()) else ""
                        cast_j_b = "CAST(" if (self[columns[j]].isbool()) else ""
                        cast_j_e = " AS INT)" if (self[columns[j]].isbool()) else ""
                        pre_comp_val = self._get_catalog_value(
                            method=method, columns=[columns[i], columns[j]]
                        )
                        if (
                            isinstance(pre_comp_val, NoneType)
                            or pre_comp_val != pre_comp_val
                        ):
                            pre_comp_val = "NULL"
                        if pre_comp_val != "VASTORBIT_NOT_PRECOMPUTED":
                            all_list += [str(pre_comp_val)]
                            nb_precomputed += 1
                        elif method in ("pearson", "spearman", "spearmand"):
                            all_list += [
                                f"""CORR({cast_i_b}{columns[i]}{cast_i_e}, {cast_j_b}{columns[j]}{cast_j_e})"""
                            ]
                        elif method == "kendall":
                            n_ = "SQRT(COUNT(*))"
                            n_c = f"""
                                (SUM(CAST(((
                                       {cast_i_b}x.{columns[i]}{cast_i_e} 
                                     < {cast_i_b}y.{columns[i]}{cast_i_e} 
                                   AND {cast_j_b}x.{columns[j]}{cast_j_e} 
                                     < {cast_j_b}y.{columns[j]}{cast_j_e})
                                   OR ({cast_i_b}x.{columns[i]}{cast_i_e} 
                                     > {cast_i_b}y.{columns[i]}{cast_i_e} 
                                   AND {cast_j_b}x.{columns[j]}{cast_j_e} 
                                     > {cast_j_b}y.{columns[j]}{cast_j_e})) AS INT)))/2"""
                            n_d = f"""
                                (SUM(CAST(((
                                       {cast_i_b}x.{columns[i]}{cast_i_e} 
                                     > {cast_i_b}y.{columns[i]}{cast_i_e} 
                                   AND {cast_j_b}x.{columns[j]}{cast_j_e} 
                                     < {cast_j_b}y.{columns[j]}{cast_j_e}) 
                                   OR ({cast_i_b}x.{columns[i]}{cast_i_e} 
                                     < {cast_i_b}y.{columns[i]}{cast_i_e} 
                                   AND {cast_j_b}x.{columns[j]}{cast_j_e} 
                                     > {cast_j_b}y.{columns[j]}{cast_j_e})) AS INT)))/2"""
                            n_1 = f"""
                                (SUM(CAST(({cast_i_b}x.{columns[i]}{cast_i_e} = 
                                           {cast_i_b}y.{columns[i]}{cast_i_e}) AS INT))-{n_})/2"""
                            n_2 = f"""(SUM(CAST((
                                      {cast_j_b}x.{columns[j]}{cast_j_e} = 
                                      {cast_j_b}y.{columns[j]}{cast_j_e}) AS INT))-{n_})/2"""
                            n_0 = f"{n_} * ({n_} - 1)/2"
                            tau_b = f"({n_c} - {n_d}) / sqrt(({n_0} - {n_1}) * ({n_0} - {n_2}))"
                            all_list += [tau_b]
                        elif method == "cov":
                            all_list += [
                                f"COVAR_POP({cast_i_b}{columns[i]}{cast_i_e}, {cast_j_b}{columns[j]}{cast_j_e})"
                            ]
                        else:
                            assert False
                if method in ("spearman", "spearmand"):
                    fun = "DENSE_RANK" if method == "spearmand" else "RANK"
                    rank = [
                        f"{fun}() OVER (ORDER BY {column}) AS {column}"
                        for column in columns
                    ]
                    table = (
                        f"(SELECT {', '.join(rank)} FROM {self}) rank_spearman_table"
                    )
                elif method == "kendall":
                    table = f"""
                                       (SELECT {", ".join(columns)} FROM {self}) x 
                            CROSS JOIN (SELECT {", ".join(columns)} FROM {self}) y"""
                else:
                    table = self._genSQL()
                if nb_precomputed == nb_loop:
                    result = _executeSQL(
                        query=f"""
                            SELECT 
                                /*+LABEL('VastFrame._aggregate_matrix')*/ 
                                {', '.join(all_list)}""",
                        print_time_sql=False,
                        method="fetchrow",
                    )
                else:
                    result = _executeSQL(
                        query=f"""
                            SELECT 
                                /*+LABEL('VastFrame._aggregate_matrix')*/ 
                                {', '.join(all_list)} 
                            FROM {table}""",
                        title=title,
                        method="fetchrow",
                    )
            except (AssertionError, QueryError):
                n = len(columns)
                result = []
                for i in loop:
                    for j in range(0, i + step):
                        result += [
                            self._aggregate_matrix(method, [columns[i], columns[j]])
                        ]
            matrix = np.array([[1.0 for i in range(0, n)] for i in range(0, n)])
            k = 0
            for i in range(i0, n):
                for j in range(0, i + step):
                    current = result[k]
                    k += 1
                    if isinstance(current, NoneType):
                        current = np.nan
                    matrix[i][j] = current
                    matrix[j][i] = current
            if show:
                vmin = 0 if (method == "cramer") else -1
                if method == "cov":
                    vmin = None
                vmax = (
                    1
                    if (
                        method
                        in (
                            "pearson",
                            "spearman",
                            "spearmand",
                            "kendall",
                            "biserial",
                            "cramer",
                        )
                    )
                    else None
                )
                vo_plt, kwargs = self.get_plotting_lib(
                    class_name="HeatMap",
                    chart=chart,
                    style_kwargs=style_kwargs,
                )
                data = {"X": matrix}
                layout = {
                    "columns": [None, None],
                    "method": method,
                    "x_labels": columns,
                    "y_labels": columns,
                    "vmax": vmax,
                    "vmin": vmin,
                    "mround": mround,
                    "with_numbers": with_numbers,
                }
                return vo_plt.HeatMap(data=data, layout=layout).draw(**kwargs)
            values = {"index": columns}
            for idx in range(len(matrix)):
                values[columns[idx]] = list(matrix[:, idx])
            for column1 in values:
                if column1 != "index":
                    val = {}
                    for idx, column2 in enumerate(values["index"]):
                        val[column2] = values[column1][idx]
                    self._update_catalog(values=val, matrix=method, column=column1)
            return TableSample(values=values).decimal_to_float()
        else:
            if method == "cramer":
                cols = self.catcol()
                assert len(cols) != 0, EmptyParameter(
                    "No categorical column found in the VastFrame."
                )
            else:
                cols = self.numcol()
                assert len(cols) != 0, EmptyParameter(
                    "No numerical column found in the VastFrame."
                )
            return self._aggregate_matrix(
                method=method,
                columns=cols,
                mround=mround,
                show=show,
                **style_kwargs,
            )

    def _aggregate_vector(
        self,
        focus: str,
        method: str = "pearson",
        columns: Optional[SQLColumns] = None,
        mround: int = 3,
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        with_numbers: bool = True,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Global method used to compute the Correlation/Cov/Beta Vector.
        """
        if not columns:
            if method == "cramer":
                cols = self.catcol()
                assert cols, EmptyParameter(
                    "No categorical column found in the VastFrame."
                )
            else:
                cols = self.numcol()
                assert cols, EmptyParameter(
                    "No numerical column found in the VastFrame."
                )
        else:
            cols = self.format_colnames(columns)
        if method != "cramer":
            method_name = "Correlation"
            method_type = f" using the method = '{method}'"
            if method == "cov":
                method_name = "Covariance"
                method_type = ""
            for column in cols:
                assert self[column].isnum(), TypeError(
                    f"VastColumn '{column}' must be numerical to "
                    f"compute the {method_name} Vector{method_type}."
                )
        if method in ("spearman", "spearmand", "pearson", "kendall", "cov") and (
            len(cols) >= 1
        ):
            try:
                fail = 0
                cast_i_b = "CAST(" if (self[focus].isbool()) else ""
                cast_i_e = "AS INT)" if (self[focus].isbool()) else ""
                all_list, all_cols = [], [focus]
                nb_precomputed = 0
                for column in cols:
                    if (
                        column.replace('"', "").lower()
                        != focus.replace('"', "").lower()
                    ):
                        all_cols += [column]
                    cast_j_b = "CAST(" if (self[column].isbool()) else ""
                    cast_j_e = "AS INT)" if (self[column].isbool()) else ""
                    pre_comp_val = self._get_catalog_value(
                        method=method, columns=[focus, column]
                    )
                    if (
                        isinstance(pre_comp_val, NoneType)
                        or pre_comp_val != pre_comp_val
                    ):
                        pre_comp_val = "NULL"
                    if pre_comp_val != "VASTORBIT_NOT_PRECOMPUTED":
                        all_list += [str(pre_comp_val)]
                        nb_precomputed += 1
                    elif method in ("pearson", "spearman", "spearmand"):
                        all_list += [
                            f"CORR({cast_i_b}{focus}{cast_i_e}, {cast_j_b}{column}{cast_j_e})"
                        ]
                    elif method == "kendall":
                        n = "SQRT(COUNT(*))"
                        n_c = f"""
                            (SUM(CAST(((
                                   {cast_i_b}x.{focus}{cast_i_e} 
                                 < {cast_i_b}y.{focus}{cast_i_e} 
                               AND {cast_j_b}x.{column}{cast_j_e}
                                 < {cast_j_b}y.{column}{cast_j_e})
                               OR ({cast_i_b}x.{focus}{cast_i_e} 
                                 > {cast_i_b}y.{focus}{cast_i_e} 
                               AND {cast_j_b}x.{column}{cast_j_e} 
                                 > {cast_j_b}y.{column}{cast_j_e})) AS DOUBLE)))/2"""
                        n_d = f"""
                            (SUM(CAST(((
                                   {cast_i_b}x.{focus}{cast_i_e} 
                                 > {cast_i_b}y.{focus}{cast_i_e} 
                               AND {cast_j_b}x.{column}{cast_j_e} 
                                 < {cast_j_b}y.{column}{cast_j_e})
                               OR ({cast_i_b}x.{focus}{cast_i_e}
                                 < {cast_i_b}y.{focus}{cast_i_e}
                               AND {cast_j_b}x.{column}{cast_j_e} 
                                 > {cast_j_b}y.{column}{cast_j_e})) AS DOUBLE)))/2"""
                        n_1 = f"(SUM(CAST(({cast_i_b}x.{focus}{cast_i_e} = {cast_i_b}y.{focus}{cast_i_e}) AS DOUBLE))-{n})/2"
                        n_2 = f"(SUM(CAST(({cast_j_b}x.{column}{cast_j_e} = {cast_j_b}y.{column}{cast_j_e}) AS DOUBLE))-{n})/2"
                        n_0 = f"{n} * ({n} - 1)/2"
                        tau_b = (
                            f"({n_c} - {n_d}) / sqrt(({n_0} - {n_1}) * ({n_0} - {n_2}))"
                        )
                        all_list += [tau_b]
                    elif method == "cov":
                        all_list += [
                            f"COVAR_POP({cast_i_b}{focus}{cast_i_e}, {cast_j_b}{column}{cast_j_e})"
                        ]
                if method in ("spearman", "spearmand"):
                    fun = "DENSE_RANK" if method == "spearmand" else "RANK"
                    rank = [
                        f"{fun}() OVER (ORDER BY {column}) AS {column}"
                        for column in all_cols
                    ]
                    table = (
                        f"(SELECT {', '.join(rank)} FROM {self}) rank_spearman_table"
                    )
                elif method == "kendall":
                    table = f"""
                        (SELECT {", ".join(all_cols)} FROM {self}) x 
             CROSS JOIN (SELECT {", ".join(all_cols)} FROM {self}) y"""
                else:
                    table = self._genSQL()
                if nb_precomputed == len(cols):
                    result = _executeSQL(
                        query=f"""
                            SELECT 
                                /*+LABEL('VastFrame._aggregate_vector')*/ 
                                {', '.join(all_list)}""",
                        method="fetchrow",
                        print_time_sql=False,
                    )
                else:
                    result = _executeSQL(
                        query=f"""
                            SELECT 
                                /*+LABEL('VastFrame._aggregate_vector')*/ 
                                {', '.join(all_list)} 
                            FROM {table} 
                            LIMIT 1""",
                        title=f"Computing the Correlation Vector ({method})",
                        method="fetchrow",
                    )
                matrix = copy.deepcopy(result)
            except QueryError:
                fail = 1
        if not (
            method in ("spearman", "spearmand", "pearson", "kendall", "cov")
            and (len(cols) >= 1)
        ) or (fail):
            matrix = []
            for column in cols:
                if column.replace('"', "").lower() == focus.replace(
                    '"', ""
                ).lower() and method in ("spearman", "spearmand", "pearson", "kendall"):
                    matrix += [1.0]
                else:
                    matrix += [
                        self._aggregate_matrix(method=method, columns=[column, focus])
                    ]
        matrix = [np.nan if isinstance(x, NoneType) else x for x in matrix]
        data = [(cols[i], float(matrix[i])) for i in range(len(matrix))]
        data.sort(key=lambda tup: abs(tup[1]), reverse=True)
        cols = [x[0] for x in data]
        matrix = np.array([[x[1] for x in data]])
        if show:
            vmin = 0 if (method == "cramer") else -1
            if method == "cov":
                vmin = None
            vmax = (
                1
                if (
                    method
                    in (
                        "pearson",
                        "spearman",
                        "spearmand",
                        "kendall",
                        "biserial",
                        "cramer",
                    )
                )
                else None
            )
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="HeatMap",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            data = {"X": matrix}
            layout = {
                "columns": [None, None],
                "method": method,
                "x_labels": [focus],
                "y_labels": cols,
                "vmax": vmax,
                "vmin": vmin,
                "mround": mround,
                "with_numbers": with_numbers,
            }
            return vo_plt.HeatMap(data=data, layout=layout).draw(**kwargs)
        for idx, column in enumerate(cols):
            self._update_catalog(
                values={focus: matrix[0][idx]}, matrix=method, column=column
            )
            self._update_catalog(
                values={column: matrix[0][idx]}, matrix=method, column=focus
            )
        return TableSample(
            values={"index": cols, focus: list(matrix[0])}
        ).decimal_to_float()

    # Correlation.

    @save_vastorbit_logs
    def corr(
        self,
        columns: Optional[SQLColumns] = None,
        method: Literal[
            "pearson", "kendall", "spearman", "spearmand", "biserial", "cramer"
        ] = "pearson",
        mround: int = 3,
        focus: Optional[str] = None,
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        with_numbers: bool = True,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Calculates the Correlation Matrix for the VastFrame.  This matrix
        provides  insights  into  how  different numerical columns in  the
        dataset are correlated with each other.  It helps in understanding
        the relationships and dependencies between variables, facilitating
        data  analysis  and  decision-making.  The correlation matrix is a
        valuable  tool  for identifying patterns,  trends,  and  potential
        associations within the dataset.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all
            numerical VastColumns are used.
        method: str, optional
            Method to use to compute the correlation.

             - pearson:
                Pearson's  correlation coefficient (linear).
             - spearman:
                Spearman's correlation coefficient (monotonic
                - rank based).
             - spearmanD:
                Spearman's correlation coefficient using the
                DENSE  RANK  function instead of the RANK
                function.
             - kendall:
                Kendall's  correlation coefficient (similar
                trends).  The method computes the Tau-B
                coefficient.

                .. warning::

                    This method  uses a CROSS JOIN  during  computation
                    and      is     therefore computationally expensive
                    at  O(n * n),  where n is the  total  count of  the
                    :py:class:`~VastFrame`.

             - cramer:
                Cramer's V (correlation between categories).
             - biserial:
                Biserial Point (correlation between binaries
                and a numericals).

        mround: int, optional
            Rounds  the coefficient using  the input number of
            digits. This is only used to display the correlation
            matrix.
        focus: str, optional
            Focus  the  computation  on  one  VastColumn.
        show: bool, optional
            If  set  to  True,  the  Plotting  object  is
            returned.
        chart: PlottingObject, optional
            The chart object used to plot.
        ``**style_kwargs``
            Any  optional  parameter  to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        Import `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Import `numpy` to create a random dataset.

        .. ipython:: python

            import numpy as np

        Generate a dataset using the following data.

        .. code-block:: python

            N = 30 # Number of records

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                    "score4": np.random.normal(14, 3, N),
                }
            )

        Draw the Pearson correlation matrix.

        .. code-block:: python

            data.corr(method = "pearson")

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            import numpy as np
            vo.set_option("plotting_lib", "plotly")
            N = 30 # Number of records
            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                    "score4": np.random.normal(14, 3, N),
                }
            )
            fig = data.corr(method = "pearson")
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_corr_matrix.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_corr_matrix.html

        You can also use the parameter focus to only compute a correlation vector.

        .. code-block:: python

            data.corr(method = "pearson", focus = "score1")

        .. ipython:: python
            :suppress:

            fig = data.corr(method = "pearson", focus = "score1")
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_corr_vector.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_corr_vector.html

        It is less expensive and it allows you to focus your search on one specific
        column.

        For more examples, please look at the :ref:`chart_gallery.corr` page of the
        :ref:`chart_gallery`.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.corr_pvalue` : Computes correlation and its p-value.
        """
        method = str(method).lower()
        columns = format_type(columns, dtype=list, na_out=self.numcol())
        columns, focus = self.format_colnames(columns, focus)
        fun = self._aggregate_matrix
        args = []
        kwargs = {
            "method": method,
            "columns": columns,
            "mround": mround,
            "show": show,
            "chart": chart,
            "with_numbers": with_numbers,
            **style_kwargs,
        }
        if focus:
            args += [focus]
            fun = self._aggregate_vector
        return fun(*args, **kwargs)

    @save_vastorbit_logs
    def corr_pvalue(
        self,
        column1: str,
        column2: str,
        method: Literal[
            "pearson",
            "kendall",
            "kendalla",
            "kendallb",
            "kendallc",
            "spearman",
            "spearmand",
            "biserial",
            "cramer",
        ] = "pearson",
    ) -> tuple[float, float]:
        """
        Computes the Correlation  Coefficient  between two input
        VastColumns,  along  with its  associated p-value. This
        calculation  helps  assess the  strength  and  direction
        of the relationship between the two columns and provides
        statistical significance through the p-value.

        Parameters
        ----------
        column1: str
            Input VastColumn.
        column2: str
            Input VastColumn.
        method: str, optional
            Method to use to compute the correlation.

             - pearson:
                Pearson's  correlation coefficient (linear).
             - spearman:
                Spearman's correlation coefficient (monotonic
                - rank based).
             - spearmanD:
                Spearman's correlation coefficient using the
                DENSE  RANK  function instead of the RANK
                function.
             - kendall:
                Kendall's  correlation coefficient (similar
                trends).  The method computes the Tau-B
                coefficient.

                .. warning::

                    This method  uses a CROSS JOIN  during  computation
                    and      is     therefore computationally expensive
                    at  O(n * n),  where n is the  total  count of  the
                    :py:class:`~VastFrame`.
             - cramer:
                Cramer's V (correlation between categories).
             - biserial:
                Biserial Point (correlation between binaries
                and a numericals).

        Returns
        -------
        tuple
            (Correlation Coefficient, pvalue)

        Examples
        --------
        For this example, let's generate a dataset and compute
        the Pearson correlation coefficient and its p-value
        between the two features: 'x' and 'y'.

        .. ipython:: python

            import vastorbit as vo

            data = vo.VastFrame(
                {
                    "x": [1, 2, 4, 9, 10, 15, 20, 22],
                    "y": [1, 2, 1, 2, 1, 1, 2, 1],
                    "z": [10, 12, 2, 1, 9, 8, 1, 3],
                }
            )
            data.corr_pvalue(
                column1 = "x",
                column2 = "y",
                method = "pearson",
            )

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.corr` : Computes the correlation matrix.
        """
        method = str(method).lower()
        column1, column2 = self.format_colnames(column1, column2)
        if method.startswith("kendall"):
            if method == "kendall":
                kendall_type = "b"
            else:
                kendall_type = method[-1]
            method = "kendall"
        else:
            kendall_type = None
        val = 0.0
        if (method == "kendall" and kendall_type == "b") or (method != "kendall"):
            val = self.corr(columns=[column1, column2], method=method)
        sql = f"""
            SELECT 
                /*+LABEL('VastFrame.corr_pvalue')*/ COUNT(*) 
            FROM {self} 
            WHERE {column1} IS NOT NULL AND {column2} IS NOT NULL;"""
        n = _executeSQL(
            sql,
            title="Computing the number of elements.",
            method="fetchfirstelem",
        )
        if method in ("pearson", "biserial"):
            x = val * math.sqrt((n - 2) / (1 - val * val))
            pvalue = 2 * scipy_st.t.sf(abs(x), n - 2)
        elif method in ("spearman", "spearmand"):
            z = math.sqrt((n - 3) / 1.06) * 0.5 * np.log((1 + val) / (1 - val))
            pvalue = 2 * scipy_st.norm.sf(abs(z))
        elif method == "kendall":
            cast_i_b = "CAST(" if (self[column1].isbool()) else ""
            cast_i_e = " AS INT)" if (self[column1].isbool()) else ""
            cast_j_b = "CAST(" if (self[column2].isbool()) else ""
            cast_j_e = " AS INT)" if (self[column2].isbool()) else ""
            n_c = f"""
                (SUM(CAST(
                    (({cast_i_b}x.{column1}{cast_i_e} < {cast_i_b}y.{column1}{cast_i_e} 
                      AND {cast_j_b}x.{column2}{cast_j_e} < {cast_j_b}y.{column2}{cast_j_e})
                     OR ({cast_i_b}x.{column1}{cast_i_e} > {cast_i_b}y.{column1}{cast_i_e}
                      AND {cast_j_b}x.{column2}{cast_j_e} > {cast_j_b}y.{column2}{cast_j_e}))
                    AS DOUBLE)) / 2)"""

            n_d = f"""
                (SUM(CAST(
                    (({cast_i_b}x.{column1}{cast_i_e} > {cast_i_b}y.{column1}{cast_i_e}
                      AND {cast_j_b}x.{column2}{cast_j_e} < {cast_j_b}y.{column2}{cast_j_e})
                     OR ({cast_i_b}x.{column1}{cast_i_e} < {cast_i_b}y.{column1}{cast_i_e} 
                      AND {cast_j_b}x.{column2}{cast_j_e} > {cast_j_b}y.{column2}{cast_j_e}))
                    AS DOUBLE)) / 2)"""
            table = f"""
                (SELECT 
                    {", ".join([column1, column2])} 
                 FROM {self}) x 
                CROSS JOIN 
                (SELECT 
                    {", ".join([column1, column2])} 
                 FROM {self}) y"""
            nc, nd = _executeSQL(
                query=f"""
                    SELECT 
                        /*+LABEL('VastFrame.corr_pvalue')*/ 
                        CAST({n_c} AS DOUBLE), 
                        CAST({n_d} AS DOUBLE) 
                    FROM {table};""",
                title="Computing nc and nd.",
                method="fetchrow",
            )
            if kendall_type in ("a", ""):
                val = (nc - nd) / (n * (n - 1) / 2)
                Z = 3 * (nc - nd) / math.sqrt(n * (n - 1) * (2 * n + 5) / 2)
            elif kendall_type in ("b", "c"):
                vt, v1_0, v2_0 = _executeSQL(
                    query=f"""
                        SELECT 
                            /*+LABEL('VastFrame.corr_pvalue')*/
                            SUM(ni * (ni - 1) * (2 * ni + 5)), 
                            SUM(ni * (ni - 1)), 
                            SUM(ni * (ni - 1) * (ni - 2)) 
                        FROM 
                            (SELECT 
                                {column1}, 
                                COUNT(*) AS ni 
                             FROM {self} 
                             GROUP BY 1) VASTORBIT_SUBTABLE""",
                    title="Computing vti.",
                    method="fetchrow",
                )
                vu, v1_1, v2_1 = _executeSQL(
                    query=f"""
                        SELECT 
                            /*+LABEL('VastFrame.corr_pvalue')*/
                            SUM(ni * (ni - 1) * (2 * ni + 5)), 
                            SUM(ni * (ni - 1)), 
                            SUM(ni * (ni - 1) * (ni - 2)) 
                       FROM 
                            (SELECT 
                                {column2}, 
                                COUNT(*) AS ni 
                             FROM {self} 
                             GROUP BY 1) VASTORBIT_SUBTABLE""",
                    title="Computing vui.",
                    method="fetchrow",
                )
                v0 = n * (n - 1) * (2 * n + 5)
                v1 = v1_0 * v1_1 / (2 * n * (n - 1))
                v2 = v2_0 * v2_1 / (9 * n * (n - 1) * (n - 2))
                Z = (nc - nd) / math.sqrt((v0 - vt - vu) / 18 + v1 + v2)
                if kendall_type == "c":
                    k, r = _executeSQL(
                        query=f"""
                            SELECT /*+LABEL('VastFrame.corr_pvalue')*/
                                APPROX_DISTINCT({column1}) AS k, 
                                APPROX_DISTINCT({column2}) AS r 
                            FROM {self} 
                            WHERE {column1} IS NOT NULL 
                              AND {column2} IS NOT NULL""",
                        title="Computing the columns categories in the pivot table.",
                        method="fetchrow",
                    )
                    m = min(k, r)
                    val = 2 * (nc - nd) / (n * n * (m - 1) / m)
            pvalue = 2 * scipy_st.norm.sf(abs(Z))
        elif method == "cramer":
            k, r = _executeSQL(
                query=f"""
                    SELECT /*+LABEL('VastFrame.corr_pvalue')*/
                        COUNT(DISTINCT {column1}) AS k, 
                        COUNT(DISTINCT {column2}) AS r 
                    FROM {self} 
                    WHERE {column1} IS NOT NULL 
                      AND {column2} IS NOT NULL""",
                title="Computing the columns categories in the pivot table.",
                method="fetchrow",
            )
            x = val * val * n * min(k, r)
            pvalue = scipy_st.chi2.sf(x, (k - 1) * (r - 1))
        else:
            raise ValueError(f"{method} is not a valid method.")

        return (val, pvalue)

    # Covariance.

    @save_vastorbit_logs
    def cov(
        self,
        columns: Optional[SQLColumns] = None,
        focus: Optional[str] = None,
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Computes the covariance matrix of the VastFrame. This matrix
        summarizes the covariances  between pairs of variables in the
        dataset, shedding light on  how variables move in relation to
        each  other.  It's an  important tool  in  understanding  the
        relationships  and interactions between variables, which  can
        be used for various statistical analyses and modeling tasks.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all numerical
            VastColumns are used.
        focus: str, optional
            Focus the computation on one VastColumn.
        show: bool, optional
            If   set  to   True,  the   Plotting   object  is
            returned.
        chart: PlottingObject, optional
            The chart object used to plot.
        ``**style_kwargs``
            Any   optional  parameter  to  pass  to  the   plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        Import `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Import `numpy` to create a random dataset.

        .. ipython:: python

            import numpy as np

        Generate a dataset using the following data.

        .. code-block:: python

            N = 30 # Number of records

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                    "score4": np.random.normal(14, 3, N),
                }
            )

        Draw the covariance matrix.

        .. code-block:: python

            data.cov()

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            import numpy as np
            vo.set_option("plotting_lib", "plotly")
            N = 30 # Number of records
            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                    "score4": np.random.normal(14, 3, N),
                }
            )
            fig = data.cov()
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_cov_matrix.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_cov_matrix.html

        You can also use the parameter focus to only compute a covariance vector.

        .. code-block:: python

            data.cov(method = "pearson", focus = "score1")

        .. ipython:: python
            :suppress:

            fig = data.cov(method = "pearson", focus = "score1")
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_cov_vector.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_cov_vector.html

        It is less expensive and it allows you to focus your search on one specific
        column.

        For more examples, please look at the :ref:`chart_gallery.corr` page of the
        :ref:`chart_gallery`. Those ones are related to correlation matrix, but the
        customization stays the same for the covariance matrix.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.corr` : Computes the correlation matrix.
        """
        columns = format_type(columns, dtype=list)
        columns, focus = self.format_colnames(columns, focus)
        fun = self._aggregate_matrix
        args = []
        kwargs = {
            "method": "cov",
            "columns": columns,
            "show": show,
            "chart": chart,
            **style_kwargs,
        }
        if focus:
            args += [focus]
            fun = self._aggregate_vector

        return fun(*args, **kwargs)

    # Regression Metrics.

    @save_vastorbit_logs
    def regr(
        self,
        columns: Optional[SQLColumns] = None,
        method: Literal[
            "avgx",
            "avgy",
            "count",
            "intercept",
            "r2",
            "slope",
            "sxx",
            "sxy",
            "syy",
            "beta",
            "alpha",
        ] = "r2",
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Calculates the regression matrix for the given VastFrame.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all numerical
            VastColumns are used.
        method: str, optional
            Method to use to compute the regression matrix.

             - avgx: Average of independent expression
             - avgy: Average of dependent expression
             - count: Count of all non-NULL rows
             - alpha / intercept: Intercept
             - beta / slope: Slope
             - r2: R-squared coefficient
             - sxx: Sum of squares of independent
             - sxy: Sum of products
             - syy: Sum of squares of dependent

        show: bool, optional
            If set to True, the Plotting object is returned.
        chart: PlottingObject, optional
            The chart object used to plot.
        ``**style_kwargs``
            Any optional parameter to pass to the plotting functions.

        Returns
        -------
        obj
            Plotting Object.
        """
        columns = format_type(columns, dtype=list)

        # Map beta/alpha to slope/intercept
        if method == "beta":
            method = "slope"
        elif method == "alpha":
            method = "intercept"

        # Validate columns
        if not columns:
            columns = self.numcol()
            assert columns, EmptyParameter(
                "No numerical column found in the VastFrame."
            )

        columns = self.format_colnames(columns)
        for column in columns:
            assert self[column].isnum(), TypeError(
                f"VastColumn {column} must be numerical to compute the Regression Matrix."
            )

        n = len(columns)
        all_list = []
        nb_precomputed = 0

        # Build SQL expressions for each cell in the matrix
        for i in range(n):
            for j in range(n):
                col_i = columns[i]
                col_j = columns[j]

                # Handle boolean columns with CAST
                if self[col_i].isbool():
                    col_i_expr = f"CAST({col_i} AS INTEGER)"
                else:
                    col_i_expr = col_i

                if self[col_j].isbool():
                    col_j_expr = f"CAST({col_j} AS INTEGER)"
                else:
                    col_j_expr = col_j

                # Check precomputed values
                pre_comp_val = self._get_catalog_value(
                    method=f"regr_{method}", columns=[columns[i], columns[j]]
                )

                if isinstance(pre_comp_val, NoneType) or pre_comp_val != pre_comp_val:
                    pre_comp_val = "NULL"

                if pre_comp_val != "VASTORBIT_NOT_PRECOMPUTED":
                    all_list.append(str(pre_comp_val))
                    nb_precomputed += 1
                else:
                    # Generate SQL expression
                    sql_expr = self._get_regr_sql(method, col_i_expr, col_j_expr)
                    all_list.append(sql_expr)

        # Execute query
        try:
            if nb_precomputed == n * n:
                result = _executeSQL(
                    query=f"""
                        SELECT 
                            /*+LABEL('VastFrame.regr')*/ 
                            {", ".join(all_list)}""",
                    print_time_sql=False,
                    method="fetchrow",
                )
            else:
                result = _executeSQL(
                    query=f"""
                        SELECT 
                            /*+LABEL('VastFrame.regr')*/
                            {", ".join(all_list)} 
                        FROM {self}""",
                    title=f"Computing the REGR_{method.upper()} Matrix.",
                    method="fetchrow",
                )

            if n == 1:
                return result[0]

        except QueryError:
            # Fallback: compute one at a time
            result = []
            for i in range(n):
                for j in range(n):
                    col_i = columns[i]
                    col_j = columns[j]

                    if self[col_i].isbool():
                        col_i_expr = f"CAST({col_i} AS INTEGER)"
                    else:
                        col_i_expr = col_i

                    if self[col_j].isbool():
                        col_j_expr = f"CAST({col_j} AS INTEGER)"
                    else:
                        col_j_expr = col_j

                    sql_expr = self._get_regr_sql(method, col_i_expr, col_j_expr)

                    result.append(
                        _executeSQL(
                            query=f"""
                                SELECT 
                                    /*+LABEL('VastFrame.regr')*/ 
                                    {sql_expr}
                                FROM {self}""",
                            title=f"Computing REGR_{method.upper()}, one at a time.",
                            method="fetchfirstelem",
                        )
                    )

        # Build matrix
        matrix = np.array([[1.0 for _ in range(n)] for _ in range(n)])
        k = 0
        for i in range(n):
            for j in range(n):
                current = result[k]
                k += 1
                if isinstance(current, NoneType):
                    current = np.nan
                matrix[i][j] = current

        # Plot or return
        if show:
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="HeatMap",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            data = {"X": matrix}
            layout = {
                "columns": [None, None],
                "x_labels": columns,
                "y_labels": columns,
                "with_numbers": True,
            }
            return vo_plt.HeatMap(data=data, layout=layout).draw(**kwargs)

        # Update catalog
        values = {"index": columns}
        for idx in range(len(matrix)):
            values[columns[idx]] = list(matrix[:, idx])

        for column1 in values:
            if column1 != "index":
                val = {}
                for idx, column2 in enumerate(values["index"]):
                    val[column2] = values[column1][idx]
                self._update_catalog(
                    values=val, matrix=f"regr_{method}", column=column1
                )

        return TableSample(values=values).decimal_to_float()

    def _get_regr_sql(self, method: str, x: str, y: str) -> str:
        """
        Generate SQL expression for regression statistic.

        Parameters
        ----------
        method : str
            Regression method
        x : str
            Independent variable (already CAST if needed)
        y : str
            Dependent variable (already CAST if needed)

        Returns
        -------
        str
            SQL expression
        """
        if method == "intercept":
            return f"REGR_INTERCEPT({y}, {x})"

        elif method == "slope":
            return f"REGR_SLOPE({y}, {x})"

        elif method == "avgx":
            return f"AVG({x})"

        elif method == "avgy":
            return f"AVG({y})"

        elif method == "count":
            return f"COUNT(CASE WHEN {x} IS NULL OR {y} IS NULL THEN NULL ELSE 1 END)"

        elif method == "r2":
            # R² = correlation coefficient squared
            return f"POWER(CORR({x}, {y}), 2)"

        elif method == "sxx":
            avg_x = self[x].avg()
            # SXX = SUM((x - mean(x))²)
            return f"SUM(POWER({x} - {avg_x}, 2))"

        elif method == "sxy":
            avg_x = self[x].avg()
            avg_y = self[y].avg()
            # SXY = SUM((x - mean(x)) * (y - mean(y)))
            return f"SUM(({x} - {avg_x}) * ({y} - {avg_y}))"

        elif method == "syy":
            avg_y = self[y].avg()
            # SYY = SUM((y - mean(y))²)
            return f"SUM(POWER({y} - {avg_y}, 2))"

        else:
            raise ValueError(f"Unknown regression method: {method}")

    # Time Series.

    @save_vastorbit_logs
    def acf(
        self,
        column: str,
        ts: str,
        by: Optional[SQLColumns] = None,
        p: Union[int, list] = 12,
        unit: str = "rows",
        method: Literal[
            "pearson", "kendall", "spearman", "spearmand", "biserial", "cramer"
        ] = "pearson",
        confidence: bool = True,
        alpha: float = 0.95,
        show: bool = True,
        kind: Literal["line", "heatmap", "bar"] = "bar",
        mround: int = 3,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Calculates the  correlations between  the specified VastColumn
        and its various time lags. This function is particularly useful
        for  time  series analysis and forecasting as it helps  uncover
        relationships  between data points at different time  intervals.
        Understanding  these  correlations  can  be  vital  for  making
        predictions  and gaining  insights into temporal data  patterns.

        Parameters
        ----------
        column: str
            Input VastColumn used to compute the Auto
            Correlation Plot.
        ts: str
            TS (Time Series)  VastColumn used to order
            the  data.  It  can  be  of type  date  or  a
            numerical VastColumn.
        by: SQLColumns, optional
            VastColumns used in the partition.
        p: int | list, optional
            Int  equal  to  the  maximum  number  of lag  to
            consider  during the  computation or  List of the
            different  lags to include during the computation.
            p must be positive or a list of positive integers.
        unit: str, optional
            Unit used to compute the lags.

             - rows:
                Natural lags.
             - else:
                Any time unit. For example, you can
                write 'hour' to compute the hours
                lags or 'day' to compute the days
                lags.

        method: str, optional
            Method used to compute the correlation.

             - pearson:
                Pearson's  correlation coefficient
                (linear).
             - spearman:
                Spearman's correlation coefficient
                (monotonic - rank based).
             - spearmanD:
                Spearman's correlation coefficient
                using  the   DENSE  RANK  function
                instead of the RANK function.
             - kendall:
                Kendall's  correlation coefficient
                (similar trends).  The method
                computes the Tau-B coefficient.

                .. warning::

                    This method  uses a CROSS JOIN  during  computation
                    and      is     therefore computationally expensive
                    at  O(n * n),  where n is the  total  count of  the
                    :py:class:`~VastFrame`.
             - cramer:
                Cramer's V (correlation between categories).
             - biserial:
                Biserial Point (correlation between binaries
                and a numericals).

        confidence: bool, optional
            If set to True, the confidence band width is drawn.
        alpha: float, optional
            Significance Level. Probability to accept H0. Only
            used   to  compute   the  confidence  band   width.
        show: bool, optional
                If  set  to True,  the Plotting object is
                returned.
        kind: str, optional
            ACF Type.

             - bar:
                Classical Autocorrelation Plot using bars.
             - heatmap:
                Draws the ACF heatmap.
             - line:
                Draws the ACF using a Line Plot.

        mround: int, optional
            Round  the  coefficient using the input number  of
            digits. It is used only to display the ACF  Matrix
            (kind must be set to 'heatmap').
        chart: PlottingObject, optional
            The chart object used to plot.
        ``**style_kwargs``
            Any optional parameter  to  pass  to  the plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        Import the amazon dataset from `vastorbit`.

        .. code-block:: python

            from vastorbit.datasets import load_amazon

            data = load_amazon()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_amazon.html

        Draw the ACF Plot.

        .. code-block:: python

            data.acf(
                column = "number",
                ts = "date",
                by = "state",
                method = "pearson",
                p = 24,
            )

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            from vastorbit.datasets import load_amazon
            vo.set_option("plotting_lib", "plotly")
            data = load_amazon()
            fig = data.acf(
                column = "number",
                ts = "date",
                by = "state",
                method = "pearson",
                p = 24,
                width = 600,
                height = 400,
            )
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_acf_plot.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_acf_plot.html

        For more examples, please look at the :ref:`chart_gallery.acf` page of the
        :ref:`chart_gallery`.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.pacf` : Computes the partial autocorrelations.
        """
        method = str(method).lower()
        by = format_type(by, dtype=list)
        by, column, ts = self.format_colnames(by, column, ts)
        if unit == "rows":
            table = self._genSQL()
        else:
            table = self.interpolate(
                ts=ts, rule=f"1 {unit}", method={column: "linear"}, by=by
            )._genSQL()
        if isinstance(p, (int, float)):
            p = range(1, p + 1)
        by = f"PARTITION BY {', '.join(by)} " if by else ""
        columns = [
            f"LAG({column}, {i}) OVER ({by}ORDER BY {ts}) AS lag_{i}_{gen_name([column])}"
            for i in p
        ]
        query = f"SELECT {', '.join([column] + columns)} FROM {table}"
        if len(p) == 1:
            return create_new_vdf(query).corr([], method=method)
        elif kind == "heatmap":
            return create_new_vdf(query).corr(
                [],
                method=method,
                mround=mround,
                focus=column,
                show=show,
                **style_kwargs,
            )
        else:
            result = create_new_vdf(query).corr(
                [], method=method, focus=column, show=False
            )
            columns = copy.deepcopy(result.values["index"])
            acf = copy.deepcopy(result.values[column])
            acf_band = []
            if confidence:
                for k in range(1, len(acf) + 1):
                    acf_band += [
                        math.sqrt(2)
                        * scipy_special.erfinv(alpha)
                        / math.sqrt(self[column].count() - k + 1)
                        * math.sqrt((1 + 2 * sum(acf[i] ** 2 for i in range(1, k))))
                    ]
            if columns[0] == column:
                columns[0] = 0
            for i in range(1, len(columns)):
                columns[i] = int(columns[i].split("_")[1])
            data = [(columns[i], acf[i]) for i in range(len(columns))]
            data.sort(key=lambda tup: tup[0])
            del result.values[column]
            result.values["index"] = [elem[0] for elem in data]
            result.values["value"] = [elem[1] for elem in data]
            if acf_band:
                result.values["confidence"] = acf_band
            if show:
                vo_plt, kwargs = self.get_plotting_lib(
                    class_name="ACFPlot",
                    chart=chart,
                    style_kwargs=style_kwargs,
                )
                data = {
                    "x": np.array(result.values["index"]),
                    "y": np.array(result.values["value"]),
                    "z": np.array(acf_band),
                }
                layout = {}
                return vo_plt.ACFPlot(
                    data=data, layout=layout, misc_layout={"kind": kind, "pacf": False}
                ).draw(**kwargs)
            return result

    @save_vastorbit_logs
    def pacf(
        self,
        column: str,
        ts: str,
        by: Optional[SQLColumns] = None,
        p: Union[int, list] = 5,
        unit: str = "rows",
        method: Literal[
            "pearson", "kendall", "spearman", "spearmand", "biserial", "cramer"
        ] = "pearson",
        confidence: bool = True,
        alpha: float = 0.95,
        show: bool = True,
        kind: Literal["line", "bar"] = "bar",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ):
        """
        Computes the partial autocorrelations of the specified VastColumn.
        Partial autocorrelations  are a fundamental concept in time series
        analysis and provide essential information about the  dependencies
        between data  points at  different  time lags. Understanding these
        partial autocorrelations can aid in modeling and predicting future
        values,  making it a  valuable  tool for time series analysis  and
        forecasting.

        Parameters
        ----------
        column: str
            Input VastColumn  used to compute the Auto
            Correlation Plot.
        ts: str
            TS (Time Series)  VastColumn used to order
            the  data.  It  can  be  of type  date  or  a
            numerical VastColumn.
        by: SQLColumns, optional
            VastColumns used in the partition.
        p: int | list, optional
            Int  equal  to  the  maximum  number  of lag  to
            consider  during the  computation or  List of the
            different  lags to include during the computation.
            p must be positive or a list of positive integers.
        unit: str, optional
            Unit used to compute the lags.

             - rows:
                Natural lags.
             - else:
                Any time unit. For example, you can
                write 'hour' to compute the hours
                lags or 'day' to compute the days
                lags.

        method: str, optional
            Method used to compute the correlation.

             - pearson:
                Pearson's  correlation coefficient
                (linear).
             - spearman:
                Spearman's correlation coefficient
                (monotonic - rank based).
             - spearmanD:
                Spearman's correlation coefficient
                using  the   DENSE  RANK  function
                instead of the RANK function.
             - kendall:
                Kendall's  correlation coefficient
                (similar trends).  The method computes
                the Tau-B coefficient.

                .. warning::

                    This method  uses a CROSS JOIN  during  computation
                    and      is     therefore computationally expensive
                    at  O(n * n),  where n is the  total  count of  the
                    :py:class:`~VastFrame`.
             - cramer:
                Cramer's V (correlation between categories).
             - biserial:
                Biserial Point (correlation between binaries
                and a numericals).

        confidence: bool, optional
            If set to True, the confidence band width is drawn.
        alpha: float, optional
            Significance Level. Probability to accept H0. Only
            used   to  compute   the  confidence  band   width.
        show: bool, optional
            If  set  to True,  the Plotting object is
            returned.
        kind: str, optional
            PACF Type.

             - bar:
                Classical Partial Autocorrelation Plot using bars.
             - line:
                Draws the PACF using a Line Plot.

        chart: PlottingObject, optional
            The chart object used to plot.
        ``**style_kwargs``
            Any optional parameter  to  pass  to  the plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        Import the amazon dataset from `vastorbit`.

        .. code-block:: python

            from vastorbit.datasets import load_amazon

            data = load_amazon()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_amazon.html

        Draw the PACF Plot.

        .. code-block:: python

            data.pacf(
                column = "number",
                ts = "date",
                by = "state",
                method = "pearson",
                p = 24,
            )

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            from vastorbit.datasets import load_amazon
            vo.set_option("plotting_lib", "plotly")
            data = load_amazon()
            fig = data.pacf(
                column = "number",
                ts = "date",
                by = "state",
                method = "pearson",
                p = 24,
                width = 600,
                height = 450,
            )
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_pacf_plot.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_pacf_plot.html

        For more examples, please look at the :ref:`chart_gallery.acf` page of the
        :ref:`chart_gallery`. Those ones are related to ACF plots, but the customization
        stays the same for the PACF plot.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.acf` : Computes the autocorrelations.
        """
        vml = get_VAST_mllib()
        if isinstance(by, str):
            by = [by]
        if isinstance(p, Iterable) and (len(p) == 1):
            p = p[0]
            if p == 0:
                return 1.0
            elif p == 1:
                return self.acf(
                    ts=ts, column=column, by=by, p=[1], unit=unit, method=method
                )
            by, column, ts = self.format_colnames(by, column, ts)
            if unit == "rows":
                table = self._genSQL()
            else:
                table = self.interpolate(
                    ts=ts, rule=f"1 {unit}", method={column: "linear"}, by=by
                )._genSQL()
            by = f"PARTITION BY {', '.join(by)} " if by else ""
            columns = [
                f"LAG({column}, {i}) OVER ({by}ORDER BY {ts}) AS lag_{i}_{gen_name([column])}"
                for i in range(1, p + 1)
            ]
            relation = f"(SELECT {', '.join([column] + columns)} FROM {table}) pacf"
            tmp_view_name = gen_tmp_name(
                schema=conf.get_option("temp_schema"), name="linear_reg_view"
            )
            try:
                drop(tmp_view_name, method="view")
                where = " AND ".join(
                    [
                        f"lag_{i}_{gen_name([column])} IS NOT NULL"
                        for i in range(1, p + 1)
                    ]
                    + [f"{column} IS NOT NULL"]
                )
                query = f"""
                    CREATE VIEW {tmp_view_name} 
                        AS SELECT /*+LABEL('VastFrame.pacf')*/ * FROM {relation}
                        WHERE {where}"""
                _executeSQL(query, print_time_sql=False)
                vdf = create_new_vdf(tmp_view_name)
                model = vml.LinearRegression()
                model.fit(
                    input_relation=tmp_view_name,
                    X=[f"lag_{i}_{gen_name([column])}" for i in range(1, p)],
                    y=column,
                    return_report=True,
                )
                model.predict(vdf, name="prediction_0")
                model2 = vml.LinearRegression()
                model2.fit(
                    input_relation=tmp_view_name,
                    X=[f"lag_{i}_{gen_name([column])}" for i in range(1, p)],
                    y=f"lag_{p}_{gen_name([column])}",
                    return_report=True,
                )
                model2.predict(vdf, name="prediction_p")
                vdf.eval(expr=f"{column} - prediction_0", name="eps_0")
                vdf.eval(
                    expr=f"lag_{p}_{gen_name([column])} - prediction_p",
                    name="eps_p",
                )
                result = vdf.corr(["eps_0", "eps_p"], method=method)
            finally:
                drop(tmp_view_name, method="view")
            return result
        else:
            if isinstance(p, (float, int)):
                p = range(0, p + 1)
            loop = tqdm(p) if conf.get_option("tqdm") else p
            pacf = []
            for i in loop:
                pacf += [self.pacf(ts=ts, column=column, by=by, p=[i], unit=unit)]
            columns = list(p)
            pacf_band = []
            if confidence:
                for k in range(1, len(pacf) + 1):
                    pacf_band += [
                        math.sqrt(2)
                        * scipy_special.erfinv(alpha)
                        / math.sqrt(self[column].count() - k + 1)
                        * math.sqrt((1 + 2 * sum(pacf[i] ** 2 for i in range(1, k))))
                    ]
            result = TableSample({"index": columns, "value": pacf})
            if pacf_band:
                result.values["confidence"] = pacf_band
            if show:
                vo_plt, kwargs = self.get_plotting_lib(
                    class_name="ACFPlot",
                    chart=chart,
                    style_kwargs=style_kwargs,
                )
                data = {
                    "x": np.array(result.values["index"]),
                    "y": np.array(result.values["value"]),
                    "z": np.array(pacf_band),
                }
                layout = {}
                return vo_plt.ACFPlot(
                    data=data, layout=layout, misc_layout={"kind": kind, "pacf": True}
                ).draw(**kwargs)
            return result

    # Weight of Evidence.

    @save_vastorbit_logs
    def iv_woe(
        self,
        y: str,
        columns: Optional[SQLColumns] = None,
        nbins: int = 10,
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Calculates the Information Value (IV) Table, a powerful tool
        for  assessing  the predictive capability of an  independent
        variable  concerning  a  dependent  variable.  The IV  Table
        provides insights into how well the independent variable can
        predict  or  explain  variations  in the dependent  variable.

        Parameters
        ----------
        y: str
            Response VastColumn.
        columns: SQLColumns, optional
            List  of  the  VastColumns names. If  empty,  all
            VastColumns  except  the response  are used.
        nbins: int, optional
            Maximum number of bins used for the discretization
            (must be > 1).
        show: bool, optional
            If  set  to True,  the  Plotting  object  is
            returned.
        chart: PlottingObject, optional
            The chart object used to plot.
        ``**style_kwargs``
            Any  optional  parameter to  pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        Import the titanic dataset from `vastorbit`.

        .. code-block:: python

            from vastorbit.datasets import load_titanic

            data = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        Draw the IV Bar chart.

        .. code-block:: python

            data.iv_woe(y = "survived", nbins = 20)

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            from vastorbit.datasets import load_titanic
            vo.set_option("plotting_lib", "plotly")
            data = load_titanic()
            fig = data.iv_woe(y = "survived", nbins = 20)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_iv_woe_plot.html")

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_iv_woe_plot.html

        .. hint::

            IV  (Information Value) and  WOE (Weight of Evidence) serve as  powerful
            tools  for identifying factors that influence a response column  without
            the need to construct a full-fledged machine learning model.
            These statistical metrics provide  valuable insights into the predictive
            power of independent variables concerning the dependent variable, aiding
            in data analysis and decision-making processes.

            Clearly, the  factors that significantly influenced the survival of  the
            passengers  were  whether they had access to  a  lifeboat,  their gender
            (women and children were prioritized),  and  their class  (passengers in
            first  class had a  higher chance  of  evacuation).  These  observations
            underscore  the  importance of these variables  in  predicting  survival
            outcomes during the Titanic disaster.

        .. seealso::
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.iv_woe` : Computes IV / WOE table.
        """
        columns = format_type(columns, dtype=list)
        columns, y = self.format_colnames(columns, y)
        if not columns:
            columns = self.get_columns(exclude_columns=[y])
        importance = np.array(
            [self[col].iv_woe(y=y, nbins=nbins)["iv"][-1] for col in columns]
        )
        if show:
            data = {
                "importance": importance,
            }
            layout = {"columns": copy.deepcopy(columns), "x_label": "IV"}
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="ImportanceBarChart",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.ImportanceBarChart(data=data, layout=layout).draw(**kwargs)
        return TableSample(
            {
                "index": copy.deepcopy(columns),
                "iv": importance,
            }
        ).sort(
            column="iv",
            desc=True,
        )


class vDCCorr(vDCEncode):
    # Weight of Evidence.

    @save_vastorbit_logs
    def iv_woe(self, y: str, nbins: int = 10) -> TableSample:
        """
        Calculates  the  Information Value (IV) / Weight  Of
        Evidence  (WOE) Table.  This table  illustrates  the
        predictive  strength  of   an  independent  variable
        concerning  the  dependent variable.  It  provides a
        measure of how  well the  independent  variable  can
        predict  or  explain  variations  in  the  dependent
        variable.   The  WOE   values   help  quantify   the
        relationship  between the independent and  dependent
        variables, offering valuable insights for predictive
        modeling.

        Parameters
        ----------
        y: str
            Response VastColumn.
        nbins: int, optional
            Maximum  number  of   nbins  used  for  the
            discretization (must be > 1)

        Returns
        -------
        obj
            Tablesample.

        Examples
        --------
        Import the titanic dataset from `vastorbit`.

        .. code-block:: python

            from vastorbit.datasets import load_titanic

            data = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        Draw the IV Bar chart.

        .. code-block:: python

            data["age"].iv_woe(y = "survived", nbins = 20)

        .. ipython:: python
            :suppress:

            from vastorbit.datasets import load_titanic
            data = load_titanic()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_iv_woe_table.html", "w")
            html_file.write(data["age"].iv_woe(y = "survived", nbins = 20)._repr_html_())
            html_file.close()

        .. raw:: html
          :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFCorr_iv_woe_table.html

        .. hint::

            The  IV/WOE  Table  plays a  pivotal  role  in calculating the  global
            Information   Value   (IV).  This  global  IV  serves  as  a  valuable
            indicator for  identifying  the predictors  most  strongly  correlated
            with a  response  column, enabling the discovery of key  relationships
            without the necessity of constructing a comprehensive machine learning
            model. It's a powerful  tool for efficient data analysis and  decision
            -making.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.iv_woe` : Draw IV Plot.
        """
        y = self._parent.format_colnames(y)
        assert self._parent[y].nunique() == 2, TypeError(
            f"VastColumn {y} must be binary to use iv_woe."
        )
        response_cat = self._parent[y].distinct()
        response_cat.sort()
        assert response_cat == [0, 1], TypeError(
            f"VastColumn {y} must be binary to use iv_woe."
        )
        self._parent[y].distinct()
        trans = self.discretize(
            method="same_width" if self.isnum() else "topk",
            nbins=nbins,
            k=nbins,
            new_category="Others",
            return_enum_trans=True,
        )[0].replace("{}", self._alias)
        query = f"""
            SELECT 
                {trans} AS {self}, 
                {self} AS ord, 
                CAST({y} AS INT) AS {y} 
            FROM {self._parent}"""
        query = f"""
            SELECT 
                {self}, 
                MIN(ord) AS ord, 
                SUM(1 - {y}) AS non_events, 
                SUM({y}) AS events 
            FROM ({query}) x GROUP BY 1"""
        query = f"""
            SELECT 
                {self}, 
                ord, 
                non_events, 
                events, 
                1.0000000 * non_events / NULLIF(SUM(non_events) OVER (), 0) AS pt_non_events, 
                1.0000000 * events / NULLIF(SUM(events) OVER (), 0) AS pt_events 
            FROM ({query}) x"""
        query = f"""
            SELECT 
                {self} AS index, 
                non_events, 
                events, 
                pt_non_events, 
                pt_events, 
                CASE 
                    WHEN non_events = 0 OR events = 0 THEN 0 
                    ELSE COALESCE(LN(1.0000000 * pt_non_events / NULLIF(pt_events, 0)), 0) 
                END AS woe, 
                CASE 
                    WHEN non_events = 0 OR events = 0 THEN 0 
                    ELSE 1.0000000 * 
                        (pt_non_events - pt_events) 
                        * COALESCE(LN(pt_non_events 
                        / NULLIF(pt_events, 0)), 0) 
                END AS iv 
            FROM ({query}) x ORDER BY ord"""
        title = f"Computing WOE & IV of {self} (response = {y})."
        result = TableSample.read_sql(
            query,
            title=title,
        )
        result.values["index"] += ["total"]
        result.values["non_events"] += [sum(result["non_events"])]
        result.values["events"] += [sum(result["events"])]
        result.values["pt_non_events"] += [""]
        result.values["pt_events"] += [""]
        result.values["woe"] += [""]
        result.values["iv"] += [sum(result["iv"])]
        return result
