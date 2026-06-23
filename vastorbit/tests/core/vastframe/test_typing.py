"""
SPDX-License-Identifier: Apache-2.0
"""

from itertools import chain
import os

import pytest

import vastorbit as vo
from vastorbit.errors import ConversionError

# Utilities
from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.parsers.json import read_json


class TestVDFTyping:
    """
    test class for Typing functions test for VastFrame class
    """

    def test_astype(self, titanic_vd_fun):
        """
        test function - astype for VastFrame
        """
        # Testing VastFrame.astype
        titanic_vd_fun.astype({"fare": "int", "cabin": "varchar(1)"})

        assert titanic_vd_fun["fare"].dtype() == "int"
        assert titanic_vd_fun["cabin"].dtype() == "varchar(1)"

    def test_bool_to_int(self, titanic_vd_fun):
        """
        test function - bool_to_int
        """
        titanic_vd_fun["survived"].astype("boolean")
        assert titanic_vd_fun["survived"].dtype() == "boolean"

        titanic_vd_fun.bool_to_int()
        assert titanic_vd_fun["survived"].dtype() == "int"

    def test_catcol(self, titanic_vd_fun):
        """
        test function - catcol
        """
        assert titanic_vd_fun.catcol(max_cardinality=6) == [
            '"pclass"',
            '"survived"',
            '"name"',
            '"sex"',
            '"ticket"',
            '"cabin"',
            '"embarked"',
            '"boat"',
            '"home.dest"',
        ]

    def test_datecol(self, amazon_vd):
        """
        test function - datecol
        """
        assert amazon_vd.datecol()[0] == '"date"'

    def test_dtypes(self, amazon_vd):
        """
        test function - dtypes
        """
        assert list(chain(*amazon_vd.dtypes().to_list())) == [
            "date",
            "varchar(32)",
            "integer",
        ]

    @pytest.mark.parametrize(
        "exclude_columns, expected",
        [
            (
                [],
                [
                    '"age"',
                    '"body"',
                    '"fare"',
                    '"parch"',
                    '"pclass"',
                    '"sibsp"',
                    '"survived"',
                ],
            ),
            (
                ["survived", "body"],
                ['"fare"', '"pclass"', '"age"', '"parch"', '"sibsp"'],
            ),
        ],
    )
    def test_numcol(self, titanic_vd_fun, exclude_columns, expected):
        """
        test function - numcol
        """
        assert sorted(titanic_vd_fun.numcol(exclude_columns=exclude_columns)) == sorted(
            expected
        )


class TestVDCTyping:
    """
    test class for Typing functions test for VastColumn class
    """

    def test_astype(self, titanic_vd_fun):
        """
        test function - astype for VastColumn
        """
        # Testing VastFrame[].astype
        # expected exception
        with pytest.raises(ConversionError) as exception_info:
            titanic_vd_fun["sex"].astype("int")
        # checking the error message
        assert exception_info.match('The VastColumn "sex" can not be converted to int')

        titanic_vd_fun["sex"].astype("varchar(10)")
        assert titanic_vd_fun["sex"].dtype() == "varchar(10)"

        titanic_vd_fun["age"].astype("real")
        assert titanic_vd_fun["age"].dtype() == "double"

    def test_astype_str_to_array(self):
        """
        test function - astype
        string to array
        """
        vdf = TableSample({"str_test": ["a,b,c,d"]}).to_vdf()
        vdf["str_test"].astype("array")
        assert vdf["str_test"][2][0] == "b"

    def test_category(self, titanic_vd_fun):
        """
        test function - category
        """
        assert titanic_vd_fun["age"].category() == "real"

    def test_ctype(self, titanic_vd_fun):
        """
        test function - ctype
        """
        assert titanic_vd_fun["survived"].ctype() == "integer"

    def test_isarray(self):
        """
        test function - isarray
        """
        vdf = TableSample({"str_test": ["a,b,c,d"]}).to_vdf()
        vdf["str_test"].astype("array")
        assert vdf["str_test"].isarray()

    def test_isbool(self, titanic_vd_fun):
        """
        test function - isbool
        """
        titanic_vd_fun["survived"].astype("boolean")
        assert titanic_vd_fun["survived"].isbool() is True

    def test_isdate(self):
        """
        test function - isdate
        """
        vdf = TableSample({"str_test": ["1993-11-03", "1997-09-12"]}).to_vdf()
        vdf["str_test"].astype("date")
        assert vdf["str_test"].isdate()

    def test_isnum(self, titanic_vd_fun):
        """
        test function - isnum
        """
        assert titanic_vd_fun["age"].isnum()

    def test_dtype(self, amazon_vd):
        """
        test function - dtypes
        """
        assert amazon_vd["state"].dtype() == "varchar(32)"
