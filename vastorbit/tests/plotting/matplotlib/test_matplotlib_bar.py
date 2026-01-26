"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCBarPlot, VDFBarPlot

COL_NAME_2 = "check 1"


class TestMatplotlibVDCBarPlot(VDCBarPlot):
    """
    Testing different attributes of Bar plot on a VastColumn
    """

    def test_data_ratios(self, dummy_vd):
        """
        Test data ratio plotted for bar chart
        """
        ### Checking if the density was plotted correctly
        nums = dummy_vd.to_pandas()[self.COL_NAME].value_counts()
        total = len(dummy_vd)
        assert set(self.result.patches[i].get_height() for i in range(0, 3)).issubset(
            {nums["A"] / total, nums["B"] / total, nums["C"] / total}
        )

    def test_all_categories_created(self):
        """
        Test all categories
        """
        assert set(
            self.result.get_xticklabels()[i].get_text() for i in range(3)
        ).issubset({"A", "B", "C"})

    def test_xaxis_category(self):
        """
        Test x-axis type
        """
        # Arrange
        # Act
        # Assert
        assert self.result.xaxis.get_scale() == "linear"

    def test_additional_options_kind_stack(self, dummy_vd, plotting_library_object):
        """
        Test stacked bar
        """
        # Arrange
        kind = "stacked"
        # Act
        result3 = dummy_vd.bar(
            columns=[self.COL_NAME],
            method="avg",
            of=COL_NAME_2,
            kind=kind,
        )
        # Assert
        assert isinstance(result3, plotting_library_object), "wrong object crated"


class TestMatplotlibVDFBarPlot(VDFBarPlot):
    """
    Testing different attributes of Bar plot on a VastFrame
    """

    def test_data_ratios(self, dummy_dist_vd):
        """
        Test data ratio
        """
        ### Checking if the density was plotted correctly
        nums = dummy_dist_vd.to_pandas()[self.COL_NAME_VDF_1].value_counts()
        total = len(dummy_dist_vd)
        assert set(self.result.patches[i].get_height() for i in range(0, 3)).issubset(
            {nums["A"] / total, nums["B"] / total, nums["C"] / total}
        )

    def test_all_categories_created(self):
        """
        Test if all categories exist in plot
        """
        assert set(
            self.result.get_xticklabels()[i].get_text() for i in range(3)
        ).issubset({"A", "B", "C"})
