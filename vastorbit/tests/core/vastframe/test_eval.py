"""
SPDX-License-Identifier: Apache-2.0
"""

from itertools import chain
import pytest


class TestEval:
    """
    test class for eval functions test
    """

    @pytest.mark.parametrize(
        "column, expr",
        [
            ("family_size", "parch + sibsp + 1"),
            ("missing_cabins", "CASE WHEN cabin IS NULL THEN 'missing' ELSE cabin END"),
        ],
    )
    def test_eval(self, titanic_vd, column, expr):
        """
        test function - evaluate expression
        """
        titanic_pdf = titanic_vd.to_pandas()
        vo_res = list(
            chain(*titanic_vd.eval(name=column, expr=expr)[[column]].to_list())
        )

        if column == "missing_cabins":
            titanic_pdf["cabin"] = titanic_pdf["cabin"].apply(
                lambda row: row if row is not None else "missing"
            )
            py_res = titanic_pdf["cabin"].values.tolist()
        else:
            py_res = titanic_pdf.eval(expr=f"{column}={expr}")[column].values.tolist()

        # Sort both lists to make comparison order-independent
        assert sorted(vo_res) == sorted(py_res)
