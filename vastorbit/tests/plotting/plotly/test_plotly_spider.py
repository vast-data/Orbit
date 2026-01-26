"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCSpiderPlot


class TestPlotlyVDCSpiderPlot(VDCSpiderPlot):
    """
    Testing different attributes of Spider plot on a VastColumn
    """

    def test_properties_method_title_at_bottom(
        self,
    ):
        """
        Test method title
        """
        # Arrange
        method_text = "(Method: Density)"
        # Act
        # Assert -
        assert (
            self.result.layout["annotations"][0]["text"] == method_text
        ), "Method title incorrect"

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
            len(self.by_result.data) == number_of_plots
        ), "Two traces not produced for two classes of binary"

    def test_data_all_categories(self, dummy_dist_vd):
        """
        Test all categories
        """
        # Arrange
        no_of_category = dummy_dist_vd["cats"].nunique()
        # Act
        assert (
            self.result.data[0]["r"].shape[0] == no_of_category
        ), "The number of categories in the data differ from the plot"
