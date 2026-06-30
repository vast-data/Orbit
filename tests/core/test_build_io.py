"""
SPDX-License-Identifier: Apache-2.0

Construction and I/O: build from dict / pandas, head, copy, to_pandas, to_db.
"""

import pandas as pd

import vastorbit as vo
from tests.helpers import cols_lower


def test_build_from_dict():
    vd = vo.VastFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    assert sorted(cols_lower(vd)) == ["a", "b"]
    assert vd.shape() == (3, 2)


def test_build_from_pandas():
    pdf = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": ["a", "b", "c"]})
    vd = vo.read_pandas(pdf)
    assert vd.shape()[0] == 3


def test_head(titanic):
    assert titanic.head(5).shape()[1] == 5  # TableSample.shape() is (cols, rows)


def test_copy_is_independent(titanic):
    vd = titanic.copy()
    vd["tmp"] = "1"
    assert "tmp" in cols_lower(vd)
    assert "tmp" not in cols_lower(titanic)


def test_to_pandas(iris):
    pdf = iris.head(10).to_pandas()
    assert isinstance(pdf, pd.DataFrame)
    assert len(pdf) == 10


def test_to_db_round_trip(titanic, name_factory):
    tbl = name_factory("io_table")
    # use well-typed numeric columns (avoid all-NULL cols like ``cabin`` whose
    # type can't be inferred when round-tripped through a TableSample)
    sub = titanic[["pclass", "age", "fare", "survived"]].dropna()
    n = sub.shape()[0]
    sub.to_db(tbl)
    assert vo.VastFrame(tbl).shape()[0] == n
