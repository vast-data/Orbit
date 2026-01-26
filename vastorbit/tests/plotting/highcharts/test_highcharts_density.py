"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCDensityPlot,
    VDCDensityMultiPlot,
    VDFDensityPlot,
)


class TestHighchartsVDCDensityPlot(VDCDensityPlot):
    """
    Testing different attributes of Density plot on a VastColumn
    """


class TestHighchartVDCDensityMultiPlot(VDCDensityMultiPlot):
    """
    Testing different attributes of Multiple Density plots on a VastColumn
    """


class TestHighchartsVDFDensityPlot(VDFDensityPlot):
    """
    Testing different attributes of Density plot on a VastFrame
    """
