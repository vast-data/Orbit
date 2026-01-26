"""
SPDX-License-Identifier: Apache-2.0
"""

import pytest

from IPython.display import HTML

import vastorbit as vo

vo.set_option("plotting_lib", "plotly")
print(vo.get_option("plotting_lib"))


class TestPlottingAnimated:
    """
    test class for PlottingAnimated functions test
    """

    # @pytest.mark.parametrize("by", ["continent", None])
    @pytest.mark.parametrize("by", ["continent"])
    def test_animated_bar(self, pop_growth_vd_fun, by):
        """
        test function - animated_bar
        """
        result = pop_growth_vd_fun.animated_bar(
            ts="year",
            columns=["city", "population"],
            by=by,
            start_date=1970,
            end_date=1980,
        )
        assert isinstance(result, HTML)

    @pytest.mark.parametrize("by", ["continent", None])
    def test_animated_pie(self, pop_growth_vd_fun, by):
        """
        test function - animated_pie
        """
        result = pop_growth_vd_fun.animated_pie(
            ts="year",
            columns=["city", "population"],
            by=by,
            start_date=1970,
            end_date=1980,
        )
        assert isinstance(result, HTML)

    def test_animated_plot(self, amazon_vd):
        """
        test function - animated_plot
        """
        result = amazon_vd.animated_plot(
            "date",
            "number",
            by="state",
        )
        assert isinstance(result, HTML)

    @pytest.mark.parametrize(
        "columns",
        [
            ["lifeExp", "gdpPercap", "country", "pop"],
            ["lifeExp", "gdpPercap", "country"],
            ["lifeExp", "gdpPercap", "pop"],
            ["lifeExp", "gdpPercap"],
        ],
    )
    def test_animated_scatter(self, gapminder_vd, columns):
        """
        test function - animated_scatter
        """
        result = gapminder_vd.animated_scatter(
            ts="year",
            columns=columns,
            by="continent",
            limit_labels=10,
            limit_over=100,
        )
        assert isinstance(result, HTML)
