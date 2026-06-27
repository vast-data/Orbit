"""
SPDX-License-Identifier: Apache-2.0

Correlation and covariance.
"""

import pytest


def test_corr_matrix(winequality):
    corr = winequality.corr(
        columns=["fixed_acidity", "citric_acid", "residual_sugar"], show=False
    )
    assert corr is not None


@pytest.mark.parametrize("method", ["pearson", "spearman"])
def test_corr_methods(winequality, method):
    corr = winequality.corr(
        columns=["fixed_acidity", "citric_acid"], method=method, show=False
    )
    assert corr is not None


def test_cov(winequality):
    cov = winequality.cov(
        columns=["fixed_acidity", "citric_acid"], show=False
    )
    assert cov is not None
