"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import plotly.graph_objects as go
from plotly.graph_objs._figure import Figure

from vastorbit.plotting._plotly.base import PlotlyBase


class RegressionPlot(PlotlyBase):
    # Properties.

    @property
    def _category(self) -> Literal["plot"]:
        return "plot"

    @property
    def _kind(self) -> Literal["regression"]:
        return "regression"

    @property
    def _compute_method(self) -> Literal["sample"]:
        return "sample"

    @property
    def _dimension_bounds(self) -> tuple[int, int]:
        return (2, 3)

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {
            "mode": "markers",
            "marker_line_width": 2,
            "marker_size": 10,
            "marker_line_color": "black",
        }
        self.init_layout_style = {
            "yaxis_title": self.layout["columns"][1],
            "xaxis_title": self.layout["columns"][0],
            "width": 700,
            "height": 600,
        }

    # Draw.

    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a regression plot using the Plotly API.
        """
        fig = self._get_fig(fig)
        x = self.data["X"][:, 0]
        y = self.data["X"][:, 1]
        min_reg_x, max_reg_x = min(x), max(x)
        y0 = self.data["coef"][0]
        slope = self.data["coef"][1]
        if len(self.layout["columns"]) == 2:
            fig = fig.add_trace(
                go.Scatter(x=x, y=y, **self.init_style, name="Scatter Points")
            )
            fig.add_trace(
                go.Scatter(
                    x=[min_reg_x, max_reg_x],
                    y=[y0 + slope * min_reg_x, y0 + slope * max_reg_x],
                    mode="lines",
                    line_shape="linear",
                    name="Regression Line",
                )
            )
            fig.update_layout(**self._update_dict(self.init_layout_style, style_kwargs))
        else:
            raise ValueError("The number of predictors is too big to draw the plot.")
        return fig
