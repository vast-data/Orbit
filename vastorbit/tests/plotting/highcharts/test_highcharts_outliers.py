"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import OutliersPlot2D, OutliersPlot


class TestHighchartsOutliersPlot(OutliersPlot):
    """
    Testing different attributes of outliers plot on a VastColumn
    """

    def test_data_all_scatter_points_for_1d(
        self,
        dummy_dist_vd,
    ):
        """
        Testing to make sure all poitns are plotted
        """
        # Arrange
        total_points = len(dummy_dist_vd[self.COL_NAME_1])
        # Act
        result = dummy_dist_vd.outliers_plot(
            columns=[self.COL_NAME_1], max_nb_points=10000
        )
        plot_points_count = sum(len(result.data_temp[i].data) for i in range(1, 3))
        assert (
            plot_points_count == total_points
        ), "All points are not plotted for 1d plot"


class TestHighchartsOutliersPlot2D(OutliersPlot2D):
    """
    Testing different attributes of outliers plot on a VastFrame
    """
