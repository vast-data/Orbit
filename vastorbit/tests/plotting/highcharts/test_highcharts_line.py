"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST

from vastorbit.tests.plotting.base_test_files import VDCLinePlot, VDFLinePlot


class TestHighchartsVDCLinePlot(VDCLinePlot):
    """
    Testing different attributes of Line plot on a VastColumn
    """

    def test_data_count_of_all_values(self, dummy_line_data_vd):
        """
        Testing total points
        """
        # Arrange
        total_count = dummy_line_data_vd.shape()[0]
        # Act
        assert (
            len(self.result.data_temp[0].data[0]) * len(self.result.data_temp[0].data)
            == total_count
        ), "The total values in the plot are not equal to the values in the dataframe."


class TestHighchartsVDFLinePlot(VDFLinePlot):
    """
    Testing different attributes of Line plot on a VastFrame
    """
