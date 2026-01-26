"""
SPDX-License-Identifier: Apache-2.0
"""

import random
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import VDCLinePlot, VDFLinePlot


class TestPlotlyVDCLinePlot(VDCLinePlot):
    """
    Testing different attributes of Line plot on a VastColumn
    """

    @pytest.mark.skip(reason="Need to change from time to time column name")
    def test_properties_xaxis_label(self):
        """
        Testing x-axis title
        """

    def test_data_count_of_all_values(self, dummy_line_data_vd):
        """
        Testing total points
        """
        # Arrange
        total_count = dummy_line_data_vd.shape()[0]
        # Act
        assert (
            self.result.data[0]["x"].shape[0] + self.result.data[1]["x"].shape[0]
            == total_count
        ), "The total values in the plot are not equal to the values in the dataframe."

    def test_data_spot_check(self, dummy_line_data_vd):
        """
        Spot check one data point
        """
        # Arrange
        # Act
        assert (
            str(
                dummy_line_data_vd[self.TIME_COL][
                    random.randint(0, len(dummy_line_data_vd)) - 1
                ]
            )
            in self.result.data[0]["x"]
        ), "Two time values that exist in the data do not exist in the plot"

    def test_additional_options_marker_on(self, dummy_line_data_vd):
        """
        Test marker option
        """
        # Arrange
        # Act
        result = dummy_line_data_vd[self.COL_NAME_1].plot(
            ts=self.TIME_COL, by=self.COL_NAME_2, markers=True
        )
        # Assert - checking if correct object created
        assert set(result.data[0]["mode"]) == set(
            "lines+markers"
        ), "Markers not turned on"


class TestPlotlyVDFLinePlot(VDFLinePlot):
    """
    Testing different attributes of Line plot on a VastFrame
    """
