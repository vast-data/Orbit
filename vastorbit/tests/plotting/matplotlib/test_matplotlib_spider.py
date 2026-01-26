"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCSpiderPlot


class TestMatplotlibVDCSpiderPlot(VDCSpiderPlot):
    """
    Testing different attributes of Spider plot on a VastColumn
    """

    def test_properties_multiple_plots_produced_for_multiplot(
        self,
    ):
        """
        Test if multiple plots produced
        """
        # Arrange
        number_of_plots = 2
        # Act
        # Assert
        assert (
            len(
                self.by_result.get_subplotspec()
                .get_topmost_subplotspec()
                .get_gridspec()
                .get_geometry()
            )
            == number_of_plots
        ), "Two traces not produced for two classes of binary"
