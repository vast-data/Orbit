"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCBoxPlot,
    VDCParitionBoxPlot,
    VDFBoxPlot,
)


class TestMatplotlibVDCBoxPlot(VDCBoxPlot):
    """
    Testing different attributes of Box plot on a VastColumn
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return [self.COL_NAME_1, ""]


class TestMatplotlibParitionVDCBoxPlot(VDCParitionBoxPlot):
    """
    Testing different attributes of Box plot on a VastColumn using "by" attribute
    """


class TestMatplotlibVDFBoxPlot(VDFBoxPlot):
    """
    Testing different attributes of Box plot on a VastFrame
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return [self.COL_NAME_1, ""]
