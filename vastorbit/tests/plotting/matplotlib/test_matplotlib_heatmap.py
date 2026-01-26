"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDFPivotHeatMap, VDFHeatMap


class TestMatplotlibVDFPivotHeatMap(VDFPivotHeatMap):
    """
    Testing different attributes of Heatmap plot on a VastFrame
    """

    def test_properties_yaxis_labels_for_categorical_data(self, titanic_vd):
        """
        Test labels for Y-axis
        """
        # Arrange
        expected_labels = (
            '"survived"',
            '"pclass"',
            '"fare"',
            '"parch"',
            '"age"',
            '"sibsp"',
            '"body"',
        )
        # Act
        result = titanic_vd.corr(method="pearson", focus="survived")
        yaxis_labels = [
            result.get_yticklabels()[i].get_text()
            for i in range(len(result.get_yticklabels()))
        ]
        # Assert
        assert set(yaxis_labels).issubset(expected_labels), "Y-axis labels incorrect"


class TestMatplotlibVDFHeatMap(VDFHeatMap):
    """
    Testing different attributes of Heatmap plot on a VastFrame
    """
