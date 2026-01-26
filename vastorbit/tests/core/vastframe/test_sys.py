"""
SPDX-License-Identifier: Apache-2.0
"""

import pytest
from vastorbit import VastFrame


class TestVDFSys:
    """
    test class for sys functions test for VastFrame class
    """

    def test_current_relation(self):
        """
        test function - current_relation
        """
        res = VastFrame("SELECT 1 AS x").current_relation()
        assert "SELECT" in res
        assert "1 AS x" in res

    def test_del_catalog(self, titanic_vd_fun):
        """
        test function - del_catalog
        """
        titanic_vd_fun.describe(method="numerical")
        catalog_val = titanic_vd_fun["age"]._catalog
        assert {"max", "avg"}.issubset(catalog_val.keys())

        titanic_vd_fun.del_catalog()
        catalog_val = titanic_vd_fun["age"]._catalog
        assert not {"max", "avg"}.issubset(catalog_val.keys())

    @pytest.mark.parametrize("test_type", ["non_empty", "empty"])
    def test_empty(self, amazon_vd, test_type):
        """
        test function - empty dataframe
        """
        if test_type == "non_empty":
            assert not amazon_vd.empty()
        else:
            assert amazon_vd.drop(["number", "date", "state"]).empty()

    @pytest.mark.parametrize(
        "col, expected",
        [
            ("expected_size", 91995.0),
            ("max_size", 526200.0),
        ],
    )
    @pytest.mark.parametrize("unit", ["b", "kb", "mb", "gb", "tb"])
    def test_expected_store_usage(self, titanic_vd_fun, col, unit, expected):
        """
        test function - expected_store_usage
        """
        res = titanic_vd_fun.expected_store_usage(unit=unit)[f"{col} ({unit})"][-1]

        if unit == "b":
            assert res == expected
        elif unit == "kb":
            assert res == expected / 1024
        elif unit == "mb":
            assert res == expected / (1024 * 1024)
        elif unit == "gb":
            assert res == expected / (1024 * 1024 * 1024)
        elif unit == "tb":
            assert res == expected / (1024 * 1024 * 1024 * 1024)

    @pytest.mark.parametrize(
        "analyze, verbose, expected_content",
        [
            (
                False,
                False,
                ["Fragment", "Output"],
            ),  # Basic explain should have fragments and output
            (True, False, ["Fragment", "CPU:"]),  # Analyze should include runtime stats
            (
                False,
                True,
                ["Fragment", "Estimates"],
            ),  # Verbose should include estimates
        ],
    )
    def test_explain(self, titanic_vd_fun, analyze, verbose, expected_content):
        """
        test function - explain
        Tests that explain returns valid query plan with expected content
        """
        res = titanic_vd_fun.explain(analyze=analyze, verbose=verbose)

        # Verify it returns a non-empty string
        assert isinstance(res, str)
        assert len(res) > 0

        # Verify it contains expected Trino plan elements
        for content in expected_content:
            assert content in res, f"Expected '{content}' in explain output"

        # Verify basic structure of Trino explain plan
        # Should contain fragment information
        assert (
            "Fragment" in res or "Output" in res
        ), "Explain plan should contain Fragment or Output information"

    @pytest.mark.parametrize("actions", [0, 1, 2])
    def test_info(self, titanic_vd_fun, actions):
        """
        test function - info
        """
        if actions == 0:
            assert titanic_vd_fun.info() == "The VastFrame was never modified."
        elif actions == 1:
            res = titanic_vd_fun.filter("age > 0")
            assert res.info().startswith(
                "The VastFrame was modified with only one action"
            )
        else:
            res = titanic_vd_fun.filter("age > 0")
            res["fare"].drop_outliers()
            assert res.info().startswith("The VastFrame was modified many times")

    @pytest.mark.skip("Test is not stable")
    @pytest.mark.parametrize(
        "column, expected",
        [(None, 1039)],
    )
    def test_memory_usage(self, amazon_vd, column, expected):
        """
        test function - memory_usage
        """
        # values are not stable
        assert amazon_vd.memory_usage()["value"][0] == pytest.approx(expected, 1e-01)

    @pytest.mark.parametrize(
        "col1, col2, expected",
        [
            (
                "pop",
                0,
                [
                    '"pop"',
                    '"year"',
                    '"country"',
                    '"continent"',
                    '"lifeexp"',
                    '"gdppercap"',
                ],
            ),
            (
                "year",
                "lifeexp",
                [
                    '"country"',
                    '"lifeexp"',
                    '"pop"',
                    '"continent"',
                    '"year"',
                    '"gdppercap"',
                ],
            ),
        ],
    )
    def test_swap(self, gapminder_vd_fun, col1, col2, expected):
        """
        test function - swap two columns
        """
        gapminder_vd_fun.swap(col1, col2)
        swap_columns = gapminder_vd_fun.get_columns()

        assert expected == swap_columns


class TestVDCSys:
    """
    test class for sys functions test for VastColumn class
    """

    def test_add_copy(self, titanic_vd_fun):
        """
        test function - add_copy
        """
        titanic_vd_fun["age"].add_copy(name="copy_age")

        assert titanic_vd_fun["copy_age"].mean() == titanic_vd_fun["age"].mean()

    @pytest.mark.skip("Test is not stable")
    @pytest.mark.parametrize(
        "column, expected",
        [("number", 1724)],
    )
    def test_memory_usage(self, amazon_vd, column, expected):
        """
        test function - memory_usage
        """
        # values are not stable
        assert amazon_vd[column].memory_usage() == pytest.approx(expected, 1e-01)

    def test_store_usage(self, titanic_vd):
        """
        test function - store_usage
        """
        res = titanic_vd["age"].store_usage()
        assert res == pytest.approx(5275, 1e-2)

    def test_rename(self, titanic_vd_fun):
        """
        test function - rename
        """
        columns = titanic_vd_fun["sex"].rename("gender", inplace=False).get_columns()
        assert '"gender"' in columns and '"sex"' not in columns
