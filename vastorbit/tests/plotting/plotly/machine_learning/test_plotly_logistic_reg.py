"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    LogisticRegressionPlot2D,
    LogisticRegressionPlot3D,
)


class TestPlotlyMachineLearningLogisticRegressionPlot2D(LogisticRegressionPlot2D):
    """
    Testing different attributes of 2D Logisti Regression plot
    """

    def test_properties_two_scatter_and_line_plot(self):
        """
        Test if two scatter plots and one line is plotted
        """
        # Arrange
        total_items = 3
        # Act
        # Assert
        assert (
            len(self.result.data) == total_items
        ), "Either line or the two scatter plots are missing"


class TestPlotlyMachineLearningLogisticRegressionPlot3D(LogisticRegressionPlot3D):
    """
    Testing different attributes of 3D Logisti Regression plot
    """

    def test_properties_zaxis_label(self):
        """
        Testing y-axis title
        """
        assert self.result.layout["scene"]["yaxis"]["title"]["text"] == self.COL_NAME_3
