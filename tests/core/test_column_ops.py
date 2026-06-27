"""
SPDX-License-Identifier: Apache-2.0

Column-level operations: discretize, decode, dummies, cut, topk, value_counts.
"""

from tests.helpers import cols_lower


def test_discretize(titanic):
    vd = titanic.copy()
    vd["age"].discretize(method="same_width", nbins=5)
    assert vd is not None


def test_cut(titanic):
    vd = titanic.copy()
    vd["age"].cut(breaks=[0, 18, 40, 100])
    assert vd is not None


def test_decode(titanic):
    vd = titanic.copy()
    vd["sex"].decode("male", 0, "female", 1, 2)
    assert vd is not None


def test_column_get_dummies(titanic):
    vd = titanic.copy()
    vd["pclass"].get_dummies()
    assert len(vd.get_columns()) > len(titanic.get_columns())


def test_topk(titanic):
    assert titanic["pclass"].topk() is not None


def test_value_counts(titanic):
    assert titanic["sex"].value_counts() is not None


def test_mode(titanic):
    assert titanic["pclass"].mode() is not None


def test_distinct(titanic):
    assert len(titanic["pclass"].distinct()) >= 1
