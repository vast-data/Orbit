"""
SPDX-License-Identifier: Apache-2.0

Linear support-vector models.
"""

import pytest

from vastorbit.machine_learning.vast import LinearSVR, LinearSVC
from tests.helpers import (
    WINE_X,
    WINE_REG_Y,
    TITANIC_NUM_X,
    TITANIC_BINARY_Y,
    cols_lower,
)


# LinearSVR wraps sklearn's liblinear solver; on the unscaled winequality
# features it may hit max_iter before converging. That does not affect what
# this test checks (fit/predict/score wiring), so the benign warning is scoped
# out here rather than globally silenced.
@pytest.mark.filterwarnings("ignore::sklearn.exceptions.ConvergenceWarning")
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
