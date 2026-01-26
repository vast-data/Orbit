"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# Standard Python Modules
import time

from vastorbit.connection.errors import CopyRejected

# Other Modules
import pandas

# vastorbit
from vastorbit import (
    drop,
)
from vastorbit.connection import current_cursor
from vastorbit.core.parsers.pandas import read_pandas
from vastorbit.datasets import load_titanic


class TestPandasExtended:
    def test_read_pandas_abort_on_error(self, titanic_vd):
        """
        Tries to use read_pandas() to load a dataframe into a table
        that has the right column names, but the wrong column type
        for the data format. Asserts that abort_on_error behaves as
        expected.
        """
        pandas_df = titanic_vd.to_pandas()
        assert pandas_df.shape == (1234, 14)
        random_name = f"titanic_hack_{int(time.time())}"
        try:
            current_cursor().execute(
                f"create table default.{random_name} like"
                f" {titanic_vd} excluding projections"
            ).fetchall()
            current_cursor().execute(
                f'alter table default.{random_name} drop column "survived"'
            ).fetchall()
            current_cursor().execute(
                f'alter table default.{random_name} add column "survived" interval'
            ).fetchall()
            with pytest.raises(CopyRejected):
                read_pandas(
                    df=pandas_df,
                    name=random_name,
                    schema="default",
                    insert=True,
                    abort_on_error=True,
                )
        finally:
            current_cursor().execute(
                f"drop table if exists default.{random_name}"
            ).fetchall()
