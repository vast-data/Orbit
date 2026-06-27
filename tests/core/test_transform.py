"""
SPDX-License-Identifier: Apache-2.0

Frame-level transforms: normalize, balance, dummies, drop_duplicates, case_when.
"""

from tests.helpers import cols_lower


def test_normalize(winequality):
    vd = winequality.copy().normalize(columns=["fixed_acidity"], method="zscore")
    assert vd is not None


def test_get_dummies(titanic):
    vd = titanic.copy().get_dummies(columns=["pclass"])
    assert len(vd.get_columns()) >= len(titanic.get_columns())


def test_balance(titanic):
    data = titanic.copy()[["age", "fare", "survived"]].dropna()
    balanced = data.balance("survived", method="under", x=0.8)
    assert balanced.shape()[0] > 0


def test_drop_duplicates(titanic):
    vd = titanic.copy()[["pclass", "sex"]].drop_duplicates()
    assert vd.shape()[0] > 0


def test_case_when(titanic):
    vd = titanic.copy()
    vd.case_when("age_group", "age < 18", "child", "adult")
    assert "age_group" in cols_lower(vd)
