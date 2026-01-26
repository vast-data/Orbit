"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import ACFPlot


class TestHighchartsVDFACFPlot(ACFPlot):
    """
    Testing different attributes of ACF plot on a VastFrame
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
            len(result.data_temp[0].data) == lag_number
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
            len(self.result.data_temp[0].data) == lag_number
        ), "Number of lag points inconsistent"
