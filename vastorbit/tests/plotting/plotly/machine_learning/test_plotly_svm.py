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


class TestPlotlyMachineLearningSVMClassifier1DPlot(SVMClassifier1DPlot):
    """
    Testing different attributes of SVM classifier plot
    """

    @pytest.mark.skip(reason="Plotly has differnt labels")
    def test_properties_xaxis_label(self):
        """
        Testing x-axis title
        """

    @pytest.mark.skip(reason="Plotly has differnt labels")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """

    def test_properties_no_of_elements(self):
        """
        Test total number of elements for 1D
        """
        # Arrange
        total_items = 2
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"


class TestPlotlyMachineLearningSVMClassifier2DPlot(SVMClassifier2DPlot):
    """
    Testing different attributes of SVM classifier plot
    """

    def test_properties_no_of_elements(self):
        """
        Test total number of elements for 1D
        """
        # Arrange
        total_items = 3
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"


class TestPlotlyMachineLearningSVMClassifier3DPlot(SVMClassifier3DPlot):
    """
    Testing different attributes of SVM classifier plot
    """

    @pytest.mark.skip(reason="Plotly has differnt labels")
    def test_properties_xaxis_label(self):
        """
        Testing x-axis title
        """

    @pytest.mark.skip(reason="Plotly has differnt labels")
    def test_properties_yaxis_label(self):
        """
        Testing y-axis title
        """

    @pytest.mark.skip(reason="3D plots do not work with custom height")
    def test_additional_options_custom_width_and_height(self):
        """
        Test custom width and height
        """

    def test_properties_no_of_elements(self):
        """
        Test total number of elements for 1D
        """
        # Arrange
        total_items = 3
        # Act
        # Assert
        assert len(self.result.data) == total_items, "Some elements missing"
