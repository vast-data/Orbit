"""
SPDX-License-Identifier: Apache-2.0

Data-definition: create_table, insert_into, drop.
"""

import vastorbit as vo
from vastorbit.sql.insert import insert_into
from tests.helpers import cols_lower


def test_create_insert_read_drop(name_factory):
    tbl = name_factory("ddl_tbl")
    vo.create_table(tbl, dtype={"id": "int", "label": "varchar"})
    insert_into(tbl, data=[[1, "a"], [2, "b"], [3, "c"]], column_names=["id", "label"])
    vd = vo.VastFrame(tbl)
    assert vd.shape()[0] == 3
    assert "label" in cols_lower(vd)


def test_drop_removes_table(name_factory):
    tbl = name_factory("ddl_drop")
    vo.create_table(tbl, dtype={"x": "int"})
    vo.drop(tbl, method="table")
    # re-creating with the same name must succeed (proves it was dropped)
    vo.create_table(tbl, dtype={"x": "int"})
