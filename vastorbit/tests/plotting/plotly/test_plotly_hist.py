"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCHistogramPlot,
    VDFHistogramPlot,
    VDFHistogramMultiPlot,
)


class TestPlotlyVDCHistogramPlot(VDCHistogramPlot):
    """
    Testing different attributes of Histogram plot on a VastColumn
    """

    def test_properties_no_of_elements(self):
        """
        Test if all elements plotted
        """
        # Arrange
        total_items = 1
        # Act
        # Assert
        assert len(self.result.data) == pytest.approx(
            total_items, abs=1
        ), "Some elements missing"


class TestPlotlyVDFHistogramPlot(VDFHistogramPlot):
    """
    Testing different attributes of Histogram plot on a VastFrame
    """


class TestPlotlyVDFHistogramMultiPlot(VDFHistogramMultiPlot):
    """
    Testing different attributes of Multi-Histogram plot on a VastFrame
    """
