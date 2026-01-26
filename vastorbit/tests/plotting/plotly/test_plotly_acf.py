"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import ACFPlot


class TestPlotlyVDFACFPlot(ACFPlot):
    """
    Testing different attributes of ACF plot on a VastFrame
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return ["Lag", "Value"]

    def test_properties_scatter_points_and_confidence(self):
        """
        Check if all 3 elements are plotted
        """
        # Arrange
        total_elements = 3
        # Act
        # Assert - checking if all plotting objects were created
        assert (
            len(self.result.data) == total_elements
        ), "Some elements of plot are missing"

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
            len(result.layout["shapes"]) == lag_number
        ), "Number of vertical lines inconsistent"

    def test_properties_mode_lines(self, amazon_vd):
        """
        Test to check number of vertical lines for kind=line
        """
        # Arrange
        mode = "lines+markers"
        # Act
        result = amazon_vd.acf(
            ts="date",
            column="number",
            p=12,
            by=["state"],
            unit="month",
            method="spearman",
            kind="line",
        )
        # Assert
        assert result.data[-1]["mode"] == mode, "Number of vertical lines inconsistent"

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
            len(self.result.data[0]["x"]) == lag_number
        ), "Number of lag points inconsistent"
