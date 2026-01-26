"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import re
import secrets
from typing import Literal, Optional, Union, TYPE_CHECKING

from vastorbit._typing import PythonNumber, PythonScalar, SQLColumns
from vastorbit._utils._gen import gen_name
from vastorbit._utils._map import vastorbit_agg_name
from vastorbit._utils._object import create_new_vdf
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._cast import to_category
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident
from vastorbit.errors import MissingColumn, QueryError

from vastorbit.core.string_sql.base import StringSQL

from vastorbit.core.vastframe._filter import vDFFilter, vDCFilter

from vastorbit.sql.dtypes import get_data_types

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame, VastColumn


class vDFMath(vDFFilter):
    def __abs__(self) -> "VastFrame":
        return self.copy().abs()

    def __ceil__(self) -> "VastFrame":
        vdf = self.copy()
        columns = vdf.numcol()
        for col in columns:
            if vdf[col].category() == "float":
                vdf[col].apply_fun(func="ceil")
        return vdf

    def __floor__(self) -> "VastFrame":
        vdf = self.copy()
        columns = vdf.numcol()
        for col in columns:
            if vdf[col].category() == "float":
                vdf[col].apply_fun(func="floor")
        return vdf

    def __len__(self) -> int:
        return int(self.shape()[0])

    def __nonzero__(self) -> bool:
        return self.shape()[0] > 0 and not self.empty()

    def __round__(self, n: int) -> "VastFrame":
        vdf = self.copy()
        columns = vdf.numcol()
        for col in columns:
            if vdf[col].category() == "float":
                vdf[col].apply_fun(func="round", x=n)
        return vdf

    @save_vastorbit_logs
    def abs(self, columns: Optional[SQLColumns] = None) -> "VastFrame":
        """
        Applies the absolute value function to all input VastColumns.

        Parameters
        ----------
        columns: SQLColumns, optional
            List  of the VastColumns names. If empty, all  numerical
            VastColumns are used.

        Returns
        -------
        VastFrame
            self

        Examples
        --------
        Let's begin by importing `vastorbit`.

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

        Let us create a dummy dataset with negative values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [10, -10, 20, -2]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_abs.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_abs.html

        Now we can convert all to absolute values:

        .. code-block:: python

            vdf.abs()

        .. ipython:: python
            :suppress:

            vdf.abs()
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_abs_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_abs_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "ABS(val)"

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.analytic` :
                Advanced Analytical functions.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.abs` :
                Absolute values for :py:class:`~VastColumn`.
        """
        columns = format_type(columns, dtype=list)
        columns = self.numcol() if not columns else self.format_colnames(columns)
        func = {}
        for column in columns:
            if not self[column].isbool():
                func[column] = "ABS({})"
        return self.apply(func)

    @save_vastorbit_logs
    def analytic(
        self,
        func: str,
        columns: Optional[SQLColumns] = None,
        by: Optional[SQLColumns] = None,
        order_by: Union[None, SQLColumns, dict] = None,
        name: Optional[str] = None,
        offset: int = 1,
        add_count: bool = True,
    ) -> "VastFrame":
        """
        Adds a new VastColumn to the VastFrame by using an advanced
        analytical function on one or two specific VastColumns.

        Parameters
        ----------
        func: str
            Function to apply. Available functions:

            Statistical:
            - aad: average absolute deviation
            - kurtosis: kurtosis
            - skewness: skewness
            - mad: median absolute deviation
            - jb: Jarque-Bera index
            - iqr: interquartile range
            - sem: standard error of the mean
            - range: max - min

            Aggregates:
            - max, min, avg, sum, count
            - stddev, variance
            - median: approximate median (using approx_percentile)
            - mode: most frequent element
            - prod: product
            - unique: cardinality
            - q%: q quantile (e.g., 50% for median)

            Window:
            - lead, lag: next/previous element
            - first_value, last_value
            - row_number, rank, dense_rank, percent_rank
            - pct_change: ratio between current and previous

            Correlation:
            - corr: Pearson correlation
            - cov: covariance
            - beta: Beta coefficient

        columns: SQLColumns, optional
            Input VastColumns (1 or 2 elements).
        by: SQLColumns, optional
            Partition columns.
        order_by: dict / list, optional
            Sort order.
        name: str, optional
            Name of new column.
        offset: int, optional
            Lead/Lag offset (default: 1).
        add_count: bool, optional
            For mode: add count column.

        Returns
        -------
        VastFrame
            self
        """
        columns, by, order_by = format_type(columns, by, order_by, dtype=list)
        columns, by = self.format_colnames(columns, by)
        by_name = ["by"] + by if by else []
        by_order = ["order_by"] + list(order_by) if order_by else []

        if not name:
            name = gen_name([func] + columns + by_name + by_order)

        func = func.lower()
        by_clause = ", ".join(by)
        by_clause = f"PARTITION BY {by_clause}" if by_clause else ""
        order_by_clause = self._get_sort_syntax(order_by)

        func = vastorbit_agg_name(func.lower(), method="VAST")

        # Functions that don't need ORDER BY
        if func in (
            "max",
            "min",
            "avg",
            "sum",
            "count",
            "stddev",
            "median",
            "variance",
            "unique",
            "top",
            "kurtosis",
            "skewness",
            "mad",
            "aad",
            "range",
            "prod",
            "jb",
            "iqr",
            "sem",
            "corr",
            "cov",
            "beta",
        ) or ("%" in func):

            if order_by_clause:
                print_message(
                    f"\u26a0 '{func}' analytic method doesn't need an "
                    "order by clause, it was ignored"
                )

            if not columns and func != "unique":
                raise MissingColumn(
                    f"The parameter 'column' must be a VastFrame Column "
                    f"when using analytic method '{func}'"
                )

            # TRINO NATIVE FUNCTIONS
            if func == "kurtosis":
                # Trino has native KURTOSIS
                self.eval(name, f"KURTOSIS({columns[0]}) OVER ({by_clause})")

            elif func == "skewness":
                # Trino has native SKEWNESS
                self.eval(name, f"SKEWNESS({columns[0]}) OVER ({by_clause})")

            elif func == "median":
                # Trino uses APPROX_PERCENTILE for median
                self.eval(
                    name, f"APPROX_PERCENTILE({columns[0]}, 0.5) OVER ({by_clause})"
                )

            elif func == "corr":
                # Trino has native CORR
                if len(columns) < 2:
                    raise MissingColumn("CORR requires 2 columns")
                self.eval(name, f"CORR({columns[0]}, {columns[1]}) OVER ({by_clause})")

            elif func == "cov":
                # Trino has native COVAR_SAMP
                if len(columns) < 2:
                    raise MissingColumn("COV requires 2 columns")
                self.eval(
                    name, f"COVAR_SAMP({columns[0]}, {columns[1]}) OVER ({by_clause})"
                )

            elif func == "beta":
                # Beta = COV(X,Y) / VAR(Y)
                if len(columns) < 2:
                    raise MissingColumn("BETA requires 2 columns")
                self.eval(
                    name,
                    f"COVAR_SAMP({columns[0]}, {columns[1]}) OVER ({by_clause}) / "
                    f"NULLIF(VAR_SAMP({columns[1]}) OVER ({by_clause}), 0)",
                )

            elif func == "jb":
                # Jarque-Bera: Use Trino native skewness and kurtosis
                self.eval(
                    name,
                    f"""COUNT({columns[0]}) OVER ({by_clause}) / 6.0 * (
                        POWER(SKEWNESS({columns[0]}) OVER ({by_clause}), 2) + 
                        0.25 * POWER(KURTOSIS({columns[0]}) OVER ({by_clause}), 2)
                    )""",
                )

            elif func == "aad":
                # Average Absolute Deviation
                random_nb = secrets.randbelow(10000001)
                column_str = columns[0].replace('"', "")
                mean_name = f"{column_str}_mean_{random_nb}"
                self.eval(mean_name, f"AVG({columns[0]}) OVER ({by_clause})")
                self.eval(
                    name, f"AVG(ABS({columns[0]} - {mean_name})) OVER ({by_clause})"
                )
                self._vars["exclude_columns"] += [quote_ident(mean_name)]

            elif func == "mad":
                # Median Absolute Deviation
                random_nb = secrets.randbelow(10000001)
                column_str = columns[0].replace('"', "")
                median_name = f"{column_str}_median_{random_nb}"
                self.eval(
                    median_name,
                    f"APPROX_PERCENTILE({columns[0]}, 0.5) OVER ({by_clause})",
                )
                self.eval(
                    name,
                    f"APPROX_PERCENTILE(ABS({columns[0]} - {median_name}), 0.5) OVER ({by_clause})",
                )
                self._vars["exclude_columns"] += [quote_ident(median_name)]

            elif func == "top" or func == "mode":
                # Most frequent: use APPROX_MOST_FREQUENT in Trino
                # Note: APPROX_MOST_FREQUENT returns MAP, need to extract
                if not by_clause:
                    by_str = f"PARTITION BY {columns[0]}"
                else:
                    by_str = f"{by_clause}, {columns[0]}"
                self.eval(name, f"ROW_NUMBER() OVER ({by_str})")
                if add_count:
                    name_str = name.replace('"', "")
                    self.eval(f"{name_str}_count", f"MAX({name}) OVER ({by_clause})")
                # Get the most frequent value
                self[name].apply(
                    f"FIRST_VALUE({columns[0]}) OVER ({by_clause} ORDER BY {{}} DESC)"
                )

            elif func == "unique":
                # Cardinality: use APPROX_DISTINCT in Trino
                self.eval(name, f"APPROX_DISTINCT({columns[0]}) OVER ({by_clause})")

            elif "%" == func[-1]:
                # Percentile
                try:
                    x = float(func[0:-1]) / 100
                except:
                    raise ValueError(
                        f"The aggregate function '{func}' doesn't exist. "
                        "Use 'x%' with x > 0. Example: 50% for median."
                    )
                # Trino uses APPROX_PERCENTILE
                self.eval(
                    name, f"APPROX_PERCENTILE({columns[0]}, {x}) OVER ({by_clause})"
                )

            elif func == "range":
                self.eval(
                    name,
                    f"MAX({columns[0]}) OVER ({by_clause}) - MIN({columns[0]}) OVER ({by_clause})",
                )

            elif func == "iqr":
                self.eval(
                    name,
                    f"""APPROX_PERCENTILE({columns[0]}, 0.75) OVER ({by_clause}) - 
                        APPROX_PERCENTILE({columns[0]}, 0.25) OVER ({by_clause})""",
                )

            elif func == "sem":
                # Standard Error of Mean
                self.eval(
                    name,
                    f"STDDEV({columns[0]}) OVER ({by_clause}) / SQRT(COUNT({columns[0]}) OVER ({by_clause}))",
                )

            elif func == "prod":
                # Product: use EXP(SUM(LN(...)))
                self.eval(
                    name,
                    f"""CASE 
                        WHEN MOD(SUM(CASE WHEN {columns[0]} < 0 THEN 1 ELSE 0 END) OVER ({by_clause}), 2) = 0 
                        THEN 1 ELSE -1 
                        END * 
                        EXP(SUM(LN(ABS({columns[0]}))) OVER ({by_clause}))""",
                )

            elif func == "variance":
                # Use VAR_SAMP or VAR_POP
                self.eval(name, f"VAR_SAMP({columns[0]}) OVER ({by_clause})")

            elif func == "stddev":
                # Use STDDEV_SAMP or STDDEV_POP
                self.eval(name, f"STDDEV_SAMP({columns[0]}) OVER ({by_clause})")

            else:
                # Generic aggregates (MAX, MIN, AVG, SUM, COUNT)
                self.eval(name, f"{func.upper()}({columns[0]}) OVER ({by_clause})")

        # Functions that NEED ORDER BY
        elif func in (
            "lead",
            "lag",
            "row_number",
            "percent_rank",
            "dense_rank",
            "rank",
            "first_value",
            "last_value",
            "pct_change",
        ):

            if not columns and func in (
                "lead",
                "lag",
                "first_value",
                "last_value",
                "pct_change",
            ):
                raise ValueError(
                    f"The parameter 'columns' must be a VastFrame column when "
                    f"using analytic method '{func}'"
                )

            if columns and func in ("row_number", "percent_rank", "dense_rank", "rank"):
                raise ValueError(
                    f"The parameter 'columns' must be empty when using analytic method '{func}'"
                )

            if by_clause and order_by_clause:
                order_by_clause = f" {order_by_clause}"

            if func in ("lead", "lag"):
                info_param = f", {offset}"
                ignore_nulls = ""
            elif func in ("last_value", "first_value"):
                info_param = ""
                ignore_nulls = " IGNORE NULLS"
            else:
                info_param = ""
                ignore_nulls = ""

            if func == "pct_change":
                self.eval(
                    name,
                    f"{columns[0]} / NULLIF(LAG({columns[0]}) OVER ({by_clause}{order_by_clause}), 0)",
                )
            else:
                columns0 = columns[0] if columns else ""
                self.eval(
                    name,
                    f"{func.upper()}({columns0}{info_param}){ignore_nulls} OVER ({by_clause}{order_by_clause})",
                )

        else:
            # Try generic function
            try:
                self.eval(
                    name,
                    f"{func.upper()}({columns[0] if columns else ''}) OVER ({by_clause}{order_by_clause})",
                )
            except:
                raise ValueError(
                    f"The aggregate function '{func}' doesn't exist or is not "
                    "managed by the 'analytic' method. Use the 'eval' method for more flexibility."
                )

        return self

    @save_vastorbit_logs
    def apply(self, func: dict) -> "VastFrame":
        """
        Applies each function of the dictionary to the input VastColumns.

        Parameters
         ----------
         func: dict
            Dictionary of functions.
            The dictionary must be in the following format:
            {column1: func1, ..., columnk: funck}. Each function variable
            must be  composed of two  flower brackets {}. For example, to
            apply the function x -> x^2 + 2, use "POWER({}, 2) + 2".

         Returns
         -------
         VastFrame
            self

        Examples
        ---------

        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us work with the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

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

        Now let us apply two functions on the two different columns.

        - "boat"
        - "age"

        For the "boat" column, we will encode it to
        a binary form which makes it easier to process in
        certain ML algorithms.

        For the "age" column, we will fill in the missing
        values based on the columns "pclass" and "sex".

        .. code-block::

            vdf.apply(func = {
                    "boat": "CASE {} WHEN NULL THEN 0 ELSE 1 END",
                    "age" : "COALESCE(age, AVG({}) OVER (PARTITION BY pclass, sex))",
                }
            )

        .. ipython:: python
            :suppress:

            vdf.apply(func = {
                    "boat": "CASE {} WHEN NULL THEN 0 ELSE 1 END",
                    "age" : "COALESCE(age, AVG({}) OVER (PARTITION BY pclass, sex))",
                }
            )
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_apply.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_apply.html

        .. note::

            Applying a function will alter the :py:class:`~VastColumn`
            structure. It's advisable to check the current
            relation of the :py:class:`~VastFrame` to ensure it
            aligns with the intended outcome. For more information
            on achieving that, check out the ``current_relation``
            documentation.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.analytic` : Advanced Analytical functions.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.applymap` : Apply functions to all columns.
        """
        func = self.format_colnames(func)
        for column in func:
            self[column].apply(func[column])
        return self

    @save_vastorbit_logs
    def applymap(self, func: str, numeric_only: bool = True) -> "VastFrame":
        """
        Applies a function to all VastColumns.

        Parameters
        ----------
        func: str
            Function to apply.
            The function variable must be composed of two flower
            brackets {}.
            For example to  apply the function ``x -> x^2 + 2``,
            use ``POWER({}, 2) + 2``.
        numeric_only: bool, optional
            If set to True,  only the  numerical columns is used.

        Returns
        -------
        VastFrame
            self

        Examples
        ---------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us work with the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

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

        Notice there are some ``null`` values for numeric
        columns such as "age". We can fill these empty values
        using ``applymap``:

        .. code-block::

            vdf.applymap(
                func = "COALESCE({}, 0)",
                numeric_only = True,
            )

        .. ipython:: python
            :suppress:

            vdf.applymap(
                func = "COALESCE({}, 0)",
                numeric_only = True,
            )
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_applymap.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_applymap.html

        Now all the ``null`` values are converted to 0.

        .. note::

            Applying a function will alter the :py:class:`~VastColumn`
            structure. It's advisable to check the current
            relation of the :py:class:`~VastFrame` to ensure it
            aligns with the intended outcome. For more information
            on achieving that, check out the ``current_relation``
            documentation.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.analytic` : Advanced Analytical functions.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.apply` : Apply functions using a dictionary.
        """
        function = {}
        columns = self.numcol() if numeric_only else self.get_columns()
        for column in columns:
            function[column] = (
                func
                if not self[column].isbool()
                else func.replace("{}", "CAST({} AS INT)")
            )
        return self.apply(function)


class vDCMath(vDCFilter):
    def __len__(self) -> int:
        return int(self.count())

    def __nonzero__(self) -> bool:
        return self.count() > 0

    @save_vastorbit_logs
    def abs(self) -> "VastFrame":
        """
        Applies the absolute value function to the input VastColumn.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with negative values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [10, -10, 20, -2]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_abs.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_abs.html

        Now we can convert all to absolute values:

        .. code-block:: python

            vdf["val"].abs()

        .. ipython:: python
            :suppress:

            vdf["val"].abs()
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_abs_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_abs_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "ABS(val)"

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.abs` :
                Absolute function for entire :py:class:`~VastFrame`.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.apply` :
                Apply functions using SQL.
        """
        return self.apply(func="ABS({})")

    @save_vastorbit_logs
    def add(self, x: PythonNumber) -> "VastFrame":
        """
        Adds the input element to the VastColumn.

        Parameters
        ----------
        x: float
            If the VastColumn type is date (date, datetime ...),
            the parameter  'x' represents the  number  of seconds,
            otherwise it represents a number.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with negative values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [10, -10, 20, -2]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_add.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_add.html

        We can conveniently add 5 to all the values in a column:

        .. code-block:: python

            vdf["val"].add(5)

        .. ipython:: python
            :suppress:

            vdf["val"].add(5)
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_add_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_add_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "val + 5"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.mul` :
                Multiply the :py:class:`~VastColumn` by a value.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.div` :
                Divide the :py:class:`~VastColumn` by a value.
        """
        if self.isdate():
            return self.apply(func=f"TIMESTAMPADD(SECOND, {x}, {{}})")
        else:
            return self.apply(func=f"{{}} + ({x})")

    @save_vastorbit_logs
    def apply(
        self, func: Union[str, StringSQL], copy_name: Optional[str] = None
    ) -> "VastFrame":
        """
        Applies a function to the VastColumn.

        Parameters
        ----------
        func: str,
            Function in pure SQL used to transform the VastColumn.
            The  function variable must be composed of two  flower
            brackets {}. For example, to apply the function

            .. math::

                x -> x^2 + 2,

            use ``POWER({}, 2) + 2``.

        copy_name: str, optional
            If non-empty, a copy is created using the input name.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us work with the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

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

        Now let us apply a function on the "boat" column.

        For the "boat" column, we will encode it to
        a binary form which makes it easier to process in
        certain ML algorithms.

        .. code-block::

            vdf["boat"].apply(func = "CASE {} WHEN NULL THEN 0 ELSE 1 END")

        .. ipython:: python
            :suppress:

            vdf["boat"].apply(func = "CASE {} WHEN NULL THEN 0 ELSE 1 END")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply.html

        We can also make a new column which has the applied function:

        .. code-block::

            vdf["boat"].apply(
                func = "CASE {} WHEN NULL THEN 0 ELSE 1 END",
                copy_name = "new_boats",
            )

        .. ipython:: python
            :suppress:

            vdf["boat"].apply(func = "CASE {} WHEN NULL THEN 0 ELSE 1 END", copy_name = "new_boats")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply_2.html

        .. note::

            Applying a function will alter the :py:class:`~VastColumn`
            structure. It's advisable to check the current
            relation of the :py:class:`~VastFrame` to ensure it
            aligns with the intended outcome. For more information
            on achieving that, check out the ``current_relation``
            documentation.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.apply` : Applies each
                function of the dictionary to the input :py:class:`~VastColumn`.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.apply_fun` : Applies a
                default function to the :py:class:`~VastColumn`.

        """
        if isinstance(func, StringSQL):
            func = str(func)
        func_apply = func.replace("{}", self._alias)
        alias_sql_repr = self._alias.replace('"', "")
        try:
            ctype = get_data_types(
                expr=f"""
                    SELECT 
                        {func_apply} AS apply_test_feature 
                    FROM {self._parent} 
                    WHERE {self} IS NOT NULL 
                    LIMIT 0""",
                column="apply_test_feature",
            )
            category = to_category(ctype=ctype)
            all_cols, max_floor = self._parent.get_columns(), 0
            for column in all_cols:
                try:
                    column_str = column.replace('"', "")
                    if (quote_ident(column) in func) or (
                        re.search(
                            re.compile(f"\\b{column_str}\\b"),
                            func,
                        )
                    ):
                        max_floor = max(len(self._parent[column]._transf), max_floor)
                except:
                    pass
            max_floor -= len(self._transf)
            if copy_name:
                copy_name_str = copy_name.replace('"', "")
                self.add_copy(name=copy_name_str)
                self._parent[copy_name_str]._transf += [
                    ("{}", self.ctype(), self.category())
                ] * max_floor
                self._parent[copy_name_str]._transf += [(func, ctype, category)]
                self._parent[copy_name_str]._catalog = self._catalog
            else:
                for k in range(max_floor):
                    self._transf += [("{}", self.ctype(), self.category())]
                self._transf += [(func, ctype, category)]
                self._parent._update_catalog(erase=True, columns=[self._alias])
            self._parent._add_to_history(
                f"[Apply]: The VastColumn '{alias_sql_repr}' was "
                f"transformed with the func 'x -> {func_apply}'."
            )
            return self._parent
        except Exception as e:
            raise QueryError(
                f"{e}\nError when applying the func 'x -> {func_apply}' "
                f"to '{alias_sql_repr}'"
            )

    @save_vastorbit_logs
    def apply_fun(
        self,
        func: Literal[
            "abs",
            "acos",
            "asin",
            "atan",
            "avg",
            "cbrt",
            "ceil",
            "contains",
            "count",
            "cos",
            "cosh",
            "cot",
            "cardinality",
            "exp",
            "element_at",
            "floor",
            "len",
            "length",
            "ln",
            "log",
            "log10",
            "max",
            "mean",
            "mod",
            "min",
            "pow",
            "power",
            "round",
            "sign",
            "sin",
            "sinh",
            "sum",
            "sqrt",
            "tan",
            "tanh",
        ],
        x: PythonScalar = 2,
    ) -> "VastFrame":
        """
        Applies a default function to the VastColumn.

        Parameters
        ----------
        func: str
            Function to use to transform the VastColumn.

            - abs:
                absolute value
            - acos:
                trigonometric inverse cosine
            - asin:
                trigonometric inverse sine
            - atan:
                trigonometric inverse tangent
            - avg / mean:
                average
            - cbrt:
                cube root
            - ceil:
                value up to the next whole number
            - contains:
                checks if ``x`` is in the array
            - count:
                number of non-null elements
            - cos:
                trigonometric cosine
            - cosh:
                hyperbolic cosine
            - cot:
                trigonometric cotangent
            - cardinality:
                number of elements in array
            - exp:
                exponential function
            - element_at:
                returns element at specified position in array
            - floor:
                value down to the next whole number
            - len / length:
                length of string or array
            - ln:
                natural logarithm
            - log:
                logarithm
            - log10:
                base 10 logarithm
            - max:
                maximum
            - min:
                minimum
            - mod:
                remainder of a division operation
            - pow / power:
                number raised to the power of another number
            - round:
                rounds a value to a specified number of
                decimal places
            - sign:
                arithmetic sign
            - sin:
                trigonometric sine
            - sinh:
                hyperbolic sine
            - sqrt:
                arithmetic square root
            - sum:
                sum
            - tan:
                trigonometric tangent
            - tanh:
                hyperbolic tangent

        x: PythonScalar, optional
            If the function has two arguments (example, power or mod),
            ``x`` represents the second argument.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with float values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [0.2, 10.6, 20.1]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply_fun.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply_fun.html

        A ``ceil`` function can be conveniently applied using the
        ``apply_fun`` function. Below, we can round off the values of
        "val" column:

        .. code-block:: python

            vdf["val"].apply_fun("ceil")

        .. ipython:: python
            :suppress:

            vdf["val"].apply_fun("ceil")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply_fun_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_apply_fun_2.html

        .. note::

            Applying a function will alter the :py:class:`~VastColumn`
            structure. It's advisable to check the current
            relation of the :py:class:`~VastFrame` to ensure it
            aligns with the intended outcome. For more information
            on achieving that, check out the ``current_relation``
            documentation.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.applymap` :
                Applies a function to all :py:class:`~VastColumn`s.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.apply` :
                Applies a function to the :py:class:`~VastColumn`.
        """
        # Normalize aliases
        func = func.lower()
        if func == "mean":
            func = "avg"
        elif func == "length":
            func = "len"
        elif func == "power":
            func = "pow"
        elif func == "contain":
            func = "contains"
        elif func == "dim":
            func = "cardinality"

        cat = self.category().lower()
        ctype = self.ctype().lower()

        # Trino array functions
        if ctype.startswith("array"):
            if func == "len":
                # For arrays, use cardinality
                expr = "CARDINALITY({})"
            elif func == "cardinality":
                expr = "CARDINALITY({})"
            elif func in ("max", "min"):
                # Trino uses array_max, array_min
                expr = f"ARRAY_{func.upper()}({{}})"
            elif func == "sum":
                # Use reduce for sum
                expr = "REDUCE({}, 0.0, (s, x) -> s + x, s -> s)"
            elif func == "avg":
                # Use reduce for average
                expr = "REDUCE({}, CAST(ROW(0.0, 0) AS ROW(sum DOUBLE, count INTEGER)), (s, x) -> CAST(ROW(s.sum + x, s.count + 1) AS ROW(sum DOUBLE, count INTEGER)), s -> IF(s.count = 0, NULL, s.sum / s.count))"
            elif func == "count":
                # Count non-null elements
                expr = "CARDINALITY(FILTER({}, x -> x IS NOT NULL))"
            elif func == "contains":
                # Check if array contains element
                if isinstance(x, str):
                    x_escaped = "'" + str(x).replace("'", "''") + "'"
                else:
                    x_escaped = str(x)
                expr = f"CONTAINS({{}}, {x_escaped})"
            elif func == "element_at":
                # Get element at position (1-indexed in Trino)
                expr = f"ELEMENT_AT({{}}, {x})"
            else:
                # Default array function
                expr = f"{func.upper()}({{}})"

        # String functions
        elif cat == "text" or ctype.startswith("varchar"):
            if func == "len":
                expr = "LENGTH({})"
            elif func == "contains":
                if isinstance(x, str):
                    x_escaped = "'" + str(x).replace("'", "''") + "'"
                else:
                    x_escaped = str(x)
                expr = f"STRPOS({{}}, {x_escaped}) > 0"
            else:
                # Standard functions
                if func not in ("log", "mod", "pow", "round"):
                    expr = f"{func.upper()}({{}})"
                elif func == "log":
                    # Trino log(base, value)
                    expr = f"LOG({x}, {{}})"
                elif func in ("mod", "pow", "round"):
                    expr = f"{func.upper()}({{}}, {x})"

        # Numeric functions (default)
        else:
            if func not in (
                "log",
                "mod",
                "pow",
                "round",
                "contains",
                "element_at",
                "cot",
            ):
                expr = f"{func.upper()}({{}})"
            elif func == "log":
                # Trino: LOG(base, value)
                expr = f"LOG({x}, {{}})"
            elif func in ("mod", "pow", "round"):
                expr = f"{func.upper()}({{}}, {x})"
            elif func == "cot":
                expr = f"COS({{}}) / SIN({{}})"
            elif func == "contains":
                # Not applicable for scalars
                raise ValueError(
                    f"Function '{func}' is only applicable to arrays or strings"
                )
            elif func == "element_at":
                # Not applicable for scalars
                raise ValueError(f"Function '{func}' is only applicable to arrays")

        return self.apply(func=expr)

    @save_vastorbit_logs
    def date_part(self, field: str) -> "VastFrame":
        """
        Extracts a specific TS field  from the VastColumn (only if
        the VastColumn type is date like). The VastColumn is
        transformed.

        Parameters
        ----------
        field: str
            The field to extract. It must be one of the following:
            century | day | decade | doq | dow | doy | epoch | hour
            | isodow | isoweek | isoyear | millennium
            | milliseconds | minute | month | quarter | second | time
             zone | timezone_hour | timezone_minute | week | year

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset that has timestamp values:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "time": [
                        "1993-11-03 00:00:00",
                        "1993-11-04 00:00:01",
                        "1993-11-05 00:00:02",
                        "1993-11-06 00:00:04",
                        "1993-11-07 00:00:05",
                    ],
                    "val": [0., 1., 2., 4.,5.],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_date_part.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_date_part.html

        We can make sure that the column has the correct data type:

        .. code-block:: python

            vdf["time"].astype("timestamp")

        Next, we can apply the ``date_part`` function to
        get the required temporal details:

        .. code-block::

            vdf["time"].date_part(field = "day")

        .. ipython:: python
            :suppress:

            vdf["time"].astype("timestamp")
            vdf["time"].date_part(field = "day")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_date_part_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_date_part_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "DATE_PART('DAY', val)"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.slice` :
                Slice the :py:class:`~VastColumn` by custom time-steps.
        """
        return self.apply(func=f"EXTRACT({field.upper()} FROM {{}})")

    @save_vastorbit_logs
    def div(self, x: PythonNumber) -> "VastFrame":
        """
        Divides the VastColumn by the input element.

        Parameters
        ----------
        x: PythonNumber
            Input number.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with some values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [10, -10, 20, -2]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_divide.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_divide.html

        We can conveniently divide all the values in a column
        by 5:

        .. code-block:: python

            vdf["val"].div(5)

        .. ipython:: python
            :suppress:

            vdf["val"].div(5)
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_divide_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_divide_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "val / 5"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.mul` :
                Multiply the :py:class:`~VastColumn` by a value.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.add` :
                Add a value to the :py:class:`~VastColumn`.
        """
        assert x != 0, ValueError("Division by 0 is forbidden !")
        return self.apply(func=f"{{}} / ({x})")

    def get_len(self) -> "VastColumn":
        """
        Returns a new :py:class:`~VastColumn` that represents
        the length of each element.

        Returns
        -------
        VastColumn
            VastColumn that includes the length of each
            element.

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with string values:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "val" : ['Hello', 'Meow', 'Gaza', 'New York'],
                },
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_get_len.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_get_len.html

        We can conveniently get the length of each row
        in a column:

        .. code-block:: python

            vdf["val"].get_len()

        .. ipython:: python
            :suppress:

            result = vdf["val"].get_len()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_get_len_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_get_len_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "LENGTH(val)"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.date_part` :
                Extracts a specific TS field from the :py:class:`~VastColumn`.
        """
        cat = self.category()

        # Determine appropriate length function based on column type
        if cat == "array":
            # For arrays, use CARDINALITY
            fun = "CARDINALITY"
        elif cat == "complex":
            # For complex types (MAP, ROW), use CARDINALITY
            fun = "CARDINALITY"
        elif cat in ("text", "varchar", "char"):
            # For strings, use LENGTH
            fun = "LENGTH"
        else:
            # Default to LENGTH (works for most types)
            fun = "LENGTH"

        elem_to_select = f"{fun}({self})"
        init_transf = f"{fun}({self._init_transf})"
        new_alias = quote_ident(self._alias[1:-1] + ".length")

        query = f"""
            SELECT 
                {elem_to_select} AS {new_alias} 
            FROM {self._parent}"""

        vcol = create_new_vdf(query)[new_alias]
        vcol._init_transf = init_transf
        return vcol

    @save_vastorbit_logs
    def round(self, n: int) -> "VastFrame":
        """
        Rounds the VastColumn by keeping only the input number
        of digits after the decimal point.

        Parameters
        ----------
        n: int
            Number of digits to keep after the decimal point.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with float values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [0.21, 11.26, 20.21]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_round.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_round.html

        AWe can conveniently round off the numbers and select the decimal
        point as well using ``n``:

        .. code-block:: python

            vdf["val"].round(n = 1)

        .. ipython:: python
            :suppress:

            vdf["val"].round(n = 1)
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_round_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_round_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "ROUND(val, 1)"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.abs` : Get the
                absolute value of a :py:class:`~VastColumn`.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.abs` : Get the
                absolute value of mutiple :py:class:`~VastColumn`.
        """
        return self.apply(func=f"ROUND({{}}, {n})")

    @save_vastorbit_logs
    def mul(self, x: PythonNumber) -> "VastFrame":
        """
        Multiplies the VastColumn by the input element.

        Parameters
        ----------
        x: PythonNumber
            Input number.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with some values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [10, -10, 20, -2]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_multiply.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_multiply.html

        We can conveniently multiply all the values in a column
        by 5:

        .. code-block:: python

            vdf["val"].mul(5)

        .. ipython:: python
            :suppress:

            vdf["val"].mul(5)
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_multiply_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_multiply_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "val * 5"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.add` :
                Add a value to the entire :py:class:`~VastColumn`.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.div` :
                Divide the :py:class:`~VastColumn` by a value.
        """
        return self.apply(func=f"{{}} * ({x})")

    @save_vastorbit_logs
    def slice(
        self, length: int, unit: str = "second", start: bool = True
    ) -> "VastFrame":
        """
        Slices and transforms the VastColumn using a time series rule.

        Parameters
        ----------
        length: int
            Slice size.
        unit: str, optional
            Slice size unit. Options: 'second', 'minute', 'hour', 'day',
            'week', 'month', 'quarter', 'year'
        start: bool, optional
            If set to True, the record is sliced using the floor
            of the slicing (start of period).

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        .. code-block:: python

            import vastorbit as vo

            vdf = vo.VastFrame({
                "time": [
                    "1993-11-03 00:00:00",
                    "1993-11-03 00:30:01",
                    "1993-11-03 00:31:00",
                    "1993-11-03 01:05:01",
                    "1993-11-03 01:41:02",
                    "1993-11-03 01:50:00",
                ],
                "val": [0., 1., 2., 4., 5., 4.],
            })

            vdf["time"].astype("timestamp")

            # Slice into 30 minute intervals
            vdf["time"].slice(30, "minute")

        .. seealso::
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.date_part` : Extracts
                a specific TS field from the VastColumn.
        """
        unit = unit.upper()

        # Trino doesn't have TIME_SLICE, use DATE_TRUNC + arithmetic
        if length == 1:
            # Simple case: use DATE_TRUNC directly
            func = f"DATE_TRUNC('{unit}', {{}})"
        else:
            # Complex case: need to compute intervals
            func = self._parent._get_time_slice_expression(length, unit, start)

        return self.apply(func=func)

    @save_vastorbit_logs
    def sub(self, x: PythonNumber) -> "VastFrame":
        """
        Subtracts the input element from the VastColumn.

        Parameters
        ----------
        x: PythonNumber
            If the VastColumn type is date (date, datetime ...),
            the parameter 'x' represents  the number of seconds,
            otherwise it represents a number.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. code-block:: python

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

        Let us create a dummy dataset with negative values:

        .. ipython:: python

            vdf = vo.VastFrame({"val" : [10, -10, 20, -2]})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_sub.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_sub.html

        We can conveniently substract 5 from all the values
        in a column:

        .. code-block:: python

            vdf["val"].sub(5)

        .. ipython:: python
            :suppress:

            vdf["val"].sub(5)
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_sub_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_math_vdc_sub_2.html

        .. note::

            While the same task can be accomplished using pure SQL (see below),
            adopting a Pythonic approach can offer greater convenience and help
            avoid potential syntax errors.

            .. code-block:: python

                vdf["val"] = "val - 5"

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.mul` :
                Multiply the :py:class:`~VastColumn` by a value.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.add` :
                Add a value to the entire :py:class:`~VastColumn`.
        """
        if self.isdate():
            return self.apply(func=f"TIMESTAMPADD(SECOND, -({x}), {{}})")
        else:
            return self.apply(func=f"{{}} - ({x})")
