"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from plotly.graph_objs._figure import Figure
from plotly.subplots import make_subplots

from vastorbit._typing import NoneType


def draw_subplots(
    figs: list[Figure],
    subplot_titles: list[str],
    rows: int,
    cols: int,
    kind: str,
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> Figure:
    """
    Draws multiple subplot
    in the same Figure.
    """
    if isinstance(height, NoneType):
        height = 600 + 133 * rows
    if isinstance(width, NoneType):
        width = 800 + 200 * cols
    param = {}
    if kind == "pie":
        param = {"specs": [[{"type": "pie"} for i in range(rows)] for j in range(cols)]}
    n, k = len(figs), len(subplot_titles)
    titles = [t for t in subplot_titles] + ["" for i in range(n - k)]
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles, **param)
    for i in range(1, cols + 1):
        for j in range(1, rows + 1):
            k = (i - 1) * 3 + j - 1
            if k < n:
                fig_tmp = figs[(i - 1) * 3 + j - 1]
                if kind == "pie":
                    fig.add_trace(fig_tmp.data[0], row=i, col=j)
                else:
                    for trace in fig_tmp.data:
                        fig.add_trace(trace, row=i, col=j)
    fig.update_layout(height=height, width=width, margin=dict(l=120, r=120, b=60, t=60))
    return fig
