"""
SPDX-License-Identifier: Apache-2.0
"""

from itertools import chain

import matplotlib.pyplot as plt
import numpy as np
import pytest

import vastorbit as vo


class TestPlotting:
    """
    test class for Plotting functions test
    """

    def test_boxplot(self):
        """
        test function - boxplot
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/plotly/test_plotly_boxplot.py"

    def test_bar(self):
        """
        test function - bar
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/plotly/test_plotly_bar.py"

    def test_barh(self):
        """
        test function - barh
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/plotly/test_plotly_barh.py"

    def test_pie(self):
        """
        test function - pie
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_hist(self):
        """
        test function - hist
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_density(self):
        """
        test function - density
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_plot(self):
        """
        test function - plot
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_range_plot(self):
        """
        test function - range_plot
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/plotly/test_plotly_range.py"

    def test_pivot_table(self):
        """
        test function - pivot_table
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_contour(self):
        """
        test function - contour
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/plotly/test_plotly_contour.py"

    def test_heatmap(self):
        """
        test function - heatmap
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_hexbin(self):
        """
        test function - hexbin
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/matplotlib/test_matplotlib_hexbin.py"

    def test_scatter(self):
        """
        test function - scatter
        """
        assert True, (
            "This test is covered under /vastorbit/vastorbit/tests/plotting/matplotlib/test_matplotlib_scatter.py, "
            "/vastorbit/vastorbit/tests/plotting/plotly/test_plotly_scatter.py, "
            "/vastorbit/vastorbit/tests/plotting/highcharts/test_highcharts_scatter.py"
        )

    @pytest.mark.parametrize(
        "columns, max_nb_points",
        [(["sepal_length", "sepal_width", "petal_width"], 5)],
    )
    def test_scatter_matrix(self, iris_vd, columns, max_nb_points, load_matplotlib):
        """
        test function - scatter_matrix
        """
        res = iris_vd.scatter_matrix(columns=columns, max_nb_points=max_nb_points)

        # Check if the axes_array is an instance of numpy ndarray
        assert isinstance(res, np.ndarray), "An ndarray not created for scatter matrix."

        # Check if all elements inside the axes_array are instances of Axes
        for ax in res.flat:
            assert isinstance(
                ax, plt.Axes
            ), "Incorrect object created for scatter matrix."

    def test_outliers_plot(self):
        """
        test function - outliers_plot
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/plotly/test_plotly_outliers.py"

    @pytest.mark.parametrize("method", ["auto", "fd", "sturges"])
    @pytest.mark.parametrize("data, column", [("market_vd", "price")])
    def test_numh(self, market_vd, data, column, method):
        """
        test function - numh
        """
        data_pdf = market_vd.to_pandas()

        # Note: For `method=auto` numpy considers min results of `fd` and `sturges` methods.
        # however, vpy considers max
        if method == "auto":
            py_res = max(
                max(np.diff(np.histogram_bin_edges(data_pdf["price"], bins="fd"))),
                max(np.diff(np.histogram_bin_edges(data_pdf["price"], bins="sturges"))),
            )
        else:
            py_res = max(
                np.diff(np.histogram_bin_edges(data_pdf["price"], bins=method))
            )

        vo_res = eval(data)[column].numh(method=method)

        assert vo_res == pytest.approx(py_res, rel=4e-02)

    def test_spider(self):
        """
        test function - spider
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/base_test_files.py"

    def test_candlestick(self):
        """
        test function - candlestick
        """
        assert (
            True
        ), "This test is covered under /vastorbit/vastorbit/tests/plotting/highcharts/test_highcharts_candlestick.py"

    def test_geo_plot_type(self, world_vd, load_matplotlib):
        """
        test function - geo_plot
        """
        africa = world_vd[world_vd["continent"] == "Africa"]

        result = africa["geometry"].geo_plot()

        isinstance(result, plt.Axes)

    def test_geo_plot_number_of_elements(self, world_vd, load_matplotlib):
        """
        test function - geo_plot
        """
        africa = world_vd[world_vd["continent"] == "Africa"]

        assert len(
            africa["geometry"]
            .geo_plot(column="pop_est", cmap="Reds")
            .get_default_bbox_extra_artists()
        ) == len(
            africa.to_geopandas(geometry="geometry")
            .plot()
            .get_default_bbox_extra_artists()
        )
