"""
SPDX-License-Identifier: Apache-2.0

Inspection / introspection helpers.
"""

import numpy as np

import vastorbit as vo


def test_describe_variants(winequality):
    assert winequality.describe(method="numerical") is not None
    assert winequality.describe(method="all") is not None


def test_column_typing_helpers(titanic):
    assert isinstance(titanic.numcol(), list)
    assert isinstance(titanic.catcol(), list)
    assert isinstance(titanic.datecol(), list)


def test_duplicated_and_count_percent(titanic):
    assert titanic.duplicated(columns=["pclass", "sex"]) is not None
    assert titanic.count_percent() is not None


def test_memory_and_relation(titanic):
    assert titanic.memory_usage() is not None
    assert isinstance(titanic.current_relation(), str)


def test_explain(titanic):
    assert isinstance(titanic.explain(), str)


def test_to_list_numpy(iris):
    small = iris.head(5)
    assert isinstance(small.to_list(), list)
    assert isinstance(small.to_numpy(), np.ndarray)


def test_frame_score():
    vd = vo.VastFrame({
        "y_true": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y_score": [1.1, 2.0, 2.9, 4.2, 4.8],
    })
    assert vd.score("y_true", "y_score", "r2") is not None
