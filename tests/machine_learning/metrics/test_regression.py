"""
SPDX-License-Identifier: Apache-2.0

Regression metrics on a small hand-built frame.
"""

import pytest

import vastorbit as vo
from vastorbit.machine_learning.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    median_absolute_error,
    max_error,
)


@pytest.fixture(scope="module")
def reg_preds():
    return vo.VastFrame({
        "y_true": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        "y_pred": [1.1, 1.9, 3.2, 3.8, 5.1, 5.9],
    })


@pytest.mark.parametrize(
    "metric",
    [r2_score, mean_squared_error, mean_absolute_error,
     median_absolute_error, max_error],
)
def test_regression_metric(reg_preds, metric):
    assert metric("y_true", "y_pred", reg_preds) is not None
