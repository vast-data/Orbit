"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

# --- VAST brand Plotly templates (brand.vastdata.com) ------------------------
_VAST_COLORWAY = [
    "#1FD9FE",
    "#29B8FF",
    "#0E86B8",
    "#5BE49B",
    "#F5A623",
    "#9FB3C8",
    "#7B8CFF",
    "#E5484D",
]
_VAST_FONT = "Moderat, Inter, Helvetica Neue, Arial, sans-serif"
_vast_templates_registered = False


def _register_vast_templates() -> None:
    """Register the VAST brand Plotly templates once per session."""
    global _vast_templates_registered
    if _vast_templates_registered:
        return
    base = dict(
        colorway=_VAST_COLORWAY,
        colorscale=dict(
            sequential=[[0, "#03142C"], [0.5, "#0E86B8"], [1, "#1FD9FE"]],
            diverging=[[0, "#E5484D"], [0.5, "#F2F2F7"], [1, "#1FD9FE"]],
        ),
    )
    pio.templates["vast_dark"] = go.layout.Template(
        layout=dict(
            **base,
            paper_bgcolor="#03142C",
            plot_bgcolor="#0A2240",
            font=dict(family=_VAST_FONT, color="#E8EFF7"),
            xaxis=dict(
                gridcolor="#1B3A5C",
                linecolor="#1B3A5C",
                zerolinecolor="#1B3A5C",
                tickcolor="#1B3A5C",
            ),
            yaxis=dict(
                gridcolor="#1B3A5C",
                linecolor="#1B3A5C",
                zerolinecolor="#1B3A5C",
                tickcolor="#1B3A5C",
            ),
            legend=dict(font=dict(color="#E8EFF7")),
            hoverlabel=dict(
                bgcolor="#0A2240", bordercolor="#1FD9FE", font=dict(color="#E8EFF7")
            ),
        )
    )
    pio.templates["vast_light"] = go.layout.Template(
        layout=dict(
            **base,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(family=_VAST_FONT, color="#03142C"),
            xaxis=dict(
                gridcolor="#E7EBF1",
                linecolor="#C7CBD4",
                zerolinecolor="#E7EBF1",
                tickcolor="#C7CBD4",
            ),
            yaxis=dict(
                gridcolor="#E7EBF1",
                linecolor="#C7CBD4",
                zerolinecolor="#E7EBF1",
                tickcolor="#C7CBD4",
            ),
            hoverlabel=dict(
                bgcolor="#FFFFFF", bordercolor="#1FD9FE", font=dict(color="#03142C")
            ),
        )
    )
    # transparent for embedding into the docs (page supplies the surface)
    pio.templates["vast_sphinx"] = go.layout.Template(
        layout=dict(
            **base,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family=_VAST_FONT, color="#888888"),
            xaxis=dict(gridcolor="rgba(136,136,136,0.25)"),
            yaxis=dict(gridcolor="rgba(136,136,136,0.25)"),
        )
    )
    _vast_templates_registered = True


from plotly.graph_objs._figure import Figure
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

import vastorbit._config.config as conf
from vastorbit.plotting.base import PlottingBase
from vastorbit._utils._logo import vast_logo_png
from vastorbit._typing import ArrayLike


class PlotlyBase(PlottingBase):
    """
    Plotly Base Class.
    """

    # Convert

    @staticmethod
    def _convert_labels_and_get_counts(
        pivot_array: ArrayLike,
        method: Optional[str] = None,
    ) -> tuple[list, list, list, list]:
        pivot_array = np.where(pivot_array == None, "NULL", pivot_array)
        pivot_array = pivot_array.astype("<U21")
        pivot_array = pivot_array.astype(str)
        pivot_array[1:-1, :] = np.char.add(pivot_array[1:-1, :], "__")
        if pivot_array.shape[0] > 3:
            pivot_array[1:-1, :] = np.char.add(
                np.char.add(pivot_array[1:-1, :], pivot_array[:-2, :]),
                pivot_array[:-3, :],
            )
        else:
            pivot_array[1:-1, :] = np.char.add(
                pivot_array[1:-1, :], pivot_array[:-2, :]
            )
        labels_count = {}
        labels_father = {}
        for j in range(pivot_array.shape[0] - 1):
            for i in range(len(pivot_array[0])):
                current_label = pivot_array[-2][i]
                if current_label not in labels_count:
                    labels_count[current_label] = 0
                if method == "min":
                    labels_count[current_label] = min(
                        labels_count[current_label], float(pivot_array[-1][i])
                    )
                elif method == "max":
                    labels_count[current_label] = max(
                        labels_count[current_label], float(pivot_array[-1][i])
                    )
                elif method == "max":
                    labels_count[current_label] = max(
                        labels_count[current_label], float(pivot_array[-1][i])
                    )
                elif method == "count":
                    labels_count[current_label] += int(pivot_array[-1][i])
                elif method == "mean":
                    labels_count[current_label] += (
                        float(pivot_array[-1][i]) / pivot_array.shape[0]
                    )
                else:
                    labels_count[current_label] += float(pivot_array[-1][i])

                if pivot_array.shape[0] > 2:
                    labels_father[current_label] = pivot_array[-3][i]
                else:
                    labels_father[current_label] = ""
            pivot_array = np.delete(pivot_array, -2, axis=0)
        labels = [s.split("__")[0] for s in list(labels_father.keys())]
        ids = list(labels_count.keys())
        parents = list(labels_father.values())
        values = list(labels_count.values())
        return ids, labels, parents, values

    @staticmethod
    def _convert_labels_for_heatmap(lst: list) -> list:
        result = []
        for item in lst:
            # Remove the brackets and split the string by semicolon
            values = item[1:-1].split(";")
            # Convert the values to floating-point numbers and take their average
            avg = str(round((float(values[0]) + float(values[1])) / 2, 2))
            # Append the average to the result list
            result.append(avg)
        return result

    # Get

    def _get_fig(
        self, fig: Optional[Figure] = None, data: Optional[dict] = None
    ) -> Figure:
        theme = conf.get_option("theme")
        pio.templates.default = self._get_theme()
        if data:
            res = go.Figure(data)
        elif fig:
            res = fig
        else:
            res = go.Figure()
        if theme == "sphinx":
            res.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict({"color": "#888888"}),
            )
        return res

    @staticmethod
    def _get_theme() -> str:
        theme = conf.get_option("theme")
        _register_vast_templates()
        if theme == "dark":
            return "vast_dark"
        elif theme == "light":
            return "vast_light"
        elif theme == "sphinx":
            return "vast_sphinx"
        return "vast_sphinx"

    @staticmethod
    def _get_max_decimal_point(arr: ArrayLike) -> int:
        max_decimals = 0
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if isinstance(arr[i][j], float):
                    string_repr = str(arr[i][j])
                    num_decimals = (
                        len(string_repr.split(".")[-1])
                        if len(string_repr.split(".")) > 1
                        else 0
                    )
                    max_decimals = max(max_decimals, num_decimals)
        return max_decimals

    @staticmethod
    def _update_dict(
        d1: dict,
        d2: dict,
        color_idx: int = 0,
        method: Literal["layout", "no_layout", None] = None,
    ) -> dict:
        """
        Updates the input dictionary using another one.
        """
        d = PlottingBase._update_dict(d1=d1, d2=d2, color_idx=color_idx)
        if method == "layout":
            d = {}

        # LOGO
        if method != "no_layout":
            if "width" in d:
                sizex_paper = 100 / d["width"]
            else:
                sizex_paper = 0.2
            if "height" in d:
                sizey_paper = 100 / d["height"]
            else:
                sizey_paper = 0.2
            d["annotations"] = [
                dict(
                    x=0.5,  # Center horizontally
                    y=-0.2,  # Below the chart
                    showarrow=False,
                    text="This chart was generated with VAST Orbit by VAST Data",
                    xanchor="center",  # Anchor text to center
                    yanchor="top",  # Anchor to top of text (so it sits below chart)
                    xref="paper",
                    yref="paper",
                    font=dict(size=8, color="gray"),
                    opacity=0.8,
                )
            ]
            d["margin"] = dict(
                b=120, t=50, l=50, r=50
            )  # Extra bottom margin for the logo height
            d["images"] = [
                dict(
                    source=vast_logo_png(),
                    xref="paper",
                    yref="paper",
                    x=0.5,  # Center horizontally (same as text)
                    y=-0.25,  # Below the text
                    sizex=0.8 * sizex_paper,
                    sizey=0.8 * sizey_paper,
                    sizing="contain",
                    xanchor="center",  # Center the logo
                    yanchor="top",  # Logo sits below the text
                    opacity=0.8,
                )
            ]
        return d
