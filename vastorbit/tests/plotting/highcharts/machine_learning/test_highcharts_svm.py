"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    SVMClassifier1DPlot,
    SVMClassifier2DPlot,
    SVMClassifier3DPlot,
)


class TestHighchartsMachineLearningSVMClassifier1DPlot(SVMClassifier1DPlot):
    """
    Testing different attributes of SVM classifier plot
    """


class TestHighchartsMachineLearningSVMClassifier2DPlot(SVMClassifier2DPlot):
    """
    Testing different attributes of SVM classifier plot
    """


@pytest.mark.skip(reason="3d plot not supported in highcharts")
class TestHighchartsMachineLearningSVMClassifier3DPlot(SVMClassifier3DPlot):
    """
    Testing different attributes of SVM classifier plot
    """
