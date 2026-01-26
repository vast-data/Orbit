"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    ROCPlot,
    CutoffCurvePlot,
    PRCPlot,
    LiftChartPlot,
)


class TestPlotlyMachineLearningROCPlot(ROCPlot):
    """
    Testing different attributes of ROC plot
    """

    def test_properties_no_of_elements(self):
        """
        Test if both elements plotted
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"


class TestPlotlyMachineLearningCutoffCurvePlot(CutoffCurvePlot):
    """
    Testing different attributes of Curve plot
    """

    def test_properties_no_of_elements(self):
        """
        Test if both elements plotted
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"


class TestPlotlyMachineLearningPRCPlot(PRCPlot):
    """
    Testing different attributes of PRC plot
    """

    def test_properties_no_of_elements(self):
        """
        Test if only element plotted
        """
        # Arrange
        total_items = 1
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"


class TestPlotlyMachineLearningLiftChartPlot(LiftChartPlot):
    """
    Testing different attributes of Lift Chart plot
    """

    def test_properties_no_of_elements(self):
        """
        Test if both elements plotted
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"
