"""
SPDX-License-Identifier: Apache-2.0

Outlier flagging and plotting.
"""

from tests.helpers import cols_lower


def test_outliers(winequality):
    vd = winequality.copy()
    vd.outliers(columns=["fixed_acidity", "citric_acid"], name="is_outlier")
    assert "is_outlier" in cols_lower(vd)


def test_outliers_plot(winequality):
    assert (
        winequality.outliers_plot(columns=["fixed_acidity", "citric_acid"]) is not None
    )
