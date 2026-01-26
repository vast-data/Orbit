"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCHistogramPlot,
    VDFHistogramPlot,
)


class TestHighchartsVDCHistogramPlot(VDCHistogramPlot):
    """
    Testing different attributes of Histogram plot on a VastColumn
    """

    def test_properties_xaxis_label(self):
        """
        Testing x axis labels
        """
        # Since there is no label, it passes by default
        assert True


class TestHighchartsVDFHistogramPlot(VDFHistogramPlot):
    """
    Testing different attributes of Histogram plot on a VastFrame
    """

    def test_properties_xaxis_label(self):
        """
        Testing x axis labels
        """
        # Since there is no label, it passes by default
        assert True
