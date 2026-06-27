"""
SPDX-License-Identifier: Apache-2.0

Aggregations and grouping.
"""


def test_describe(titanic):
    assert titanic.describe() is not None


def test_column_aggregations(titanic):
    assert titanic["age"].count() > 0
    assert titanic["age"].max() >= titanic["age"].min()
    assert titanic["age"].mean() is not None
    assert titanic["fare"].sum() is not None
    assert titanic["age"].std() is not None


def test_frame_aggregate(titanic):
    res = titanic.aggregate(func=["min", "max", "avg"], columns=["age", "fare"])
    assert res is not None


def test_groupby(titanic):
    g = titanic.groupby(["pclass"], ["AVG(age) AS avg_age", "COUNT(*) AS n"])
    assert g.shape()[0] >= 1


def test_count_distinct(titanic):
    assert titanic["pclass"].nunique() >= 1
