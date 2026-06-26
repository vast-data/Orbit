"""
SPDX-License-Identifier: Apache-2.0
"""

import datetime
from typing import Optional, Union

from vastorbit._typing import SQLColumns, TYPE_CHECKING
from vastorbit._utils._gen import gen_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, format_interval

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
            the data may be randomly shuffled. A time-based
            (``RANGE``) window **requires** ``order_by`` to be a
            single timestamp/date column.

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
                window = (-1, 1),
                columns = ["sale"],
                order_by = ["date"],
            )

        .. ipython:: python
            :suppress:

            vdf["date"].astype("timestamp")
            vdf.rolling(func="sum", window=(-1, 1), columns=["sale"], order_by=["date"])
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

        # ── Is this a time (RANGE) window, and what does it sort by? ─────────
        # "5 minutes" / a timedelta -> RANGE; plain ints -> ROWS. For a RANGE
        # frame the bound type must match the ORDER BY key type:
        #   - timestamp/date key -> interval bound  (e.g. 5 * INTERVAL '1' MINUTE)
        #   - integer/float key  -> numeric bound in SECONDS (e.g. the credit-card
        #     "Time" column, an integer count of seconds).
        def _is_time_bound(w):
            if isinstance(w, datetime.timedelta):
                return True
            return isinstance(w, str) and w.strip().lower() != "unbounded"

        range_as_seconds = False
        if any(_is_time_bound(w) for w in window):
            if not order_by:
                raise ValueError(
                    "A time-based (RANGE) window requires `order_by` set to the column "
                    "that defines time (a timestamp/date, or an integer count of seconds)."
                )
            if len(order_by) != 1:
                raise ValueError(
                    "A RANGE window frame allows exactly one ORDER BY column in Trino; "
                    f"got {len(order_by)}."
                )
            # Numeric sort key -> express the bound in seconds instead of an interval.
            if isinstance(order_by, dict):
                first_order_by = list(order_by.keys())[0]
            elif isinstance(order_by, (list, tuple)):
                first_order_by = order_by[0]
            else:
                first_order_by = order_by
            range_as_seconds = self[first_order_by].category() != "date"

        # ── Parse the two window bounds into full SQL frame tokens ───────────
        bound = ["", ""]
        method = "rows"
        for idx, w in enumerate(window):
            if isinstance(w, (int, float)) and abs(w) == float("inf"):
                w = "unbounded"

            if isinstance(w, str):
                if w.strip().lower() == "unbounded":
                    bound[idx] = "UNBOUNDED " + ("PRECEDING" if idx == 0 else "FOLLOWING")
                else:
                    # Leading minus signs (optionally space-separated) -> PRECEDING.
                    i = nb_min = 0
                    for i, char in enumerate(w):
                        if char == "-":
                            nb_min += 1
                        elif char != " ":
                            break
                    side = "PRECEDING" if nb_min % 2 == 1 else "FOLLOWING"
                    value = format_interval(w[i:].strip(), as_seconds=range_as_seconds)
                    # Works for both "0" (seconds) and "0 * INTERVAL ..." (interval).
                    is_zero = value.split(" * ", 1)[0].strip() == "0"
                    bound[idx] = "CURRENT ROW" if is_zero else f"{value} {side}"
                    method = "range"

            elif isinstance(w, datetime.timedelta):
                side = "PRECEDING" if w < datetime.timedelta(0) else "FOLLOWING"
                seconds = abs(int(w.total_seconds()))
                if seconds == 0:
                    bound[idx] = "CURRENT ROW"
                elif range_as_seconds:
                    bound[idx] = f"{seconds} {side}"
                else:
                    bound[idx] = f"INTERVAL '{seconds}' SECOND {side}"
                method = "range"

            else:
                n = int(w)
                side = "PRECEDING" if n < 0 else "FOLLOWING"
                bound[idx] = "CURRENT ROW" if n == 0 else f"{abs(n)} {side}"

        if not name:
            name = "moving_" + gen_name([func, *columns, bound[0], bound[1]])

        columns, by = self.format_colnames(columns, by)
        by = "PARTITION BY " + ", ".join(by) if by else ""

        # ── ORDER BY (range validity already checked above) ──────────────────
        if not order_by:
            order_by = f" ORDER BY {columns[0]}"
        else:
            order_by = self._get_sort_syntax(order_by)

        # ── Window frame ("#" in each expression below is replaced by this) ──
        windows_frame = (
            f" OVER ({by}{order_by} {method.upper()} "
            f"BETWEEN {bound[0]} AND {bound[1]})"
        )

        # ── Function -> SQL ──────────────────────────────────────────────────
        func_lower = func.lower()
        col = columns[0]
        col2 = columns[1] if len(columns) > 1 else None

        simple = {
            "mean": f"AVG({col})#",
            "avg": f"AVG({col})#",
            "std": f"STDDEV({col})#",
            "var": f"VAR_SAMP({col})#",
            "kurtosis": f"KURTOSIS({col})#",
            "skewness": f"SKEWNESS({col})#",
            "count": f"COUNT({col})#",
            "max": f"MAX({col})#",
            "min": f"MIN({col})#",
            "sum": f"SUM({col})#",
            "range": f"MAX({col})# - MIN({col})#",
            "sem": f"STDDEV({col})# / SQRT(COUNT({col})#)",
        }

        mean_name = None
        if func_lower in simple:
            expr = simple[func_lower]

        elif func_lower == "jb":
            expr = (
                f"COUNT({col})# / 6.0 * ("
                f"POWER(SKEWNESS({col})#, 2) + "
                f"POWER(KURTOSIS({col})# - 3, 2) / 4.0)"
            )

        elif func_lower == "aad":
            import secrets

            mean_name = f"{col.replace(chr(34), '').lower()}_mean_{secrets.randbelow(10_000_001)}"
            self.eval(mean_name, f"AVG({col}){windows_frame}")
            expr = f"AVG(ABS({col} - {mean_name}))#"

        elif func_lower == "prod":
            expr = (
                "CASE "
                f"WHEN COUNT(CASE WHEN {col} = 0 THEN 1 END)# > 0 THEN 0 "
                "ELSE "
                f"CASE MOD(COUNT(CASE WHEN {col} < 0 THEN 1 END)#, 2) "
                "WHEN 0 THEN 1 ELSE -1 END "
                f"* EXP(SUM(LN(ABS({col})))#) "
                "END"
            )

        elif func_lower in ("corr", "cov", "beta"):
            if col2 is None or col2 == col:
                expr = f"VAR_SAMP({col})#" if func_lower == "cov" else "1"
            elif func_lower == "corr":
                expr = f"CORR({col}, {col2})#"
            elif func_lower == "beta":
                expr = f"COVAR_SAMP({col}, {col2})# / NULLIF(VAR_SAMP({col2})#, 0)"
            else:  # cov
                expr = f"COVAR_SAMP({col}, {col2})#"

        else:
            expr = f"{func.upper()}({col})#"

        # Splice the window frame into every aggregate and materialise the column.
        self.eval(name=name, expr=expr.replace("#", windows_frame))

        if mean_name is not None:
            self._vars["exclude_columns"].append(f'"{mean_name}"')

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