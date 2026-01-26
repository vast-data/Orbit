"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCDensityPlot,
    VDCDensityMultiPlot,
    VDFDensityPlot,
)


class TestMatplotlibVDCDensityPlot(VDCDensityPlot):
    """
    Testing different attributes of Density plot on a VastColumn
    """


class TestHighchartVDCDensityMultiPlot(VDCDensityMultiPlot):
    """
    Testing different attributes of Multiple Density plots on a VastColumn
    """

    def test_properties_multiple_plots_produced_for_multiplot(
        self,
    ):
        """
        Test if two plots created
        """
        # Arrange
        number_of_plots = 2
        # Act
        # Assert
        assert (
            len(self.result.lines) == number_of_plots
        ), "Two plots not produced for two classes"


class TestHighchartsVDFDensityPlot(VDFDensityPlot):
    """
    Testing different attributes of Density plot on a VastFrame
    """
