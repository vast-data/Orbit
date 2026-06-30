"""
SPDX-License-Identifier: Apache-2.0

Model-selection utilities. Kept light (cv=3, flat relations, tiny models) so
they stay well under Trino's default stage budget.
"""

from vastorbit.machine_learning.vast import LinearRegression, LogisticRegression
from vastorbit.machine_learning.model_selection import cross_validate, learning_curve
from tests.helpers import (
    WINE_X,
    WINE_REG_Y,
    TITANIC_NUM_X,
    TITANIC_BINARY_Y,
)


def test_train_test_split(titanic):
    train, test = titanic.train_test_split(test_size=0.33, random_state=42)
    assert train.shape()[0] > 0
    assert test.shape()[0] > 0


def test_cross_validate_regression(winequality, name_factory):
    model = LinearRegression(name=name_factory("cv_reg"))
    assert cross_validate(model, winequality, WINE_X, WINE_REG_Y, cv=3) is not None


def test_cross_validate_classification(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = LogisticRegression(name=name_factory("cv_clf"))
    assert (
        cross_validate(model, data, TITANIC_NUM_X, TITANIC_BINARY_Y, cv=3) is not None
    )


def test_learning_curve(winequality, name_factory):
    model = LinearRegression(name=name_factory("lc_reg"))
    result = learning_curve(
        model, winequality, WINE_X, WINE_REG_Y, sizes=[0.3, 0.6, 0.9], cv=3
    )
    assert result is not None
