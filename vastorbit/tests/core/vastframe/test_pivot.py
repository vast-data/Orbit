"""
SPDX-License-Identifier: Apache-2.0
"""

import os
import json
import pandas as pd
import pytest
import vastorbit as vo

# Utilities
from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.parsers.json import read_json


class TestPivot:
    """
    test class for Pivot functions test
    """

    def test_merge_similar_names(self):
        """
        test function - merge_similar_names
        """
        x = TableSample(
            {
                "age": [50, None, None, None],
                "information.age": [100, None, 30, None],
                "dict.age": [None, 80, None, None],
                "age.people": [None, None, None, 10],
                "num": [1, 2, 3, 4],
            }
        ).to_vdf()
        result = x.merge_similar_names(skip_word=["information.", "dict.", ".people"])
        assert result[["age"]].sort({"age": "DESC"})[1] == [50]

    @pytest.mark.parametrize(
        "index, columns, values, aggr",
        [
            ("date", "state", "number", "sum"),
        ],
    )
    def test_narrow(self, amazon_vd, index, columns, values, aggr):
        """
        test function - narrow
        """
        amazon_pdf = amazon_vd.to_pandas()
        vo_pv = amazon_vd.pivot(
            index=index,
            columns=columns,
            values=values,
            aggr=aggr,
        )
        py_pv = pd.pivot_table(
            amazon_pdf,
            index=[index],
            columns=[columns],
            values=values,
            aggfunc=aggr,
        )

        vo_res = vo_pv.narrow(index, col_name=columns, val_name=values)[columns].count()

        py_res = pd.melt(
            py_pv, ignore_index=False, var_name=columns, value_name=values
        )[columns].count()

        assert vo_res == py_res

    @pytest.mark.parametrize(
        "index, columns, values, aggr, parm, value",
        [
            ("date", "state", "number", "sum", "columns_val", None),
            ("date", "state", "number", "sum", "agg_col", "ACRE"),
            ("date", "state", "number", "sum", "prefix", "pv_"),
        ],
    )
    def test_pivot(self, amazon_vd, index, columns, values, aggr, parm, value):
        """
        test function - pivot
        """
        amazon_pdf = amazon_vd.to_pandas()
        _vo_res = amazon_vd.pivot(
            index=index,
            columns=columns,
            values=values,
            aggr=aggr,
            prefix=value if parm == "prefix" else "",
        )
        _py_res = pd.pivot_table(
            amazon_pdf,
            index=[index],
            columns=[columns],
            values=values,
            aggfunc=aggr,
        )

        if parm == "columns_val":
            vo_res = [v.replace('"', "") for v in _vo_res.get_columns()][1:]
            py_res = _py_res.columns.to_list()
        elif parm == "agg_col":
            vo_res = _vo_res[value].sum()
            py_res = _py_res[value].sum()
        else:
            vo_res = [v.replace('"', "") for v in _vo_res.get_columns()][1]
            py_res = f"{value}{_py_res.columns.to_list()[0]}"

        assert vo_res == py_res
