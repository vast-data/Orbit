"""
SPDX-License-Identifier: Apache-2.0
"""

from scipy.stats import median_abs_deviation
import pytest


class TestScaler:
    """
    test class for Scale function test
    """

    @pytest.mark.parametrize(
        "columns, method",
        [("age", "zscore"), ("age", "robust_zscore"), ("age", "minmax")],
    )
    def test_scale_vdf(self, titanic_vd, columns, method):
        """
        test function - scaling for VastFrame
        """
        titanic_pdf = titanic_vd.to_pandas()
        titanic_pdf[columns] = titanic_pdf[columns].astype(float)

        py_data = titanic_pdf[[columns]]
        if method == "zscore":
            vo_res = titanic_vd.scale(columns=[columns], method=method)[columns].std()
            py_res = ((py_data - py_data.mean()) / py_data.std()).std()
        elif method == "robust_zscore":
            vo_res = titanic_vd.scale(columns=[columns], method=method)[columns].std()
            py_res = (
                (py_data - py_data.median())
                / (1.4826 * median_abs_deviation(py_data, nan_policy="omit"))
            ).std()
        else:
            vo_res = titanic_vd.scale(columns=[columns], method=method)[columns].mean()
            py_res = (
                (py_data - py_data.min()) / (py_data.max() - py_data.min())
            ).mean()

        print(
            f"method name: {method} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )

        assert vo_res == pytest.approx(py_res, 1e-1)

    @pytest.mark.parametrize(
        "columns, method",
        [("age", "zscore"), ("age", "robust_zscore"), ("age", "minmax")],
    )
    @pytest.mark.parametrize("partition_by", ["pclass", None])
    def test_scale_VastColumn(self, titanic_vd_fun, partition_by, columns, method):
        """
        test function - scaling for VastColumns
        """
        titanic_pdf = titanic_vd_fun.to_pandas()
        titanic_pdf[columns] = titanic_pdf[columns].astype(float)
        py_data = titanic_pdf[[columns]]
        vo_data = titanic_vd_fun[columns]

        if method == "zscore":
            vo_res = vo_data.scale(method=method, by=partition_by)[columns].std()
            py_res = ((py_data - py_data.mean()) / py_data.std()).std()
        elif method == "robust_zscore":
            vo_res = vo_data.scale(method=method)[columns].std()
            # vo_res = _res.std() if partition_by else _res["age"].std()
            py_res = (
                (py_data - py_data.median())
                / (1.4826 * median_abs_deviation(py_data, nan_policy="omit"))
            ).std()
        else:
            vo_res = vo_data.scale(method=method, by=partition_by)[columns].mean()
            py_res = (
                (py_data - py_data.min()) / (py_data.max() - py_data.min())
            ).mean()

        print(
            f"method name: {method} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )

        assert vo_res == pytest.approx(py_res, rel=1e-00, abs=1e-02)
