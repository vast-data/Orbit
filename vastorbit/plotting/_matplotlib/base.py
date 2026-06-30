"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
from typing import Optional, Union

from matplotlib.axes import Axes
from matplotlib.pyplot import Figure
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from PIL import Image
import base64
from io import BytesIO

import vastorbit._config.config as conf
from vastorbit._utils._logo import vast_logo_png
from vastorbit._utils._sql._format import format_type
from vastorbit._typing import ArrayLike

from vastorbit.plotting.base import PlottingBase


class MatplotlibBase(PlottingBase):
    @staticmethod
    def _get_ax_fig(
        ax,
        size: tuple[int, int] = (8, 6),
        set_axis_below: bool = True,
        grid: Union[str, bool] = True,
        dim: int = 2,
        style_kwargs: Optional[dict] = None,
    ) -> tuple[Axes, Figure]:
        theme = conf.get_option("theme")
        style_kwargs = format_type(style_kwargs, dtype=dict)
        kwargs = copy.deepcopy(style_kwargs)
        if "figsize" in kwargs and isinstance(kwargs, tuple):
            size = kwargs["figsize"]
            del kwargs["size"]
        if "width" in kwargs:
            size = (kwargs["width"], size[1])
            del kwargs["width"]
        if "height" in kwargs:
            size = (size[0], kwargs["height"])
            del kwargs["height"]
        if not ax and dim == 3:
            if conf.get_import_success("IPython"):
                plt.figure(figsize=size)
            ax = plt.axes(projection="3d")
            fig = plt
        elif not ax:
            fig, ax = plt.subplots()
            if conf.get_import_success("IPython"):
                fig.set_size_inches(*size)
            if grid:
                if grid in ("x", "y"):
                    ax.grid(axis=grid)
                else:
                    ax.grid()
            ax.set_axisbelow(set_axis_below)
            if theme == "sphinx":
                fig.patch.set_alpha(0.0)
                ax.set_facecolor("none")
                plt.title("", color="#888888")
                plt.xlabel("", color="#888888")
                plt.ylabel("", color="#888888")
                plt.xticks(color="#888888")
                plt.yticks(color="#888888")
            elif theme == "dark":
                # VAST navy ramp — figure on navy-1, axes panel on navy-2
                fig.patch.set_facecolor("#03142C")
                ax.set_facecolor("#0A2240")
                ax.grid(color="#1B3A5C", linewidth=0.8)
                for spine in ax.spines.values():
                    spine.set_color("#1B3A5C")
                ax.tick_params(colors="#9FB3C8")
                plt.title("", color="#E8EFF7")
                plt.xlabel("", color="#9FB3C8")
                plt.ylabel("", color="#9FB3C8")
                plt.xticks(color="#9FB3C8")
                plt.yticks(color="#9FB3C8")
            elif theme == "light":
                ...
        else:
            fig = plt

        # LOGO

        # Get logo from base64 string
        logo_base64 = vast_logo_png()
        if logo_base64.startswith("data:"):
            logo_base64 = logo_base64.split(",")[1]

        logo_bytes = base64.b64decode(logo_base64)
        logo = Image.open(BytesIO(logo_bytes))

        # Crop transparent padding to get actual logo bounds
        # This removes extra whitespace that might offset centering
        bbox = logo.getbbox()  # Get bounding box of non-transparent pixels
        if bbox:
            logo = logo.crop(bbox)

        # Add logo centered below the text
        imagebox = OffsetImage(logo, zoom=0.06, alpha=0.7)  # Bit smaller
        ab = AnnotationBbox(
            imagebox,
            xy=(0.5, 0.03),  # Below the text
            xycoords="figure fraction",
            frameon=False,
            box_alignment=(0.5, 0.5),
        )
        try:
            fig.add_artist(ab)
            # Text centered below the graphic
            fig.text(
                0.5,
                0.04,  # Higher position for text
                "This chart was generated with VAST Orbit by VAST Data",
                ha="center",
                va="bottom",
                fontsize=7,  # Bit bigger
                color="gray",
                alpha=0.7,
            )
        except Exception:
            pass

        # Adjust layout to make room

        if size[1] < 3:
            bottoms = 0.4
        elif size[1] < 6:
            bottoms = 0.33
        elif size[1] < 9:
            bottoms = 0.17
        else:
            bottoms = 0.12

        plt.subplots_adjust(bottom=bottoms)

        return ax, fig, kwargs

    @staticmethod
    def _get_matrix_fig_size(
        n: int,
    ) -> tuple[int, int]:
        if conf.get_import_success("IPython"):
            return min(1.5 * (n + 1), 500), min(1.5 * (n + 1), 500)
        else:
            return min(int((n + 1) / 1.1), 500), min(int((n + 1) / 1.1), 500)

    @staticmethod
    def _format_string(x: ArrayLike, th: int = 50) -> ArrayLike:
        res = copy.deepcopy(x)
        if isinstance(x[0], str):
            n = len(res)
            for i in range(n):
                if len(str(res[i])) > th:
                    res[i] = str(res[i][: th - 3]) + "..."
        return res
