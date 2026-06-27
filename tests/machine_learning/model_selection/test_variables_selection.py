"""
SPDX-License-Identifier: Apache-2.0

Stepwise feature selection.
"""

from vastorbit.machine_learning.vast import LogisticRegression
from vastorbit.machine_learning.model_selection import stepwise
from tests.helpers import TITANIC_NUM_X, TITANIC_BINARY_Y


def test_stepwise(titanic, name_factory):
    data = titanic.copy()[TITANIC_NUM_X + ["pclass", TITANIC_BINARY_Y]].dropna()
    model = LogisticRegression(name=name_factory("stepwise"))
    res = stepwise(
        model, data, TITANIC_NUM_X + ["pclass"], TITANIC_BINARY_Y,
        direction="backward", print_info=False, show=False,
    )
    assert res is not None
