"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import plotly.graph_objects as go
from plotly.graph_objs._figure import Figure

from vastorbit.plotting._plotly.base import PlotlyBase


class DensityPlot(PlotlyBase):
    # Properties.

    @property
    def _category(self) -> Literal["graph"]:
        return "graph"

    @property
    def _kind(self) -> Literal["density"]:
        return "density"

    @property
    def _compute_method(self) -> Literal["density"]:
        return "density"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {
            "width": 700,
            "height": 500,
            "autosize": False,
            "xaxis_title": self._clean_quotes(self.layout["x_label"]),
            "yaxis_title": self.layout["y_label"],
            "xaxis": dict(
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                zeroline=False,
            ),
            "yaxis": dict(
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                zeroline=False,
            ),
        }

    # Draw.

    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a density plot using the Plotly API.
        """
        fig = self._get_fig(fig)
        fig.add_trace(
            go.Scatter(
                x=self.data["x"],
                y=self.data["y"],
                fill="tozeroy",
                marker=dict(
                    color=self.get_colors()[0],
                ),
            )
        )
        fig.update_layout(**self._update_dict(self.init_style, style_kwargs))
        return fig


class MultiDensityPlot(DensityPlot):
    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a multi-density plot using the Plotly API.
        """
        fig = self._get_fig(fig)
        ncolors = len(self.get_colors())
        for i in range(self.data["X"].shape[1]):
            fig.add_trace(
                go.Scatter(
                    x=self.data["X"][:, i],
                    y=self.data["Y"][:, i],
                    fill="tozeroy",
                    name=str(self.layout["labels"][i]),
                    marker=dict(
                        color=self.get_colors()[i % ncolors],
                    ),
                )
            )
        fig.update_layout(**self._update_dict(self.init_style, style_kwargs))
        return fig


class DensityPlot2D(PlotlyBase): ...
