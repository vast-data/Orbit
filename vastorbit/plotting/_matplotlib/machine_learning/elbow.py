"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

from matplotlib.axes import Axes

from vastorbit.plotting._matplotlib.base import MatplotlibBase


class ElbowCurve(MatplotlibBase):
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
            "color": self.get_colors(idx=0),
            "marker": "o",
            "markerfacecolor": "white",
            "markersize": 7,
            "markeredgecolor": "black",
        }

    # Draw.

    def draw(
        self,
        ax: Optional[Axes] = None,
        **style_kwargs,
    ) -> Axes:
        """
        Draws a machine learning bubble plot using the Matplotlib API.
        """
        ax, _fig, style_kwargs = self._get_ax_fig(
            ax, size=(8, 6), set_axis_below=False, grid="y", style_kwargs=style_kwargs
        )
        ax.plot(
            self.data["x"],
            self.data["y"],
            **self._update_dict(self.init_style, style_kwargs),
        )
        ax.set_title(self.layout["title"])
        ax.set_xlabel(self.layout["x_label"])
        ax.set_ylabel(self.layout["y_label"])
        return ax
