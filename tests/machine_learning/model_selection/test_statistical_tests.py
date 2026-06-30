"""
SPDX-License-Identifier: Apache-2.0

Statistical tests: normality (norm), time-series (tsa) and OLS diagnostics.
Time-series tests run on a small synthetic series; normality/OLS on winequality.
"""

import pytest

import vastorbit as vo
from vastorbit.machine_learning.vast import LinearRegression
from vastorbit.machine_learning.model_selection.statistical_tests.norm import (
    normaltest,
    jarque_bera,
    kurtosistest,
    skewtest,
)
from vastorbit.machine_learning.model_selection.statistical_tests.tsa import (
    adfuller,
    durbin_watson,
    ljungbox,
    mkt,
    seasonal_decompose,
    cochrane_orcutt,
)
from vastorbit.machine_learning.model_selection.statistical_tests.ols import (
    het_white,
    het_breuschpagan,
    variance_inflation_factor,
)
from vastorbit.machine_learning.model_selection import plot_acf_pacf
from tests.helpers import WINE_X, trend_series


@pytest.fixture(scope="module")
def ts_frame():
    return vo.VastFrame(trend_series(40))


# ---- normality ----
@pytest.mark.parametrize("test", [normaltest, jarque_bera, kurtosistest, skewtest])
def test_normality(winequality, test):
    stat, pval = test(winequality, "fixed_acidity")
    assert stat is not None and pval is not None


# ---- time series ----
def test_adfuller(ts_frame):
    assert adfuller(ts_frame, "value", "month") is not None


def test_durbin_watson(ts_frame):
    assert durbin_watson(ts_frame, eps="value", ts="month") is not None


def test_ljungbox(ts_frame):
    assert ljungbox(ts_frame, "value", "month") is not None


def test_mkt(ts_frame):
    assert mkt(ts_frame, "value", "month") is not None


def test_seasonal_decompose(ts_frame):
    res = seasonal_decompose(ts_frame, "value", "month", period=4)
    assert res is not None


def test_plot_acf_pacf(ts_frame):
    assert plot_acf_pacf(ts_frame, "value", "month", p=10, show=False) is not None


def test_cochrane_orcutt(ts_frame, name_factory):
    model = LinearRegression(name=name_factory("co"))
    model.fit(ts_frame, ["month"], "value")
    res = cochrane_orcutt(model, ts_frame, ts="month")
    assert res is not None


# ---- OLS diagnostics ----
def test_variance_inflation_factor(winequality):
    assert variance_inflation_factor(winequality, WINE_X) is not None


def test_het_white(winequality):
    # use a numeric column as the residual proxy for a smoke check
    assert het_white(winequality, "quality", WINE_X) is not None


def test_het_breuschpagan(winequality):
    assert het_breuschpagan(winequality, "quality", WINE_X) is not None
