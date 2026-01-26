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


class TestPlotlyVDCDensityPlot(VDCDensityPlot):
    """
    Testing different attributes of Density plot on a VastColumn
    """

    def test_data_x_axis_range(self, dummy_dist_vd):
        """
        Test x-axis range
        """
        # Arrange
        x_min = dummy_dist_vd["0"].min()
        x_max = dummy_dist_vd["0"].max()

        # Act
        assert pytest.approx(self.result.data[0]["x"].min(), 4) == pytest.approx(
            x_min, 4
        ) and pytest.approx(self.result.data[0]["x"].max(), 4) == pytest.approx(
            x_max, 4
        ), "The range in data is not consistent with plot"


class TestplotlyVDCDensityMultiPlot(VDCDensityMultiPlot):
    """
    Testing different attributes of Multiple Density plots on a VastColumn
    """


class TestPlotlyVDFDensityPlot(VDFDensityPlot):
    """
    Testing different attributes of Density plot on a VastFrame
    """
