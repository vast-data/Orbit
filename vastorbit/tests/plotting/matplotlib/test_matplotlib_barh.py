"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import (
    VDCBarhPlot,
    VDFBarhPlot,
    VDFBarhPlot2D,
)


class TestMatplotlibVDCBarhPlot(VDCBarhPlot):
    """
    Testing different attributes of HHorizontal Bar plot on a VastColumn
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return ["density", self.COL_NAME]

    def test_data_sum_equals_one(self):
        """
        Test if sume is 1
        """
        # Arrange
        # Act
        # Assert - Comparing total adds up to 1
        assert sum(self.result.patches[i].get_width() for i in range(0, 3)) == 1

    def test_data_ratios(self, dummy_vd):
        """
        Test data ratio plotted
        """
        ### Checking if the density was plotted correctly
        nums = dummy_vd.to_pandas()[self.COL_NAME].value_counts()
        total = len(dummy_vd)
        assert set(self.result.patches[i].get_width() for i in range(0, 3)).issubset(
            set([nums["A"] / total, nums["B"] / total, nums["C"] / total])
        )

    def test_all_categories_created(self):
        """
        Test all categories
        """
        assert set(
            self.result.get_yticklabels()[i].get_text() for i in range(3)
        ).issubset(set(["A", "B", "C"]))


class TestMatplotlibVDFBarhPlot(VDFBarhPlot):
    """
    Testing different attributes of HHorizontal Bar plot on a VastFrame
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return ["density", self.COL_NAME_VDF_1]

    def test_data_ratios(self, dummy_dist_vd):
        """
        Test ratios plotted
        """
        ### Checking if the density was plotted correctly
        nums = dummy_dist_vd.to_pandas()[self.COL_NAME_VDF_1].value_counts()
        total = len(dummy_dist_vd)
        assert set(self.result.patches[i].get_width() for i in range(0, 3)).issubset(
            set([nums["A"] / total, nums["B"] / total, nums["C"] / total])
        )

    def test_all_categories_created(self):
        """
        Test all categories
        """
        assert set(
            self.result.get_yticklabels()[i].get_text() for i in range(3)
        ).issubset(set(["A", "B", "C"]))


class TestMatplotlibVDFBarhPlot2D(VDFBarhPlot2D):
    """
    Testing different attributes of HHorizontal Bar plot on a VastFrame
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return ["density", self.COL_NAME_VDF_1]
