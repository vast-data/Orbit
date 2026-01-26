"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
from typing import Literal, Optional

from vastorbit._typing import HChart
from vastorbit.plotting._highcharts.base import HighchartsBase


class ImportanceBarChart(HighchartsBase):
    # Properties.

    @property
    def _category(self) -> Literal["chart"]:
        return "chart"

    @property
    def _kind(self) -> Literal["importance"]:
        return "importance"

    # Styling Methods.

    def _init_style(self) -> None:
        legend = len(self.data["signs"][self.data["signs"] == -1]) != 0
        self.init_style = {
            "title": {"text": ""},
            "chart": {"type": "column", "inverted": True},
            "xAxis": {"type": "category"},
            "legend": {"enabled": legend},
            "xAxis": {
                "title": {
                    "text": (
                        self.layout["y_label"]
                        if "y_label" in self.layout
                        else "Features"
                    )
                },
                "categories": self.layout["columns"],
            },
            "yAxis": {
                "title": {
                    "text": (
                        self.layout["x_label"]
                        if "x_label" in self.layout
                        else "Importance (%)"
                    )
                }
            },
            "tooltip": {"headerFormat": "", "pointFormat": "{point.y}%"},
            "plotOptions": {"series": {"stacking": "normal"}},
            "colors": self.get_colors(),
        }

    # Draw.

    def draw(
        self,
        chart: Optional[HChart] = None,
        **style_kwargs,
    ) -> HChart:
        """
        Draws a coefficient importance bar chart using the HC API.
        """
        chart, style_kwargs = self._get_chart(chart, style_kwargs=style_kwargs)
        chart.set_dict_options(self.init_style)
        chart.set_dict_options(style_kwargs)
        importances_pos = copy.deepcopy(self.data["importance"])
        importances_pos[self.data["signs"] == -1] = 0.0
        importances_pos = importances_pos.tolist()
        importances_neg = copy.deepcopy(self.data["importance"])
        importances_neg[self.data["signs"] == 1] = 0.0
        importances_neg = importances_neg.tolist()
        chart.add_data_set(importances_pos, "bar", name="+1")
        chart.add_data_set(importances_neg, "bar", name="-1")
        return chart
