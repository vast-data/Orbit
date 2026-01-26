"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCHistogramPlot,
    VDFHistogramPlot,
    VDFHistogramMultiPlot,
)


class TestMatplotlibVDCHistogramPlot(VDCHistogramPlot):
    """
    Testing different attributes of Histogram plot on a VastColumn
    """


class TestMatplotlibVDFHistogramPlot(VDFHistogramPlot):
    """
    Testing different attributes of Histogram plot on a VastFrame
    """


class TestMatplotlibVDFHistogramMultiPlot(VDFHistogramMultiPlot):
    """
    Testing different attributes of Multi-Histogram plot on a VastFrame
    """

    def test_properties_xaxis_label(self):
        """
        Testing x-axis label
        """
        assert self.result.get_xlabel() == "", "X axis label incorrect"
