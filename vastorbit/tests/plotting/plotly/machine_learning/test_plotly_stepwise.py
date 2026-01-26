"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit.tests.plotting.base_test_files import StepwisePlot


class TestPlotlyMachineLearningStepwisePlot(StepwisePlot):
    """
    Testing different attributes of Stepwise plot
    """

    def test_properties_no_of_elements(self):
        """
        Test all objects
        """
        # Arrange
        total_items = 8
        # Act
        # Assert
        assert len(self.result.data) == pytest.approx(
            total_items, abs=1
        ), "Some elements missing"

    def test_data_start_and_end(self):
        """
        Test start and end objects
        """
        # Arrange
        start = "Start"
        end = "End"
        # Act
        # Assert
        assert start in [
            self.result.data[i]["name"] for i in range(len(self.result.data))
        ] and end in [
            self.result.data[i]["name"] for i in range(len(self.result.data))
        ], "Some elements missing"
