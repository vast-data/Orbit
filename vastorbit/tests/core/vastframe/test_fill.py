"""
SPDX-License-Identifier: Apache-2.0
"""

import datetime
import pandas as pd
import pytest


class TestFill:
    """
    test class for fill function test
    """

    @pytest.mark.parametrize(
        "column, val, method",
        [
            (
                "age",
                None,
                {"age": "mean"},
            ),
            (
                "boat",
                None,
                {"boat": "mode"},
            ),
            (
                "fare",
                None,
                {"fare": "median"},
            ),
            (
                "body",
                None,
                {"body": "0ifnull"},
            ),
            (
                "cabin",
                None,
                {"cabin": "auto"},
            ),
            # (
            #     "boat",
            #     {"boat": "No boat"},
            #     None,
            # ),
        ],
    )
    @pytest.mark.parametrize(
        "function_type, numeric_only, expr, by, order_by",
        [
            ("VastFrame", None, None, None, None),
            ("VastColumn", None, None, None, None),
        ],
    )
    def test_fillna(
        self,
        titanic_vd,
        function_type,
        column,
        val,
        method,
        numeric_only,
        expr,
        by,
        order_by,
    ):
        """
        test function - fillna
        """
        titanic_pdf = titanic_vd.to_pandas()
        titanic_pdf["age"] = titanic_pdf["age"].astype(float)

        if function_type == "VastFrame":
            vo_res = titanic_vd.fillna(
                val=val, method=method, numeric_only=numeric_only
            )[column]
        else:
            vo_res = titanic_vd[column].fillna(
                val=val, method=method[column], expr=expr, by=by, order_by=order_by
            )[column]

        if method[column] == "auto":
            method[column] = (
                "mean" if titanic_vd[column].dtype().startswith("decimal") else "mode"
            )

        if method[column] == "mode":
            titanic_pdf[column] = eval(
                f"titanic_pdf[column].fillna(titanic_pdf[column].{method[column]}()[0])"
            )
        elif method[column] == "0ifnull":
            titanic_pdf[[column]] = titanic_pdf[[column]].applymap(
                lambda x: 0 if pd.isnull(x) else 1
            )
        else:
            titanic_pdf[column] = eval(
                f"titanic_pdf[column].fillna(titanic_pdf[column].{method[column]}())"
            )
        py_res = titanic_pdf[column]

        if titanic_vd[column].dtype().startswith("decimal"):
            vo_res = vo_res.sum()
            py_res = py_res.sum()
        else:
            vo_res = vo_res.count()
            py_res = py_res.count()

        print(
            f"method name: {method[column]} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )

        assert vo_res == pytest.approx(py_res)

    @pytest.mark.parametrize(
        "ts, rule, method, by, expected",
        [
            ("time", "10 hour", "bfill", "id", [10, 0, 1.147]),
            ("time", "10 hour", "ffill", "id", [10, 0, 0.029]),
            ("time", "10 hour", "linear", "id", [10, 0, 0.5880000000000001]),
        ],
    )
    def test_interpolate(self, smart_meters_vd, ts, rule, method, by, expected):
        """
        test function - interpolate
        """
        vo_res = smart_meters_vd.interpolate(
            ts=ts, rule=rule, method={"val": method}, by=[by]
        )
        vo_res.sort({"id": "asc", "time": "asc"})

        assert (vo_res["time"][3] - vo_res["time"][2]) == datetime.timedelta(
            hours=expected[0]
        )
        assert vo_res["id"][2] == expected[1]
        assert vo_res["val"][2] == pytest.approx(expected[2])

    def test_clip(self, market_vd):
        """
        test function - clip
        """
        market_pdf = market_vd.to_pandas()
        vo_res = market_vd["price"].clip(lower=1.0, upper=4.0)["price"].mean()
        py_res = market_pdf["price"].clip(1.0, 4.0).mean()

        print(
            f"method name: 'Clip' \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )

        assert vo_res == pytest.approx(py_res)

    @pytest.mark.parametrize(
        "column, method, threshold, use_threshold, alpha",
        [
            ("price", "null", 0.4, True, 0.05),
            ("price", "winsorize", 0.4, True, 0.05),
            ("price", "winsorize", None, False, 0.2),
            ("price", "mean", 0.4, True, 0.05),
            ("price", "mean", 0.4, True, 0.05),
        ],
    )
    def test_fill_outliers(
        self, market_vd, column, method, threshold, use_threshold, alpha
    ):
        """
        test function - fill_outliers
        """
        market_pdf = market_vd.to_pandas()
        py_data = market_pdf[[column]]

        if use_threshold:
            lower_limit = -threshold * py_data[column].std() + py_data[column].mean()
            upper_limit = threshold * py_data[column].std() + py_data[column].mean()
        else:
            lower_limit, upper_limit = (
                py_data.quantile(alpha)[column],
                py_data.quantile(1 - alpha)[column],
            )

        if method == "null":
            lower_limit_val = upper_limit_val = None
        elif method == "winsorize":
            lower_limit_val, upper_limit_val = lower_limit, upper_limit
        else:
            lower_limit_val, upper_limit_val = (
                py_data.loc[py_data[column] < lower_limit].mean()[column],
                py_data.loc[py_data[column] > upper_limit].mean()[column],
            )

        vo_res = (
            market_vd[column]
            .fill_outliers(
                method=method,
                threshold=threshold,
                use_threshold=use_threshold,
                alpha=alpha,
            )[column]
            .mean()
        )

        py_res = py_data.apply(
            lambda x: (
                lower_limit_val
                if x[column] < lower_limit
                else (upper_limit_val if x[column] > upper_limit else x[column])
            ),
            axis=1,
        ).mean()

        print(
            f"method name: {'method'} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )

        assert vo_res == pytest.approx(py_res)
