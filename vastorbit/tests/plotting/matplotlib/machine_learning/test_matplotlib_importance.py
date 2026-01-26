"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import ImportanceBarChartPlot


class TestMatplotlibMachineLearningImportanceBarChart(ImportanceBarChartPlot):
    """
    Testing different attributes of Importance Bar Chart plot
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return ["Importance (%)", "Features"]

    def test_properties_xaxis_label(self):
        """
        Testing x-axis title
        """

    def test_data_no_of_columns(self):
        """
        Test if four columns are produced
        """
        # Arrange
        total_items = 4
        # Act
        # Assert
        assert len(self.result.containers[0]) == total_items, "Some columns missing"
