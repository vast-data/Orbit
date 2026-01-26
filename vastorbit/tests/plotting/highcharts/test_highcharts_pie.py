"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCPiePlot, NestedVDFPiePlot


class TestHighchartsVDCPiePlot(VDCPiePlot):
    """
    Testing different attributes of Pie plot on a VastColumn
    """

    def test_plot_type_wedges(
        self,
    ):
        """
        Test if multiple sections of pie plot is created
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert len(self.result.data_temp[0].data) > 1


class TestHighchartsNestedVDFPiePlot(NestedVDFPiePlot):
    """
    Testing different attributes of Pie plot on a VastFrame
    """

    def test_plot_type_wedges(
        self,
    ):
        """
        Test if nested plots are produced
        """
        # Arrange
        all_elements_count = sum(len(item.data) for item in self.result.data_temp)
        # Act
        # Assert - check value corresponding to 0s
        assert all_elements_count > 2
