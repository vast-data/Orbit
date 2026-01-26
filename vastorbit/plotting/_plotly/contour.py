"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

from plotly.graph_objs._figure import Figure
import plotly.graph_objects as go
import numpy as np

from vastorbit.plotting._plotly.base import PlotlyBase


class ContourPlot(PlotlyBase):
    # Properties.

    @property
    def _category(self) -> Literal["plot"]:
        return "plot"

    @property
    def _kind(self) -> Literal["contour"]:
        return "contour"

    @property
    def _compute_method(self) -> Literal["contour"]:
        return "contour"

    @property
    def _dimension_bounds(self) -> tuple[int, int]:
        return (2, 2)

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {
            "width": 500,
            "height": 500,
            "xaxis": dict(
                showline=True,
                linewidth=2,
                linecolor="black",
                mirror=True,
                zeroline=False,
                title=self.layout["columns"][0],
            ),
            "yaxis": dict(
                showline=True,
                linewidth=2,
                linecolor="black",
                mirror=True,
                zeroline=False,
                title=self.layout["columns"][1],
            ),
        }

    def _get_color_style(self, style_kwargs: dict) -> dict:
        if "colorscale" not in style_kwargs:
            return {
                "colorscale": [
                    [0, self.get_colors(idx=2)],
                    [0.5, "#ffffff"],
                    [1, self.get_colors(idx=0)],
                ]
            }
        else:
            tmp_output = {"colorscale": style_kwargs["colorscale"]}
            style_kwargs.pop("colorscale")
            return tmp_output

    # Draw.

    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a contour plot using the Plotly API.
        """
        fig_base = self._get_fig(fig)
        if "color_scale" in style_kwargs:
            style_kwargs["colorscale"] = style_kwargs["color_scale"]
            style_kwargs.pop("color_scale")
        color_options = self._get_color_style(style_kwargs)
        fig = go.Figure(
            data=go.Contour(
                z=self.data["Z"],
                x=np.unique(self.data["X"]),
                y=np.unique(self.data["Y"]),
                hovertemplate=f"{self.init_style['xaxis']['title']}: "
                "%{x:.2f} <br> "
                f"{self.init_style['yaxis']['title']}:"
                " %{y:.2f} <extra></extra> <br> Color: %{z:.2f}",
                **color_options,
            )
        )
        fig.update_layout(width=500, height=500)
        fig.update_layout(
            **self._update_dict(self.init_style, style_kwargs),
        )
        fig_base.add_trace(fig.data[0])
        fig_base.update_layout(fig.layout)
        return fig_base
