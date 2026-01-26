"""
SPDX-License-Identifier: Apache-2.0
"""

import copy

from typing import Literal, Optional

import plotly.graph_objects as go
from plotly.graph_objs._figure import Figure

from vastorbit.plotting._plotly.base import PlotlyBase


class ImportanceBarChart(PlotlyBase):
    # Properties.

    @property
    def _category(self) -> Literal["chart"]:
        return "chart"

    @property
    def _kind(self) -> Literal["importance"]:
        return "importance"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_layout_style = {
            "yaxis_title": (
                self.layout["y_label"] if "xylabel" in self.layout else "Features"
            ),
            "xaxis": dict(
                title=self.layout["x_label"] if "x_label" in self.layout else "Importance (%)",
                side="top",  # Position axis on top (optional)
                title_standoff=25
            ),
            "margin": dict(l=200, r=200, t=100, b=100),
            "barmode": "stack",
            "yaxis": {"categoryorder": "total descending"},
        }

    # Draw.

    def draw(
        self,
        fig: Optional[Figure] = None,
        **style_kwargs,
    ) -> Figure:
        """
        Draws a coefficient importance bar chart using the Plotly API.
        """
        fig = self._get_fig(fig)
        importances_pos = copy.deepcopy(self.data["importance"])
        importances_pos[self.data["signs"] == -1] = 0.0
        importances_pos = importances_pos.tolist()
        importances_neg = copy.deepcopy(self.data["importance"])
        importances_neg[self.data["signs"] == 1] = 0.0
        importances_neg = importances_neg.tolist()
        fig.add_trace(
            go.Bar(
                x=importances_pos,
                y=self.layout["columns"],
                orientation="h",
                name="Positive",
                marker=dict(
                    color=self.get_colors()[0],
                ),
            )
        )
        showlegend = False
        if len(self.data["signs"][self.data["signs"] == -1]) != 0:
            fig.add_trace(
                go.Bar(
                    x=importances_neg,
                    y=self.layout["columns"],
                    orientation="h",
                    name="Negative",
                    marker=dict(
                        color=self.get_colors()[1],
                    ),
                )
            )
            showlegend = True
        fig.update_layout(
            showlegend=showlegend,
            **self._update_dict(self.init_layout_style, style_kwargs),
        )
        return fig
