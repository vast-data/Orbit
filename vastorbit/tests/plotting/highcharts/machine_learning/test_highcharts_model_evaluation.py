"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    ROCPlot,
    CutoffCurvePlot,
    PRCPlot,
    LiftChartPlot,
)


class TestHighchartsMachineLearningROCPlot(ROCPlot):
    """
    Testing different attributes of ROC plot
    """


class TestHighchartsMachineLearningCutoffCurvePlot(CutoffCurvePlot):
    """
    Testing different attributes of Curve plot
    """

    @pytest.mark.skip(reason="Cannot extract y axis value from highchart")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """


class TestHighchartsMachineLearningPRCPlot(PRCPlot):
    """
    Testing different attributes of PRC plot
    """


class TestHighchartsMachineLearningLiftChartPlot(LiftChartPlot):
    """
    Testing different attributes of Lift Chart plot
    """

    @pytest.mark.skip(reason="Need to fix y axis")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """
