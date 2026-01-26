"""
SPDX-License-Identifier: Apache-2.0
"""

from math import ceil, floor

import numpy as np
import pandas as pd

import vastorbit as vo
import vastorbit.sql.functions as vof


class TestMiscellaneousVDF:
    """
    test class to test Miscellaneous functions for VastFrame
    """

    def test_repr(self, titanic_vd_fun):
        """
        test function - repr
        """
        repr_vdf = titanic_vd_fun.__repr__()
        assert "pclass" in repr_vdf
        assert "survived" in repr_vdf
        assert 10000 < len(repr_vdf) < 1000000
        repr_html_vdf = titanic_vd_fun._repr_html_()
        assert 10000 < len(repr_html_vdf) < 10000000
        assert "<table>" in repr_html_vdf
        assert isinstance(repr_html_vdf, str)

        # vdc
        repr_vdc = titanic_vd_fun["age"].__repr__()
        assert "age" in repr_vdc
        assert "60" in repr_vdc
        assert 500 < len(repr_vdc) < 5000
        repr_html_vdc = titanic_vd_fun["age"]._repr_html_()
        assert 10000 < len(repr_html_vdc) < 10000000
        assert "<table>" in repr_html_vdc
        assert isinstance(repr_html_vdc, str)

    def test_magic(self, titanic_vd):
        """
        test function - magic
        """
        assert (
            str(titanic_vd["name"]._in(["Madison", "Ashley", None]))
            == "(\"name\") IN ('Madison', 'Ashley', NULL)"
        )
        assert str(titanic_vd["age"]._between(1, 4)) == '("age") BETWEEN (1) AND (4)'
        assert str(titanic_vd["age"]._as("age2")) == '("age") AS age2'
        assert str(titanic_vd["age"]._distinct()) == 'DISTINCT ("age")'
        assert (
            str(
                vof.sum(titanic_vd["age"])._over(
                    by=[titanic_vd["pclass"], titanic_vd["sex"]],
                    order_by=[titanic_vd["fare"]],
                )
            )
            == 'SUM("age") OVER (PARTITION BY "pclass", "sex" ORDER BY "fare")'
        )
        assert str(abs(titanic_vd["age"])) == 'ABS("age")'
        assert str(ceil(titanic_vd["age"])) == 'CEIL("age")'
        assert str(floor(titanic_vd["age"])) == 'FLOOR("age")'
        assert str(round(titanic_vd["age"], 2)) == 'ROUND("age", 2)'
        assert str(-titanic_vd["age"]) == '-("age")'
        assert str(+titanic_vd["age"]) == '+("age")'
        assert str(titanic_vd["age"] % 2) == 'MOD("age", 2)'
        assert str(2 % titanic_vd["age"]) == 'MOD(2, "age")'
        assert str(titanic_vd["age"] ** 2) == 'POWER("age", 2)'
        assert str(2 ** titanic_vd["age"]) == 'POWER(2, "age")'
        assert str(titanic_vd["age"] + 3) == '("age") + (3)'
        assert str(3 + titanic_vd["age"]) == '(3) + ("age")'
        assert str(titanic_vd["age"] - 3) == '("age") - (3)'
        assert str(3 - titanic_vd["age"]) == '(3) - ("age")'
        assert str(titanic_vd["age"] * 3) == '("age") * (3)'
        assert str(3 * titanic_vd["age"]) == '(3) * ("age")'
        assert str(titanic_vd["age"] // 3) == '("age") // (3)'
        assert str(3 // titanic_vd["age"]) == '(3) // ("age")'
        assert str(titanic_vd["age"] > 3) == '("age") > (3)'
        assert str(3 > titanic_vd["age"]) == '("age") < (3)'
        assert str(titanic_vd["age"] >= 3) == '("age") >= (3)'
        assert str(3 >= titanic_vd["age"]) == '("age") <= (3)'
        assert str(titanic_vd["age"] < 3) == '("age") < (3)'
        assert str(3 < titanic_vd["age"]) == '("age") > (3)'
        assert str(titanic_vd["age"] <= 3) == '("age") <= (3)'
        assert str(3 <= titanic_vd["age"]) == '("age") >= (3)'
        assert (
            str((3 >= titanic_vd["age"]) & (titanic_vd["age"] <= 50))
            == '(("age") <= (3)) AND (("age") <= (50))'
        )
        assert (
            str((3 >= titanic_vd["age"]) | (titanic_vd["age"] <= 50))
            == '(("age") <= (3)) OR (("age") <= (50))'
        )
        assert str("Mr " + titanic_vd["name"]) == "('Mr ') || (\"name\")"
        assert str(titanic_vd["name"] + " .") == "(\"name\") || (' .')"
        assert str(3 * titanic_vd["name"]) == 'REPEAT("name", 3)'
        assert str(titanic_vd["name"] * 3) == 'REPEAT("name", 3)'
        assert str(titanic_vd["age"] == 3) == '("age") = (3)'
        assert str(3 == titanic_vd["age"]) == '("age") = (3)'
        assert str(titanic_vd["age"] != 3) == '("age") != (3)'
        assert str(None != titanic_vd["age"]) == '("age") IS NOT NULL'
        assert titanic_vd["fare"][0] >= 0
        assert titanic_vd[["fare"]][0][0] >= 0
        assert titanic_vd[titanic_vd["fare"] > 500].shape()[0] == 4
        assert titanic_vd[titanic_vd["fare"] < 500].shape()[0] == 1304
        assert titanic_vd[titanic_vd["fare"] * 4 + 2 < 500].shape()[0] == 1241
        assert titanic_vd[titanic_vd["fare"] / 4 - 2 < 500].shape()[0] == 1308

    def test_sql(self, titanic_vd_fun):
        """
        test function - sql
        """
        sql = f"""-- Selecting some columns \n
                 SELECT 
                    age, 
                    fare 
                 FROM titanic 
                 WHERE age IS NOT NULL;"""
        vdf = vo.VastFrame(sql)
        assert vdf.shape() == (1046, 2)
        vdf = vo.VastFrame(sql, usecols=["age"])
        assert vdf.shape() == (1046, 1)


class TestVDFCreate:
    """
    test class to test VastFrame create options
    """

    def test_using_input_relation(self, titanic_vd_fun):
        """
        test create VastFrame using input relation
        """
        vdf = vo.VastFrame(input_relation="titanic")

        assert vdf["pclass"].count() == 1309

    def test_using_input_relation_schema(self, titanic_vd_fun):
        """
        test create VastFrame using input relation and schema
        """
        vdf = vo.VastFrame(input_relation="titanic")

        assert vdf["pclass"].count() == 1309

    def test_using_input_relation_VastColumns(self, titanic_vd_fun):
        """
        test create VastFrame using relation `VastColumns`
        """
        vdf = vo.VastFrame(
            input_relation=f"titanic",
            usecols=["age", "survived"],
        )

        assert vdf["survived"].count() == 1309

    def test_using_pandas_dataframe(self, titanic_vd_fun):
        """
        test create VastFrame using pandas dataframe
        """
        pdf = pd.DataFrame(
            [[1, "first1", "last1"], [2, "first2", "last2"]],
            columns=["id", "fname", "lname"],
        )
        vdf = vo.VastFrame(pdf)

        assert vdf["id"].count() == 2

    def test_using_list(self):
        """
        test create VastFrame using list
        """
        vdf = vo.VastFrame(
            input_relation=[[1, "first1", "last1"], [2, "first2", "last2"]],
            usecols=["id", "fname", "lname"],
        )

        assert vdf.shape() == (2, 3)
        vdf["id"].astype("int")
        assert vdf["id"].avg() == 1.5

    def test_using_np_array(self):
        """
        test create VastFrame using numpy array
        """
        vdf = vo.VastFrame(
            input_relation=np.array([[1, "first1", "last1"], [2, "first2", "last2"]]),
        )

        assert vdf.shape() == (2, 3)
        vdf["col0"].astype("int")
        assert vdf["col0"].avg() == 1.5

    def test_using_tablesample(self):
        """
        test create VastFrame using `TableSample`
        """
        tb = vo.TableSample(
            {"id": [1, 2], "fname": ["first1", "first2"], "lname": ["last1", "last2"]}
        )
        vdf = vo.VastFrame(
            input_relation=tb,
        )

        assert vdf.shape() == (2, 3)
        assert vdf["id"].avg() == 1.5

        vdf = vo.VastFrame(input_relation=tb, usecols=["id", "lname"])

        assert vdf.shape() == (2, 2)
        assert vdf.get_columns() == ['"id"', '"lname"']

    def test_using_dict(self):
        """
        test create VastFrame using dictionary
        """
        tb = {"id": [1, 2], "fname": ["first1", "first2"], "lname": ["last1", "last2"]}
        vdf = vo.VastFrame(
            input_relation=tb,
        )

        assert vdf.shape() == (2, 3)
        assert vdf["id"].avg() == 1.5

        vdf = vo.VastFrame(input_relation=tb, usecols=["id", "lname"])

        assert vdf.shape() == (2, 2)
        assert vdf.get_columns() == ['"id"', '"lname"']

    def test_from_sql(self, titanic_vd_fun):
        """
        test create VastFrame using sql
        """
        vdf = vo.VastFrame(f"SELECT * FROM titanic")

        assert vdf["survived"].count() == 1309

        vdf = vo.VastFrame(f"SELECT * FROM titanic", usecols=["survived"])

        assert vdf["survived"].count() == 1309
        assert vdf.get_columns() == ['"survived"']
