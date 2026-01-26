"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import ElbowCurvePlot


class TestPlotlyMachineLearningElbowCurvePlot(ElbowCurvePlot):
    """
    Testing different attributes of Elbow Curve plot
    """

    def test_data_all_scatter_points(self):
        """
        Test if both line and markers are displayed
        """
        # Arrange
        mode = "markers+line"
        # Act
        # Assert - checking if correct object created
        assert set(self.result.data[0]["mode"]) == set(
            mode
        ), "Either lines or marker missing"
