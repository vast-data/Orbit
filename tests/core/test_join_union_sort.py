"""
SPDX-License-Identifier: Apache-2.0

Joins, unions (append) and sorting.
"""

import vastorbit as vo


def test_sort(titanic):
    s = titanic.copy().sort({"age": "asc"})
    assert s.shape()[0] == titanic.shape()[0]


def test_append(titanic):
    head = titanic.copy().head(10).to_vdf()
    combined = head.append(titanic.copy().head(5).to_vdf())
    assert combined.shape()[0] == 15


def test_join():
    left = vo.VastFrame({"k": [1, 2, 3], "lv": ["a", "b", "c"]})
    right = vo.VastFrame({"k": [1, 2, 3], "rv": ["x", "y", "z"]})
    joined = left.join(right, on={"k": "k"}, how="inner", expr1=["lv"], expr2=["rv"])
    assert joined.shape()[0] == 3
