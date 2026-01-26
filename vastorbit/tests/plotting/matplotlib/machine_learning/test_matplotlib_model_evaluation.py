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


class TestMatplotlibMachineLearningROCPlot(ROCPlot):
    """
    Testing different attributes of ROC plot
    """


class TestMatplotlibMachineLearningCutoffCurvePlot(CutoffCurvePlot):
    """
    Testing different attributes of Curve plot
    """


class TestMatplotlibMachineLearningPRCPlot(PRCPlot):
    """
    Testing different attributes of PRC plot
    """


class TestMatplotlibMachineLearningLiftChartPlot(LiftChartPlot):
    """
    Testing different attributes of Lift Chart plot
    """
