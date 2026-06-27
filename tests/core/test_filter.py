"""
SPDX-License-Identifier: Apache-2.0

Filtering, searching and sampling.
"""


def test_filter(titanic):
    n_all = titanic.shape()[0]
    survived = titanic.copy().filter("survived = 1")
    assert 0 < survived.shape()[0] <= n_all


def test_search(titanic):
    res = titanic.search(conditions="age > 30")
    assert res.shape()[0] > 0


def test_sample(titanic):
    s = titanic.sample(n=50)
    assert s.shape()[0] <= titanic.shape()[0]
