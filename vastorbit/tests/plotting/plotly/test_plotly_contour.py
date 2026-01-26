"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDFContourPlot


class TestPlotlyVDFContourPlot(VDFContourPlot):
    """
    Testing different attributes of Contour plot on a VastFrame
    """

    def test_data_count_xaxis_default_bins(
        self,
    ):
        """
        Testing default bins
        """
        # Arrange
        # Act
        # Assert
        assert self.result.data[0]["x"].shape[0] == 100, "The default bins are not 100."

    def test_data_count_xaxis_custom_bins(self, dummy_dist_vd):
        """
        Test different bin sizes
        """
        # Arrange
        custom_bins = 200

        def func(param_a, param_b):
            return param_b + param_a * 0

        # Act
        result = dummy_dist_vd.contour(
            columns=[self.COL_NAME_1, self.COL_NAME_2], nbins=custom_bins, func=func
        )
        # Assert
        assert (
            result.data[0]["x"].shape[0] == custom_bins
        ), "The custom bins option is not working."

    def test_data_x_axis_range(self, dummy_dist_vd):
        """
        Test x-axis range
        """
        # Arrange
        x_min = dummy_dist_vd[self.COL_NAME_1].min()
        x_max = dummy_dist_vd[self.COL_NAME_1].max()
        # Act
        # Assert
        assert (
            self.result.data[0]["x"].min() == x_min
            and self.result.data[0]["x"].max() == x_max
        ), "The range in data is not consistent with plot"
