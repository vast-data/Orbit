"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import numpy as np

from vastorbit._typing import HChart
from vastorbit.plotting._highcharts.base import HighchartsBase


class ElbowCurve(HighchartsBase):
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
            "title": {"text": self.layout["title"]},
            "xAxis": {
                "reversed": False,
                "title": {"enabled": True, "text": self.layout["x_label"]},
                "startOnTick": True,
                "endOnTick": True,
                "showLastLabel": True,
                "min": int(self.data["x"][0]),
                "max": int(self.data["x"][-1]),
            },
            "yAxis": {
                "title": {"text": self.layout["y_label"]},
                "min": 0.0,
                "max": 1.0,
            },
            "legend": {"enabled": False},
            "tooltip": {
                "headerFormat": "",
                "pointFormat": "[{point.x}, {point.y}]",
            },
            "colors": self.get_colors(),
        }

    # Draw.

    def draw(
        self,
        chart: Optional[HChart] = None,
        **style_kwargs,
    ) -> HChart:
        """
        Draws a machine learning ROC curve using the HC API.
        """
        chart, style_kwargs = self._get_chart(chart, style_kwargs=style_kwargs)
        chart.set_dict_options(self.init_style)
        chart.set_dict_options(style_kwargs)
        data = np.column_stack((self.data["x"], self.data["y"])).tolist()
        chart.add_data_set(data, "spline", self.layout["y_label"])
        return chart
