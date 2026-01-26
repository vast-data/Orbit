"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import datetime
from typing import Literal, Optional, Union, TYPE_CHECKING

from vastorbit.connection.errors import QueryError

import vastorbit._config.config as conf
from vastorbit._typing import (
    NoneType,
    PythonNumber,
    PythonScalar,
    TimeInterval,
    SQLColumns,
)
from vastorbit._utils._object import create_new_vdf
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit.errors import QueryError as vQueryError

from vastorbit.core.string_sql.base import StringSQL

from vastorbit.core.vastframe._pivot import vDFPivot
from vastorbit.core.vastframe._math import vDCMath

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFFill(vDFPivot):
    @save_vastorbit_logs
    def fillna(
        self,
        val: Optional[dict] = None,
        method: Optional[dict] = None,
        numeric_only: bool = False,
    ) -> "VastFrame":
        """
        Fills missing elements in :py:class:`~VastColumn`
        using specific rules.

        Parameters
        ----------
        val: dict, optional
            Dictionary of values. The ``dictionary``
            must be similar to the following:
            ``{"column1": val1 ..., "columnk": valk}``.
            Each key of the ``dictionary`` must be
            a :py:class:`~VastColumn` . The missing
            values of the input :py:class:`~VastColumn`
            are replaced by the input value.
        method: dict, optional
            Method used to impute the missing values.

            - auto:
                Mean for the numerical and Mode for the
                categorical :py:class:`~VastColumn`.
            - mean:
                Average.
            - median:
                Median.
            - mode:
                Mode (most occurent element).
            - 0ifnull:
                0 when the :py:class:`~VastColumn`
                is ``None``, 1 otherwise.

            More Methods are available in the
            ``VastColumn.``:py:meth:`~vastorbit.VastColumn.fillna` method.
        numeric_only: bool, optional
            If parameters 'val' and 'method' are
            empty and 'numeric_only' is set to
            ``True``, all numerical :py:class:`~VastColumn`
            are imputed by their average. If set
            to ``False``, all categorical
            :py:class:`~VastColumn` are also
            imputed by their mode.

        Returns
        -------
        VastFrame
            self

        Examples
        ---------

        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        For this example, we will use the Titanic dataset.

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            data = load_titanic()

        .. raw:: html
            :file: :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        We can see the count of each column to check
        if any column has missing values.

        .. code-block:: python

            data.count()

        .. ipython:: python
            :suppress:

            res = data.count()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_count.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_count.html

        From the above table, we can see that the
        count of boats is less than 1234. This suggests
        that it is missing some values.

        Now we can use the ``fillna`` method
        to fill those values. Let's use a custom
        function to fill these values.

        .. code-block:: python

            data.fillna(
                val = {"boat": "No boat"},
                method = {
                    "age": "mean",
                    "embarked": "mode",
                    "fare": "median",
                }
            )

        .. ipython:: python
            :suppress:

            res = data.fillna(
                val = {"boat": "No boat"},
                method = {
                    "age": "mean",
                    "embarked": "mode",
                    "fare": "median",
                }
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_final.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_final.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.interpolate` : Fill missing values by interpolating.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.fill_outliers` : Fill the outliers using the input method.
        """
        val, method = format_type(val, method, dtype=dict)
        print_info = conf.get_option("print_info")
        conf.set_option("print_info", False)
        try:
            if not val and not method:
                cols = self.get_columns()
                for column in cols:
                    if numeric_only:
                        if self[column].isnum():
                            self[column].fillna(method="auto")
                    else:
                        self[column].fillna(method="auto")
            else:
                for column in val:
                    self[self.format_colnames(column)].fillna(val=val[column])
                for column in method:
                    self[self.format_colnames(column)].fillna(
                        method=method[column],
                    )
            return self
        finally:
            conf.set_option("print_info", print_info)

    @save_vastorbit_logs
    def interpolate(
        self,
        ts: str,
        rule: TimeInterval,
        method: Optional[dict] = None,
        by: Optional[SQLColumns] = None,
    ) -> "VastFrame":
        """
        Computes a regular time interval VastFrame by interpolating the
        missing values using different techniques.

        Parameters
        ----------
        ts: str
            TS (Time Series) VastColumn used to order the data. The
            VastColumn type must be date (date, datetime, timestamp...).
        rule: TimeInterval
            Interval used to create the time slices. The final
            interpolation is divided by these intervals. For example,
            specifying '5 minutes' creates records separated by time
            intervals of '5 minutes'.
            Format: '1 second', '5 minutes', '1 hour', '1 day', etc.
        method: dict, optional
            Dictionary of interpolation methods. Must be in the following
            format:
            {"column1": "interpolation1" ..., "columnk": "interpolationk"}
            Interpolation methods must be one of the following:

            - bfill/backfill:
                Interpolates with the next non-null value.
            - ffill/pad:
                Interpolates with the previous non-null value.
            - linear:
                Linear interpolation between points.

        by: SQLColumns, optional
            VastColumns used in the partition.

        Returns
        -------
        VastFrame
            object result of the interpolation.

        Examples
        --------
        .. code-block:: python

            import vastorbit as vo

            vdf = vo.VastFrame({
                "time": [
                    "1993-11-03 00:00:00",
                    "1993-11-03 00:00:01",
                    "1993-11-03 00:00:02",
                    "1993-11-03 00:00:04",
                    "1993-11-03 00:00:05",
                ],
                "val": [0., 1., 2., 4., 5.],
            })

            vdf["time"].astype("timestamp")

            # Linear interpolation
            result = vdf.interpolate(
                ts="time",
                rule="1 second",
                method={"val": "linear"},
            )
        """
        method = format_type(method, dtype=dict)
        by = format_type(by, dtype=list)
        method, ts, by = self.format_colnames(method, ts, by)

        # Parse interval (e.g., "1 second", "5 minutes")
        interval_value, interval_unit = self._parse_interval(rule)

        # Validate methods
        for column in method:
            assert method[column] in (
                "bfill",
                "backfill",
                "pad",
                "ffill",
                "linear",
            ), ValueError(
                "Each element of the 'method' dictionary must be "
                "in bfill|backfill|pad|ffill|linear"
            )

        # Build partition clause
        partition_clause = ""
        if by:
            partition_clause = f"PARTITION BY {', '.join(quote_ident(by))} "

        # Step 1: Generate time series grid
        time_grid_query = f"""
        WITH 
        source_data AS (
            SELECT * FROM {self}
        ),
        time_bounds AS (
            SELECT 
                {f'{partition_clause.replace("PARTITION BY ", "")}, ' if by else ''}
                MIN(CAST({quote_ident(ts)} AS TIMESTAMP)) as min_time,
                MAX(CAST({quote_ident(ts)} AS TIMESTAMP)) as max_time
            FROM source_data
            {f'GROUP BY {", ".join(quote_ident(by))}' if by else ''}
        ),
        time_series AS (
            SELECT 
                {f'{", ".join(quote_ident(by))}, ' if by else ''}
                sequence(
                    min_time,
                    max_time,
                    INTERVAL '{interval_value}' {interval_unit}
                ) as time_array
            FROM time_bounds
        ),
        expanded_times AS (
            SELECT 
                {f'{", ".join(quote_ident(by))}, ' if by else ''}
                time_point as slice_time
            FROM time_series
            CROSS JOIN UNNEST(time_array) AS t(time_point)
        )
        """

        # Step 2: Join with original data and interpolate
        interpolation_selects = []

        for column in method:
            interp_method = method[column]

            if interp_method in ("ffill", "pad"):
                # Forward fill: use LAST_VALUE with IGNORE NULLS
                interpolation_selects.append(f"""
                    LAST_VALUE({column}) IGNORE NULLS OVER (
                        {partition_clause}
                        ORDER BY slice_time
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS {quote_ident(column)}
                """)

            elif interp_method in ("bfill", "backfill"):
                # Backward fill: use LAST_VALUE with IGNORE NULLS in reverse
                interpolation_selects.append(f"""
                    LAST_VALUE({column}) IGNORE NULLS OVER (
                        {partition_clause}
                        ORDER BY slice_time DESC
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS {quote_ident(column)}
                """)

            elif interp_method == "linear":
                # Linear interpolation
                interpolation_selects.append(f"""
                    CASE 
                        WHEN {column} IS NOT NULL THEN {column}
                        ELSE 
                            -- Linear interpolation: y = y0 + (y1 - y0) * (t - t0) / (t1 - t0)
                            COALESCE(
                                LAST_VALUE({column}) IGNORE NULLS OVER (
                                    {partition_clause}
                                    ORDER BY slice_time
                                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                                ) + 
                                (
                                    FIRST_VALUE({column}) IGNORE NULLS OVER (
                                        {partition_clause}
                                        ORDER BY slice_time
                                        ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING
                                    ) - 
                                    LAST_VALUE({column}) IGNORE NULLS OVER (
                                        {partition_clause}
                                        ORDER BY slice_time
                                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                                    )
                                ) * 
                                CAST(
                                    DATE_DIFF(
                                        '{interval_unit}',
                                        LAST_VALUE(slice_time) IGNORE NULLS OVER (
                                            {partition_clause}
                                            ORDER BY slice_time
                                            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                                        ),
                                        slice_time
                                    ) AS DOUBLE
                                ) / 
                                NULLIF(
                                    CAST(
                                        DATE_DIFF(
                                            '{interval_unit}',
                                            LAST_VALUE(slice_time) IGNORE NULLS OVER (
                                                {partition_clause}
                                                ORDER BY slice_time
                                                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                                            ),
                                            FIRST_VALUE(slice_time) IGNORE NULLS OVER (
                                                {partition_clause}
                                                ORDER BY slice_time
                                                ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING
                                            )
                                        ) AS DOUBLE
                                    ),
                                    0.0
                                ),
                                {column}  -- Fallback if can't interpolate
                            )
                    END AS {quote_ident(column)}
                """)

        # Build final query
        select_parts = [f"slice_time AS {quote_ident(ts)}"]
        if by:
            select_parts.extend(quote_ident(by))
        select_parts.extend(interpolation_selects)

        query = time_grid_query + f"""
        SELECT 
            {', '.join(select_parts)}
        FROM (
            SELECT 
                et.slice_time,
                {f'{", ".join([f"et.{quote_ident(col)}" for col in by])}, ' if by else ''}
                {', '.join([f'sd.{quote_ident(col)}' for col in method.keys()])}
            FROM expanded_times et
            LEFT JOIN source_data sd 
                ON CAST(sd.{quote_ident(ts)} AS TIMESTAMP) = et.slice_time
                {f'AND {" AND ".join([f"et.{quote_ident(col)} = sd.{quote_ident(col)}" for col in by])}' if by else ''}
        ) interpolated
        ORDER BY {', '.join(quote_ident(by)) + ', ' if by else ''}{quote_ident(ts)}
        """

        return create_new_vdf(query)

    asfreq = interpolate


class vDCFill(vDCMath):
    @save_vastorbit_logs
    def clip(
        self,
        lower: Optional[PythonScalar] = None,
        upper: Optional[PythonScalar] = None,
    ) -> "VastFrame":
        """
        Clips  the VastColumn by  transforming the values less  than
        the lower bound to the lower bound value and the values higher
        than the upper bound to the upper bound value.

        Parameters
        ----------
        lower: PythonScalar, optional
            Lower bound.
        upper: PythonScalar, optional
            Upper bound.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        For this example, we will use a dummy time-series data:

        .. ipython:: python

            vdf = vo.VastFrame({"vals": [-20, -10, 0, -20, 10, 20, 120]})

        .. ipython:: python
            :suppress:

            res=vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_clip_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_clip_data.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        We can see that there are some extreme values in the data.
        We may need to clip those values at extremes. For this we can
        use the ``clip`` function.

        .. code-block:: python

            vdf["vals"].clip(lower=0,upper=100)

        .. ipython:: python
            :suppress:

            res = vdf["vals"].clip(lower=0,upper=100)
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_clip_ouput.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_clip_ouput.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.fillna` : Fill the missing values using the input method.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.fill_outliers` : Fill the outliers using the input method.
        """
        assert (not isinstance(lower, NoneType)) or (
            not isinstance(upper, NoneType)
        ), ValueError("At least 'lower' or 'upper' must have a numerical value")
        lower_when = (
            f"WHEN {{}} < {lower} THEN {lower} "
            if (isinstance(lower, (float, int)))
            else ""
        )
        upper_when = (
            f"WHEN {{}} > {upper} THEN {upper} "
            if (isinstance(upper, (float, int)))
            else ""
        )
        func = f"(CASE {lower_when}{upper_when}ELSE {{}} END)"
        self.apply(func=func)
        return self._parent

    @save_vastorbit_logs
    def fill_outliers(
        self,
        method: Literal["winsorize", "null", "mean"] = "winsorize",
        threshold: PythonNumber = 4.0,
        use_threshold: bool = True,
        alpha: PythonNumber = 0.05,
    ) -> "VastFrame":
        """
        Fills the VastColumns outliers using the input method.

        Parameters
        ----------
        method: str, optional
            Method used to fill the VastColumn outliers.

            - mean:
                Replaces  the  upper and lower outliers  by
                their respective average.
            - null:
                Replaces  the  outliers  by the NULL  value.
            - winsorize:
                If 'use_threshold' is set to False, clips the
                VastColumn using quantile(alpha) as lower
                bound and quantile(1-alpha) as upper bound;
                otherwise uses the lower and upper ZScores.
        threshold: PythonNumber, optional
            Uses the Gaussian distribution  to define the outliers. After
            normalizing the data (Z-Score),  if the absolute value of the
            record is greater than the threshold, it will be considered as
            an outlier.
        use_threshold: bool, optional
            Uses the threshold instead of the 'alpha' parameter.
        alpha: PythonNumber, optional
            Number representing the outliers threshold. Values less than
            quantile(alpha) or greater than quantile(1-alpha) are filled.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        For this example, we will use a dummy data that has one outlier:

        .. ipython:: python

            vdf = vo.VastFrame({"vals": [20, 10, 0, -20, 10, 20, 1200]})

        .. ipython:: python
            :suppress:

            res=vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_fill_outliers_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_fill_outliers_data.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        We can see that there are some extreme values in the data.
        We may need to remove those values. For this we can
        use the ``fill_outliers`` function.

        .. code-block:: python

            vdf["vals"].fill_outliers(method = "null", threshold = 1)

        .. ipython:: python
            :suppress:

            res = vdf["vals"].fill_outliers(method = "null", threshold = 1)
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_fill_outliers_ouput.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_fill_outliers_ouput.html

        .. note::

            We can use either the ``alpha`` parameter or
            the z-score ``threshold`` parameter. By default
            it uses the ``threshold``.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.fillna` : Fill the missing values using the input method.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.fill_outliers` : Fill the outliers using the input method.
        """
        if use_threshold:
            result = self.aggregate(func=["std", "avg"]).transpose().values
            p_alpha, p_1_alpha = (
                -threshold * result["std"][0] + result["avg"][0],
                threshold * result["std"][0] + result["avg"][0],
            )
        else:
            query = f"""
                SELECT /*+LABEL('VastColumn.fill_outliers')*/ 
                    APPROX_PERCENTILE({self}, {alpha}),
                    APPROX_PERCENTILE({self}, 1 - {alpha})
                FROM {self._parent} LIMIT 1"""
            p_alpha, p_1_alpha = _executeSQL(
                query=query,
                title=f"Computing the quantiles of {self}.",
                method="fetchrow",
                sql_push_ext=self._parent._vars["sql_push_ext"],
                symbol=self._parent._vars["symbol"],
            )
        if method == "winsorize":
            self.clip(lower=p_alpha, upper=p_1_alpha)
        elif method == "null":
            self.apply(
                func=f"(CASE WHEN ({{}} BETWEEN {p_alpha} AND {p_1_alpha}) THEN {{}} ELSE NULL END)"
            )
        elif method == "mean":
            query = f"""
                WITH vdf_table AS 
                    (SELECT 
                        /*+LABEL('VastColumn.fill_outliers')*/ * 
                    FROM {self._parent}) 
                    SELECT * FROM (
                        (SELECT 
                            AVG({self}) 
                        FROM vdf_table WHERE {self} < {p_alpha}) 
                        UNION ALL 
                        (SELECT 
                            AVG({self}) 
                        FROM vdf_table WHERE {self} > {p_1_alpha})
                    ) t0 ORDER BY 1"""
            mean_alpha, mean_1_alpha = [
                item[0]
                for item in _executeSQL(
                    query=query,
                    title=f"Computing the average of the {self}'s lower and upper outliers.",
                    method="fetchall",
                    sql_push_ext=self._parent._vars["sql_push_ext"],
                    symbol=self._parent._vars["symbol"],
                )
            ]
            if isinstance(mean_alpha, NoneType):
                mean_alpha = "NULL"
            if isinstance(mean_1_alpha, NoneType):
                mean_1_alpha = "NULL"
            self.apply(func=f"""
                    (CASE 
                        WHEN {{}} < {p_alpha} 
                        THEN {mean_alpha} 
                        WHEN {{}} > {p_1_alpha} 
                        THEN {mean_1_alpha} 
                        ELSE {{}} 
                    END)""")
        return self._parent

    @save_vastorbit_logs
    def fillna(
        self,
        val: Union[int, float, str, datetime.datetime, datetime.date] = None,
        method: Literal[
            "auto",
            "mode",
            "0ifnull",
            "mean",
            "avg",
            "median",
            "ffill",
            "pad",
            "bfill",
            "backfill",
        ] = "auto",
        expr: Union[str, StringSQL] = "",
        by: Optional[SQLColumns] = None,
        order_by: Optional[SQLColumns] = None,
    ) -> "VastFrame":
        """
        Fills missing elements in the VastColumn with a user-specified
        rule.

        Parameters
        ----------
        val: PythonScalar / date, optional
            Value used to impute the VastColumn.
        method: dict, optional
            Method used to impute the missing values.

            - auto:
                Mean  for  the  numerical  and  Mode  for  the
                categorical VastColumns.
            - bfill:
                Back Propagation of the next element (Constant
                Interpolation).
            - ffill:
                Propagation  of  the  first element  (Constant
                Interpolation).
            - mean:
                Average.
            - median:
                Median.
            - mode:
                Mode (most occurent element).
            - 0ifnull:
                0 when the VastColumn is null, 1 otherwise.
        expr: str, optional
            SQL string.
        by: SQLColumns, optional
            VastColumns used in the partition.
        order_by: SQLColumns, optional
            List of the VastColumns used to sort the data when using
            TS methods.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        For this example, we will use the Titanic dataset.

        .. ipython:: python

            from vastorbit.datasets import load_titanic
            data = load_titanic()

        .. raw:: html
            :file: :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        We can see the count of each column to check
        if any column has missing values.

        .. code-block:: python

            data.count()

        .. ipython:: python
            :suppress:

            res = data.count()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_vdc__fillna_count.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_vdc__fillna_count.html

        From the above table, we can see that the
        count of boats is less than 1234. This suggests
        that it is missing some values.

        Now we can use the ``fillna`` method
        to fill those values. Let's use a custom
        function to fill these values.

        .. code-block:: python

            data["age"].fillna(method = "avg", by = ["pclass", "sex"])

        .. ipython:: python
            :suppress:

            res = data["age"].fillna(method = "avg", by = ["pclass", "sex"])
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_vdc_fillna_final.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_vdc_fillna_final.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.interpolate` : Fill missing values by interpolating.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.fill_outliers` : Fill the outliers using the input method.
        """
        if isinstance(method, str):
            method = method.lower()
        by, order_by = format_type(by, order_by, dtype=list)
        by, order_by = self._parent.format_colnames(by, order_by)
        if method == "auto":
            method = "mean" if (self.isnum() and self.nunique(True) > 6) else "mode"
        total = self.count()
        if (method == "mode") and isinstance(val, NoneType):
            val = self.mode(dropna=True)
            if isinstance(val, NoneType):
                warning_message = (
                    f"The VastColumn {self} has no mode "
                    "(only missing values).\nNothing was filled."
                )
                print_message(warning_message, "warning")
                return self._parent
        if isinstance(val, str):
            val = val.replace("'", "''")
        if not isinstance(val, NoneType):
            if self.isnum():
                new_column = f"COALESCE({{}}, {val})"
            else:
                new_column = f"COALESCE({{}}, '{val}')"
        elif expr:
            new_column = f"COALESCE({{}}, {expr})"
        elif method == "0ifnull":
            new_column = "CASE {} WHEN NULL THEN 0 ELSE 1 END"
        elif method in ("mean", "avg", "median"):
            fun = "MEDIAN" if (method == "median") else "AVG"
            if by == []:
                if fun == "AVG":
                    val = self.avg()
                elif fun == "MEDIAN":
                    val = self.median()
                new_column = f"COALESCE({{}}, {val})"
            elif (len(by) == 1) and (self._parent[by[0]].nunique() < 50):
                try:
                    fun_param = ""
                    if fun == "MEDIAN":
                        fun = "APPROX_PERCENTILE"
                        fun_param = ", 0.5"
                    query = f"""
                        SELECT 
                            /*+LABEL('VastColumn.fillna')*/ {by[0]}, 
                            {fun}({self}{fun_param})
                        FROM {self._parent} 
                        GROUP BY {by[0]};"""
                    result = _executeSQL(
                        query=query,
                        title="Computing the different aggregations.",
                        method="fetchall",
                        sql_push_ext=self._parent._vars["sql_push_ext"],
                        symbol=self._parent._vars["symbol"],
                    )
                    for idx, x in enumerate(result):
                        if isinstance(x[0], NoneType):
                            result[idx][0] = "NULL"
                        else:
                            x0 = str(x[0]).replace("'", "''")
                            result[idx][0] = f"'{x0}'"
                        result[idx][1] = (
                            "NULL" if isinstance(x[1], NoneType) else str(x[1])
                        )
                    val = " ".join([f"WHEN {x[0]} THEN {x[1]}" for x in result])
                    new_column = f"COALESCE({{}}, CASE {by[0]} {val} END)"
                    _executeSQL(
                        query=f"""
                            SELECT 
                                /*+LABEL('VastColumn.fillna')*/ 
                                {new_column.format(self._alias)} 
                            FROM {self._parent} 
                            LIMIT 1""",
                        print_time_sql=False,
                        sql_push_ext=self._parent._vars["sql_push_ext"],
                        symbol=self._parent._vars["symbol"],
                    )
                except QueryError:
                    new_column = f"""
                        COALESCE({{}}, {fun}({{}}) 
                            OVER (PARTITION BY {', '.join(by)}))"""
            else:
                new_column = f"""
                    COALESCE({{}}, {fun}({{}}) 
                        OVER (PARTITION BY {', '.join(by)}))"""
        elif method in ("ffill", "pad", "bfill", "backfill"):
            assert order_by, ValueError(
                "If the method is in ffill|pad|bfill|backfill then 'order_by'"
                " must be a list of at least one element to use to order the data"
            )
            desc = "" if (method in ("ffill", "pad")) else " DESC"
            partition_by = f"PARTITION BY {', '.join(by)}" if by else ""
            order_by_ts = ", ".join([quote_ident(column) + desc for column in order_by])
            new_column = f"""
                COALESCE({{}}, LAST_VALUE({{}}) IGNORE NULLS 
                    OVER ({partition_by} 
                    ORDER BY {order_by_ts}))"""
        if method in ("mean", "median") or isinstance(val, float):
            category, ctype = "float", "float"
        elif method == "0ifnull":
            category, ctype = "int", "bool"
        else:
            category, ctype = self.category(), self.ctype()
        copy_trans = copy.deepcopy(self._transf)
        total = self.count()
        if method not in ["mode", "0ifnull"]:
            max_floor = 0
            all_partition = by
            if method in ["ffill", "pad", "bfill", "backfill"]:
                all_partition += list(order_by)
            for elem in all_partition:
                if len(self._parent[elem]._transf) > max_floor:
                    max_floor = len(self._parent[elem]._transf)
            max_floor -= len(self._transf)
            self._transf += [("{}", self.ctype(), self.category())] * max_floor
        self._transf += [(new_column, ctype, category)]
        try:
            sauv = copy.deepcopy(self._catalog)
            self._parent._update_catalog(erase=True, columns=[self._alias])
            total = abs(self.count() - total)
        except Exception as e:
            self._transf = copy.deepcopy(copy_trans)
            raise vQueryError(f"{e}\nAn Error happened during the filling.")
        if total > 0:
            if "count" in sauv:
                parent_cnt = self._parent.shape()[0]
                self._catalog["count"] = int(sauv["count"]) + total
                if parent_cnt == 0:
                    self._catalog["percent"] = 100
                else:
                    self._catalog["percent"] = (
                        100 * (int(sauv["count"]) + total) / parent_cnt
                    )
            total = int(total)
            conj = "s were " if total > 1 else " was "
            print_message(f"{total} element{conj}filled.")
            self._parent._add_to_history(
                f"[Fillna]: {total} {self} missing value{conj} filled."
            )
        else:
            print_message("Nothing was filled.")
            self._transf = [t for t in copy_trans]
            for s in sauv:
                self._catalog[s] = sauv[s]
        return self._parent
