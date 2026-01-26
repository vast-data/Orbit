"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCBoxPlot,
    VDCParitionBoxPlot,
    VDFBoxPlot,
)


class TestHighchartsVDCBoxPlot(VDCBoxPlot):
    """
    Testing different attributes of Box plot on a VastColumn
    """


class TestHighchartsParitionVDCBoxPlot(VDCParitionBoxPlot):
    """
    Testing different attributes of Box plot on a VastColumn using "by" attribute
    """


class TestHighchartsVDFBoxPlot(VDFBoxPlot):
    """
    Testing different attributes of Box plot on a VastFrame
    """

    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """
        # Arrange
        test_title = self.COL_NAME_1
        # Act
        # Assert - checking y axis label
        assert (
            self.result.options["xAxis"].categories[0] == test_title
        ), "X axis label incorrect"
