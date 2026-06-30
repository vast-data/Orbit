"""
SPDX-License-Identifier: Apache-2.0

Decomposition: PCA, SVD, MCA.
"""

import pytest

from vastorbit.machine_learning.vast import PCA, SVD, MCA, OneHotEncoder
from tests.helpers import WINE_X

LINEAR_DECOMP = [
    ("PCA", lambda n: PCA(name=n, n_components=2)),
    ("SVD", lambda n: SVD(name=n, n_components=2)),
]


@pytest.mark.parametrize(
    "label, factory", LINEAR_DECOMP, ids=[d[0] for d in LINEAR_DECOMP]
)
def test_linear_decomposition(winequality, name_factory, label, factory):
    model = factory(name_factory(f"dec_{label}"))
    model.fit(winequality, WINE_X)
    assert model.transform(winequality) is not None


def test_pca_explained_variance(winequality, name_factory):
    model = PCA(name=name_factory("pca_ev"), n_components=2)
    model.fit(winequality, WINE_X)
    assert model.explained_variance_ratio_ is not None


def test_mca(titanic, name_factory):
    enc = OneHotEncoder(name=name_factory("ohe_mca"))
    enc.fit(titanic, ["sex", "pclass"])
    encoded = enc.transform(titanic)
    cols = [
        c for c in encoded.get_columns() if "sex" in c.lower() or "pclass" in c.lower()
    ]
    model = MCA(name=name_factory("mca"))
    model.fit(encoded, cols)
    assert model.transform(encoded) is not None
