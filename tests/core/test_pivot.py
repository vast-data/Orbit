"""
SPDX-License-Identifier: Apache-2.0

Pivot tables.
"""


def test_pivot_table_count(titanic):
    res = titanic.pivot_table(["pclass", "sex"], method="count")
    assert res is not None


def test_pivot_table_avg(titanic):
    res = titanic.pivot_table(["pclass"], method="avg", of="age")
    assert res is not None
