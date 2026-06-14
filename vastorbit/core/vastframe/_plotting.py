"""
SPDX-License-Identifier: Apache-2.0
"""

import math
from collections.abc import Iterable
from typing import Callable, Literal, Optional, Union
import numpy as np

import vastorbit._config.config as conf
from vastorbit._typing import (
    ArrayLike,
    ColorType,
    NoneType,
    PlottingMethod,
    PlottingObject,
    PythonNumber,
    PythonScalar,
    SQLColumns,
)
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._object import get_VAST_mllib
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.core.tablesample.base import TableSample

from vastorbit.core.vastframe._machine_learning import vDFMachineLearning
from vastorbit.core.vastframe._scaler import vDCScaler

from vastorbit.plotting.base import PlottingBase


class vDFPlot(vDFMachineLearning):
    # Boxplots.

    @save_vastorbit_logs
    def boxplot(
        self,
        columns: Optional[SQLColumns] = None,
        q: tuple[float, float] = (0.25, 0.75),
        max_nb_fliers: int = 30,
        whis: float = 1.5,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the Box Plot of the input VastColumns.

        Parameters
        ----------
        columns: SQLColumns, optional
            List  of the VastColumns names.  If  empty, all
            numerical VastColumns are used.
        q: tuple, optional
            Tuple including the 2 quantiles used to draw the
            BoxPlot.
        max_nb_fliers: int, optional
            Maximum number of points to use to represent the
            fliers  of each category.  Drawing  fliers  will
            slow down the graphic computation.
        whis: float, optional
            The position of the whiskers.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to
            pass to the plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.boxplot`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 50

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                }
            )

        Below are examples of two types of boxplot:

        - Single (for one column)
        - Multi (for more than one column)

        Check out the tabs below for specific examples.

        .. tab:: Single

            .. code-block:: python

                data.boxplot(["score1"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.boxplot(["score1"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_boxplot_single.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_boxplot_single.html

        .. tab:: Multi

            .. code-block:: python

                data.boxplot(columns = ["score1", "score2", "score3"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.boxplot(columns = ["score1", "score2", "score3"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_boxplot_multi.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_boxplot_multi.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.outliers_plot` : Outliers Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.boxplot` : Box Plot.

        """
        columns = format_type(columns, dtype=list)
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="BoxPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.BoxPlot(
            vdf=self,
            columns=columns,
            q=q,
            whis=whis,
            max_nb_fliers=max_nb_fliers,
        ).draw(**kwargs)

    # 2D / ND CHARTS.

    @save_vastorbit_logs
    def bar(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: tuple[int, int] = (6, 6),
        h: tuple[PythonNumber, PythonNumber] = (None, None),
        kind: Literal["auto", "drilldown", "stacked"] = "auto",
        categoryorder: Literal[
            "trace",
            "category ascending",
            "category descending",
            "total ascending",
            "total descending",
            "min ascending",
            "min descending",
            "max ascending",
            "max descending",
            "sum ascending",
            "sum descending",
            "mean ascending",
            "mean descending",
            "median ascending",
            "median descending",
        ] = "trace",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the bar chart of the input VastColumns based
        on an aggregation.

        Parameters
        ----------
        columns: SQLColumns
            ``list`` of the
            :py:class:`~VastColumns`
            names.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).
            - None:
                No Aggregations. Parameter ``of``
                must be empty, otherwise it is
                ignored.

            It can also be a cutomized aggregation,
            for example: ``AVG(column1) + 5``
        of: str, optional
            The :py:class:`~VastColumns` used
            to compute the  aggregation.
        max_cardinality: tuple, optional
            Maximum number of distinct elements
            for :py:class:`~VastColumns` 1 and
            2 to be used as categorical. For
            these elements, no ``h`` is picked
            or computed.

            .. important::

                This parameter is only used for
                categorical data types. For numerics
                use ``h`` to discretize them first
        h: tuple, optional
            Interval width of the
            :py:class:`~VastColumns`
            1 and 2 bars.

            .. important::

                Only valid if the
                :py:class:`~VastColumns` are
                numerical. Optimized ``h`` will
                be computed if the parameter is
                empty or invalid.
        kind: str, optional
            The BarChart Type.

            - auto:
                Regular Bar Chart based on 1
                or 2 :py:class:`~VastColumns`.
            - drilldown:
                Drilldown Bar Chart.
            - pyramid:
                Pyramid Density Bar Chart.
                Only works if one of the two
                :py:class:`~VastColumns` is
                binary and the ``method='density'``.
            - stacked:
                Stacked Bar Chart based on 2
                :py:class:`~VastColumns`.
            - fully_stacked:
                Fully Stacked Bar Chart based
                on 2 :py:class:`~VastColumns`.
        categoryorder: str, optional
            How to sort the bars.
            One of the following options:

            - trace (no transformation)
            - category ascending
            - category descending
            - total ascending
            - total descending
            - min ascending
            - min descending
            - max ascending
            - max descending
            - sum ascending
            - sum descending
            - mean ascending
            - mean descending
            - median ascending
            - median descending

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any optional parameter to
            pass  to the plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.bar`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "gender": ['M', 'M', 'M', 'F', 'F', 'F', 'F'],
                    "grade": ['A','B','C','A','B','B', 'B'],
                }
            )

        Below are examples of two types of bar plots:

        - 1D
        - 2D

        .. tab:: 1D

            .. code-block:: python

                data.bar(["grade"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.bar(["grade"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_bar_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_bar_1d.html

        .. tab:: 2D

            .. code-block:: python

                data.bar(columns = ["grade", "gender"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.bar(columns = ["grade", "gender"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_bar_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_bar_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.barh` : Horizontal Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.bar` : Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.barh` : Horizontal Bar Chart.

        """
        columns = format_type(columns, dtype=list)
        columns, of = self.format_colnames(columns, of, expected_nb_of_cols=[1, 2, 3])
        if not (isinstance(max_cardinality, Iterable)):
            max_cardinality = (max_cardinality, max_cardinality)
        if not (isinstance(h, Iterable)):
            h = (h, h)

        if len(columns) == 1:
            return self[columns[0]].bar(
                method=method,
                of=of,
                max_cardinality=max_cardinality[0],
                h=h[0],
                categoryorder=categoryorder,
                **style_kwargs,
            )
        elif len(columns) == 2 and isinstance(method, NoneType) and not (of):
            return self[columns[0]].bar(
                method=None,
                of=columns[1],
                max_cardinality=max_cardinality[0],
                categoryorder=categoryorder,
                **style_kwargs,
            )
        elif kind == "drilldown":
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="DrillDownBarChart",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.DrillDownBarChart(
                vdf=self,
                columns=columns,
                method=method,
                of=of,
                h=h,
                max_cardinality=max_cardinality,
                categoryorder=categoryorder,
            ).draw(**kwargs)
        else:
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="BarChart2D",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.BarChart2D(
                vdf=self,
                columns=columns,
                method=method,
                of=of,
                h=h,
                max_cardinality=max_cardinality,
                misc_layout={"kind": kind},
                categoryorder=categoryorder,
            ).draw(**kwargs)

    @save_vastorbit_logs
    def barh(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: tuple[int, int] = (6, 6),
        h: tuple[PythonNumber, PythonNumber] = (None, None),
        kind: Literal[
            "auto",
            "drilldown",
            "fully_stacked",
            "stacked",
            "fully",
            "fully stacked",
            "pyramid",
            "density",
        ] = "auto",
        categoryorder: Literal[
            "trace",
            "category ascending",
            "category descending",
            "total ascending",
            "total descending",
            "min ascending",
            "min descending",
            "max ascending",
            "max descending",
            "sum ascending",
            "sum descending",
            "mean ascending",
            "mean descending",
            "median ascending",
            "median descending",
        ] = "trace",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the horizontal bar chart of the
        input :py:class:`~VastColumns` based
        on an aggregation.

        Parameters
        ----------
        columns: SQLColumns
            ``list`` of the
            :py:class:`~VastColumns`
            names.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).
            - None:
                No Aggregations. Parameter ``of``
                must be empty, otherwise it is
                ignored.

            It can also be a cutomized aggregation,
            for example: ``AVG(column1) + 5``
        of: str, optional
            The :py:class:`~VastColumns` used
            to compute the  aggregation.
        max_cardinality: tuple, optional
            Maximum number of distinct elements
            for :py:class:`~VastColumns` 1 and
            2 to be used as categorical. For
            these elements, no ``h`` is picked
            or computed.

            .. important::

                This parameter is only used for
                categorical data types. For numerics
                use ``h`` to discretize them first
        h: tuple, optional
            Interval width of the
            :py:class:`~VastColumns`
            1 and 2 bars.

            .. important::

                Only valid if the
                :py:class:`~VastColumns` are
                numerical. Optimized ``h`` will
                be computed if the parameter is
                empty or invalid.
        kind: str, optional
            The BarChart Type.

            - auto:
                Regular Bar Chart based
                on 1 or 2 :py:class:`~VastColumns`.
            - drilldown:
                Drilldown Bar Chart.
            - pyramid:
                Pyramid Density Bar Chart.
                Only works if one of the two
                :py:class:`~VastColumns` is
                binary and the ``method='density'``.
            - stacked:
                Stacked Bar Chart based on 2
                :py:class:`~VastColumns`.
            - fully_stacked:
                Fully Stacked Bar Chart based
                on 2 :py:class:`~VastColumns`.

        categoryorder: str, optional
            How to sort the bars.
            One of the following options:

            - trace (no transformation)
            - category ascending
            - category descending
            - total ascending
            - total descending
            - min ascending
            - min descending
            - max ascending
            - max descending
            - sum ascending
            - sum descending
            - mean ascending
            - mean descending
            - median ascending
            - median descending

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to
            pass to the plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.bar`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "gender": ['M', 'M', 'M', 'F', 'F', 'F', 'F'],
                    "grade": ['A','B','C','A','B','B', 'B'],
                }
            )

        Below are examples of two types of barh plots:

        - 1D
        - 2D

        .. tab:: 1D

            .. code-block:: python

                data.barh(["grade"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.barh(["grade"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_barh_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_barh_1d.html

        .. tab:: 2D

            .. code-block:: python

                data.barh(columns = ["grade", "gender"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.barh(columns = ["grade", "gender"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_barh_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_barh_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.bar` : Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.barh` : Horizontal Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.bar` : Bar Chart.


        """
        columns = format_type(columns, dtype=list)
        columns, of = self.format_colnames(columns, of, expected_nb_of_cols=[1, 2, 3])
        if not (isinstance(max_cardinality, Iterable)):
            max_cardinality = (max_cardinality, max_cardinality)
        if not (isinstance(h, Iterable)):
            h = (h, h)

        if len(columns) == 1:
            return self[columns[0]].barh(
                method=method,
                of=of,
                max_cardinality=max_cardinality[0],
                h=h[0],
                chart=chart,
                categoryorder=categoryorder,
                **style_kwargs,
            )
        elif len(columns) == 2 and isinstance(method, NoneType) and not (of):
            return self[columns[0]].barh(
                method=None,
                of=columns[1],
                max_cardinality=max_cardinality[0],
                categoryorder=categoryorder,
                **style_kwargs,
            )
        elif kind == "drilldown":
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="DrillDownHorizontalBarChart",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.DrillDownHorizontalBarChart(
                vdf=self,
                columns=columns,
                method=method,
                of=of,
                h=h,
                max_cardinality=max_cardinality,
                categoryorder=categoryorder,
            ).draw(**kwargs)
        else:
            if kind in ("fully", "fully stacked"):
                kind = "fully_stacked"
            elif kind == "pyramid":
                kind = "density"
            vo_plt, kwargs = self.get_plotting_lib(
                class_name="HorizontalBarChart2D",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.HorizontalBarChart2D(
                vdf=self,
                columns=columns,
                method=method,
                of=of,
                max_cardinality=max_cardinality,
                h=h,
                misc_layout={"kind": kind},
                categoryorder=categoryorder,
            ).draw(**kwargs)

    @save_vastorbit_logs
    def pie(
        self,
        columns: SQLColumns,
        method: str = "count",
        of: Optional[str] = None,
        max_cardinality: Union[None, int, tuple] = None,
        h: Union[None, int, tuple] = None,
        chart: Optional[PlottingObject] = None,
        categoryorder: Literal[
            "trace",
            "category ascending",
            "category descending",
            "total ascending",
            "total descending",
        ] = "trace",
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the nested pie chart of
        the input :py:class:`~VastColumns`.

        Parameters
        ----------
        columns: SQLColumns
            ``list`` of the
            :py:class:`~VastColumns`
            names.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation,
            for example: ``AVG(column1) + 5``
        of: str, optional
            The :py:class:`~VastColumns` used
            to compute the  aggregation.
        max_cardinality: int | tuple, optional
            Maximum number of distinct elements
            for :py:class:`~VastColumns` 1 and 2
            to be used as categorical. For these
            elements, no  ``h
            is picked or computed.
            If  of type tuple, represents the
            'max_cardinality' of each column.
        h: int | tuple, optional
            Interval width of the bar.
            If empty, an optimized ``h``
            will be computed.
            If  of type tuple, it must
            represent each column's ``h``.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any optional parameter to
            pass to the plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.pie`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "gender": ['M', 'M', 'M', 'F', 'F', 'F', 'F'],
                    "grade": ['A','B','C','A','B','B', 'B'],
                }
            )

        Below are examples of two types of pie plots:

        - Regular
        - Nested

        .. tab:: Regular

            .. code-block:: python

                data.pie(["grade"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.pie(["grade"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_pie_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_pie_1d.html

        .. tab:: Nested

            .. code-block:: python

                data.pie(columns = ["grade", "gender"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.pie(columns = ["grade", "gender"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_pie_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_pie_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.hist` : Histogram.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.bar` : Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.pie` : Pie Chart.

        """
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="NestedPieChart",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.NestedPieChart(
            vdf=self,
            columns=columns,
            method=method,
            of=of,
            max_cardinality=max_cardinality,
            h=h,
            categoryorder=categoryorder,
        ).draw(**kwargs)

    # Histogram & Density.

    @save_vastorbit_logs
    def hist(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        h: Optional[PythonNumber] = None,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws  the  histograms  of  the  input VastColumns
        based on an aggregation.

        Parameters
        ----------
        columns: SQLColumns
            ``list`` of  the
            :py:class:`~VastColumns` names.
            The ``list``  must have less
            than 5 elements.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation,
            for example: ``AVG(column1) + 5``
        of: str, optional
            The :py:class:`~VastColumns` used
            to compute the  aggregation.
        h: tuple, optional
            Interval width of the  input VastColumns. Optimized
            h  will be  computed if  the  parameter  is empty or
            invalid.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to  pass  to  the plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.hist`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 50

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                }
            )

        Below are examples of two types of hist plots:

        - Single
        - Multi

        .. tab:: Single

            .. code-block:: python

                data.hist(["score1"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.hist(["score1"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_hist_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_hist_1d.html

        .. tab:: Multi

            .. code-block:: python

                data.hist(columns = ["score1", "score2"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.hist(columns = ["score1", "score2"], width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_hist_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_hist_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.bar` : Bar Chart.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.barh` : Horizontal Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.hist` : Histogram.

        """
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="Histogram",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.Histogram(
            vdf=self,
            columns=columns,
            method=method,
            of=of,
            h=h,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def density(
        self,
        columns: Optional[SQLColumns] = None,
        nbins: int = 100,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the VastColumns Density Plot using histogram approximation.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty,
            all numerical VastColumns are selected.
        nbins: int, optional
            Number of bins for histogram approximation.
            Higher values give smoother density estimates.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any optional parameter to pass to the plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.density`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 50

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                    "score2": np.random.normal(8, 1.5, N),
                    "score3": np.random.normal(10, 2, N),
                }
            )

        Below are examples of two types of density plots:

        - Single
        - Multi

        .. tab:: Single

            .. code-block:: python

                data.density(["score1"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.density(["score1"], width=600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_density_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_density_1d.html

        .. tab:: Multi

            .. code-block:: python

                data.density(columns=["score1", "score2"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.density(columns=["score1", "score2"], width=600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_density_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_density_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.hist` : Histogram.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.range_plot` : Range Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.density` : Density Plot.

        """
        
        # Compute histogram-based density for each column
        if len(columns) == 1:

            vo_plt, kwargs = self.get_plotting_lib(
                class_name="DensityPlot",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.DensityPlot(vdf=self, columns=columns, nbins=nbins).draw(**kwargs)
        
        else:

            vo_plt, kwargs = self.get_plotting_lib(
                class_name="MultiDensityPlot",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.MultiDensityPlot(vdf=self, columns=columns, nbins=nbins).draw(**kwargs)

    # Time Series.

    @save_vastorbit_logs
    def plot(
        self,
        ts: str,
        columns: Optional[SQLColumns] = None,
        start_date: Optional[PythonScalar] = None,
        end_date: Optional[PythonScalar] = None,
        kind: Literal[
            "area_percent", "area_stacked", "line", "spline", "step"
        ] = "line",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the time series.

        Parameters
        ----------
        ts: str
            TS (Time Series)  VastColumn used to order
            the data.  The VastColumn type must be  date
            (date, datetime, timestamp...) or numerical.
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all
            numerical VastColumns are used.
        start_date: PythonScalar, optional
            Input   Start  Date.  For  example,   time  =
            '03-11-1993'  will  filter the data when 'ts'
            is less than the 3rd of November 1993.
        end_date: PythonScalar, optional
            Input   End   Date.   For   example,   time =
            '03-11-1993'   will  filter  the  data   when
            'ts' is greater than the 3rd of November 1993.
        kind: str, optional
            The plot type.

            - line:
                Line Plot.
            - spline:
                Spline Plot.
            - step:
                Step Plot.
            - area_stacked:
                Stacked Area Plot.
            - area_percent:
                Fully Stacked Area Plot.

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any   optional  parameter  to   pass  to  the
            plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.line`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "date": [1900, 1950, 2000],
                    "Asia": [947, 1402, 3634],
                    "Africa": [133, 221, 767],
                    "Europe": [408, 547, 729],
                    "America": [156, 339, 818],
                    "Oceania": [6, 13, 30],
                }
            )

        Below are examples of two types of plot plots:

        - Single
        - Multi

        .. tab:: Single

            .. code-block:: python

                data.plot(columns = ["Asia"], ts = "date", kind = "spline")

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.plot(columns = ["Asia"], ts = "date", kind = "spline", width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_plot_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_plot_1d.html

        .. tab:: Multi

            .. code-block:: python

                data.plot(columns = ["Asia", "Africa", "Europe", "America", "Oceania"], ts = "date")

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.plot(columns = ["Asia", "Africa", "Europe", "America", "Oceania"], ts = "date", width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_plot_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_plot_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.range_plot` : Range Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.plot` : Line Plot.

        """
        columns = format_type(columns, dtype=list)
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="MultiLinePlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.MultiLinePlot(
            vdf=self,
            order_by=ts,
            columns=columns,
            order_by_start=start_date,
            order_by_end=end_date,
            misc_layout={"kind": kind},
        ).draw(**kwargs)

    @save_vastorbit_logs
    def range_plot(
        self,
        columns: SQLColumns,
        ts: str,
        q: tuple[float, float] = (0.25, 0.75),
        start_date: Optional[PythonScalar] = None,
        end_date: Optional[PythonScalar] = None,
        plot_median: bool = False,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the range plot of the input VastColumns. The
        aggregations used to draw the plot are the median
        and the two user-specified quantiles.

        Parameters
        ----------
        columns: SQLColumns
            List of VastColumns names.
        ts: str
            TS (Time Series) VastColumn used to order the
            data.  The  VastColumn  type must be date
            (date, datetime, timestamp...) or numerical.
        q: tuple, optional
            Tuple that includes the 2 quantiles used to draw
            the Plot.
        start_date: str / PythonNumber / date, optional
            Input Start Date. For example, time = '03-11-1993'
            will  filter  the data when 'ts' is  less  than
            the 3rd of November 1993.
        end_date: str / PythonNumber / date, optional
            Input End Date.  For example, time = '03-11-1993'
            will  filter the  data when 'ts' is greater than
            the 3rd of November 1993.
        plot_median: bool, optional
            If set to True, the Median is drawn.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.range`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "date": [1990 + i for i in range(N)] * 5,
                    "population1": [100 + i for i in range(N)] + [300 + i * 2 for i in range(N)] + [200 + i ** 2 - 3 * i for i in range(N)] + [50 + i ** 2 - 6 * i for i in range(N)] + [700 + i ** 2 - 10 * i for i in range(N)],
                    "population2": [200 + i ** 2 - i for i in range(N)] + [1000 + i * 2 for i in range(N)] + [500 + i ** 2 - 5 * i for i in range(N)] + [900 + i ** 2 + 3 * i for i in range(N)] + [100 + i ** 2 - 0.5 * i for i in range(N)],
                }
            )

        Below are examples of two types of range_plot plots:

        - Single
        - Multi

        .. tab:: Single

            .. code-block:: python

                data.range_plot(columns = ["population1", "population2"], ts = "date")

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.range_plot(columns = ["population1"], ts = "date", width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_range_plot_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_range_plot_1d.html

        .. tab:: Multi

            .. code-block:: python

                data.range_plot(columns = ["population1", "population2"], ts = "date")

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.range_plot(columns = ["population1", "population2"], ts = "date", width = 600)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_range_plot_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_range_plot_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.plot` : Line Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.range_plot` : Range Plot.

        """
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="RangeCurve",
            chart=chart,
            matplotlib_kwargs={
                "plot_median": plot_median,
            },
            plotly_kwargs={
                "plot_median": plot_median,
            },
            style_kwargs=style_kwargs,
        )
        return vo_plt.RangeCurve(
            vdf=self,
            columns=columns,
            order_by=ts,
            q=q,
            order_by_start=start_date,
            order_by_end=end_date,
        ).draw(**kwargs)

    # 2D MAP.

    @save_vastorbit_logs
    def _pivot_table(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "count",
        of: Optional[str] = None,
        max_cardinality: tuple[int, int] = (20, 20),
        h: tuple[PythonNumber, PythonNumber] = (None, None),
        fill_none: float = 0.0,
    ) -> TableSample:
        """
        Computes and  returns the pivot table of one or two
        columns based on an aggregation.

        Parameters
        ----------
        columns: SQLColumns
            List  of the VastColumns names.  The list  must
            have one or two elements.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation,
            (ex: AVG(column1) + 5).
        of: str, optional
            The VastColumn used to compute the aggregation.
        max_cardinality: tuple, optional
            Maximum number of distinct elements for VastColumns
            1  and  2  to be used as categorical. For these
            elements, no  h is picked or computed.
        h: tuple, optional
            Interval width of the VastColumns 1 and 2 bars.
            Only valid if  the  VastColumns  are numerical.
            Optimized h will be computed if the parameter is
            empty or invalid.
        fill_none: float, optional
            The  empty  values  of the pivot table are
            filled by this number.

        Returns
        -------
        obj
            TableSample.

        """
        columns = format_type(columns, dtype=list)
        columns, of = self.format_colnames(columns, of, expected_nb_of_cols=[1, 2])
        vo_plt = self.get_plotting_lib(class_name="HeatMap")[0]
        plt_obj = vo_plt.HeatMap(
            vdf=self,
            columns=columns,
            method=method,
            of=of,
            h=h,
            max_cardinality=max_cardinality,
            fill_none=fill_none,
        )
        values = {"index": plt_obj.layout["x_labels"]}
        if len(plt_obj.data["X"].shape) == 1:
            values[plt_obj.layout["aggregate"]] = list(plt_obj.data["X"])
        else:
            for idx in range(plt_obj.data["X"].shape[1]):
                values[plt_obj.layout["y_labels"][idx]] = list(
                    plt_obj.data["X"][:, idx]
                )
        return TableSample(values=values)

    @save_vastorbit_logs
    def pivot_table(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "count",
        of: Optional[str] = None,
        max_cardinality: tuple[int, int] = (20, 20),
        h: tuple[PythonNumber, PythonNumber] = (None, None),
        fill_none: float = 0.0,
        mround: int = 3,
        with_numbers: bool = True,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the pivot table of one or two columns based on
        an aggregation.

        Parameters
        ----------
        columns: SQLColumns
            List  of the VastColumns names.  The list  must
            have one or two elements.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation
            (ex: AVG(column1) + 5).
        of: str, optional
            The VastColumn used to compute the aggregation.
        max_cardinality: tuple, optional
            Maximum number of distinct elements for VastColumns
            1  and  2  to be used as categorical. For these
            elements, no  h is picked or computed.
        h: tuple, optional
            Interval width of the VastColumns 1 and 2 bars.
            Only valid if the VastColumns  are numerical.
            Optimized h will be computed if the parameter is
            empty or invalid.
        fill_none: float, optional
            The  empty  values  of the pivot table  are
            filled by this number.
        mround: int, optional
            Rounds the coefficient using the input number of
            digits.  It  is only  used to display the  final
            pivot table.
        with_numbers: bool, optional
            If  set to True, no number is displayed in
            the final drawing.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.pivot`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "category1": [np.random.choice(['A','B','C']) for _ in range(N)],
                    "category2": [np.random.choice(['D','E']) for _ in range(N)],
                }
            )

        Below are examples of one types of pivot_table plots:

        - Pivot Plot

        .. tab:: Pivot Plot

            .. code-block:: python

                data.pivot_table(columns = ["category1", "category2"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.pivot_table(columns = ["category1", "category2"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_pivot_table_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_pivot_table_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.contour` : Contour Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.scatter_matrix` : Scatter Matrix.

        """
        columns = format_type(columns, dtype=list)
        columns, of = self.format_colnames(columns, of, expected_nb_of_cols=[1, 2])
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="HeatMap",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.HeatMap(
            vdf=self,
            columns=columns,
            method=method,
            of=of,
            h=h,
            max_cardinality=max_cardinality,
            fill_none=fill_none,
            misc_layout={
                "mround": mround,
                "with_numbers": with_numbers,
            },
        ).draw(**kwargs)

    @save_vastorbit_logs
    def contour(
        self,
        columns: SQLColumns,
        func: Union[Callable, str],
        nbins: int = 100,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws  the  contour  plot of the input function
        using two input VastColumns.

        Parameters
        ----------
        columns: SQLColumns
            List  of the  VastColumns  names. The list must
            have two elements.
        func: function / str
            Function  used to compute  the contour score. It
            can also be a SQL expression.
        nbins: int, optional
            Number of bins used to  discretize the two input
            numerical VastColumns.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to pass to  the plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.contour`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        For contour plots, we also need a function to apply:

        .. ipython:: python

            def f(x, y):
                return x ** 2 - y + 1

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "x": np.random.normal(5, 1, N),
                    "y": np.random.normal(8, 1.5, N),
                }
            )

        Below is an examples of one type of contour plots:

        - Contour Plot

        .. tab:: Contour Plot

            .. code-block:: python

                data.contour(columns = ["x", "y"], func = f)

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.contour(columns = ["x", "y"], func = f)
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_contour_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_contour_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.hexbin` : Hexbin Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.heatmap` : Heatmap.

        """
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="ContourPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        func_name = None
        if "func_name" in kwargs:
            func_name = kwargs["func_name"]
            del kwargs["func_name"]
        return vo_plt.ContourPlot(
            vdf=self,
            columns=columns,
            func=func,
            nbins=nbins,
            func_name=func_name,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def heatmap(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "count",
        of: Optional[str] = None,
        h: tuple = (None, None),
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the Heatmap of  the two input VastColumns.

        Parameters
        ----------
        columns: SQLColumns
            List of the VastColumns names. The list must
            have two elements.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation
            (ex: AVG(column1) + 5).
        of: str, optional
            The VastColumn used to compute the aggregation.
        h: tuple, optional
            Interval width  of  the VastColumns 1  and  2
            bars.  Optimized  h  will  be computed if  the
            parameter is empty or invalid.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any optional parameter to pass to the plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "x": np.random.normal(5, 1, N),
                    "y": np.random.normal(8, 1.5, N),
                }
            )

        Below is an examples of one type of heatmap plots:

        - Heatmap

        .. tab:: Heatmap

            .. code-block:: python

                data.heatmap(columns = ["x", "y"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.heatmap(columns = ["x", "y"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_heatmap_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_heatmap_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.hexbin` : Hexbin Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.contour` : Contour Plot.

        """
        columns = format_type(columns, dtype=list)
        columns, of = self.format_colnames(columns, of, expected_nb_of_cols=2)
        for column in columns:
            assert self[column].isnum(), TypeError(
                f"VastColumn {column} must be numerical to draw the Heatmap."
            )
        min_max = self.agg(func=["min", "max"], columns=columns).transpose()
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="HeatMap",
            chart=chart,
            matplotlib_kwargs={
                "extent": min_max[columns[0]] + min_max[columns[1]],
            },
            style_kwargs=style_kwargs,
        )
        return vo_plt.HeatMap(
            vdf=self,
            columns=columns,
            method=method,
            of=of,
            h=h,
            max_cardinality=(0, 0),
            fill_none=0.0,
            misc_layout={
                "with_numbers": False,
            },
        ).draw(**kwargs)

    @save_vastorbit_logs
    def hexbin(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "count",
        of: Optional[str] = None,
        bbox: Optional[list] = None,
        img: Optional[str] = None,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the Hexbin of the  input VastColumns based
        on an aggregation.

        Parameters
        ----------
        columns: SQLColumns
            List of the VastColumns names. The list must
            have two elements.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).
            - None:
                No Aggregations.

        of: str, optional
            The VastColumn used to compute the aggregation.
        bbox: list, optional
            List of 4 elements  to delimit the boundaries of
            the final Plot. It must be similar the following
            list: [xmin, xmax, ymin, ymax]
        img: str, optional
            Path  to the  image used as a background.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "x": np.random.normal(5, 1, N),
                    "y": np.random.normal(8, 1.5, N),
                }
            )

        Below is an example of one type of hexbin plots:

        - Hexbin

        .. tab:: Hexbin

            .. ipython:: python

                @suppress
                vo.set_option("plotting_lib", "matplotlib")

                @savefig core_VastFrame_plotting_vdf_hexbin_1.png
                data.hexbin(columns = ["x", "y"])

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.heatmap` : Heatmap.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.contour` : Contour Plot.

        """
        columns, bbox = format_type(columns, bbox, dtype=list)
        columns, of = self.format_colnames(columns, of, expected_nb_of_cols=2)
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="HexbinMap",
            chart=chart,
            matplotlib_kwargs={"bbox": bbox, "img": img},
            style_kwargs=style_kwargs,
        )
        return vo_plt.HexbinMap(
            vdf=self,
            columns=columns,
            method=method,
            of=of,
        ).draw(**kwargs)

    # Scatters.

    @save_vastorbit_logs
    def scatter(
        self,
        columns: SQLColumns,
        by: Optional[str] = None,
        size: Optional[str] = None,
        cmap_col: Optional[str] = None,
        max_cardinality: int = 6,
        cat_priority: Union[None, PythonScalar, ArrayLike] = None,
        max_nb_points: int = 20000,
        dimensions: tuple = None,
        bbox: Optional[tuple] = None,
        img: Optional[str] = None,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the scatter plot of the input VastColumns.

        Parameters
        ----------
        columns: SQLColumns
            List of the VastColumns names.
        by: str, optional
            Categorical VastColumn used to label the data.
        size: str
            Numerical  VastColumn used to represent  the
            Bubble size.
        cmap_col: str, optional
            Numerical  column used  to represent the  color
            map.
        max_cardinality: int, optional
            Maximum  number  of  distinct elements for  'by'
            to  be  used as categorical.  The less  frequent
            elements are gathered together  to create a
            new category: 'Others'.
        cat_priority: PythonScalar / ArrayLike, optional
            ArrayLike list of the different categories to
            consider when  labeling  the  data using  the
            VastColumn 'by'.  The  other  categories  are
            filtered.
        max_nb_points: int, optional
            Maximum number of points to display.
        dimensions: tuple, optional
            Tuple of two  elements representing the IDs of the
            PCA's components. If empty and the number of input
            columns  is greater  than 3, the first and  second
            PCA are drawn.
        bbox: list, optional
            Tuple  of 4 elements to delimit the boundaries  of
            the  final Plot. It must be similar the  following
            list: [xmin, xmax, ymin, ymax]
        img: str, optional
            Path to the image to display as background.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.scatter`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "category": [np.random.choice(['A','B','C']) for _ in range(N)],
                    "x": np.random.normal(5, 1, N),
                    "y": np.random.normal(8, 1.5, N),
                    "z": np.random.normal(10, 2, N),
                }
            )

        Below are examples of two types of scatter plots:

        - 2D
        - 3D

        .. tab:: 2D

            .. code-block:: python

                data.scatter(columns = ["x", "y"], by = "category")

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.scatter(columns = ["x", "y"], by = "category")
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_scatter_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_scatter_2d.html

        .. tab:: 3D

            .. code-block:: python

                data.scatter(columns = ["x", "y", "z"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.scatter(columns = ["x", "y", "z"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_scatter_3d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_scatter_3d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.density` : Density Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.outliers_plot` : Outliers Plot.

        """
        vml = get_VAST_mllib()
        if img and not bbox and len(columns) == 2:
            aggr = self.agg(columns=columns, func=["min", "max"])
            bbox = (
                aggr.values["min"][0],
                aggr.values["max"][0],
                aggr.values["min"][1],
                aggr.values["max"][1],
            )
        if len(columns) > 3 and isinstance(dimensions, NoneType):
            dimensions = (1, 2)
        if isinstance(dimensions, Iterable):
            model_name = gen_tmp_name(
                schema=conf.get_option("temp_schema"), name="pca_plot"
            )
            model = vml.PCA(model_name)
            model.drop()
            try:
                model.fit(self, columns, return_report=True)
                vdf = model.transform(self)
                ev_1 = round(model.explained_variance_ratio_[dimensions[0] - 1] * 100, 5)
                x_label = f"Dim{dimensions[0]} ({ev_1}%)"
                ev_2 = round(model.explained_variance_ratio_[dimensions[1] - 1] * 100, 5)
                y_label = f"Dim{dimensions[1]} ({ev_2}%)"
                vdf[f"col{dimensions[0]}"].rename(x_label)
                vdf[f"col{dimensions[1]}"].rename(y_label)
                chart = vdf.scatter(
                    columns=[x_label, y_label],
                    by=by,
                    cmap_col=cmap_col,
                    size=size,
                    max_cardinality=max_cardinality,
                    cat_priority=cat_priority,
                    max_nb_points=max_nb_points,
                    bbox=bbox,
                    img=img,
                    chart=chart,
                    **style_kwargs,
                )
            finally:
                model.drop()
            return chart
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="ScatterPlot",
            chart=chart,
            matplotlib_kwargs={
                "bbox": bbox,
                "img": img,
            },
            style_kwargs=style_kwargs,
        )
        return vo_plt.ScatterPlot(
            vdf=self,
            columns=columns,
            by=by,
            cmap_col=cmap_col,
            size=size,
            max_cardinality=max_cardinality,
            cat_priority=cat_priority,
            max_nb_points=max_nb_points,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def scatter_matrix(
        self,
        columns: Optional[SQLColumns] = None,
        max_nb_points: int = 1000,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the scatter matrix of the VastFrame.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty,
            all numerical  VastColumns are used.
        max_nb_points: int, optional
            Maximum  number of points to display for
            each scatter plot.
        **style_kwargs
            Any  optional  parameter  to pass to the
            plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "x": np.random.normal(5, 1, N),
                    "y": np.random.normal(8, 1.5, N),
                }
            )

        Below is an examples of one type of scatter_matrix plots:

        - Scatter Matrix

        .. tab:: Scatter Matrix

            .. ipython:: python

                @suppress
                vo.set_option("plotting_lib", "matplotlib")

                @savefig core_VastFrame_plotting_vdf_scatter_matrix.png
                data.scatter_matrix(columns = ["x", "y"])

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.contour` : Contour Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.heatmap` : Heatmap.

        """
        columns = format_type(columns, dtype=list)
        columns = self.format_colnames(columns)
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="ScatterMatrix",
            style_kwargs=style_kwargs,
        )
        return vo_plt.ScatterMatrix(
            vdf=self, columns=columns, max_nb_points=max_nb_points
        ).draw(**kwargs)

    @save_vastorbit_logs
    def outliers_plot(
        self,
        columns: SQLColumns,
        threshold: float = 3.0,
        max_nb_points: int = 500,
        color: ColorType = "orange",
        outliers_color: ColorType = PlottingBase().get_colors(idx=1),
        inliers_color: ColorType = PlottingBase().get_colors(idx=0),
        inliers_border_color: ColorType = "red",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the global  outliers plot of one or two
        columns based on their ZSCORE.

        Parameters
        ----------
        columns: SQLColumns
            List  of  one or two  VastColumn  names.
        threshold: float, optional
            ZSCORE threshold used to detect outliers.
        max_nb_points: int, optional
            Maximum number of points to display.
        color: ColorType, optional
            Inliers Area color.
        outliers_color: ColorType, optional
            Outliers color.
        inliers_color: ColorType, optional
            Inliers color.
        inliers_border_color: ColorType, optional
            Inliers border color.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter to pass to  the
            plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.outliers`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            # Normal Distributions
            x = np.random.normal(5, 1, round(N / 2))
            y = np.random.normal(3, 1, round(N / 2))

            # Creating a VastFrame with a few outliers
            data = vo.VastFrame(
                {
                    "x": np.concatenate([x, [15]]),
                    "y": np.concatenate([y, [12]]),
                }
            )

        Below are examples of two types of outliers_plot plots:

        - 1D
        - 2D

        .. tab:: 1D

            .. code-block:: python

                data.outliers_plot(columns = ["x"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.outliers_plot(columns = ["x"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_outliers_plot_1d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_outliers_plot_1d.html

        .. tab:: 2D

            .. code-block:: python

                data.outliers_plot(columns = ["x", "y"])

            .. ipython:: python
                :suppress:
                :okwarning:

                vo.set_option("plotting_lib", "plotly")
                fig = data.outliers_plot(columns = ["x", "y"])
                fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_outliers_plot_2d.html")

            .. raw:: html
                :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdf_outliers_plot_2d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.scatter` : Scatter Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.boxplot` : Box Plot.

        """
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="OutliersPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.OutliersPlot(
            vdf=self,
            columns=columns,
            threshold=threshold,
            max_nb_points=max_nb_points,
            misc_layout={
                "color": color,
                "outliers_color": outliers_color,
                "inliers_color": inliers_color,
                "inliers_border_color": inliers_border_color,
            },
        ).draw(**kwargs)


class vDCPlot(vDCScaler):
    # Special Methods.

    def numh(
        self, method: Literal["sturges", "freedman_diaconis", "fd", "auto"] = "auto"
    ) -> float:
        """
        Computes the optimal VastColumn bar width.

        Parameters
        ----------
        method: str, optional
            Method used to compute the optimal h.
                auto              : Combination of Freedman Diaconis
                                    and Sturges.
                freedman_diaconis : Freedman Diaconis
                                    [2 * IQR / n ** (1 / 3)]
                sturges           : Sturges [CEIL(log2(n)) + 1]

        Returns
        -------
        float
            optimal bar width.
        """
        if method == "auto":
            pre_comp = self._parent._get_catalog_value(self._alias, "numh")
            if pre_comp != "VASTORBIT_NOT_PRECOMPUTED":
                return pre_comp
        assert self.isnum() or self.isdate(), ValueError(
            "numh is only available on type numeric|date"
        )
        if self.isnum():
            result = (
                self._parent.describe(
                    method="numerical", columns=[self._alias], unique=False
                )
                .transpose()
                .values[self._alias]
            )
            (
                count,
                VastColumn_min,
                VastColumn_025,
                VastColumn_075,
                VastColumn_max,
            ) = (
                result[0],
                result[3],
                result[4],
                result[6],
                result[7],
            )
        elif self.isdate():
            result = _executeSQL(
                f"""
                SELECT 
                    /*+LABEL('VastColumn.numh')*/ COUNT({self}) AS NAs, 
                    MIN({self}) AS min, 
                    APPROX_PERCENTILE({self} 
                       , 0.25) AS Q1, 
                    APPROX_PERCENTILE({self} 
                       , 0.75) AS Q3, 
                    MAX({self}) AS max 
                FROM 
                    (SELECT 
                        DATEDIFF('second', 
                                 '{self.min()}'::timestamp, 
                                 {self}) AS {self} 
                    FROM {self._parent}) vastorbit_OPTIMAL_H_TABLE""",
                title="Different aggregations to compute the optimal h.",
                method="fetchrow",
            )
            (
                count,
                VastColumn_min,
                VastColumn_025,
                VastColumn_075,
                VastColumn_max,
            ) = result
        sturges = max(
            float(VastColumn_max - VastColumn_min)
            / int(math.floor(math.log(count, 2) + 2)),
            1e-99,
        )
        fd = max(
            2.0 * (VastColumn_075 - VastColumn_025) / (count) ** (1.0 / 3.0), 1e-99
        )
        if str(method).lower() == "sturges":
            best_h = sturges
        elif str(method).lower() in ("freedman_diaconis", "fd"):
            best_h = fd
        else:
            best_h = max(sturges, fd)
            self._parent._update_catalog({"index": ["numh"], self._alias: [best_h]})
        if self.category() == "int":
            best_h = max(math.floor(best_h), 1)
        return best_h

    # Boxplots.

    @save_vastorbit_logs
    def boxplot(
        self,
        by: Optional[str] = None,
        q: tuple[float, float] = (0.25, 0.75),
        h: PythonNumber = 0,
        max_cardinality: int = 8,
        cat_priority: Union[None, PythonScalar, ArrayLike] = None,
        max_nb_fliers: int = 30,
        whis: float = 1.5,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the box plot of the VastColumn.

        Parameters
        ----------
        by: str, optional
            VastColumn used to partition  the  data.
        q: tuple, optional
            Tuple including the 2 quantiles used to draw
            the BoxPlot.
        h: PythonNumber, optional
            Interval  width  if  the 'by'  VastColumn is
            numerical or of a date-like type. Optimized h
            will be computed if the parameter is empty or
            invalid.
        max_cardinality: int, optional
            Maximum   number   of   distinct VastColumn
            elements to be used as categorical.
            The less frequent  elements  are gathered
            together to create a new category : 'Others'.
        cat_priority: PythonScalar / ArrayLike, optional
            ArrayLike list of the different categories to
            consider when drawing the box plot. The other
            categories are filtered.
        max_nb_fliers: int, optional
            Maximum  number of points used to represent
            the fliers of each category.
            Drawing fliers slows down the  graphic
            computation.
        whis: float, optional
            The position of the whiskers.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to  pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.boxplot`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 50

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["score1"].boxplot()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["score1"].boxplot(width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_boxplot_single.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_boxplot_single.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.boxplot` : Box Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.outliers_plot` : Outliers Plot.

        """
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="BoxPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.BoxPlot(
            vdf=self._parent,
            columns=[self._alias],
            by=by,
            q=q,
            h=h,
            max_cardinality=max_cardinality,
            cat_priority=cat_priority,
            max_nb_fliers=max_nb_fliers,
            whis=whis,
        ).draw(**kwargs)

    # 1D CHARTS.

    @save_vastorbit_logs
    def bar(
        self,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: int = 6,
        nbins: int = 0,
        h: PythonNumber = 0,
        categorical: bool = True,
        bargap: float = 0.06,
        categoryorder: Literal[
            "trace",
            "category ascending",
            "category descending",
            "total ascending",
            "total descending",
        ] = "trace",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the bar chart of the VastColumn based on an
        aggregation.

        Parameters
        ----------
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).
            - None:
                No Aggregations.

            It can also be a cutomized aggregation
            (ex: AVG(column1) + 5).
        of: str, optional
            The VastColumn  used to compute the aggregation.
        max_cardinality: int, optional
            Maximum number of distinct VastColumns elements
            to be used as categorical. For these elements, no
            h is picked or computed.
        nbins: int, optional
            Number  of  bins. If empty, an  optimized number of
            bins is computed.
        h: PythonNumber, optional
            Interval width of the bar. If empty, an optimized h
            is computed.
        categorical: bool, optional
            If  set to False and the  VastColumn is numerical,
            the parmater  'max_cardinality' is ignored and
            the bar  chart is represented as a histogram.
        bargap: float, optional
            A float between  (0, 1] that represents the
            proportion  taken out of each bar to render the
            chart. This proportion creates gaps between each
            bar. The bigger the value, the bigger the gap.
        categoryorder: str, optional
            How to sort the bars.
            One of the following options:

            - trace (no transformation)
            - category ascending
            - category descending
            - total ascending
            - total descending

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to  pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.bar`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "gender": ['M', 'M', 'M', 'F', 'F', 'F', 'F'],
                    "grade": ['A','B','C','A','B','B', 'B'],
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["grade"].bar()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["grade"].bar()
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_bar_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_bar_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.bar` : Bar Chart.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.barh` : Horizontal Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.barh` : Horizontal Bar Chart.

        """
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="BarChart",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.BarChart(
            vdc=self,
            method=method,
            of=of,
            max_cardinality=max_cardinality,
            nbins=nbins,
            h=h,
            pie=categorical,
            bargap=bargap,
            categoryorder=categoryorder,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def barh(
        self,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: int = 6,
        nbins: int = 0,
        h: PythonNumber = 0,
        categorical: bool = True,
        bargap: float = 0.06,
        categoryorder: Literal[
            "trace",
            "category ascending",
            "category descending",
            "total ascending",
            "total descending",
        ] = "trace",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws  the horizontal bar  chart of the VastColumn
        based on an aggregation.

        Parameters
        ----------
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).
            - None:
                No Aggregations.

            It can also be a cutomized aggregation
            (ex: AVG(column1) + 5).
        of: str, optional
            The VastColumn  used to compute the aggregation.
        max_cardinality: int, optional
            Maximum number of distinct elements for VastColumns
            to be used as categorical. For these elements, no
            h is picked or computed.
        nbins: int, optional
            Number  of  bins. If empty, an  optimized number of
            bins is computed.
        h: PythonNumber, optional
            Interval width of the bar. If empty, an optimized h
            is computed.
        categorical: bool, optional
            If  set to False and the  VastColumn is numerical,
            the parmater  'max_cardinality' is ignored and
            the bar  chart is represented as a histogram.
        bargap: float, optional
            A float between  (0, 1] that represent the
            proportion  taken out of each bar to render the
            chart. This proportion creates between  each bar.
            The  bigger the value,  the bigger the gap.
        categoryorder: str, optional
            How to sort the bars.
            One of the following options:

            - trace (no transformation)
            - category ascending
            - category descending
            - total ascending
            - total descending

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to  pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.bar`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "gender": ['M', 'M', 'M', 'F', 'F', 'F', 'F'],
                    "grade": ['A','B','C','A','B','B', 'B'],
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["grade"].barh()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["grade"].barh()
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_barh_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_barh_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.bar` : Bar Chart.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.barh` : Horizontal Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.bar` : Bar Chart.

        """
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="HorizontalBarChart",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.HorizontalBarChart(
            vdc=self,
            method=method,
            of=of,
            max_cardinality=max_cardinality,
            nbins=nbins,
            h=h,
            pie=categorical,
            bargap=bargap,
            categoryorder=categoryorder,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def pie(
        self,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: int = 6,
        h: PythonNumber = 0,
        kind: Literal["auto", "donut", "rose", "3d"] = "auto",
        categoryorder: Literal[
            "trace",
            "category ascending",
            "category descending",
            "total ascending",
            "total descending",
        ] = "trace",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the pie chart of the VastColumn based on an
        aggregation.

        Parameters
        ----------
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).
            - None:
                No Aggregations.

            It can also be a cutomized aggregation
            (ex: ``AVG(column1) + 5``).
        of: str, optional
            The VastColumn used to compute the aggregation.
        max_cardinality: int, optional
            Maximum number of distinct elements for VastColumns
            to be used as categorical. For these elements, no
            h is picked or computed.
        h: PythonNumber, optional
            Interval width of the bar. If empty, an optimized
            h is computed.
        kind: str, optional
            The type of pie chart.

            - auto:
                Regular pie chart.
            - donut:
                Donut chart.
            - rose:
                Rose chart.
            - 3d: 3D Pie.
        categoryorder: str, optional
            How to sort the bars.
            One of the following options:

            - trace (no transformation)
            - category ascending
            - category descending
            - total ascending
            - total descending

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to pass to  the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.pie`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "gender": ['M', 'M', 'M', 'F', 'F', 'F', 'F'],
                    "grade": ['A','B','C','A','B','B', 'B'],
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["grade"].pie()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["grade"].pie(width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_pie_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_pie_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.hist` : Histogram.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.pie` : Pie Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.bar` : Bar Chart.

        """
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="PieChart",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.PieChart(
            vdc=self,
            method=method,
            of=of,
            max_cardinality=max_cardinality,
            h=h,
            pie=True,
            misc_layout={"kind": kind},
            categoryorder=categoryorder,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def spider(
        self,
        by: Optional[str] = None,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: tuple[int, int] = (6, 6),
        h: tuple[PythonNumber, PythonNumber] = (None, None),
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the spider plot of the input VastColumn based on
        an aggregation.

        Parameters
        ----------
        by: str, optional
            VastColumn used to partition the data.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation
            (ex: ``AVG(column1) + 5``).
        of: str, optional
            The VastColumn used to compute the aggregation.
        max_cardinality: int, optional
            Maximum number of distinct elements for VastColumns
            to be used as categorical. For these elements, no
            h is picked or computed.
        h: PythonNumber, optional
            Interval width of the bar. If empty, an optimized
            h is computed.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional parameter to pass to  the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.spider`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "category": [np.random.choice(['A','B','C']) for _ in range(N)],
                    "score1": np.random.normal(5, 1, N),
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["score1"].spider()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["score1"].spider(width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_spider_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_spider_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.pie` : Pie Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.pie` : Pie Chart.

        """
        by, of = self._parent.format_colnames(by, of)
        columns = [self._alias]
        if by:
            columns += [by]
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="SpiderChart",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.SpiderChart(
            vdf=self._parent,
            columns=columns,
            method=method,
            of=of,
            max_cardinality=max_cardinality,
            h=h,
        ).draw(**kwargs)

    # Histogram & Density.

    @save_vastorbit_logs
    def hist(
        self,
        by: Optional[str] = None,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        h: Optional[PythonNumber] = None,
        h_by: PythonNumber = 0,
        max_cardinality: int = 8,
        cat_priority: Union[None, PythonScalar, ArrayLike] = None,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws  the histogram of the input VastColumn based
        on an aggregation.

        Parameters
        ----------
        by: str, optional
            VastColumn  used  to  partition  the  data.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation
            (ex: AVG(column1) + 5).
        of: str, optional
            The  VastColumn  used to compute the  aggregation.
        h: PythonNumber, optional
            Interval  width of the  input VastColumns. Optimized
            h  will be  computed  if  the  parameter is empty  or
            invalid.
        h_by: PythonNumber, optional
            Interval  width if the 'by' VastColumn is  numerical
            or of a date-like type. Optimized  h will be computed
            if the parameter is empty or invalid.
        max_cardinality: int, optional
            Maximum number of distinct elements for VastColumns
            to be used as categorical.
            The less frequent  elements are gathered together
            to create a new category : 'Others'.
            This parameter is used to discretize the VastColumn
            'by' when the main input nVastColumn is nnumerical.
            Otherwise, it  is  used  to   discretize    all the
            VastColumn inputs.
        cat_priority: PythonScalar / ArrayLike, optional
            ArrayLike list of the different categories to consider
            when drawing the box plot.  The other categories are
            filtered.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to  pass  to  the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.hist`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 50

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["score1"].hist()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["score1"].hist(width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_hist_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_hist_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.hist` : Histogram.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.barh` : Horizontal Bar Chart.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.bar` : Bar Chart.

        """
        if self.isnum() and not (self.isbool()):
            vo_plt, kwargs = self._parent.get_plotting_lib(
                class_name="Histogram",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.Histogram(
                vdf=self._parent,
                columns=[self._alias],
                by=by,
                method=method,
                of=of,
                h=h,
                h_by=h_by,
                max_cardinality=max_cardinality,
                cat_priority=cat_priority,
            ).draw(**kwargs)
        else:
            warning_message = (
                f"The Virtual Column {self._alias} is not "
                "numerical. A bar chart will be drawn instead."
            )
            print_message(warning_message, "warning")
            if by:
                return self._parent.bar(
                    columns=[self._alias, by],
                    method=method,
                    of=of,
                    max_cardinality=(max_cardinality, max_cardinality),
                    h=(h, h),
                    chart=chart,
                    **style_kwargs,
                )
            else:
                return self.bar(
                    method=method,
                    of=of,
                    max_cardinality=max_cardinality,
                    h=h,
                    chart=chart,
                    **style_kwargs,
                )

    @save_vastorbit_logs
    def density(
        self,
        by: Optional[str] = None,
        nbins: int = 100,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the VastColumn Density Plot using histogram approximation.

        Parameters
        ----------
        by: str, optional
            VastColumn used to partition the data.
        nbins: int, optional
            Number of bins for histogram approximation.
            Higher values give smoother density estimates.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any optional parameter to pass to the
            plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.density`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 50

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "score1": np.random.normal(5, 1, N),
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["score1"].density()

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["score1"].density(width=600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_density_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_density_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.density` : Density Plot.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.range_plot` : Range Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.hist` : Histogram.

        """
        if not by:

            vo_plt, kwargs = self._parent.get_plotting_lib(
                class_name="DensityPlot",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.DensityPlot(vdf=self._parent, columns=self._alias, by=by, nbins=nbins).draw(**kwargs)
        
        else:

            vo_plt, kwargs = self._parent.get_plotting_lib(
                class_name="MultiDensityPlot",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.MultiDensityPlot(vdf=self._parent, columns=self._alias, by=by, nbins=nbins).draw(**kwargs)

    # Time Series.

    @save_vastorbit_logs
    def candlestick(
        self,
        ts: str,
        method: PlottingMethod = "sum",
        q: tuple[float, float] = (0.25, 0.75),
        start_date: Optional[PythonScalar] = None,
        end_date: Optional[PythonScalar] = None,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the Time Series of the VastColumn.

        Parameters
        ----------
        ts: str
            TS  (Time Series)  VastColumn used to order the
            data.  The  VastColumn  type must  be  date
            like (date, datetime, timestamp...) or  numerical.
        method: str, optional
            The method used to aggregate the data.

            - count:
                Number of elements.
            - density:
                Percentage of the distribution.
            - mean:
                Average of the
                :py:class:`~VastColumns` ``of``.
            - min:
                Minimum of the
                :py:class:`~VastColumns` ``of``.
            - max:
                Maximum of the
                :py:class:`~VastColumns` ``of``.
            - sum:
                Sum of the
                :py:class:`~VastColumns` ``of``.
            - q%:
                q Quantile of the
                :py:class:`~VastColumns` ``of``
                (ex: 50% to get the median).

            It can also be a cutomized aggregation
            (ex: ``AVG(column1) + 5``).
        q: tuple, optional
            Tuple including the  2 quantiles used to draw the
            Plot.
        start_date: str / PythonNumber / date, optional
            Input Start Date. For example, time = '03-11-1993'
            will  filter  the  data  when 'ts' is less than
            the 3rd of November 1993.
        end_date: str / PythonNumber / date, optional
            Input  End  Date. For example, time = '03-11-1993'
            will filter  the data when 'ts' is  greater  than
            the 3rd of November 1993.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.candlestick`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "date": [1990 + i for i in range(N)] * 5,
                    "population": [100 + i for i in range(N)] + [300 + i * 2 for i in range(N)] + [200 + i ** 2 - 3 * i for i in range(N)] + [50 + i ** 2 - 6 * i for i in range(N)] + [700 + i ** 2 - 10 * i for i in range(N)],
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["population"].candlestick(ts = "date")

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["population"].candlestick(ts = "date", width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_cadnlestick_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_cadnlestick_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.range_plot` : Range Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.range_plot` : Range Plot.

        """
        ts = self._parent.format_colnames(ts)
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="CandleStick",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.CandleStick(
            vdf=self._parent,
            order_by=ts,
            method=method,
            q=q,
            column=self._alias,
            order_by_start=start_date,
            order_by_end=end_date,
        ).draw(**kwargs)

    @save_vastorbit_logs
    def plot(
        self,
        ts: str,
        by: Optional[str] = None,
        start_date: Optional[PythonScalar] = None,
        end_date: Optional[PythonScalar] = None,
        kind: Literal[
            "area", "area_percent", "area_stacked", "line", "spline", "step"
        ] = "line",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the Time Series of the VastColumn.

        Parameters
        ----------
        ts: str
            TS  (Time Series)  VastColumn used to order the
            data.  The  VastColumn  type must  be  date
            like (date, datetime, timestamp...) or  numerical.
        by: str, optional
            VastColumn used to partition the TS.
        start_date: str / PythonNumber / date, optional
            Input Start Date. For example, time = '03-11-1993'
            will  filter  the  data  when 'ts' is less than
            the 3rd of November 1993.
        end_date: str / PythonNumber / date, optional
            Input  End  Date. For example, time = '03-11-1993'
            will filter  the data when 'ts' is  greater  than
            the 3rd of November 1993.
        kind: str, optional
            The plot type.

            - line:
                Line Plot.
            - spline:
                Spline Plot.
            - step:
                Step Plot.
            - area_stacked:
                Stacked Area Plot.
            - area_percent:
                Fully Stacked Area Plot.

        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.line`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "date": [1900, 1950, 2000],
                    "Asia": [947, 1402, 3634],
                    "Africa": [133, 221, 767],
                    "Europe": [408, 547, 729],
                    "America": [156, 339, 818],
                    "Oceania": [6, 13, 30],
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["Asia"].plot(ts = "date", kind = "spline")

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["Asia"].plot(ts = "date", kind = "spline", width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_plot_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_plot_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.plot` : Line Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.range_plot` : Range Plot.

        """
        ts, by = self._parent.format_colnames(ts, by)
        vo_plt, kwargs = self._parent.get_plotting_lib(
            class_name="LinePlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.LinePlot(
            vdf=self._parent,
            order_by=ts,
            columns=[self._alias, by] if by else [self._alias],
            order_by_start=start_date,
            order_by_end=end_date,
            misc_layout={"kind": kind},
        ).draw(**kwargs)

    @save_vastorbit_logs
    def range_plot(
        self,
        ts: str,
        q: tuple[float, float] = (0.25, 0.75),
        start_date: Optional[PythonScalar] = None,
        end_date: Optional[PythonScalar] = None,
        plot_median: bool = False,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws  the  range   plot  of  the  VastColumn.  The
        aggregations  used  to draw the plot are  the  median
        and the two user-specified quantiles.

        Parameters
        ----------
        ts: str
            TS  (Time Series)  VastColumn  used  to order
            the  data.  The  VastColumn  type must  be  date
            like (date, datetime, timestamp...) or  numerical.
        q: tuple, optional
            Tuple including the  2 quantiles used to draw the
            Plot.
        start_date: str / PythonNumber / date, optional
            Input Start Date. For example, time = '03-11-1993'
            will  filter  the  data  when 'ts' is less than
            the 3rd of November 1993.
        end_date: str / PythonNumber / date, optional
            Input  End  Date. For example, time = '03-11-1993'
            will filter  the data when 'ts' is  greater  than
            the 3rd of November 1993.
        plot_median: bool, optional
            If set to True, the Median is drawn.
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any  optional  parameter  to pass to the  plotting
            functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.range`

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's also import `numpy` to create a dataset.

        .. ipython:: python

            import numpy as np

        We can create a variable ``N`` to fix the size:

        .. ipython:: python

            N = 30

        Let's generate a dataset using the following data.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "date": [1990 + i for i in range(N)] * 5,
                    "population1": [100 + i for i in range(N)] + [300 + i * 2 for i in range(N)] + [200 + i ** 2 - 3 * i for i in range(N)] + [50 + i ** 2 - 6 * i for i in range(N)] + [700 + i ** 2 - 10 * i for i in range(N)],
                    "population2": [200 + i ** 2 - i for i in range(N)] + [1000 + i * 2 for i in range(N)] + [500 + i ** 2 - 5 * i for i in range(N)] + [900 + i ** 2 + 3 * i for i in range(N)] + [100 + i ** 2 - 0.5 * i for i in range(N)],
                }
            )

        Now we are ready to draw the plot:

        .. code-block:: python

            data["population1"].range_plot(ts = "date")

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = data["population1"].range_plot(ts = "date", width = 600)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_range_plot_1d.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_plotting_vdc_range_plot_1d.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.range_plot` : Range Plot.
            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.plot` : Line Plot.

        """
        return self._parent.range_plot(
            columns=[self._alias],
            ts=ts,
            q=q,
            start_date=start_date,
            end_date=end_date,
            plot_median=plot_median,
            chart=chart,
            **style_kwargs,
        )

    # Geospatial.

    @save_vastorbit_logs
    def geo_plot(self, *args, **kwargs) -> PlottingObject:
        """
        Draws the Geospatial object.

        Parameters
        ----------
        *args / **kwargs:
            Any optional parameter to pass to the geopandas
            plot function.
            For more information, see:
            https://geopandas.readthedocs.io/en/latest/
            docs/reference/api/geopandas.GeoDataFrame.plot.html

        Returns
        -------
        ax
            Axes

        Examples
        ---------

        .. note::

            The below example is a very basic one. For
            other more detailed examples and customization
            options, please see :ref:`chart_gallery.geo`

        Let's begin by importing the dataset module of `vastorbit`.
        It provides a range of datasets for both training and
        exploring vastorbit's capabilities.

        .. ipython:: python

            import vastorbit.datasets as vod

        Let's utilize the World dataset to demonstrate geospatial capabilities.

        .. code-block:: python

            import vastorbit.datasets as vod

            world = vod.load_world()

            # We filter to select only the African continent
            africa = world[world["continent"] == "Africa"]

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            import vastorbit.datasets as vod

            vo.set_option("plotting_lib", "matplotlib")

            world = vod.load_world()

            # We filter to select only the African continent
            africa = world[world["continent"] == "Africa"]

        Now we can draw the plot:

        .. ipython:: python
            :okwarning:

            @savefig core_VastFrame_plotting_vdc_geo_plot.png
            africa["geometry"].geo_plot(edgecolor = "black", color = "white")

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.plot` : Line Plot.

        """
        import matplotlib.pyplot as plt

        theme = conf.get_option("theme")
        columns = [self._alias]
        check = True
        if len(args) > 0:
            column = args[0]
        elif "column" in kwargs:
            column = kwargs["column"]
        else:
            check = False
        if check:
            column = self._parent.format_colnames(column)
            columns += [column]
            if "cmap" not in kwargs:
                kwargs["cmap"] = PlottingBase().get_cmap(idx=0)
        else:
            if "color" not in kwargs:
                kwargs["color"] = PlottingBase().get_colors(idx=0)
        if "legend" not in kwargs:
            kwargs["legend"] = True
        if "figsize" not in kwargs:
            kwargs["figsize"] = (14, 10)
        ax = self._parent[columns].to_geopandas(self._alias).plot(*args, **kwargs)
        if theme == "sphinx":
            ax.get_figure().patch.set_alpha(0.0)
            ax.set_facecolor("none")
            plt.title("", color="#888888")
            plt.xlabel("", color="#888888")
            plt.ylabel("", color="#888888")
            plt.xticks(color="#888888")
            plt.yticks(color="#888888")
        elif theme == "dark":
            ax.set_facecolor("#11111A")
            plt.title("", color="#AAAAAA")
            plt.xlabel("", color="#AAAAAA")
            plt.ylabel("", color="#AAAAAA")
            plt.xticks(color="#AAAAAA")
            plt.yticks(color="#AAAAAA")
        elif theme == "light":
            ...
        return ax
