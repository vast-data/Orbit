"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCBarhPlot, VDFBarhPlot


class TestHighchartsVDCBarhPlot(VDCBarhPlot):
    """
    Testing different attributes of HHorizontal Bar plot on a VastColumn
    """

    def test_additional_options_bargap(self, dummy_vd):
        """
        Test bargap option
        """
        # Arrange
        # Act
        result = dummy_vd[self.COL_NAME].barh(
            bargap=0.5,
        )
        # Assert - checking if correct object created
        assert result.data_temp[0].pointPadding == 0.25, "Custom bargap not working"

    def test_data_ratios(self, dummy_vd):
        """
        Test data ratio plotted
        """
        ### Checking if the density was plotted correctly
        nums = dummy_vd.to_pandas()[self.COL_NAME].value_counts()
        total = len(dummy_vd)
        assert set(self.result.data_temp[0].data).issubset(
            set([nums["A"] / total, nums["B"] / total, nums["C"] / total])
        )

    def test_all_categories_created(self):
        """
        Test all categories
        """
        assert set(self.result.options["xAxis"].categories).issubset(
            set(["A", "B", "C"])
        )


class TestHighchartsVDFBarhPlot(VDFBarhPlot):
    """
    Testing different attributes of HHorizontal Bar plot on a VastFrame
    """
