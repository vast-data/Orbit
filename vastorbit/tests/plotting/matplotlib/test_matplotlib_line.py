"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST

from vastorbit.tests.plotting.base_test_files import VDCLinePlot, VDFLinePlot


class TestMatplotlibVDCLinePlot(VDCLinePlot):
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
            sum(len(line.get_xdata()) for line in self.result.get_lines())
            == total_count
        ), "The total values in the plot are not equal to the values in the dataframe."


class TestMatplotlibVDFLinePlot(VDFLinePlot):
    """
    Testing different attributes of Line plot on a VastFrame
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return [self.TIME_COL, ""]
