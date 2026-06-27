"""
SPDX-License-Identifier: Apache-2.0

Linear models: regressors + LogisticRegression.
"""

import pytest

from vastorbit.machine_learning.vast import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    PoissonRegressor,
    PLSRegression,
    LogisticRegression,
)
from tests.helpers import (
    WINE_X, WINE_REG_Y, TITANIC_NUM_X, TITANIC_BINARY_Y, cols_lower,
)

REGRESSORS = [
    ("LinearRegression", lambda n: LinearRegression(name=n)),
    ("Ridge", lambda n: Ridge(name=n)),
    ("Lasso", lambda n: Lasso(name=n)),
    ("ElasticNet", lambda n: ElasticNet(name=n)),
    ("PoissonRegressor", lambda n: PoissonRegressor(name=n)),
    ("PLSRegression", lambda n: PLSRegression(name=n, n_components=2)),
]


@pytest.mark.parametrize("label, factory", REGRESSORS, ids=[r[0] for r in REGRESSORS])
def test_regressor_lifecycle(winequality, name_factory, label, factory):
    model = factory(name_factory(f"lin_{label}"))
    model.fit(winequality, WINE_X, WINE_REG_Y)
    pred = model.predict(winequality, name="pred")
    assert "pred" in cols_lower(pred)
    assert model.score() is not None
    assert model.regression_report() is not None
    assert isinstance(model.get_params(), dict)
    assert isinstance(model.deploySQL(), str)


def test_logistic_regression(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = LogisticRegression(name=name_factory("logit"))
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    assert "pred" in cols_lower(model.predict(data, name="pred"))
    assert model.predict_proba(data, name="prob") is not None
    assert model.classification_report() is not None
