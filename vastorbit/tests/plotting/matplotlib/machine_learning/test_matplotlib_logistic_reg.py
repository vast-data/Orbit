"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    LogisticRegressionPlot2D,
    LogisticRegressionPlot3D,
)


class TestMatplotlibMachineLearningLogisticRegressionPlot2D(LogisticRegressionPlot2D):
    """
    Testing different attributes of 2D Logisti Regression plot
    """

    @pytest.mark.skip(reason="Need to capitalize P in the label")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """


class TestMatplotlibMachineLearningLogisticRegressionPlot3D(LogisticRegressionPlot3D):
    """
    Testing different attributes of 3D Logisti Regression plot
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return [self.COL_NAME_1, self.COL_NAME_3, f"P({self.COL_NAME_2} = 1)"]

    @pytest.mark.skip(reason="Need to add 'P' in the title to represent probability")
    def test_properties_zaxis_label(self):
        """
        Testing z-axis title
        """
