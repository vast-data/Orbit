"""
SPDX-License-Identifier: Apache-2.0

Pipeline composition (transformer + estimator).
"""

from vastorbit.machine_learning.vast import (
    StandardScaler,
    LinearRegression,
    Pipeline,
)
from tests.helpers import WINE_X, WINE_REG_Y, cols_lower


def test_pipeline_fit_predict(winequality, name_factory):
    steps = [
        ("scaler", StandardScaler(name=name_factory("pipe_scaler"))),
        ("reg", LinearRegression(name=name_factory("pipe_reg"))),
    ]
    pipe = Pipeline(steps)
    pipe.fit(winequality, WINE_X, WINE_REG_Y)
    assert "pred" in cols_lower(pipe.predict(winequality, name="pred"))
