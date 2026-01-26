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


class TestHighchartsMachineLearningLogisticRegressionPlot2D(LogisticRegressionPlot2D):
    """
    Testing different attributes of 2D Logisti Regression plot
    """

    @pytest.mark.skip(reason="Need to capitalize P in the label")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """


@pytest.mark.skip(reason="Currently highchart only supports 2D plot")
class TestHighchartsMachineLearningLogisticRegressionPlot3D(LogisticRegressionPlot3D):
    """
    Testing different attributes of 3D Logisti Regression plot
    """
