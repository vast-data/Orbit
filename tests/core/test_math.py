"""
SPDX-License-Identifier: Apache-2.0

Column-level math: apply, abs, round and arithmetic-derived columns.
"""

from tests.helpers import cols_lower


def test_abs(titanic):
    vd = titanic.copy()
    vd["age"].abs()
    assert vd is not None


def test_round(titanic):
    vd = titanic.copy()
    vd["fare"].round(1)
    assert vd is not None


def test_apply(titanic):
    vd = titanic.copy()
    vd["age"].apply("{} + 1")
    assert vd is not None


def test_apply_fun(titanic):
    vd = titanic.copy()
    vd["fare"].apply_fun("log")
    assert vd is not None


def test_derived_column(titanic):
    vd = titanic.copy()
    vd["family"] = "sibsp + parch"
    assert "family" in cols_lower(vd)
    assert vd["family"].max() is not None
