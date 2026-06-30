"""
SPDX-License-Identifier: Apache-2.0

Datasets Generators.
"""

from vastorbit.datasets.generators import gen_meshgrid


def test_gen_meshgrid():
    res = gen_meshgrid(
        {"x": {"type": int, "range": [0, 10]}, "y": {"type": int, "range": [0, 10]}}
    )
    assert res is not None
