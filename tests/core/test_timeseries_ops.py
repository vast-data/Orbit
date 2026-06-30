"""
SPDX-License-Identifier: Apache-2.0

Time-aware operations needing a real timestamp column.
"""

import pandas as pd
import pytest

import vastorbit as vo
from tests.helpers import cols_lower


@pytest.fixture(scope="module")
def ts_vd():
    pdf = pd.DataFrame(
        {
            "ts": pd.date_range("2023-01-01", periods=24, freq="h"),
            "uid": [1, 2] * 12,
            "value": [float(i) for i in range(24)],
        }
    )
    return vo.read_pandas(pdf)


def test_date_part(ts_vd):
    vd = ts_vd.copy()
    vd["ts"].date_part("hour")
    assert vd is not None


def test_sessionize(ts_vd):
    vd = ts_vd.copy().sessionize("ts", by=["uid"], session_threshold="2 hours")
    assert "session_id" in cols_lower(vd)


def test_interpolate(ts_vd):
    vd = ts_vd.copy().interpolate(
        "ts", rule="1 hour", method={"value": "linear"}, by=["uid"]
    )
    assert vd is not None
