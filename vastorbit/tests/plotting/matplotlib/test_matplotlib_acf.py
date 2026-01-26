"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import ACFPlot


class TestMatplotlibVDFACFPlot(ACFPlot):
    """
    Testing different attributes of ACF plot on a VastFrame
    """

    @pytest.mark.skip(reason="Matplotlib does not have a y-axis")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis label
        """

    def test_properties_vertical_lines_for_custom_lag(self, amazon_vd):
        """
        Test to check number of vertical lines
        """
        # Arrange
        lag_number = 24
        # Act
        result = amazon_vd.acf(
            ts="date",
            column="number",
            p=lag_number - 1,
            by=["state"],
            unit="month",
            method="spearman",
        )
        # Assert
        assert (
            len(result.get_lines()[0].get_xdata()) - 2 == lag_number
        ), "Number of vertical lines inconsistent"

    def test_data_all_scatter_points(
        self,
    ):
        """
        Test to check if all points plotted
        """
        # Arrange
        lag_number = 13
        # Act
        # Assert
        assert (
            len(self.result.get_lines()[0].get_xdata()) - 2 == lag_number
        ), "Number of lag points inconsistent"
