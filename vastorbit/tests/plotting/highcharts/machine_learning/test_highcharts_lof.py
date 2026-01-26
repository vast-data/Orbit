"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import LOFPlot2D, LOFPlot3D


class TestHighchartsMachineLearningLOFPlot2D(LOFPlot2D):
    """
    Testing different attributes of 2D LOF plot
    """


@pytest.mark.skip(reason="Currently highchart only supports 2D plot")
class TestHighchartsMachineLearningLOFPlot3D(LOFPlot3D):
    """
    Testing different attributes of 3D LOF plot
    """
