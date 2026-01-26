"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCRangeCurve, VDFRangeCurve


class TestMatplotlibVDCRangeCurve(VDCRangeCurve):
    """
    Testing different attributes of range curve plot on a VastColumn
    """

    def test_data_x_axis(self, dummy_date_vd):
        """
        Test x-ticks
        """
        # Arrange
        test_set = set(dummy_date_vd.to_numpy()[:, 0])
        # Act
        assert test_set.issubset(self.result.get_xticks())


class TestMatplotlibVDFRangeCurve(VDFRangeCurve):
    """
    Testing different attributes of range curve plot on a VastFrame
    """

    def test_data_x_axis(self, dummy_date_vd):
        """
        Test all unique values
        """
        # Arrange
        test_set = set(dummy_date_vd.to_numpy()[:, 0])
        # Act
        # Assert
        assert test_set.issubset(self.result.get_xticks())
