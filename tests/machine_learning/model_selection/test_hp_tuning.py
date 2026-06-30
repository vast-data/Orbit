"""
SPDX-License-Identifier: Apache-2.0

Hyper-parameter search. Grids are tiny and cv is small to stay fast.
"""

from vastorbit.machine_learning.vast import LinearRegression, RandomForestClassifier
from vastorbit.machine_learning.model_selection import (
    grid_search_cv,
    randomized_search_cv,
    randomized_features_search_cv,
    validation_curve,
    parameter_grid,
)
from tests.helpers import (
    WINE_X,
    WINE_REG_Y,
    TITANIC_NUM_X,
    TITANIC_BINARY_Y,
)


def test_parameter_grid():
    grid = parameter_grid({"a": [1, 2], "b": [3, 4]})
    assert len(grid) == 4


def test_grid_search_cv(winequality, name_factory):
    model = LinearRegression(name=name_factory("gs"))
    res = grid_search_cv(
        model,
        {"solver": ["newton", "bfgs"]},
        winequality,
        WINE_X,
        WINE_REG_Y,
        cv=3,
        print_info=False,
    )
    assert res is not None


def test_validation_curve(winequality, name_factory):
    model = LinearRegression(name=name_factory("vc"))
    res = validation_curve(
        model,
        "solver",
        ["newton", "bfgs"],
        winequality,
        WINE_X,
        WINE_REG_Y,
        cv=3,
    )
    assert res is not None


def test_randomized_features_search(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    model = RandomForestClassifier(
        name=name_factory("rfs"), n_estimators=5, max_depth=3
    )
    res = randomized_features_search_cv(
        model,
        data,
        TITANIC_NUM_X,
        TITANIC_BINARY_Y,
        cv=3,
        print_info=False,
    )
    assert res is not None
