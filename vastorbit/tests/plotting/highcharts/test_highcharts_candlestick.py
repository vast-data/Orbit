"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import VDCCandlestick

# Highcharts
try:
    from vertica_highcharts import Highstock
except:
    Highstock = type(None)


# Testing variables
COL_NAME_1 = "values"
TIME_COL = "date"
COL_OF = "survived"
BY_COL = "category"


class TestHighChartsVDCCandlestick(VDCCandlestick):
    """
    Testing different attributes of Candlestick plot on a VastColumn
    """

    def test_properties_output_type(self, plotting_library_object):
        """
        Test if correct object created
        """
        # Arrange
        # Act
        # Assert - checking if correct object created
        assert isinstance(self.result, Highstock), "Wrong object created"

    @pytest.mark.parametrize(
        "method, start_date", [("count", 1910), ("density", 1920), ("max", 1920)]
    )
    def test_properties_output_type_for_all_options(
        self, dummy_line_data_vd, method, start_date
    ):
        """
        Test "method" and "start date" parameters
        """
        # Arrange
        # Act
        result = dummy_line_data_vd[COL_NAME_1].candlestick(
            ts=TIME_COL, method=method, start_date=start_date
        )
        # Assert - checking if correct object created
        assert isinstance(result, Highstock), "Wrong object created"

    @pytest.mark.skip(reason="The plot does not have custom width and height yet")
    def test_additional_options_custom_width_and_height(
        self,
    ):
        """
        Testing custom width and height
        """
