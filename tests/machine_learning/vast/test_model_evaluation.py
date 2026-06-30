"""
SPDX-License-Identifier: Apache-2.0

Model-evaluation surface: reports, curves, attributes and SQL export.
A single classifier / regressor is fitted once per module and reused.
"""

import pytest

import vastorbit as vo
from vastorbit.machine_learning.vast import LogisticRegression, LinearRegression
from tests.helpers import (
    WINE_X,
    WINE_REG_Y,
    TITANIC_NUM_X,
    TITANIC_BINARY_Y,
    unique_name,
)


@pytest.fixture(scope="module")
def fitted_classifier(_titanic_raw):
    data = _titanic_raw.copy()[TITANIC_NUM_X + [TITANIC_BINARY_Y]].dropna()
    name = unique_name("eval_clf")
    model = LogisticRegression(name=name, overwrite_model=True)
    model.fit(data, TITANIC_NUM_X, TITANIC_BINARY_Y)
    yield model
    try:
        model.drop()
    except Exception:
        pass


@pytest.fixture(scope="module")
def fitted_regressor(_winequality_raw):
    name = unique_name("eval_reg")
    model = LinearRegression(name=name, overwrite_model=True)
    model.fit(_winequality_raw.copy(), WINE_X, WINE_REG_Y)
    yield model
    try:
        model.drop()
    except Exception:
        pass


def test_report(fitted_classifier):
    assert fitted_classifier.report() is not None


def test_confusion_matrix(fitted_classifier):
    assert fitted_classifier.confusion_matrix() is not None


@pytest.mark.parametrize(
    "curve", ["roc_curve", "prc_curve", "lift_chart", "cutoff_curve"]
)
def test_curves(fitted_classifier, curve):
    assert getattr(fitted_classifier, curve)(show=False) is not None


def test_get_attributes(fitted_classifier):
    assert fitted_classifier.get_attributes() is not None


def test_summarize(fitted_classifier):
    assert isinstance(fitted_classifier.summarize(), str)


def test_deploysql(fitted_classifier):
    assert isinstance(fitted_classifier.deploySQL(), str)


def test_to_sql(fitted_classifier):
    assert fitted_classifier.to_sql() is not None


def test_to_python(fitted_classifier):
    fn = fitted_classifier.to_python()
    assert fn([[30.0, 50.0]]) is not None


def test_regressor_report(fitted_regressor):
    assert fitted_regressor.report() is not None
    assert isinstance(fitted_regressor.summarize(), str)
    assert fitted_regressor.get_attributes() is not None
