"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

from matplotlib.axes import Axes
import matplotlib.patches as mpatches

from vastorbit.plotting._matplotlib.base import MatplotlibBase


class ImportanceBarChart(MatplotlibBase):
    # Properties.

    @property
    def _category(self) -> Literal["chart"]:
        return "chart"

    @property
    def _kind(self) -> Literal["importance"]:
        return "importance"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {"alpha": 0.86}

    # Draw.

    def draw(
        self,
        ax: Optional[Axes] = None,
        **style_kwargs,
    ) -> Axes:
        """
        Draws a coefficient importance bar chart using the Matplotlib API.
        """
        n = len(self.data["importance"])
        x_label = (
            self.layout["x_label"] if "x_label" in self.layout else "Importance (%)"
        )
        y_label = self.layout["y_label"] if "y_label" in self.layout else "Features"
        ax, _fig, style_kwargs = self._get_ax_fig(
            ax,
            size=(12, int(n / 2) + 1),
            set_axis_below=True,
            grid=True,
            style_kwargs=style_kwargs,
        )
        plus = self.get_colors(d=style_kwargs, idx=0)
        minus = self.get_colors(d=style_kwargs, idx=1)
        style_kwargs = self._update_dict(self.init_style, style_kwargs)
        style_kwargs["color"] = [
            self.get_colors(d=style_kwargs, idx={-1: 1, 0: 0, 1: 0}[int(i)])
            for i in self.data["signs"]
        ]
        ax.barh(range(0, n), self.data["importance"], 0.9, **style_kwargs)
        if len(self.data["signs"][self.data["signs"] == -1]) != 0:
            color_plus = mpatches.Patch(color=plus, label="sign +")
            color_minus = mpatches.Patch(color=minus, label="sign -")
            ax.legend(
                handles=[color_plus, color_minus],
                loc="center left",
                bbox_to_anchor=[1, 0.5],
            )
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_yticks(range(0, n))
        ax.set_yticklabels(self.layout["columns"])
        return ax
