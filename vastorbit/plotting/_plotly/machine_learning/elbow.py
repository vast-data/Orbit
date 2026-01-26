"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import plotly.express as px
from plotly.graph_objs._figure import Figure

from vastorbit.plotting._plotly.base import PlotlyBase


class ElbowCurve(PlotlyBase):
    # Properties.

    @property
    def _category(self) -> Literal["graph"]:
        return "graph"

    @property
    def _kind(self) -> Literal["elbow"]:
        return "elbow"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {
            "mode": "markers+lines",
            "marker_line_width": 2,
            "marker_color": "white",
            "marker_size": 10,
            "marker_line_color": "black",
        }
        self.init_layout_style = {
            "yaxis_title": self.layout["y_label"],
            "xaxis_title": self.layout["x_label"],
            "width": 650,
            "height": 650,
        }

    # Draw.

    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a machine learning bubble plot using the Plotly API.
        """
        fig_base = self._get_fig(fig)
        fig = px.line(x=self.data["x"], y=self.data["y"], markers=True)
        fig_base.add_trace(fig.data[0])
        fig_base.update_traces(**self.init_style)
        fig_base.update_layout(
            **self._update_dict(self.init_layout_style, style_kwargs)
        )
        return fig_base
