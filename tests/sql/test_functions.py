"""
SPDX-License-Identifier: Apache-2.0

SQL function builders applied to VastFrame columns.
"""

import vastorbit as vo
from vastorbit.sql.functions.math import sqrt, ln, exp
from vastorbit.sql.functions.string import length, upper, lower
from tests.helpers import cols_lower


def test_math_functions():
    vd = vo.VastFrame({"x": [1.0, 4.0, 9.0]})
    vd["root"] = sqrt(vd["x"])
    vd["logn"] = ln(vd["x"])
    vd["e"] = exp(vd["x"])
    for c in ("root", "logn", "e"):
        assert c in cols_lower(vd)
    assert abs(vd["root"].max() - 3.0) < 1e-6


def test_string_functions():
    vd = vo.VastFrame({"s": ["abc", "de", "f"]})
    vd["len_s"] = length(vd["s"])
    vd["up"] = upper(vd["s"])
    vd["lo"] = lower(vd["s"])
    assert vd["len_s"].max() == 3
    for c in ("up", "lo"):
        assert c in cols_lower(vd)
