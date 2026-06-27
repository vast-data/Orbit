"""
SPDX-License-Identifier: Apache-2.0

Naive Bayes family. Each variant is fitted on data of the kind it expects
(Gaussian -> continuous, Bernoulli -> binary, Multinomial -> counts,
Categorical -> categories).
"""

import vastorbit as vo
from vastorbit.machine_learning.vast import (
    NaiveBayes,
    GaussianNB,
    BernoulliNB,
    MultinomialNB,
    CategoricalNB,
)
from tests.helpers import IRIS_X, IRIS_MULTI_Y, cols_lower


def test_naive_bayes_auto(iris, name_factory):
    model = NaiveBayes(name=name_factory("nb"))
    model.fit(iris, IRIS_X, IRIS_MULTI_Y)
    assert "pred" in cols_lower(model.predict(iris, name="pred"))
    assert model.score() is not None


def test_gaussian_nb(iris, name_factory):
    model = GaussianNB(name=name_factory("gnb"))
    model.fit(iris, IRIS_X, IRIS_MULTI_Y)
    assert model.classification_report() is not None


def test_bernoulli_nb(name_factory):
    data = vo.VastFrame({
        "f1": [0, 1, 0, 1, 1, 0, 1, 0],
        "f2": [1, 0, 1, 0, 1, 1, 0, 0],
        "cls": ["a", "b", "a", "b", "b", "a", "b", "a"],
    })
    model = BernoulliNB(name=name_factory("bnb"))
    model.fit(data, ["f1", "f2"], "cls")
    assert model.predict(data, name="pred") is not None


def test_multinomial_nb(name_factory):
    data = vo.VastFrame({
        "c1": [1, 2, 0, 3, 1, 2, 0, 4],
        "c2": [0, 1, 2, 1, 3, 0, 2, 1],
        "cls": ["a", "b", "a", "b", "a", "b", "a", "b"],
    })
    model = MultinomialNB(name=name_factory("mnb"))
    model.fit(data, ["c1", "c2"], "cls")
    assert model.predict(data, name="pred") is not None


def test_categorical_nb(name_factory):
    data = vo.VastFrame({
        "color": ["r", "g", "b", "r", "g", "b", "r", "g"],
        "size": ["s", "m", "l", "s", "m", "l", "l", "s"],
        "cls": ["a", "b", "a", "b", "a", "b", "a", "b"],
    })
    model = CategoricalNB(name=name_factory("cnb"))
    model.fit(data, ["color", "size"], "cls")
    assert model.predict(data, name="pred") is not None
