"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import ImportanceBarChartPlot


class TestHighchartsMachineLearningImportanceBarChartPlot(ImportanceBarChartPlot):
    """
    Testing different attributes of Importance Bar Chart plot
    """

    def test_data_no_of_columns(self):
        """
        Test if four columns are produced
        """
        # Arrange
        total_items = 4
        # Act
        # Assert
        assert len(self.result.data_temp[0].data) == total_items, "Some columns missing"
