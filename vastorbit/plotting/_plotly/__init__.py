"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.plotting._plotly.base import PlotlyBase

from vastorbit.plotting._plotly.machine_learning.champion_challenger import (
    ChampionChallengerPlot,
)
from vastorbit.plotting._plotly.machine_learning.elbow import ElbowCurve
from vastorbit.plotting._plotly.machine_learning.importance import ImportanceBarChart
from vastorbit.plotting._plotly.machine_learning.kmeans import VoronoiPlot
from vastorbit.plotting._plotly.machine_learning.lof import LOFPlot
from vastorbit.plotting._plotly.machine_learning.logistic_reg import (
    LogisticRegressionPlot,
)
from vastorbit.plotting._plotly.machine_learning.model_evaluation import (
    CutoffCurve,
    LiftChart,
    PRCCurve,
    ROCCurve,
)
from vastorbit.plotting._plotly.machine_learning.pca import (
    PCACirclePlot,
    PCAScreePlot,
    PCAVarPlot,
)
from vastorbit.plotting._plotly.machine_learning.regression import RegressionPlot
from vastorbit.plotting._plotly.machine_learning.regression_tree import (
    RegressionTreePlot,
)
from vastorbit.plotting._plotly.machine_learning.stepwise import StepwisePlot
from vastorbit.plotting._plotly.machine_learning.svm import SVMClassifierPlot
from vastorbit.plotting._plotly.machine_learning.tsa import TSPlot

from vastorbit.plotting._plotly.acf import ACFPlot
from vastorbit.plotting._plotly.bar import BarChart, BarChart2D
from vastorbit.plotting._plotly.barh import HorizontalBarChart, HorizontalBarChart2D
from vastorbit.plotting._plotly.boxplot import BoxPlot
from vastorbit.plotting._plotly.candlestick import CandleStick
from vastorbit.plotting._plotly.contour import ContourPlot
from vastorbit.plotting._plotly.density import DensityPlot, MultiDensityPlot
from vastorbit.plotting._plotly.heatmap import HeatMap
from vastorbit.plotting._plotly.hist import Histogram
from vastorbit.plotting._plotly.pie import PieChart, NestedPieChart
from vastorbit.plotting._plotly.range import RangeCurve
from vastorbit.plotting._plotly.line import LinePlot, MultiLinePlot
from vastorbit.plotting._plotly.outliers import OutliersPlot
from vastorbit.plotting._plotly.scatter import ScatterPlot
from vastorbit.plotting._plotly.spider import SpiderChart
from vastorbit.plotting._plotly.subplots import draw_subplots


import plotly.io as pio
import plotly.graph_objects as go

pio.templates["vastorbit"] = go.layout.Template(
    layout_colorway=PlotlyBase().get_colors()
)
pio.templates.default = "vastorbit"
