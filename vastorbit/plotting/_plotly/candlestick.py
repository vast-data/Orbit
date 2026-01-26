"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import plotly.graph_objects as go
from plotly.graph_objs._figure import Figure
from vastorbit.plotting._plotly.base import PlotlyBase


class CandleStick(PlotlyBase):
    # Properties.

    @property
    def _category(self) -> Literal["graph"]:
        return "graph"

    @property
    def _kind(self) -> Literal["candlestick"]:
        return "candlestick"

    @property
    def _compute_method(self) -> Literal["candle"]:
        return "candle"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {
            "width": 700,
            "height": 500,
        }

    def _color_style(self, style_kwargs) -> None:
        color_list = self.get_colors()
        if "colors" in style_kwargs:
            color_list = (
                style_kwargs["colors"] + color_list
                if isinstance(style_kwargs["colors"], list)
                else [style_kwargs["colors"]] + color_list
            )
            style_kwargs.pop("colors")

        return {
            "increasing_line_color": color_list[0],
            "decreasing_line_color": color_list[1],
        }

    # Draw.

    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a candlestick plot using the Plotly API.
        """
        fig_base = self._get_fig(fig)
        fig_base.add_trace(
            go.Candlestick(
                x=self.data["x"],
                low=self.data["Y"][:, 0],
                open=self.data["Y"][:, 2],
                close=self.data["Y"][:, 1],
                high=self.data["Y"][:, 3],
                **self._color_style(style_kwargs),
            )
        )
        fig_base.update_layout(
            **style_kwargs,
        )
        fig_base.update_layout(**self._update_dict(self.init_style, style_kwargs))
        return fig_base
