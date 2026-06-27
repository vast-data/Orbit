"""
SPDX-License-Identifier: Apache-2.0

Clustering: KMeans, BisectingKMeans, DBSCAN, and the NearestCentroid
classifier (which lives in the clustering module).
"""

import pytest

from vastorbit.machine_learning.vast import (
    KMeans,
    BisectingKMeans,
    DBSCAN,
    NearestCentroid,
)
from tests.helpers import IRIS_X, IRIS_MULTI_Y, cols_lower

KMEANS_LIKE = [
    ("KMeans", lambda n: KMeans(name=n, n_cluster=3, max_iter=10)),
    ("BisectingKMeans", lambda n: BisectingKMeans(name=n, n_cluster=3, max_iter=10)),
]


@pytest.mark.parametrize("label, factory", KMEANS_LIKE, ids=[c[0] for c in KMEANS_LIKE])
def test_kmeans_like(iris, name_factory, label, factory):
    model = factory(name_factory(f"clu_{label}"))
    model.fit(iris, IRIS_X)
    assert model.predict(iris) is not None


def test_dbscan(iris, name_factory):
    model = DBSCAN(name=name_factory("dbscan"), eps=0.5, min_samples=5)
    model.fit(iris, IRIS_X)
    assert model.n_clusters_ is not None


def test_nearest_centroid(iris, name_factory):
    model = NearestCentroid(name=name_factory("ncentroid"))
    model.fit(iris, IRIS_X, IRIS_MULTI_Y)
    assert "pred" in cols_lower(model.predict(iris, name="pred"))
