"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import VornoiPlot


class TestPlotlyMachineLearningKmeansPlot(VornoiPlot):
    """
    Testing different attributes of Importance Bar Chart plot
    """

    def test_properties_no_of_elements(self):
        """
        Test if all objects plotted
        """
        # Arrange
        total_items = 20
        # Act
        # Assert
        assert len(self.result.data) == pytest.approx(
            total_items, abs=5
        ), "Some elements missing"
