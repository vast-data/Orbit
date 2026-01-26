"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import LearningRegressionTreePlot


class TestPlotlyMachineLearningRegressionTreePlot(LearningRegressionTreePlot):
    """
    Testing different attributes of Regression Tree plot
    """

    def test_properties_observations_label(self):
        """
        Test plot title
        """
        # Arrange
        test_title = "Observations"
        # Act
        # Assert
        assert self.result.data[0]["name"] == test_title, "X axis label incorrect"

    def test_properties_prediction_label(self):
        """
        Test plot title
        """
        # Arrange
        test_title = "Prediction"
        # Act
        # Assert
        assert self.result.data[1]["name"] == test_title, "Y axis label incorrect"

    def test_properties_hover_label(self):
        """
        Test hover labels
        """
        # Arrange
        test_title = (
            f"{self.COL_NAME_1}: %" "{x} <br>" f"{self.COL_NAME_2}: %" "{y} <br>"
        )
        # Act
        # Assert
        assert (
            self.result.data[0]["hovertemplate"] == test_title
        ), "Hover information incorrect"

    def test_properties_no_of_elements(self):
        """
        Test number of elements
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == pytest.approx(
            total_items, abs=1
        ), "Some elements missing"
