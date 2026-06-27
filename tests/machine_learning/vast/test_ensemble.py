"""
SPDX-License-Identifier: Apache-2.0

Ensembles: random forests, gradient boosting, isolation forest.
All tree counts are tiny to keep the suite fast.
"""

import pytest

from vastorbit.machine_learning.vast import (
    RandomForestRegressor,
    RandomForestClassifier,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
    IsolationForest,
)
from tests.helpers import (
    WINE_X, WINE_REG_Y, TITANIC_NUM_X, TITANIC_BINARY_Y, IRIS_X, cols_lower,
)

REGRESSORS = [
    ("RandomForestRegressor",
     lambda n: RandomForestRegressor(name=n, n_estimators=5, max_depth=3)),
    ("GradientBoostingRegressor",
     lambda n: GradientBoostingRegressor(name=n, n_estimators=5, max_depth=3)),
]
CLASSIFIERS = [
    ("RandomForestClassifier",
     lambda n: RandomForestClassifier(name=n, n_estimators=5, max_depth=3)),
    ("GradientBoostingClassifier",
     lambda n: GradientBoostingClassifier(name=n, n_estimators=5, max_depth=3)),
]


@pytest.mark.parametrize("label, factory", REGRESSORS, ids=[r[0] for r in REGRESSORS])
def test_ensemble_regressor(winequality, name_factory, label, factory):
    model = factory(name_factory(f"ens_{label}"))
    model.fit(winequality, WINE_X, WINE_REG_Y)
    assert "pred" in cols_lower(model.predict(winequality, name="pred"))
    assert model.score() is not None
    assert model.features_importance(show=False) is not None


@pytest.mark.parametrize("label, factory", CLASSIFIERS, ids=[c[0] for c in CLASSIFIERS])
def test_ensemble_classifier(titanic, name_factory, label, factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = factory(name_factory(f"ens_{label}"))
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    assert "pred" in cols_lower(model.predict(data, name="pred"))
    assert model.classification_report() is not None


def test_isolation_forest(iris, name_factory):
    model = IsolationForest(name=name_factory("iforest"), n_estimators=5)
    model.fit(iris, IRIS_X)
    assert model.predict(iris) is not None
