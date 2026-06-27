"""
SPDX-License-Identifier: Apache-2.0

Rolling-window features.
"""

import vastorbit as vo
from tests.helpers import trend_series, cols_lower


def test_rolling_mean():
    vd = vo.VastFrame(trend_series(30))
    vd.rolling("avg", (-2, 0), "value", order_by=["month"], name="roll_avg")
    assert "roll_avg" in cols_lower(vd)
