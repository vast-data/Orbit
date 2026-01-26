"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import LearningRegressionPlot


class TestMatplotlibMachineLearningRegressionPlot(LearningRegressionPlot):
    """
    Testing different attributes of Regression plot
    """

    def test_data_all_scatter_points(self, dummy_scatter_vd):
        """
        Test if all points are plotted
        """
        # Arrange
        # Act
        # Assert
        assert len(self.result.collections[0].get_offsets()) == len(
            dummy_scatter_vd
        ), "Discrepancy between points plotted and total number ofp oints"
