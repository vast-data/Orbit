"""
SPDX-License-Identifier: Apache-2.0

Plotting smoke tests on the matplotlib (Agg) backend, which is the session
default set in conftest. We only check that a chart object is produced.
"""


def _ok(obj):
    return obj is not None


def test_column_hist(titanic):
    assert _ok(titanic["age"].hist())


def test_column_bar(titanic):
    assert _ok(titanic["pclass"].bar())


def test_column_boxplot(titanic):
    assert _ok(titanic["fare"].boxplot())


def test_column_density(titanic):
    assert _ok(titanic["age"].density())


def test_frame_bar(titanic):
    assert _ok(titanic.bar(["pclass"]))


def test_frame_scatter(iris):
    assert _ok(iris.scatter(["SepalLengthCm", "PetalLengthCm"]))


def test_frame_hist(winequality):
    assert _ok(winequality.hist(["fixed_acidity"]))


def test_frame_boxplot(winequality):
    assert _ok(winequality.boxplot(["fixed_acidity", "citric_acid"]))


def test_heatmap(winequality):
    assert _ok(
        winequality.corr(
            columns=["fixed_acidity", "citric_acid", "residual_sugar"], show=True
        )
    )
