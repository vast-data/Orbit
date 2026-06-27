"""
SPDX-License-Identifier: Apache-2.0

The same smoke checks on the plotly backend, to exercise that rendering path.
The backend is switched for this module and restored afterwards.
"""

import pytest

import vastorbit as vo


@pytest.fixture(autouse=True)
def plotly_backend():
    vo.set_option("plotting_lib", "plotly")
    yield
    vo.set_option("plotting_lib", "matplotlib")


def _ok(obj):
    return obj is not None


def test_column_hist_plotly(titanic):
    assert _ok(titanic["age"].hist())


def test_column_bar_plotly(titanic):
    assert _ok(titanic["pclass"].bar())


def test_frame_scatter_plotly(iris):
    assert _ok(iris.scatter(["SepalLengthCm", "PetalLengthCm"]))
