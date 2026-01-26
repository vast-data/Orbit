"""
SPDX-License-Identifier: Apache-2.0
"""

import numpy as np

# VAST
from vastorbit.tests.plotting.base_test_files import (
    ScatterVDF2DPlot,
    ScatterVDF3DPlot,
)


class TestMatplotlibScatterVDF2DPlot(ScatterVDF2DPlot):
    """
    Testing different attributes of 2D scatter plot on a VastFrame
    """

    def test_properties_all_unique_values_for_by(
        self,
    ):
        """
        Test if all unique valies are inside the plot
        """
        # Arrange
        # Act
        result = self.data.scatter(
            [
                self.COL_NAME_2,
                self.COL_NAME_3,
            ],
            by=self.COL_NAME_4,
        )
        # Assert
        assert len(np.unique(result.collections[0].get_facecolors(), axis=0)) == len(
            self.all_categories
        ), "Some unique values were not found in the plot"

    def test_data_total_number_of_points(self):
        """
        Test if all datapoints were plotted
        """
        # Arrange
        # Act
        # Assert - checking if correct object created
        assert len(self.result.collections[0].get_offsets()) == len(
            self.data
        ), "Number of points not consistent with data"


class TestMatplotlibVDFScatter3DPlot(ScatterVDF3DPlot):
    """
    Testing different attributes of 3D scatter plot on a VastFrame
    """

    def test_properties_all_unique_values_for_by_3d_plot(self):
        """
        Test if all unique values plotted
        """
        # Arrange
        # Act
        # Assert
        assert len(
            np.unique(self.result.collections[0].get_facecolors(), axis=0)
        ) == len(self.all_categories), "Some unique values were not found in the plot"

    def test_data_total_number_of_points_3d_plot(self, dummy_scatter_vd):
        """
        Test if all datapoints were plotted
        """
        # Arrange
        # Act
        # Assert - checking if correct object created
        assert len(self.result.collections[0].get_offsets()) == len(
            dummy_scatter_vd
        ), "Number of points not consistent with data"
