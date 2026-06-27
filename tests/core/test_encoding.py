"""
SPDX-License-Identifier: Apache-2.0

Column evaluation, typing, renaming and dropping.
"""

from tests.helpers import cols_lower


def test_new_column(titanic):
    vd = titanic.copy()
    vd["age_x2"] = "age * 2"
    assert "age_x2" in cols_lower(vd)


def test_drop_column(titanic):
    vd = titanic.copy()
    vd["tmp"] = "1"
    vd = vd.drop(["tmp"])
    assert "tmp" not in cols_lower(vd)


def test_astype(titanic):
    vd = titanic.copy()
    vd["pclass"].astype("float")
    assert vd is not None


def test_rename(titanic):
    vd = titanic.copy()
    vd["age"].rename("passenger_age")
    assert "passenger_age" in cols_lower(vd)
