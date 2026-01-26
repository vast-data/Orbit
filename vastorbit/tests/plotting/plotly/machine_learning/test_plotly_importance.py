"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import ImportanceBarChartPlot


class TestPlotlyMachineLearningImportanceBarChartPlot(ImportanceBarChartPlot):
    """
    Testing different attributes of Importance Bar Chart plot
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return ["Importance (%)", "Features"]

    def test_data_no_of_columns(self):
        """
        Test if all columns used
        """
        # Arrange
        total_items = 4
        # Act
        # Assert
        assert len(self.result.data[0]["x"]) == total_items, "Some columns missing"
