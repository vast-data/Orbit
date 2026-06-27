"""
SPDX-License-Identifier: Apache-2.0

Single decision trees (regressor + classifier).
"""

from vastorbit.machine_learning.vast import (
    DecisionTreeRegressor,
    DecisionTreeClassifier,
)
from tests.helpers import (
    WINE_X, WINE_REG_Y, TITANIC_NUM_X, TITANIC_BINARY_Y, cols_lower,
)


def test_decision_tree_regressor(winequality, name_factory):
    model = DecisionTreeRegressor(name=name_factory("dtr"), max_depth=3)
    model.fit(winequality, WINE_X, WINE_REG_Y)
    assert "pred" in cols_lower(model.predict(winequality, name="pred"))
    assert model.score() is not None
    assert model.features_importance(show=False) is not None


def test_decision_tree_classifier(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = DecisionTreeClassifier(name=name_factory("dtc"), max_depth=3)
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    assert "pred" in cols_lower(model.predict(data, name="pred"))
    assert model.classification_report() is not None
