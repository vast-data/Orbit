"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# VAST
from vastorbit.tests.plotting.base_test_files import VDCPiePlot, NestedVDFPiePlot

# Test variables
all_elements = {"1", "0", "A", "B", "C"}


class TestPlotlyHighchartsVDCPiePlot(VDCPiePlot):
    """
    Testing different attributes of Pie plot on a VastColumn
    """

    def test_data_0_values(self, dummy_vd):
        """
        Test data for "0" category values
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert (
            self.result.data[0]["values"][0]
            == dummy_vd[dummy_vd[self.COL_NAME] == 0][self.COL_NAME].count()
            / dummy_vd[self.COL_NAME].count()
        )

    def test_data_1_values(self, dummy_vd):
        """
        Test data for "1" category values
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert (
            self.result.data[0]["values"][1]
            == dummy_vd[dummy_vd[self.COL_NAME] == 1][self.COL_NAME].count()
            / dummy_vd[self.COL_NAME].count()
        )

    def test_properties_labels(self, dummy_vd):
        """
        Test plot labels
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert set(self.result.data[0]["labels"]) == set(
            dummy_vd.to_pandas()[self.COL_NAME].unique()
        )


class TestPlotlyNestedVDFPiePlot(NestedVDFPiePlot):
    """
    Testing different attributes of Pie plot on a VastFrame
    """

    def test_properties_branch_values(self):
        """
        Test if the branch values are covering all
        """
        # Arrange
        # Act
        # Assert - checking if the branch values are covering all
        assert self.result.data[0]["branchvalues"] == "total"

    def test_data_all_labels_for_nested(self):
        """
        Test if all labels are plotted
        """
        # Arrange
        # Act
        # Assert - checking if all the labels exist
        assert set(self.result.data[0]["labels"]) == all_elements

    def test_data_check_parent_of_0(self):
        """
        Test parent of "0"
        """
        # Arrange
        # Act
        # Assert - checking the parent of '0' which is an element of column "check 1"
        assert self.result.data[0]["parents"][
            self.result.data[0]["labels"].index("0")
        ] in [""]
