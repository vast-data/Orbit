"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.plotting._matplotlib.base import MatplotlibBase
from vastorbit.plotting._matplotlib.animated.base import AnimatedBase

from vastorbit.plotting._matplotlib.animated.bar import AnimatedBarChart
from vastorbit.plotting._matplotlib.animated.bubble import AnimatedBubblePlot
from vastorbit.plotting._matplotlib.animated.line import AnimatedLinePlot
from vastorbit.plotting._matplotlib.animated.pie import AnimatedPieChart

from vastorbit.plotting._matplotlib.machine_learning.champion_challenger import (
    ChampionChallengerPlot,
)
from vastorbit.plotting._matplotlib.machine_learning.elbow import ElbowCurve
from vastorbit.plotting._matplotlib.machine_learning.importance import (
    ImportanceBarChart,
)
from vastorbit.plotting._matplotlib.machine_learning.kmeans import VoronoiPlot
from vastorbit.plotting._matplotlib.machine_learning.lof import LOFPlot
from vastorbit.plotting._matplotlib.machine_learning.logistic_reg import (
    LogisticRegressionPlot,
)
from vastorbit.plotting._matplotlib.machine_learning.model_evaluation import (
    CutoffCurve,
    LiftChart,
    PRCCurve,
    ROCCurve,
)
from vastorbit.plotting._matplotlib.machine_learning.pca import (
    PCACirclePlot,
    PCAScreePlot,
    PCAVarPlot,
)
from vastorbit.plotting._matplotlib.machine_learning.regression import RegressionPlot
from vastorbit.plotting._matplotlib.machine_learning.regression_tree import (
    RegressionTreePlot,
)
from vastorbit.plotting._matplotlib.machine_learning.stepwise import StepwisePlot
from vastorbit.plotting._matplotlib.machine_learning.svm import SVMClassifierPlot
from vastorbit.plotting._matplotlib.machine_learning.tsa import TSPlot

from vastorbit.plotting._matplotlib.acf import ACFPlot, ACFPACFPlot
from vastorbit.plotting._matplotlib.bar import BarChart, BarChart2D
from vastorbit.plotting._matplotlib.barh import HorizontalBarChart, HorizontalBarChart2D
from vastorbit.plotting._matplotlib.boxplot import BoxPlot
from vastorbit.plotting._matplotlib.contour import ContourPlot
from vastorbit.plotting._matplotlib.density import (
    DensityPlot,
    DensityPlot2D,
    MultiDensityPlot,
)
from vastorbit.plotting._matplotlib.heatmap import HeatMap
from vastorbit.plotting._matplotlib.hexbin import HexbinMap
from vastorbit.plotting._matplotlib.hist import Histogram
from vastorbit.plotting._matplotlib.line import LinePlot, MultiLinePlot
from vastorbit.plotting._matplotlib.outliers import OutliersPlot
from vastorbit.plotting._matplotlib.pie import PieChart, NestedPieChart
from vastorbit.plotting._matplotlib.range import RangeCurve
from vastorbit.plotting._matplotlib.scatter import ScatterMatrix, ScatterPlot
from vastorbit.plotting._matplotlib.spider import SpiderChart
from vastorbit.plotting._matplotlib.candlestick import CandleStick
