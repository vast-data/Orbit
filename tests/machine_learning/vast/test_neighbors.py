"""
SPDX-License-Identifier: Apache-2.0

K-nearest-neighbours regressor/classifier and the LOF outlier detector.
"""

from vastorbit.machine_learning.vast import (
    KNeighborsRegressor,
    KNeighborsClassifier,
    LocalOutlierFactor,
)
from tests.helpers import (
    WINE_X,
    WINE_REG_Y,
    TITANIC_NUM_X,
    TITANIC_BINARY_Y,
    IRIS_X,
    cols_lower,
)


def test_knn_regressor(winequality, name_factory):
    model = KNeighborsRegressor(name=name_factory("knnr"), n_neighbors=5)
    model.fit(winequality, WINE_X, WINE_REG_Y)
    assert "pred" in cols_lower(model.predict(winequality, name="pred"))


def test_knn_classifier(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = KNeighborsClassifier(name=name_factory("knnc"), n_neighbors=5)
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    assert "pred" in cols_lower(model.predict(data, name="pred"))


def test_local_outlier_factor(iris, name_factory):
    # LOF.predict() takes no args; returns the LOF-scored training frame
    model = LocalOutlierFactor(name=name_factory("lof"), n_neighbors=5)
    model.fit(iris, IRIS_X)
    assert model.predict() is not None
