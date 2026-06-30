"""
SPDX-License-Identifier: Apache-2.0

Geo SQL helpers.
"""

from vastorbit.sql.geo.functions import coordinate_converter


def test_coordinate_converter(name_factory):
    import vastorbit as vo

    vd = vo.VastFrame({"x": [10.0, 20.0], "y": [30.0, 40.0]})
    out = coordinate_converter(vd, "x", "y")
    assert out is not None
