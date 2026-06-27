"""
SPDX-License-Identifier: Apache-2.0

In-database -> in-memory model export and pure-python prediction.
"""

from vastorbit.machine_learning.vast import LinearRegression, LogisticRegression
from tests.helpers import (
    WINE_X, WINE_REG_Y, TITANIC_NUM_X, TITANIC_BINARY_Y,
)


def test_to_memmodel(winequality, name_factory):
    model = LinearRegression(name=name_factory("mm_reg"))
    model.fit(winequality, WINE_X, WINE_REG_Y)
    mm = model.to_memmodel()
    out = mm.predict([[0.0] * len(WINE_X)])
    assert out is not None


def test_to_python(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = LogisticRegression(name=name_factory("py_clf"))
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    predict_fn = model.to_python()
    assert predict_fn([[30.0, 50.0]]) is not None
