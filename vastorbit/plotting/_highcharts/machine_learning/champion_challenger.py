"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

import numpy as np

from vastorbit._typing import HChart
from vastorbit.plotting._highcharts.base import HighchartsBase


class ChampionChallengerPlot(HighchartsBase):
    # Properties.

    @property
    def _category(self) -> Literal["plot"]:
        return "plot"

    @property
    def _kind(self) -> Literal["champion"]:
        return "champion"

    # Styling Methods.

    def _init_style(self) -> None:
        self.init_style = {
            "title": {"text": ""},
            "xAxis": {
                "reversed": self.layout["reverse"][0],
                "title": {"enabled": True, "text": self.layout["x_label"]},
                "startOnTick": True,
                "endOnTick": True,
                "showLastLabel": True,
            },
            "yAxis": {
                "reversed": self.layout["reverse"][1],
                "title": {"text": self.layout["y_label"]},
            },
            "legend": {"enabled": True},
            "plotOptions": {
                "scatter": {
                    "marker": {
                        "radius": 5,
                        "states": {
                            "hover": {"enabled": True, "lineColor": "rgb(100,100,100)"}
                        },
                    },
                    "states": {"hover": {"marker": {"enabled": False}}},
                }
            },
            "tooltip": {
                "headerFormat": '<span style="color:{series.color}">\u25cf</span> {series.name} <br/>',
                "pointFormat": "<b>"
                + str(self.layout["x_label"])
                + "</b>: {point.x}<br><b>"
                + str(self.layout["y_label"])
                + "</b>: {point.y}<br>"
                + str(self.layout["z_label"])
                + "</b>: {point.z}<br>",
            },
            "colors": self.get_colors(),
        }

    # Draw.

    def draw(self, chart: Optional[HChart] = None, **style_kwargs) -> HChart:
        """
        Draws a champion challenger plot using the HC API.
        """
        chart, style_kwargs = self._get_chart(chart, style_kwargs=style_kwargs)
        chart.set_dict_options(self.init_style)
        chart.set_dict_options(style_kwargs)
        uniques = np.unique(self.data["c"])
        for c in uniques:
            x = self.data["x"][self.data["c"] == c]
            y = self.data["y"][self.data["c"] == c]
            s = self.data["s"][self.data["c"] == c]
            data = np.column_stack((x, y, s)).tolist()
            chart.add_data_set(data, "bubble", c)
        return chart
