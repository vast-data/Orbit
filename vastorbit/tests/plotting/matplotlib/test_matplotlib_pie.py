"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCPiePlot, NestedVDFPiePlot


class TestMatplotlibVDCPiePlot(VDCPiePlot):
    """
    Testing different attributes of Pie plot on a VastColumn
    """

    def test_plot_type_wedges(
        self,
    ):
        """
        Test if multiple sections of pie plot is created
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert len(self.result.patches) > 1

    def test_properties_labels(self, dummy_vd):
        """
        Test if all unique values grouped
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert set(
            self.result.get_legend().get_texts()[i].get_text()
            for i in range(len(self.result.get_legend().get_texts()))
        ) == set(dummy_vd.to_pandas()[self.COL_NAME].unique())


class TestMatplotlibNestedVDFPiePlot(NestedVDFPiePlot):
    """
    Testing different attributes of Pie plot on a VastFrame
    """

    def test_plot_type_wedges(
        self,
    ):
        """
        Test if nested plots are produced
        """
        # Arrange
        # Act
        # Assert - check value corresponding to 0s
        assert len(self.result.patches) > 2
