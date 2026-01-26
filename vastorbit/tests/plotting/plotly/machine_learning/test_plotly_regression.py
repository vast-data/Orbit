"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import LearningRegressionPlot


class TestPlotlyMachineLearningRegressionPlot(LearningRegressionPlot):
    """
    Testing different attributes of Regression plot
    """

    def test_properties_scatter_and_line_plot(self):
        """
        Test two items exist
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Either line or scatter missing"

    def test_data_all_scatter_points(self, dummy_scatter_vd):
        """
        Test all datapoints
        """
        # Arrange
        no_of_points = len(dummy_scatter_vd)
        # Act
        # Assert
        assert (
            len(self.result.data[0]["x"]) == no_of_points
        ), "Discrepancy between points plotted and total number of points"
