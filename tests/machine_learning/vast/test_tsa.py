"""
SPDX-License-Identifier: Apache-2.0

Time-series models on tiny synthetic series (no external loaders).
"""

import pytest

import vastorbit as vo
from vastorbit.machine_learning.vast import AR, ARMA, ARIMA, VAR
from tests.helpers import trend_series, multivariate_series

UNIVARIATE = [
    ("AR", lambda n: AR(name=n, p=2)),
    ("ARMA", lambda n: ARMA(name=n, order=(2, 0, 1))),
    ("ARIMA", lambda n: ARIMA(name=n, order=(2, 1, 1))),
]


@pytest.fixture(scope="module")
def ts_data():
    return vo.VastFrame(trend_series(40))


@pytest.mark.parametrize("label, factory", UNIVARIATE, ids=[m[0] for m in UNIVARIATE])
def test_univariate_timeseries(ts_data, name_factory, label, factory):
    model = factory(name_factory(f"ts_{label}"))
    model.fit(ts_data, "month", "value")
    assert model.predict() is not None


def test_var(name_factory):
    data = vo.VastFrame(multivariate_series(30))
    model = VAR(name=name_factory("var"), p=2)
    model.fit(data, "t", ["a", "b"])
    assert model.predict() is not None
