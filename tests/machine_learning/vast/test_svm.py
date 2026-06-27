"""
SPDX-License-Identifier: Apache-2.0

Linear support-vector models.
"""

from vastorbit.machine_learning.vast import LinearSVR, LinearSVC
from tests.helpers import (
    WINE_X, WINE_REG_Y, TITANIC_NUM_X, TITANIC_BINARY_Y, cols_lower,
)


def test_linear_svr(winequality, name_factory):
    model = LinearSVR(name=name_factory("svr"))
    model.fit(winequality, WINE_X, WINE_REG_Y)
    assert "pred" in cols_lower(model.predict(winequality, name="pred"))
    assert model.score() is not None


def test_linear_svc(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = LinearSVC(name=name_factory("svc"))
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    assert "pred" in cols_lower(model.predict(data, name="pred"))
    assert model.classification_report() is not None
