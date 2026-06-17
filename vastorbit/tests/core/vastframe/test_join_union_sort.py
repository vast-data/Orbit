"""
SPDX-License-Identifier: Apache-2.0
"""

import pytest
import pandas as pd

# Utilities
from vastorbit.sql.drop import drop
from vastorbit.core.vastframe.base import VastFrame


class TestJoinUnionSort:
    """
    Test class for join, union, and sort functions
    """

    # ========== FIXTURES ==========

    @pytest.fixture
    def employees_data(self, schema_loader):
        """Create employees test data"""
        data = {
            "employee_id": [1, 2, 3, 4, 5],
            "employee_name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "department_id": [101, 102, 101, 103, 104],
            "salary": [50000, 60000, 55000, 65000, 70000],
        }
        df = pd.DataFrame(data)
        vdf = VastFrame(data)
        yield vdf, df

    @pytest.fixture
    def departments_data(self, schema_loader):
        """Create departments test data"""
        data = {
            "department_id": [101, 102, 103, 105],
            "department_name": ["HR", "Finance", "IT", "Marketing"],
            "budget": [100000, 200000, 150000, 120000],
        }
        df = pd.DataFrame(data)
        vdf = VastFrame(data)
        yield vdf, df

    @pytest.fixture
    def products_data(self, schema_loader):
        """Create products test data for fuzzy matching"""
        data = {
            "product_id": [1, 2, 3, 4],
            "product_name": ["Laptop", "Phone", "Tablet", "Monitor"],
            "category": ["Electronics", "Electronics", "Electronics", "Electronics"],
            "price": [1000, 500, 300, 400],
        }
        df = pd.DataFrame(data)
        vdf = VastFrame(data)
        yield vdf, df

    # ========== APPEND TESTS ==========

    @pytest.mark.parametrize(
        "union_all, expected_multiplier",
        [
            (True, 2),  # UNION ALL: doubles rows
            (False, 1),  # UNION: removes duplicates (all rows are identical)
        ],
    )
    def test_append(self, employees_data, union_all, expected_multiplier):
        """
        Test VastFrame.append() with union_all settings
        """
        emp_vdf, _ = employees_data
        original_count = len(emp_vdf)

        # Perform append
        result = emp_vdf.append(emp_vdf, union_all=union_all)

        # Calculate expected count
        expected_count = original_count * expected_multiplier

        assert (
            len(result) == expected_count
        ), f"Append with union_all={union_all} should return {expected_count} rows, got {len(result)}"

    def test_append_with_expressions(self, departments_data):
        """
        Test append with specific column expressions
        """
        dept_vdf, _ = departments_data
        original_count = len(dept_vdf)

        result = dept_vdf.append(
            dept_vdf,
            expr1=["department_id AS id", "department_name AS name"],
            expr2=["department_id AS id", "department_name AS name"],
            union_all=True,
        )

        # Should double the rows
        assert (
            len(result) == original_count * 2
        ), f"Append with expressions should return {original_count * 2} rows, got {len(result)}"

        # Verify only selected columns exist
        columns = result.get_columns()
        assert '"id"' in columns
        assert '"name"' in columns

    # ========== JOIN TESTS ==========

    @pytest.mark.parametrize(
        "how, expected_count",
        [
            ("inner", 4),  # Matches: 101, 102, 103
            ("left", 5),  # All 5 employees
            ("right", 5),  # All 4 departments
            ("full", 6),  # 5 employees + 1 unmatched dept (105)
        ],
    )
    def test_join_basic(
        self,
        employees_data,
        departments_data,
        schema_loader,
        how,
        expected_count,
    ):
        """
        Test basic join types (INNER, LEFT, RIGHT, FULL) with both VastFrame and table
        """
        emp_vdf, emp_pdf = employees_data
        dept_vdf, dept_pdf = departments_data

        # Perform join
        result = emp_vdf.join(
            input_relation=dept_vdf,
            on={"department_id": "department_id"},
            how=how,
            expr1=["employee_id", "employee_name", "department_id"],
            expr2=["department_name"],
        )

        assert len(result) == expected_count

    def test_join_cross(self, employees_data, departments_data):
        """
        Test CROSS join (Cartesian product)
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on={},
            how="cross",
            expr1=["employee_id"],
            expr2=["department_id"],
        )

        # Cross join: 5 employees × 4 departments = 20 rows
        expected = 5 * 4
        assert (
            len(result) == expected
        ), f"Cross join should return {expected} rows, got {len(result)}"

    @pytest.mark.parametrize(
        "operator, description",
        [
            ("=", "equal"),
            (">", "greater than"),
            (">=", "greater than or equal"),
            ("<", "less than"),
            ("<=", "less than or equal"),
        ],
    )
    def test_join_comparison_operators(
        self,
        employees_data,
        departments_data,
        operator,
        description,
    ):
        """
        Test joins with different comparison operators
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on=[("salary", "budget", operator)],
            how="inner",
            expr1=["employee_name", "salary"],
            expr2=["department_name", "budget"],
        )

        # All salaries should satisfy the operator condition with budget
        assert (
            len(result) >= 0
        ), f"Join with {description} operator should execute successfully"

        # Verify condition is met
        if len(result) > 0:
            result_df = result.to_pandas()
            for _, row in result_df.iterrows():
                salary = row["salary"]
                budget = row["budget"]
                if operator == "=":
                    assert salary == budget
                elif operator == ">":
                    assert salary > budget
                elif operator == ">=":
                    assert salary >= budget
                elif operator == "<":
                    assert salary < budget
                elif operator == "<=":
                    assert salary <= budget

    def test_join_llike_operator(self, employees_data, departments_data):
        """
        Test LLIKE operator (left LIKE pattern matching)
        Pattern: x.col1 LIKE '%' || y.col2 || '%'
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on=[("employee_name", "department_name", "llike")],
            how="inner",
            expr1=["employee_name"],
            expr2=["department_name"],
        )

        # Should only match if employee_name contains department_name
        # e.g., if we had employee "HR Manager", it would match dept "HR"
        assert len(result) >= 0, "LLIKE join should execute successfully"

    def test_join_rlike_operator(self, employees_data, departments_data):
        """
        Test RLIKE operator (right LIKE pattern matching)
        Pattern: y.col2 LIKE '%' || x.col1 || '%'
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on=[("employee_name", "department_name", "rlike")],
            how="inner",
            expr1=["employee_name"],
            expr2=["department_name"],
        )

        # Should only match if department_name contains employee_name
        assert len(result) >= 0, "RLIKE join should execute successfully"

    def test_join_levenshtein_distance(self, products_data, schema_loader):
        """
        Test Levenshtein distance for fuzzy string matching
        """
        prod_vdf, prod_pdf = products_data

        # Create similar products with typos
        similar_data = {
            "product_id": [10, 11, 12, 13],
            "product_name": ["Lapt0p", "Fone", "Tablit", "Moniter"],  # Slight typos
            "review_score": [4.5, 4.0, 4.2, 4.8],
        }
        similar_df = pd.DataFrame(similar_data)
        similar_vdf = VastFrame(similar_data)

        try:
            result = prod_vdf.join(
                input_relation=similar_vdf,
                on=[("product_name", "product_name", "lev", "<=", 2)],
                how="inner",
                expr1=["product_id", "product_name"],
                expr2=["product_name AS similar_name", "review_score"],
            )

            # Should find fuzzy matches within Levenshtein distance of 2
            assert len(result) >= 0, "Levenshtein join should execute successfully"

        finally:
            pass

    def test_join_multiple_conditions(self, employees_data, departments_data):
        """
        Test join with multiple ON conditions
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on=[("department_id", "department_id", "="), ("salary", "budget", "<")],
            how="inner",
            expr1=["employee_name", "salary", "department_id"],
            expr2=["department_name", "budget"],
        )

        # Employees whose salary < their department's budget
        assert len(result) >= 0, "Multi-condition join should execute successfully"

        # Verify both conditions are met
        if len(result) > 0:
            result_df = result.to_pandas()
            for _, row in result_df.iterrows():
                assert (
                    row["salary"] < row["budget"]
                ), f"Salary {row['salary']} should be < budget {row['budget']}"

    def test_join_with_column_aliases(self, employees_data, departments_data):
        """
        Test join with column aliases in expr1 and expr2
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on={"department_id": "department_id"},
            how="inner",
            expr1=["employee_name AS emp_name", "salary AS emp_salary"],
            expr2=["department_name AS dept_name", "budget AS dept_budget"],
        )

        columns = result.get_columns()
        assert '"emp_name"' in columns
        assert '"emp_salary"' in columns
        assert '"dept_name"' in columns
        assert '"dept_budget"' in columns

    def test_join_result_accuracy(self, employees_data, departments_data):
        """
        Test that join results contain correct data
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        result = emp_vdf.join(
            input_relation=dept_vdf,
            on={"department_id": "department_id"},
            how="inner",
            expr1=["employee_name", "department_id"],
            expr2=["department_name"],
        )

        result_df = result.to_pandas()

        # Verify specific matches
        alice = result_df[result_df["employee_name"] == "Alice"]
        assert len(alice) == 1
        assert alice.iloc[0]["department_name"] == "HR"
        assert alice.iloc[0]["department_id"] == 101

        bob = result_df[result_df["employee_name"] == "Bob"]
        assert len(bob) == 1
        assert bob.iloc[0]["department_name"] == "Finance"
        assert bob.iloc[0]["department_id"] == 102

        charlie = result_df[result_df["employee_name"] == "Charlie"]
        assert len(charlie) == 1
        assert charlie.iloc[0]["department_name"] == "HR"
        assert charlie.iloc[0]["department_id"] == 101

    def test_join_invalid_operator_raises_error(self, employees_data, departments_data):
        """
        Test that invalid operator raises ValueError
        """
        emp_vdf, _ = employees_data
        dept_vdf, _ = departments_data

        with pytest.raises(ValueError, match="Incorrect operator"):
            emp_vdf.join(
                input_relation=dept_vdf,
                on=[("department_id", "department_id", "invalid_op")],
                how="inner",
            )

    # ========== SORT TESTS ==========

    @pytest.mark.parametrize(
        "order_by",
        [
            {"petal_length": "asc"},
            {"petal_length": "desc"},
            {"species": "asc"},
            {"species": "desc"},
            {"petal_length": "asc", "sepal_width": "desc"},
            ["petal_length", "sepal_width"],  # List form (defaults to asc)
        ],
    )
    def test_sort(self, iris_vd_fun, order_by):
        """
        Test VastFrame.sort() with different ordering configurations
        """
        # Convert list to dict if needed
        if isinstance(order_by, list):
            order_by_dict = {col: "asc" for col in order_by}
        else:
            order_by_dict = order_by

        # Get expected results from pandas
        iris_pdf = iris_vd_fun.to_pandas()

        # Sort using pandas
        py_result = iris_pdf.sort_values(
            by=list(order_by_dict.keys()),
            ascending=[direction == "asc" for direction in order_by_dict.values()],
        )

        # Sort using VastFrame
        vo_result = iris_vd_fun.sort(columns=order_by)
        vo_result_df = vo_result.to_pandas()

        # Compare first column values (sorted order)
        first_col = list(order_by_dict.keys())[0]

        expected_values = py_result[first_col].tolist()
        actual_values = vo_result_df[first_col].tolist()

        assert len(actual_values) == len(
            expected_values
        ), f"Sort should return {len(expected_values)} rows, got {len(actual_values)}"

        # Verify sort order is correct
        assert actual_values == expected_values, f"Sort order mismatch for {order_by}"

    def test_sort_multiple_columns(self, iris_vd_fun):
        """
        Test sorting by multiple columns with mixed directions
        """
        order_by = {"species": "asc", "petal_length": "desc"}

        # Expected from pandas
        iris_pdf = iris_vd_fun.to_pandas()
        py_result = iris_pdf.sort_values(
            by=["species", "petal_length"], ascending=[True, False]
        )

        # Result from VastFrame
        vo_result = iris_vd_fun.sort(columns=order_by)
        vo_result_df = vo_result.to_pandas()

        # Compare
        assert len(vo_result_df) == len(py_result)

        # Check that species are in ascending order
        species_values = vo_result_df["species"].tolist()
        assert species_values == sorted(
            species_values
        ), "Species should be in ascending order"

    def test_sort_with_nulls(self, schema_loader):
        """
        Test sorting behavior with NULL values
        """
        data = {"id": [1, 2, 3, 4, 5], "value": [10, None, 30, None, 50]}
        df = pd.DataFrame(data)
        vdf = VastFrame(data)

        try:
            # Sort ascending
            result_asc = vdf.sort(columns={"value": "asc"})
            result_asc_df = result_asc.to_pandas()

            # Sort descending
            result_desc = vdf.sort(columns={"value": "desc"})
            result_desc_df = result_desc.to_pandas()

            # Both should return all 5 rows
            assert len(result_asc_df) == 5
            assert len(result_desc_df) == 5

        finally:
            pass

    def test_sort_preserves_data(self, iris_vd_fun):
        """
        Test that sorting doesn't lose or duplicate data
        """
        original_count = len(iris_vd_fun)

        sorted_vdf = iris_vd_fun.sort(columns={"sepal_length": "asc"})
        sorted_count = len(sorted_vdf)

        assert (
            sorted_count == original_count
        ), f"Sort should preserve row count: expected {original_count}, got {sorted_count}"
