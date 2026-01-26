"""
SPDX-License-Identifier: Apache-2.0
"""

# vastorbit
from vastorbit.tests.plotting.base_test_files import (
    SVMClassifier1DPlot,
    SVMClassifier2DPlot,
    SVMClassifier3DPlot,
)


class TestMatplotlibMachineLearningSVMClassifier1DPlot(SVMClassifier1DPlot):
    """
    Testing different attributes of SVM classifier plot
    """

    @property
    def cols(self):
        """
        Store labels for X,Y,Z axis to check.
        """
        return [
            self.COL_NAME_1,
            "",
        ]


class TestMatplotlibMachineLearningSVMClassifier2DPlot(SVMClassifier2DPlot):
    """
    Testing different attributes of SVM classifier plot
    """


class TestMatplotlibMachineLearningSVMClassifier3DPlot(SVMClassifier3DPlot):
    """
    Testing different attributes of SVM classifier plot
    """
