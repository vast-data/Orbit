"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import LOFPlot2D, LOFPlot3D


class TestPlotlyMachineLearningLOFPlot2D(LOFPlot2D):
    """
    Testing different attributes of 2D LOF plot
    """

    def test_properties_scatter_and_line_plot(self):
        """
        Test outline and scatter
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Either outline or scatter missing"

    def test_properties_hoverinfo_for_2d(self):
        """
        Test hover info
        """
        # Arrange
        x_val = "{x}"
        y_val = "{y}"
        # Act
        # Assert
        assert (
            x_val in self.result.data[1]["hovertemplate"]
            and y_val in self.result.data[1]["hovertemplate"]
        ), "Hover information does not contain x or y"


@pytest.mark.skip(reason="Currently highchart only supports 2D plot")
class TestHighchartsMachineLearningLOFPlot3D(LOFPlot3D):
    """
    Testing different attributes of 3D LOF plot
    """
