"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest
import numpy as np

# VAST
from vastorbit.tests.plotting.base_test_files import VDFPivotHeatMap, VDFHeatMap


class TestPlotlyVDFPivotHeatMap(VDFPivotHeatMap):
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
        # Assert
        assert result.data[0]["y"] == expected_labels, "Y-axis labels incorrect"

    def test_data_matrix_shape_for_pivot_table(
        self,
    ):
        """
        Test shape of matrix
        """
        # Arrange
        expected_shape = (3, 2)
        # Act
        # Assert
        assert (
            self.result.data[0]["z"].shape == expected_shape
        ), "Incorrect shape of output matrix"


@pytest.mark.skip("Error in Plotly need to be fixed")
class TestPlotlyVDFHeatMap(VDFHeatMap):
    """
    Testing different attributes of Heatmap plot on a VastFrame
    """

    def test_data_matrix_shape(
        self,
    ):
        """
        Test shape of matrix
        """
        # Arrange
        expected_shape = (9, 6)
        # Act
        # Assert
        assert (
            self.result.data[0]["z"].shape == expected_shape
        ), "Incorrect shape of output matrix"

    def test_data_x_range(self, iris_vd):
        """
        Test x-axis range
        """
        # Arrange
        upper_bound = iris_vd[self.COL_NAME_1].max()
        lower_bound = iris_vd[self.COL_NAME_1].min()
        # Act
        x_array = np.array(self.result.data[0]["x"], dtype=float)
        # Assert
        assert np.all(
            (x_array[1:] >= lower_bound) & (x_array[:-1] <= upper_bound)
        ), "X-axis Values outside of data range"

    def test_data_y_range(self, iris_vd):
        """
        Test y-axis range
        """
        # Arrange
        upper_bound = iris_vd[self.COL_NAME_2].max()
        lower_bound = iris_vd[self.COL_NAME_2].min()
        # Act
        y_array = np.array(self.result.data[0]["y"], dtype=float)
        # Assert
        assert np.all(
            (y_array[:-1] >= lower_bound) & (y_array[1:] <= upper_bound)
        ), "X-axis Values outside of data range"
