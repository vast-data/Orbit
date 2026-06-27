"""
SPDX-License-Identifier: Apache-2.0

TableSample container.
"""

import pandas as pd

from vastorbit.core.tablesample.base import TableSample


def test_build_and_convert():
    ts = TableSample({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    pdf = ts.to_pandas()
    assert isinstance(pdf, pd.DataFrame)
    assert len(pdf) == 3


def test_to_list():
    ts = TableSample({"a": [1, 2], "b": [3, 4]})
    assert isinstance(ts.to_list(), list)
