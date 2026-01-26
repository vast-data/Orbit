"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import (
    ScatterVDF2DPlot,
    ScatterVDF3DPlot,
)


class TestHighchartsScatterVDF2DPlot(ScatterVDF2DPlot):
    """
    Testing different attributes of 2D scatter plot on a VastFrame
    """

    def test_properties_all_unique_values_for_by(self, dummy_scatter_vd):
        """
        Test if all unique valies are inside the plot
        """
        # Arrange
        # Act
        result = dummy_scatter_vd.scatter(
            [
                self.COL_NAME_2,
                self.COL_NAME_3,
            ],
            by=self.COL_NAME_4,
        )
        # Assert
        assert len(result.data_temp) == len(
            self.all_categories
        ), "Some unique values were not found in the plot"

    def test_data_total_number_of_points(self, dummy_scatter_vd):
        """
        Test if all datapoints were plotted
        """
        # Arrange
        # Act
        # Assert - checking if correct object created
        assert sum(len(item.data) for item in self.result.data_temp) == len(
            dummy_scatter_vd
        ), "Number of points not consistent with data"


class TestHighchartsScatterVDF3DPlot(ScatterVDF3DPlot):
    """
    Testing different attributes of 3D scatter plot on a VastFrame
    """

    def test_properties_all_unique_values_for_by_3d_plot(
        self,
    ):
        """
        Test if all unique values plotted
        """
        # Arrange
        # Act
        # Assert
        assert len(self.result.data_temp) == len(
            self.all_categories
        ), "Some unique values were not found in the plot"

    def test_data_total_number_of_points_3d_plot(self, dummy_scatter_vd):
        """
        Test if all datapoints were plotted
        """
        # Arrange
        # Act
        # Assert - checking if correct object created
        assert sum(len(item.data) for item in self.result.data_temp) == len(
            dummy_scatter_vd
        ), "Number of points not consistent with data"
