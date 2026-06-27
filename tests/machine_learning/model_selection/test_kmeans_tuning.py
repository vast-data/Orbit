"""
SPDX-License-Identifier: Apache-2.0

KMeans cluster-count helpers.
"""

from vastorbit.machine_learning.model_selection import elbow, best_k
from tests.helpers import IRIS_X


def test_elbow(iris):
    res = elbow(iris, IRIS_X, n_clusters=(1, 5), show=False)
    assert res is not None


def test_best_k(iris):
    k = best_k(iris, IRIS_X, n_clusters=(1, 5))
    assert isinstance(k, int)
