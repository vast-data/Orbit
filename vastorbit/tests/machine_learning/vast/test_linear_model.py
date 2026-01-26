"""
SPDX-License-Identifier: Apache-2.0
"""

from collections import namedtuple
from decimal import Decimal
import numpy as np
import pytest

import pandas as pd
import sklearn.metrics as skl_metrics

from vastorbit.tests.machine_learning.vast.test_base_model_methods import (
    rel_abs_tol_map,
    REL_TOLERANCE,
    regression_metrics_args,
    model_params,
    model_score,
    anova_report_args,
    details_report_args,
    regression_report_none,
    regression_report_details,
    regression_report_anova,
    calculate_tolerance,
)


@pytest.mark.parametrize(
    "model_class",
    [
        "Ridge",
        "Lasso",
        "ElasticNet",
        "LinearRegression",
        # # "LinearSVR",
        "PoissonRegressor",
        "AR",
        "MA",
        "ARMA",
        "ARIMA",
    ],
)
class TestLinearModel:
    """
    test class - TestLinearModel
    """

    abs_error_report_lr = {}
    model_class_set_lr = set()

    @pytest.mark.parametrize(
        "fit_attr, ts_fit_attr, py_ts_fit_attr",
        [
            ("coef_", "phi_", "arparams"),
            ("intercept_", "intercept_", "params"),
            ("score", "mse_", "mse"),
        ],
    )
    def test_fit(
        self,
        get_vo_model,
        get_py_model,
        model_class,
        fit_attr,
        ts_fit_attr,
        py_ts_fit_attr,
        model_params,
    ):
        """
        test function - fit
        """
        vo_model_obj, py_model_obj = (
            get_vo_model(model_class),
            get_py_model(model_class),
        )
        vo_res, py_res = 0.0, 0.0

        if model_class in ["AR", "MA", "ARMA", "ARIMA"]:
            _model_class_tuple = (
                None
                if model_class in ["DummyTreeRegressor", "DummyTreeClassifier"]
                else namedtuple(model_class, model_params[0])(*model_params[1][0])
            )
            if ts_fit_attr == "phi_":
                vo_res = getattr(vo_model_obj.model, ts_fit_attr)
                py_res = list(getattr(py_model_obj.model, py_ts_fit_attr))
            elif ts_fit_attr == "intercept_":
                if model_class in ["AR"]:
                    pytest.skip(
                        f"statsmodels ARIMA has high intercept value then independent AutoReg{model_class} function"
                    )
                else:
                    pytest.skip(
                        f"VAST {model_class} model does not have {ts_fit_attr} attributes"
                    )
            else:
                vo_model_obj = get_vo_model(model_class)
                vo_res = vo_model_obj.model.score(
                    start=(
                        _model_class_tuple.q
                        if model_class == "MA"
                        else (
                            _model_class_tuple.p
                            if model_class == "AR"
                            else _model_class_tuple.order[0]
                        )
                    ),
                    npredictions=len(vo_model_obj.pred_vdf),
                    metric="mse",
                )

                py_model_obj = get_py_model(model_class, npredictions=None)
                py_res = getattr(skl_metrics, "mean_squared_error")(
                    py_model_obj.y, py_model_obj.pred
                )

            print(f"VAST: {vo_res}, sklearn: {py_res}")
            assert vo_res == pytest.approx(
                py_res, rel=rel_abs_tol_map[model_class][ts_fit_attr]["rel"]
            )
        else:
            if fit_attr == "score":
                vo_res = getattr(vo_model_obj.model, fit_attr)()
                py_res = getattr(py_model_obj.model, fit_attr)(
                    py_model_obj.X, py_model_obj.y
                )
            else:
                vo_res = getattr(vo_model_obj.model, fit_attr)
                py_res = getattr(py_model_obj.model, fit_attr)

            print(f"VAST: {vo_res}, sklearn: {py_res}")
            assert vo_res == pytest.approx(
                py_res, rel=rel_abs_tol_map[model_class][fit_attr]["rel"]
            )
        if (isinstance(vo_res, (list, np.ndarray)) and len(vo_res) > 0) or isinstance(
            vo_res, float
        ):
            _rel_tol, _abs_tol = calculate_tolerance(vo_res, py_res)
            print(
                f"Model_class: {model_class}, Metric_name: {fit_attr}, rel_tol(e): {'%.e' % Decimal(_rel_tol)}, abs_tol(e): {'%.e' % Decimal(_abs_tol)}"
            )

    @pytest.mark.parametrize(*regression_metrics_args)
    @pytest.mark.parametrize("fun_name", ["regression", "report"])
    def test_regression_report_none(
        self,
        get_vo_model,
        get_py_model,
        model_class,
        regression_metrics,
        fun_name,
        vo_metric_name,
        py_metric_name,
        model_params,
    ):
        """
        test function - regression/report None
        """

        vo_score, py_score = regression_report_none(
            get_vo_model,
            get_py_model,
            model_class,
            regression_metrics,
            fun_name,
            vo_metric_name,
            py_metric_name,
            model_params,
        )

        _rel_tol, _abs_tol = calculate_tolerance(vo_score, py_score)
        print(
            f"Model_class: {model_class}, Metric_name: {vo_metric_name}, rel_tol(e): {'%.e' % Decimal(_rel_tol)}, abs_tol(e): {'%.e' % Decimal(_abs_tol)}"
        )

        assert vo_score == pytest.approx(
            py_score, rel=rel_abs_tol_map[model_class][vo_metric_name[0]]["rel"]
        )

    @pytest.mark.parametrize(*details_report_args)
    @pytest.mark.parametrize("fun_name", ["regression", "report"])
    def test_regression_report_details(
        self,
        model_class,
        get_vo_model,
        get_py_model,
        regression_metrics,
        fun_name,
        metric,
        expected,
    ):
        """
        test function - regression/report details
        """
        if model_class in [
            "AR",
            "MA",
            "ARMA",
            "ARIMA",
        ]:
            pytest.skip(
                f"report function with metrics details/anova is not available for {model_class} model"
            )
        else:
            vo_reg_rep_details_map, py_res = regression_report_details(
                model_class,
                get_vo_model,
                get_py_model,
                regression_metrics,
                fun_name,
                metric,
                expected,
            )

            if metric in [
                "Dep. Variable",
                "Model",
                "No. Observations",
                "No. Predictors",
            ]:
                tol = REL_TOLERANCE
            else:
                tol = rel_abs_tol_map[model_class][metric]["rel"]
                _rel_tol, _abs_tol = calculate_tolerance(
                    vo_reg_rep_details_map[metric], py_res
                )
                try:
                    print(
                        f"Model_class: {model_class}, Metric_name: {metric}, rel_tol(e): {'%.e' % Decimal(_rel_tol)}, abs_tol(e): {'%.e' % Decimal(_abs_tol)}"
                    )
                except:
                    print(
                        f"Model_class: {model_class}, Metric_name: {metric}, rel_tol(e): {'%.e' % float(_rel_tol)}, abs_tol(e): {'%.e' % float(_abs_tol)}"
                    )

            if py_res == 0:
                assert vo_reg_rep_details_map[metric] == pytest.approx(
                    py_res, abs=rel_abs_tol_map[model_class][metric]["abs"]
                )
            else:
                assert vo_reg_rep_details_map[metric] == pytest.approx(py_res, rel=tol)

    @pytest.mark.parametrize(*anova_report_args)
    @pytest.mark.parametrize("fun_name", ["regression", "report"])
    def test_regression_report_anova(
        self,
        model_class,
        get_vo_model,
        get_py_model,
        regression_metrics,
        fun_name,
        metric,
        metric_types,
    ):
        """
        test function - regression/report anova
        """
        if model_class in [
            "AR",
            "MA",
            "ARMA",
            "ARIMA",
        ]:
            pytest.skip(
                f"report function with metrics details/anova is not available for {model_class} model"
            )
        else:
            reg_rep_anova, regression_metrics_map = regression_report_anova(
                model_class,
                get_vo_model,
                get_py_model,
                regression_metrics,
                fun_name,
            )

            for vo_res, metric_type in zip(reg_rep_anova[metric], metric_types):
                py_res = regression_metrics_map[metric_type]

                if metric_type != "":
                    _rel_tol, _abs_tol = calculate_tolerance(vo_res, py_res)
                    try:
                        print(
                            f"Model_class: {model_class}, Metric_name: {metric}, Metric_type: {metric_type}, rel_tol(e): {'%.e' % Decimal(_rel_tol)}, abs_tol(e): {'%.e' % Decimal(_abs_tol)}"
                        )
                    except:
                        print(
                            f"Model_class: {model_class}, Metric_name: {metric}, Metric_type: {metric_type}, rel_tol(e): {'%.e' % float(_rel_tol)}, abs_tol(e): {'%.e' % float(_abs_tol)}"
                        )

                    if py_res == 0:
                        assert vo_res == pytest.approx(py_res, abs=1e-9)
                    else:
                        assert vo_res == pytest.approx(
                            py_res, rel=rel_abs_tol_map[model_class][metric]["rel"]
                        )

    @pytest.mark.parametrize(*regression_metrics_args)
    def test_score(
        self,
        model_class,
        get_vo_model,
        get_py_model,
        regression_metrics,
        vo_metric_name,
        py_metric_name,
        model_params,
        request,
    ):
        """
        test function - test_score
        """
        vo_score, py_score = model_score(
            model_class,
            get_vo_model,
            get_py_model,
            regression_metrics,
            vo_metric_name,
            py_metric_name,
            model_params,
        )

        _rel_tol, _abs_tol = calculate_tolerance(vo_score, py_score)

        self.abs_error_report_lr[(model_class, py_metric_name)] = {
            "Model_class": model_class,
            "Metric_name": (
                py_metric_name.title()
                if "_" in py_metric_name
                else py_metric_name.upper()
            ),
            "rel_tol": _rel_tol,
            "abs_tol": _abs_tol,
            "rel_tol(e)": "%.e" % Decimal(_rel_tol),
            "abs_tol(e)": "%.e" % Decimal(_abs_tol),
            "Absolute_percentage_difference": (
                (vo_score - py_score) / (py_score if py_score else 1e-15)
            )
            * 100,
        }
        print(self.abs_error_report_lr[(model_class, py_metric_name)])

        self.model_class_set_lr.add(model_class)
        tc_count = (len(request.node.keywords["pytestmark"][0].args[1])) * len(
            self.model_class_set_lr
        )
        print(len(self.abs_error_report_lr.keys()), tc_count)

        if len(self.abs_error_report_lr.keys()) == tc_count:
            abs_error_report_lr_pdf = (
                pd.DataFrame(self.abs_error_report_lr.values())
                .sort_values(by=["Model_class", "Metric_name"])
                .reset_index(drop=True)
            )
            abs_error_report_lr_pdf.to_csv("abs_error_report_lr.csv", index=False)

        assert vo_score == pytest.approx(
            py_score, rel=rel_abs_tol_map[model_class][vo_metric_name[0]]["rel"]
        )
