"""
SPDX-License-Identifier: Apache-2.0

Missing-value handling.
"""


def test_dropna(titanic):
    vd = titanic.copy()[["age", "fare"]]
    cleaned = vd.dropna()
    assert cleaned.shape()[0] <= vd.shape()[0]
    assert cleaned["age"].count() == cleaned.shape()[0]


def test_fillna_column(titanic):
    vd = titanic.copy()
    vd["age"].fillna(method="mean")
    assert vd["age"].count() == vd.shape()[0]
