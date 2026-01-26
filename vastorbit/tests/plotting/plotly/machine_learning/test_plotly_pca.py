"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    PCACirclePlot,
    PCAScreePlot,
    PCAVarPlot,
)


class TestPlotlyMachineLearningPCACirclePlot(PCACirclePlot):
    """
    Testing different attributes of PCA circle plot
    """

    def test_data_no_of_columns(self):
        """
        Test all columns
        """
        # Arrange
        total_items = 3
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some columns missing"


class TestPlotlyMachineLearningPCAVarPlot(PCAVarPlot):
    """
    Testing different attributes of PCA Var plot
    """


class TestPlotlyMachineLearningPCAScreePlot(PCAScreePlot):
    """
    Testing different attributes of PCA Scree plot
    """
