"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import numpy as np

from matplotlib.axes import Axes

from vastorbit.plotting._matplotlib.base import MatplotlibBase

import matplotlib

# matplotlib renamed ``boxplot``'s ``labels`` argument to ``tick_labels`` in
# 3.9 and removed ``labels`` in 3.11. Pick the spelling the installed version
# accepts so the call works across supported matplotlib releases.
try:
    _MPL_MAJOR_MINOR = tuple(
        int(part) for part in matplotlib.__version__.split(".")[:2]
    )
except ValueError:
    _MPL_MAJOR_MINOR = (3, 9)
_BOXPLOT_LABELS_KW = "tick_labels" if _MPL_MAJOR_MINOR >= (3, 9) else "labels"
# matplotlib deprecated boxplot's boolean ``vert`` argument in 3.10 in favour of
# ``orientation`` ("vertical"/"horizontal"). Pass whichever the installed version
# expects so no PendingDeprecationWarning is emitted.
_BOXPLOT_USE_ORIENTATION = _MPL_MAJOR_MINOR >= (3, 10)


class BoxPlot(MatplotlibBase):
    # Properties.

    @property
    def _category(self) -> Literal["plot"]:
        return "plot"

    @property
    def _kind(self) -> Literal["box"]:
        return "box"

    @property
    def _compute_method(self) -> Literal["describe"]:
        return "describe"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {"widths": 0.3}

    # Draw.

    def draw(
        self,
        ax: Optional[Axes] = None,
        **style_kwargs,
    ) -> Axes:
        """
        Draws a multi-box plot using the Matplotlib API.
        """
        style_kwargs = self._fix_color_style_kwargs(style_kwargs)
        m = self.data["X"].shape[1]
        if m == 1 and "vert" not in style_kwargs:
            style_kwargs["vert"] = False
        elif "vert" not in style_kwargs:
            style_kwargs["vert"] = True
        ax, _fig, style_kwargs = self._get_ax_fig(
            ax,
            size=(10, 6),
            set_axis_below=True,
            grid="y" if style_kwargs["vert"] else "x",
            style_kwargs=style_kwargs,
        )
        if style_kwargs["vert"]:
            set_lim = ax.set_ylim
            set_tick = ax.set_xticklabels
        else:
            set_lim = ax.set_xlim
            set_tick = ax.set_yticklabels
        if _BOXPLOT_USE_ORIENTATION:
            orientation_kw = {
                "orientation": "vertical" if style_kwargs["vert"] else "horizontal"
            }
        else:
            orientation_kw = {"vert": style_kwargs["vert"]}
        box = ax.boxplot(
            self.data["X"],
            notch=False,
            patch_artist=True,
            **orientation_kw,
            **{_BOXPLOT_LABELS_KW: self.layout["labels"]},
            **self.init_style,
            **{
                key: value
                for key, value in style_kwargs.items()
                if key not in ("color", "vert")
            },
        )
        set_tick(self.layout["labels"], rotation=90)
        for median in box["medians"]:
            median.set(
                color="black",
                linewidth=1,
            )
        for i, patch in enumerate(box["boxes"]):
            patch.set_facecolor(self.get_colors(d=style_kwargs, idx=i))
        for i, flier in enumerate(box["fliers"]):
            xdata = [i + 1] * len(self.data["fliers"][i])
            ydata = self.data["fliers"][i]
            if style_kwargs["vert"]:
                kwargs = {"xdata": xdata, "ydata": ydata}
            else:
                kwargs = {"xdata": ydata, "ydata": xdata}
            flier.set(**kwargs)
        if self.layout["has_category"]:
            if not style_kwargs["vert"]:
                x_label, y_label = self.layout["y_label"], self.layout["x_label"]
            else:
                x_label, y_label = self.layout["x_label"], self.layout["y_label"]
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
        min_lim = min(
            min(min(f) if len(f) > 0 else np.inf for f in self.data["fliers"]),
            self.data["X"].min(),
        )
        max_lim = max(
            max(max(f) if len(f) > 0 else -np.inf for f in self.data["fliers"]),
            self.data["X"].max(),
        )
        h = (max_lim - min_lim) * 0.01
        set_lim(min_lim - h, max_lim + h)
        return ax
