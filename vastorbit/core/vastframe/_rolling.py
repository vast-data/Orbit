"""
SPDX-License-Identifier: Apache-2.0
"""

import datetime
from typing import Optional, Union

from vastorbit._typing import SQLColumns, TYPE_CHECKING
from vastorbit._utils._gen import gen_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type

from vastorbit.core.vastframe._corr import vDFCorr

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFRolling(vDFCorr):
    @save_vastorbit_logs
    def rolling(
        self,
        func: str,
        window: Union[list, tuple],
        columns: SQLColumns,
        by: Optional[SQLColumns] = None,
        order_by: Union[None, dict, list] = None,
        name: Optional[str] = None,
    ) -> "VastFrame":
        """
        Adds a new :py:class:`~VastColumn` to the
        :py:class:`~VastFrame` by using an advanced
        analytical window function on one or two
        specific :py:class:`~VastColumn`.

        .. warning::

            Some window functions can make the
            VastFrame structure heavier. It is
            recommended to always check the current
            structure with the ``current_relation``
            method and to save it with the ``to_db``
            method, using the parameters ``inplace
            = True`` and ``relation_type = table``.

        .. warning::

            Make use of the ``order_by`` parameter to sort
            your data. Otherwise, you might encounter unexpected
            results, as databases do not work with indexes, and
            the data may be randomly shuffled.

        Parameters
        ----------
        func: str
            Function to use.

            - aad:
                average absolute deviation
            - beta:
                Beta Coefficient between 2 VastColumns
            - count:
                number of non-missing elements
            - corr:
                Pearson correlation between 2 VastColumns
            - cov:
                covariance between 2 VastColumns
            - kurtosis:
                kurtosis
            - jb:
                Jarque-Bera index
            - max:
                maximum
            - mean:
                average
            - min:
                minimum
            - prod:
                product (geometric mean via exp/log)
            - range:
                difference between the max and the min
            - sem:
                standard error of the mean
            - skewness:
                skewness
            - sum:
                sum
            - std:
                standard deviation
            - var:
                variance

            Other window functions could work if it is part of
            the DB version you are using.

        window: list | tuple
            Window Frame Range.
            If set to two integers, computes a Row Window, otherwise
            it computes a Time Window. For example, if set to
            ``(-5, 1)``, the moving windows will take 5 rows preceding
            and one following. If set to ``('- 5 minutes', '0 minutes')``,
            the moving window will take all elements of the last 5
            minutes.
        columns: SQLColumns
            Input :py:class:`~VastColumn`. Must be a list of one
            or two elements.
        by: SQLColumns, optional
            VastColumns used in the partition.
        order_by: dict | list, optional
            List of the VastColumns used to sort the data using
            ascending/descending order or a dictionary of all the
            sorting methods.
            For example, to sort by "column1" ASC and "column2" DESC,
            use: ``{"column1": "asc", "column2": "desc"}``.
        name: str, optional
            Name of the new :py:class:`~VastColumn`. If empty, a
            default name is generated.

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

        For this example, let's generate
        the following dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "date": [
                        "2014-01-01",
                        "2014-01-02",
                        "2014-01-03",
                        "2014-01-04",
                        "2014-01-05",
                        "2014-01-06",
                        "2014-01-07",
                    ],
                    "expenses": [40, 10, 12, 54, 98, 132, 50],
                    "sale": [100, 120, 120, 110, 100, 90, 80],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_rolling_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_rolling_1.html

        Let us make sure the correct data type is assigned:

        .. code-block:: python

            vdf["date"].astype("timestamp")

        We can now employ the ``rolling`` function,
        specifying a custom window size, to visualize
        the data.

        .. code-block:: python

            vdf.rolling(
                func = "sum",
                window = (-1,1),
                columns = ["sale"],
            )

        .. ipython:: python
            :suppress:

            vdf["date"].astype("timestamp")
            vdf.rolling(func = "sum", window = (-1,1), columns = ["sale"])
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_rolling.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_rolling.html

        .. note::

            Rolling windows are valuable in time-series data for creating
            features because they allow us to analyze a specified number
            of past data points at each step. This approach is useful
            for capturing trends over time, adapting to different time
            scales, and smoothing out noise in the data. By applying
            aggregation functions within these windows, such as calculating
            averages or sums, we can generate new features that provide
            insights into the historical patterns of the dataset.
            These features, based on past observations, contribute to
            building more informed and predictive models, enhancing
            our understanding of the underlying trends in the data.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.analytic` : Advanced Analytical functions.
        """
        columns, by, order_by = format_type(columns, by, order_by, dtype=list)
        if len(window) != 2:
            raise ValueError("The window must be composed of exactly 2 elements.")

        window = list(window)
        rule = [0, 0]
        method = "rows"

        # Parse window bounds
        for idx, w in enumerate(window):
            if isinstance(w, (int, float)) and abs(w) == float("inf"):
                w = "unbounded"

            if isinstance(w, str):
                if w.lower() == "unbounded":
                    rule[idx] = "PRECEDING" if idx == 0 else "FOLLOWING"
                    window[idx] = "UNBOUNDED"
                else:
                    # Parse time intervals like "- 5 minutes"
                    nb_min = 0
                    for i, char in enumerate(window[idx]):
                        if char == "-":
                            nb_min += 1
                        elif char != " ":
                            break
                    rule[idx] = "PRECEDING" if nb_min % 2 == 1 else "FOLLOWING"
                    interval_str = window[idx][i:].strip()
                    window[idx] = f"INTERVAL '{interval_str}'"
                    method = "range"
            elif isinstance(w, datetime.timedelta):
                rule[idx] = (
                    "PRECEDING" if window[idx] < datetime.timedelta(0) else "FOLLOWING"
                )
                # Convert timedelta to interval
                total_seconds = abs(int(window[idx].total_seconds()))
                window[idx] = f"INTERVAL '{total_seconds}' SECOND"
                method = "range"
            else:
                rule[idx] = "PRECEDING" if int(window[idx]) < 0 else "FOLLOWING"
                window[idx] = abs(int(window[idx]))

        columns = format_type(columns, dtype=list)
        if not name:
            name = gen_name(
                [func] + columns + [str(window[0]), rule[0], str(window[1]), rule[1]]
            )
            name = f"moving_{name}"

        columns, by = self.format_colnames(columns, by)
        by = "" if not by else "PARTITION BY " + ", ".join(by)

        if not order_by:
            order_by = f" ORDER BY {columns[0]}"
        else:
            order_by = self._get_sort_syntax(order_by)

        # Build window frame
        windows_frame = f""" 
            OVER ({by}{order_by} 
            {method.upper()} 
            BETWEEN {window[0]} {rule[0]} 
            AND {window[1]} {rule[1]})"""

        func_lower = func.lower()

        # Map function names to SQL functions
        if func_lower in ("mean", "avg"):
            expr = f"AVG({columns[0]})#"

        elif func_lower == "std":
            expr = f"STDDEV({columns[0]})#"

        elif func_lower == "var":
            expr = f"VAR_SAMP({columns[0]})#"

        elif func_lower == "kurtosis":
            # Trino has built-in KURTOSIS function
            expr = f"KURTOSIS({columns[0]})#"

        elif func_lower == "skewness":
            # Trino has built-in SKEWNESS function
            expr = f"SKEWNESS({columns[0]})#"

        elif func_lower == "jb":
            # Jarque-Bera = n/6 * (S^2 + (K-3)^2/4)
            # where S = skewness, K = kurtosis, n = count
            expr = f"""
                COUNT({columns[0]})# / 6.0 * (
                    POWER(SKEWNESS({columns[0]})#, 2) + 
                    POWER(KURTOSIS({columns[0]})# - 3, 2) / 4.0
                )"""

        elif func_lower == "aad":
            # Average absolute deviation from mean
            # Need to compute mean first, then avg of abs deviations
            # For window functions, we'll use the approximation
            import secrets

            columns_0_str = columns[0].replace('"', "").lower()
            random_int = secrets.randbelow(10000001)
            mean_name = f"{columns_0_str}_mean_{random_int}"

            self.eval(mean_name, f"AVG({columns[0]}){windows_frame}")
            expr = f"AVG(ABS({columns[0]} - {mean_name}))#"

        elif func_lower == "prod":
            # Product using exp(sum(ln(abs(x))))
            # Handle sign and zeros
            expr = f"""
                CASE 
                    WHEN COUNT(CASE WHEN {columns[0]} = 0 THEN 1 END)# > 0 THEN 0
                    ELSE 
                        CASE MOD(COUNT(CASE WHEN {columns[0]} < 0 THEN 1 END)#, 2)
                            WHEN 0 THEN 1
                            ELSE -1
                        END 
                        * EXP(SUM(LN(ABS({columns[0]})))#)
                END"""

        elif func_lower in ("corr", "cov", "beta"):
            if len(columns) < 2 or columns[1] == columns[0]:
                if func_lower == "cov":
                    expr = f"VAR_SAMP({columns[0]})#"
                else:
                    expr = "1"
            else:
                if func_lower == "corr":
                    expr = f"CORR({columns[0]}, {columns[1]})#"
                elif func_lower == "beta":
                    expr = f"COVAR_SAMP({columns[0]}, {columns[1]})# / NULLIF(VAR_SAMP({columns[1]})#, 0)"
                else:  # cov
                    expr = f"COVAR_SAMP({columns[0]}, {columns[1]})#"

        elif func_lower == "range":
            expr = f"MAX({columns[0]})# - MIN({columns[0]})#"

        elif func_lower == "sem":
            # Standard error of mean = STDDEV / SQRT(COUNT)
            expr = f"STDDEV({columns[0]})# / SQRT(COUNT({columns[0]})#)"

        elif func_lower == "count":
            expr = f"COUNT({columns[0]})#"

        elif func_lower in ("max", "min", "sum"):
            expr = f"{func_lower.upper()}({columns[0]})#"

        else:
            # Try using the function as-is (for any other SQL aggregate functions)
            expr = f"{func.upper()}({columns[0]})#"

        # Replace # with window frame
        expr = expr.replace("#", windows_frame)

        self.eval(name=name, expr=expr)

        if func_lower == "aad":
            self._vars["exclude_columns"] += [f'"{mean_name}"']

        return self

    @save_vastorbit_logs
    def cummax(
        self,
        column: str,
        by: Optional[SQLColumns] = None,
        order_by: Union[None, dict, list] = None,
        name: Optional[str] = None,
    ) -> "VastFrame":
        """
        Adds a new :py:class:`~VastColumn` to the
        :py:class:`~VastFrame` by computing the
        cumulative maximum of the input
        :py:class:`~VastColumn`.

        .. warning::

            Make use of the ``order_by`` parameter to sort
            your data. Otherwise, you might encounter unexpected
            results, as databases do not work with indexes, and
            the data may be randomly shuffled.

        Parameters
        ----------
        column: str
            Input :py:class:`~VastColumn`.
        by: list, optional
            VastColumns used in the partition.
        order_by: dict | list, optional
            List of the :py:class:`~VastColumn` used to
            sort the data using ascending/descending order
            or a dictionary of all the sorting methods.
            For example, to sort by "column1" ASC and
            "column2" DESC, use:
            ``{"column1": "asc", "column2": "desc"}``.
        name: str, optional
            Name of the new :py:class:`~VastColumn`. If
            empty, a default name is generated.

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

        For this example, let's generate
        the following dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "id": [0, 1, 2, 3, 4, 5, 6],
                    "sale": [100, 120, 120, 110, 100, 90, 80],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummax_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummax_1.html

        Now the cumulative maximum of the selected
        column can be easily calculated:

        .. code-block:: python

            vdf.cummax(
                "sale",
                name = "cummax_sales",
                order_by = "id",
            )

        .. ipython:: python
            :suppress:

            vdf.cummax("sale", name = "cummax_sales", order_by = "id")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummax.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummax.html

        .. note::

            Rolling windows are valuable in time-series data for creating
            features because they allow us to analyze a specified number
            of past data points at each step. This approach is useful
            for capturing trends over time, adapting to different time
            scales, and smoothing out noise in the data. By applying
            aggregation functions within these windows, such as calculating
            averages or sums, we can generate new features that provide
            insights into the historical patterns of the dataset.
            These features, based on past observations, contribute to
            building more informed and predictive models, enhancing
            our understanding of the underlying trends in the data.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.rolling` : Advanced analytical
                window function.
        """
        return self.rolling(
            func="max",
            window=("UNBOUNDED", 0),
            columns=column,
            by=by,
            order_by=order_by,
            name=name,
        )

    @save_vastorbit_logs
    def cummin(
        self,
        column: str,
        by: Optional[SQLColumns] = None,
        order_by: Union[None, dict, list] = None,
        name: Optional[str] = None,
    ) -> "VastFrame":
        """
        Adds a new :py:class:`~VastColumn` to the
        :py:class:`~VastFrame` by computing the
        cumulative minimum of the input
        :py:class:`~VastColumn`.

        .. warning::

            Make use of the ``order_by`` parameter to sort
            your data. Otherwise, you might encounter unexpected
            results, as databases do not work with indexes, and
            the data may be randomly shuffled.

        Parameters
        ----------
        column: str
            Input :py:class:`~VastColumn`.
        by: list, optional
            VastColumns used in the partition.
        order_by: dict | list, optional
            List of the :py:class:`~VastColumn` used to
            sort the data using ascending/descending order
            or a dictionary of all the sorting methods.
            For example, to sort by "column1" ASC and
            "column2" DESC, use:
            ``{"column1": "asc", "column2": "desc"}``.
        name: str, optional
            Name of the new :py:class:`~VastColumn`. If
            empty, a default name is generated.

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

        For this example, let's generate
        the following dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "id": [0, 1, 2, 3, 4, 5, 6],
                    "sale": [100, 120, 120, 50, 100, 90, 80],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummin_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummin_1.html

        Now the cumulative minimum of the selected
        column can be easily calculated:

        .. code-block:: python

            vdf.cummin(
                "sale",
                name = "cummin_sales",
                order_by = "id",
            )

        .. ipython:: python
            :suppress:

            vdf.cummin("sale", name = "cummin_sales", order_by = "id")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummin.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cummin.html

        .. note::

            Rolling windows are valuable in time-series data for creating
            features because they allow us to analyze a specified number
            of past data points at each step. This approach is useful
            for capturing trends over time, adapting to different time
            scales, and smoothing out noise in the data. By applying
            aggregation functions within these windows, such as calculating
            averages or sums, we can generate new features that provide
            insights into the historical patterns of the dataset.
            These features, based on past observations, contribute to
            building more informed and predictive models, enhancing
            our understanding of the underlying trends in the data.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.rolling` : Advanced analytical
                window function.
        """
        return self.rolling(
            func="min",
            window=("UNBOUNDED", 0),
            columns=column,
            by=by,
            order_by=order_by,
            name=name,
        )

    @save_vastorbit_logs
    def cumprod(
        self,
        column: str,
        by: Optional[SQLColumns] = None,
        order_by: Union[None, dict, list] = None,
        name: Optional[str] = None,
    ) -> "VastFrame":
        """
        Adds a new :py:class:`~VastColumn` to the
        :py:class:`~VastFrame` by computing the
        cumulative product of the input
        :py:class:`~VastColumn`.

        .. warning::

            Make use of the ``order_by`` parameter to sort
            your data. Otherwise, you might encounter unexpected
            results, as databases do not work with indexes, and
            the data may be randomly shuffled.

        Parameters
        ----------
        column: str
            Input :py:class:`~VastColumn`.
        by: list, optional
            VastColumns used in the partition.
        order_by: dict | list, optional
            List of the :py:class:`~VastColumn` used to
            sort the data using ascending/descending order
            or a dictionary of all the sorting methods.
            For example, to sort by "column1" ASC and
            "column2" DESC, use:
            ``{"column1": "asc", "column2": "desc"}``.
        name: str, optional
            Name of the new :py:class:`~VastColumn`. If
            empty, a default name is generated.

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

        For this example, let's generate
        the following dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "id": [0, 1, 2, 3, 4, 5, 6],
                    "sale": [2, 3, 2, 2, 2, 2, 2],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumprod_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumprod_1.html

        Now the cumulative product of the selected
        column can be easily calculated:

        .. code-block:: python

            vdf.cumprod(
                "sale",
                name = "cumprod_sales",
                order_by = "id",
            )

        .. ipython:: python
            :suppress:

            vdf.cumprod("sale", name = "cumprod_sales", order_by = "id")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumprod.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumprod.html

        .. note::

            Rolling windows are valuable in time-series data for creating
            features because they allow us to analyze a specified number
            of past data points at each step. This approach is useful
            for capturing trends over time, adapting to different time
            scales, and smoothing out noise in the data. By applying
            aggregation functions within these windows, such as calculating
            averages or sums, we can generate new features that provide
            insights into the historical patterns of the dataset.
            These features, based on past observations, contribute to
            building more informed and predictive models, enhancing
            our understanding of the underlying trends in the data.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.rolling` : Advanced analytical
                window function.
        """
        return self.rolling(
            func="prod",
            window=("UNBOUNDED", 0),
            columns=column,
            by=by,
            order_by=order_by,
            name=name,
        )

    @save_vastorbit_logs
    def cumsum(
        self,
        column: str,
        by: Optional[SQLColumns] = None,
        order_by: Union[None, dict, list] = None,
        name: Optional[str] = None,
    ) -> "VastFrame":
        """
        Adds a new :py:class:`~VastColumn` to the
        :py:class:`~VastFrame` by computing the
        cumulative sum of the input
        :py:class:`~VastColumn`.

        .. warning::

            Make use of the ``order_by`` parameter to sort
            your data. Otherwise, you might encounter unexpected
            results, as databases do not work with indexes, and
            the data may be randomly shuffled.

        Parameters
        ----------
        column: str
            Input :py:class:`~VastColumn`.
        by: list, optional
            VastColumns used in the partition.
        order_by: dict | list, optional
            List of the :py:class:`~VastColumn` used to
            sort the data using ascending/descending order
            or a dictionary of all the sorting methods.
            For example, to sort by "column1" ASC and
            "column2" DESC, use:
            ``{"column1": "asc", "column2": "desc"}``.
        name: str, optional
            Name of the new :py:class:`~VastColumn`. If
            empty, a default name is generated.

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

        For this example, let's generate
        the following dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "id": [0, 1, 2, 3, 4, 5, 6],
                    "sale": [100, 120, 120, 50, 100, 90, 80],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumsum_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumsum_1.html

        Now the cumulative sum of the selected
        column can be easily calculated:

        .. code-block:: python

            vdf.cumsum(
                "sale",
                name = "cumsum_sales",
                order_by = "id",
            )

        .. ipython:: python
            :suppress:

            vdf.cumsum("sale", name = "cumsum_sales", order_by = "id")
            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumsum.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_cumsum.html

        .. note::

            Rolling windows are valuable in time-series data for creating
            features because they allow us to analyze a specified number
            of past data points at each step. This approach is useful
            for capturing trends over time, adapting to different time
            scales, and smoothing out noise in the data. By applying
            aggregation functions within these windows, such as calculating
            averages or sums, we can generate new features that provide
            insights into the historical patterns of the dataset.
            These features, based on past observations, contribute to
            building more informed and predictive models, enhancing
            our understanding of the underlying trends in the data.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.rolling` : Advanced analytical
                window function.
        """
        return self.rolling(
            func="sum",
            window=("UNBOUNDED", 0),
            columns=column,
            by=by,
            order_by=order_by,
            name=name,
        )
