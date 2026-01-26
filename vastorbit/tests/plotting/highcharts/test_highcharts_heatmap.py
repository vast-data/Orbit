"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import VDFPivotHeatMap, VDFHeatMap


class TestHighchartsVDFPivotHeatMap(VDFPivotHeatMap):
    """
    Testing different attributes of Heatmap plot on a VastFrame
    """


@pytest.mark.skip("Error in highcharts need to be fixed")
class TestHighchartsVDFHeatMap(VDFHeatMap):
    """
    Testing different attributes of Heatmap plot on a VastFrame
    """
