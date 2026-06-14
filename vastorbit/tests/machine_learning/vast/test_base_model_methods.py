"""
SPDX-License-Identifier: Apache-2.0
"""

from collections import namedtuple
from decimal import Decimal
import os
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pytest
import plotly
from scipy import stats

import vastorbit as vo
from vastorbit.connection import current_cursor
from vastorbit.tests.machine_learning.vast import (
    REL_TOLERANCE,
    rel_abs_tol_map,
    REGRESSION_MODELS,
    CLASSIFICATION_MODELS,
    TIMESERIES_MODELS,
    CLUSTER_MODELS,
)
from vastorbit.tests.machine_learning.vast.model_utils import (
    get_model_attributes,
    get_train_function,
    get_predict_function,
    get_xy,
)
from vastorbit.machine_learning.vast.base import VASTModel
from vastorbit.connection.errors import QueryError

details_report_args = (
    "metric, expected",
    [
        ("Dep. Variable", '"quality"'),
        ("Model", "LinearRegression"),
        ("No. Observations", None),
        ("No. Predictors", None),
        ("R-squared", None),
        ("Adj. R-squared", None),
        ("F-statistic", None),
        ("Prob (F-statistic)", None),
        ("Kurtosis", None),
        ("Skewness", None),
        ("Jarque-Bera (JB)", None),
    ],
)
anova_report_args = (
    "metric, metric_types",
    [
        ("df", ("dfr", "dfe")),
        ("ss", ("ssr", "sse")),
        ("ms", ("msr", "mse")),
        ("f", ("f", "")),
        ("p_value", ("p_value", "")),
    ],
)

regression_metrics_args = (
    "vo_metric_name, py_metric_name",
    [
        (("explained_variance", None), "explained_variance_score"),
        (("max_error", None), "max_error"),
        (("median_absolute_error", None), "median_absolute_error"),
        (("mean_absolute_error", None), "mean_absolute_error"),
        (("mean_squared_error", None), "mean_squared_error"),
        (("mean_squared_log_error", None), "mean_squared_log_error"),
        (("rmse", "root_mean_squared_error"), "rmse"),
        (("r2", None), "r2_score"),
        (("r2_adj", None), "rsquared_adj"),
        (("aic", None), "aic"),
        (("bic", None), "bic"),
    ],
)

classification_metrics_args = (
    "vo_metric_name, py_metric_name",
    [
        (("auc", None), "auc"),
        (("prc_auc", None), "prc_auc"),
        (("accuracy", None), "accuracy_score"),
        # VAST uses log base 10, sklean uses natural log(e)
        (("log_loss", None), "log_loss"),
        (("precision", None), "precision_score"),
        (("recall", None), "recall_score"),
        (("f1_score", None), "f1_score"),
        (("mcc", None), "matthews_corrcoef"),
        # (("informedness", None), "informedness"), # getting mismatch for xgb
        (("markedness", None), "markedness"),
        (("csi", None), "critical_success_index"),
    ],
)


@pytest.fixture
def model_params(model_class):
    """
    fixture - model parameters
    """
    model_params_map = {
        "RandomForestRegressor": (
            "n_estimators, max_features, max_leaf_nodes, sample, max_depth, min_samples_leaf, min_info_gain, nbins",
            [
                # (None, None, None, None, None, None, None, None),  # accuracy does not mach with default parameters
                (10, 1, 10, 0.632, 5, 1, None, None),
                # (5, 'max', 1e6, 0.42, 6, 8, 0.3, 20),
            ],
        ),
        "RandomForestClassifier": (
            "n_estimators, max_features, max_leaf_nodes, sample, max_depth, min_samples_leaf, min_info_gain, nbins",
            [
                # (None, None, None, None, None, None, None, None),  # accuracy does not mach with default parameters
                (10, 2, 10, 0.632, 10, 1, None, None),
                # (5, 'max', 1e6, 0.42, 6, 8, 0.3, 20),
            ],
        ),
        "DecisionTreeRegressor": (
            "max_features, max_leaf_nodes, max_depth, min_samples_leaf, min_info_gain, nbins",
            [
                # (None, None, None, None, None, None, None, None),  # accuracy does not mach with default parameters
                (1, 10, 5, 1, None, None),
                # (5, 'max', 1e6, 0.42, 6, 8, 0.3, 20),
            ],
        ),
        "DecisionTreeClassifier": (
            "max_features, max_leaf_nodes, max_depth, min_samples_leaf, min_info_gain, nbins",
            [
                # (None, None, None, None, None, None, None, None),  # accuracy does not mach with default parameters
                (1, 10, 5, 1, None, None),
                # (5, 'max', 1e6, 0.42, 6, 8, 0.3, 20),
            ],
        ),
        "XGBRegressor": (
            "max_ntree, max_depth, nbins, learning_rate, min_split_loss, weight_reg, sample, col_sample_by_tree, col_sample_by_node",
            [
                # (None, None, None, None, None, None, None, None),  # accuracy does not mach with default parameters
                (10, 5, 32, 0.1, 0.0, 0.0, 1.0, 1.0, 1.0),
                # (5, 'max', 1e6, 0.42, 6, 8, 0.3, 20),
            ],
        ),
        "XGBClassifier": (
            "max_ntree, max_depth, nbins, learning_rate, min_split_loss, weight_reg, sample, col_sample_by_tree, col_sample_by_node",
            [
                # (None, None, None, None, None, None, None, None),  # accuracy does not mach with default parameters
                (10, 5, 32, 0.1, 0.0, 0.0, 1.0, 1.0, 1.0),
                # (5, 'max', 1e6, 0.42, 6, 8, 0.3, 20),
            ],
        ),
        "DummyTreeRegressor": (),
        "DummyTreeClassifier": (),
        "Ridge": (
            "tol, c, max_iter, solver, fit_intercept",
            [
                (1e-6, 1, 100, "bfgs", True),
                (1e-4, 0.99, 200, "newton", False),
            ],
        ),
        "Lasso": (
            "tol, c, max_iter, solver, fit_intercept",
            [
                # (1e-6, 1, 100, 'bfgs', True), # bfgs not supported
                # (1e-4, 0.99, 200, 'newton', False), # newton not supported
                (1e-4, 1, 200, "cgd", False)
            ],
        ),
        "ElasticNet": (
            "tol, c, max_iter, solver, l1_ratio, fit_intercept",
            [
                # (1e-6, 1, 100, 'bfgs', 0.5, True), # bfgs not supported
                # (1e-4, 0.99, 200, 'newton', 0.9, False), # newton not supported
                (
                    1e-4,
                    1,
                    200,
                    "cgd",
                    0.5,
                    True,
                )  # l1_ratio 0.4 not matches with python
            ],
        ),
        "LinearRegression": (
            "tol, max_iter, solver, fit_intercept",
            [
                (1e-6, 100, "bfgs", True),
                (1e-4, 200, "newton", False),
                (1e-4, 200, "cgd", False),
            ],
        ),
        "LinearSVR": (
            "tol, c, intercept_scaling, intercept_mode, acceptable_error_margin, max_iter",
            [
                (1e-6, 1, 1, "regularized", 0.1, 100),
                (1e-4, 1, 0.6, "unregularized", 0, 200),
                (1e-4, 1, 0, "regularized", 1, 400),
                (1e-4, 1, 3, "unregularized", 0.5, 500),
            ],
        ),
        "PoissonRegressor": (
            "tol, penalty, c, max_iter, solver, fit_intercept",
            [
                (1e-6, "l2", 1, 100, "newton", True),
            ],
        ),
        "AR": (
            "p, method, penalty, c, missing, npredictions",
            [
                (3, "ols", "none", 1, "linear_interpolation", 144),
            ],
        ),
        "MA": (
            "q, penalty, c, missing, npredictions",
            [
                (1, "none", 1, "linear_interpolation", 144),
            ],
        ),
        "ARMA": (
            "order, tol, max_iter, init, missing, npredictions",
            [
                ((2, 0, 1), 1e-6, 100, "zero", "linear_interpolation", 144),
            ],
        ),
        "ARIMA": (
            "order, tol, max_iter, init, missing, npredictions",
            [
                ((2, 1, 1), 1e-6, 100, "zero", "linear_interpolation", 144),
            ],
        ),
    }

    return model_params_map[model_class]


def calculate_tolerance(vo_score, py_score):
    """
    function to calculate tolerance for a given model
    """
    if isinstance(vo_score, (list, np.ndarray)):
        vo_score, py_score = vo_score[0], py_score[0]

    _rel_tol = abs(vo_score - py_score) / min(abs(vo_score), abs(py_score))
    _abs_tol = abs(vo_score - py_score) / (1 + min(abs(vo_score), abs(py_score)))

    try:
        print(
            f"rel_tol(e): {'%.e' % Decimal(_rel_tol)}, abs_tol(e): {'%.e' % Decimal(_abs_tol)}"
        )
    except:
        print(
            f"rel_tol(e): {'%.e' % float(_rel_tol)}, abs_tol(e): {'%.e' % float(_abs_tol)}"
        )

    return _rel_tol, _abs_tol


def regression_report_none(
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
    _model_class_tuple = (
        None
        if model_class in ["DummyTreeRegressor", "DummyTreeClassifier"]
        else namedtuple(model_class, model_params[0])(*model_params[1][0])
    )
    vo_model_obj = get_vo_model(model_class)

    if model_class in TIMESERIES_MODELS:
        if model_class == "AR":
            p_val = _model_class_tuple.p
        elif model_class == "MA":
            p_val = _model_class_tuple.q
        else:
            p_val = _model_class_tuple.order[0]

        reg_rep = (
            vo_model_obj.model.report(
                start=p_val,
                npredictions=_model_class_tuple.npredictions,
            )
            if fun_name == "report"
            else vo_model_obj.model.regression_report(
                start=p_val,
                npredictions=_model_class_tuple.npredictions,
            )
        )
    else:
        reg_rep = (
            vo_model_obj.model.report()
            if fun_name == "report"
            else vo_model_obj.model.regression_report()
        )
    vo_rep_map = dict(zip(reg_rep["index"], reg_rep["value"]))

    if vo_metric_name[0] in vo_rep_map or vo_metric_name[1] in vo_rep_map:
        vo_score = vo_rep_map[
            vo_metric_name[0] if vo_metric_name[1] is None else vo_metric_name[1]
        ]
    else:
        pytest.skip(f"{vo_metric_name[0]} metric is not applicable for {model_class}")

    if model_class in [
        "RandomForestRegressor",
        "DecisionTreeRegressor",
        "DummyTreeRegressor",
        "XGBRegressor",
    ]:
        py_model_obj = get_py_model(model_class)
        regression_metrics_map = regression_metrics(model_class, model_obj=py_model_obj)
    else:
        # py_model_obj = get_py_model(model_class)
        regression_metrics_map = regression_metrics(model_class)

    py_score = regression_metrics_map[py_metric_name]

    print(
        f"Metric Name: {vo_metric_name, py_metric_name}, VAST: {vo_score}, sklearn: {py_score}"
    )

    return vo_score, py_score


def regression_report_details(
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
    vo_model_obj = get_vo_model(model_class)

    reg_rep_details = (
        vo_model_obj.model.report(metrics="details")
        if fun_name == "report"
        else vo_model_obj.model.regression_report(metrics="details")
    )
    vo_reg_rep_details_map = dict(
        zip(reg_rep_details["index"], reg_rep_details["value"])
    )

    # Python
    if model_class in [
        "RandomForestRegressor",
        "DecisionTreeRegressor",
        "DummyTreeRegressor",
        "XGBRegressor",
    ]:
        py_model_obj = get_py_model(model_class)
        regression_metrics_map = regression_metrics(model_class, model_obj=py_model_obj)
    else:
        py_model_obj = get_py_model(model_class)
        regression_metrics_map = regression_metrics(model_class)

    if metric == "No. Observations":
        py_res = len(py_model_obj.y)
    elif metric == "Model":
        if model_class == "RandomForestRegressor":
            py_res = "RandomForestRegressor"
        elif model_class == "DecisionTreeRegressor":
            py_res = "RandomForestRegressor"  # need to check on this
        elif model_class == "XGBRegressor":
            py_res = "XGBRegressor"  # need to check on this
        elif model_class == "DummyTreeRegressor":
            py_res = "DummyTreeRegressor"
        elif model_class == "LinearSVR":
            py_res = "LinearSVR"
        elif model_class == "PoissonRegressor":
            py_res = "PoissonRegressor"
        elif model_class == "ElasticNet":
            py_res = "ElasticNet"
        elif model_class == "Lasso":
            py_res = "Lasso"
        elif model_class == "Ridge":
            py_res = "Ridge"
        else:
            py_res = "LinearRegression"
    elif metric == "No. Predictors":
        py_res = len(py_model_obj.X.columns)
    elif metric == "R-squared":
        py_res = regression_metrics_map["r2_score"]
    elif metric == "Adj. R-squared":
        py_res = regression_metrics_map["rsquared_adj"]
    elif metric == "F-statistic":
        py_res = regression_metrics_map["f"]
    elif metric == "Prob (F-statistic)":
        py_res = regression_metrics_map["p_value"]
    elif metric == "Kurtosis":
        py_res = stats.kurtosis(py_model_obj.y)
    elif metric == "Skewness":
        py_res = stats.skew(py_model_obj.y)
    elif metric == "Jarque-Bera (JB)":
        py_res = stats.jarque_bera(py_model_obj.y).statistic
    else:
        py_res = expected

    return vo_reg_rep_details_map, py_res


def regression_report_anova(
    model_class,
    get_vo_model,
    get_py_model,
    regression_metrics,
    fun_name,
):
    """
    test function - regression/report anova
    """
    vo_model_obj = get_vo_model(model_class)

    reg_rep_anova = (
        vo_model_obj.model.report(metrics="anova")
        if fun_name == "report"
        else vo_model_obj.model.regression_report(metrics="anova")
    )

    # Python
    if model_class in [
        "RandomForestRegressor",
        "DecisionTreeRegressor",
        "DummyTreeRegressor",
        "XGBRegressor",
    ]:
        py_model_obj = get_py_model(model_class)
        regression_metrics_map = regression_metrics(model_class, model_obj=py_model_obj)
    else:
        regression_metrics_map = regression_metrics(model_class)

    return reg_rep_anova, regression_metrics_map


def model_score(
    model_class,
    get_vo_model,
    get_py_model,
    _metrics,
    vo_metric_name,
    py_metric_name,
    model_params,
):
    """
    test function - score
    """
    _model_class_tuple = (
        None
        if model_class in ["DummyTreeRegressor", "DummyTreeClassifier"]
        else namedtuple(model_class, model_params[0])(*model_params[1][0])
    )

    # # skipping a test
    # if (model_class in ["Ridge", "LinearRegression"] and _model_class.solver == "cgd") or (
    #         model_class in ["Lasso", "ElasticNet"]
    #         and _model_class.solver
    #         in [
    #             "bfgs",
    #             "newton",
    #         ]
    # ):
    #     pytest.skip(
    #         f"optimizer [{_model_class.solver}] is not supported for [{model_class}] model"
    #     )

    if model_class == "RandomForestRegressor":
        vo_model_obj = get_vo_model(
            model_class,
            n_estimators=_model_class_tuple.n_estimators,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            sample=_model_class_tuple.sample,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
            min_info_gain=_model_class_tuple.min_info_gain,
            nbins=_model_class_tuple.nbins,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class in ["RandomForestClassifier"]:
        vo_model_obj = get_vo_model(
            model_class,
            n_estimators=_model_class_tuple.n_estimators,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            sample=_model_class_tuple.sample,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
            min_info_gain=_model_class_tuple.min_info_gain,
            nbins=_model_class_tuple.nbins,
        )
        vo_score = vo_model_obj.model.score(
            metric=vo_metric_name[0], average="binary", pos_label=1
        )
    elif model_class == "DecisionTreeRegressor":
        vo_model_obj = get_vo_model(
            model_class,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
            min_info_gain=_model_class_tuple.min_info_gain,
            nbins=_model_class_tuple.nbins,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class == "DecisionTreeClassifier":
        vo_model_obj = get_vo_model(
            model_class,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
            min_info_gain=_model_class_tuple.min_info_gain,
            nbins=_model_class_tuple.nbins,
        )
        vo_score = vo_model_obj.model.score(
            metric=vo_metric_name[0], average="binary", pos_label=1
        )
    elif model_class == "XGBRegressor":
        vo_model_obj = get_vo_model(
            model_class,
            max_ntree=_model_class_tuple.max_ntree,
            max_depth=_model_class_tuple.max_depth,
            nbins=_model_class_tuple.nbins,
            learning_rate=_model_class_tuple.learning_rate,
            min_split_loss=_model_class_tuple.min_split_loss,
            weight_reg=_model_class_tuple.weight_reg,
            sample=_model_class_tuple.sample,
            col_sample_by_tree=_model_class_tuple.col_sample_by_tree,
            col_sample_by_node=_model_class_tuple.col_sample_by_node,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class == "XGBClassifier":
        vo_model_obj = get_vo_model(
            model_class,
            max_ntree=_model_class_tuple.max_ntree,
            max_depth=_model_class_tuple.max_depth,
            nbins=_model_class_tuple.nbins,
            learning_rate=_model_class_tuple.learning_rate,
            min_split_loss=_model_class_tuple.min_split_loss,
            weight_reg=_model_class_tuple.weight_reg,
            sample=_model_class_tuple.sample,
            col_sample_by_tree=_model_class_tuple.col_sample_by_tree,
            col_sample_by_node=_model_class_tuple.col_sample_by_node,
        )
        vo_score = vo_model_obj.model.score(
            metric=vo_metric_name[0], average="binary", pos_label=1
        )
    elif model_class in ["DummyTreeRegressor", "DummyTreeClassifier"]:
        vo_model_obj = get_vo_model(model_class)
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class == "LinearSVR":
        vo_model_obj = get_vo_model(
            model_class,
            tol=_model_class_tuple.tol,
            c=_model_class_tuple.c,
            intercept_scaling=_model_class_tuple.intercept_scaling,
            intercept_mode=_model_class_tuple.intercept_mode,
            acceptable_error_margin=_model_class_tuple.acceptable_error_margin,
            max_iter=_model_class_tuple.max_iter,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class == "PoissonRegressor":
        vo_model_obj = get_vo_model(
            model_class,
            penalty=_model_class_tuple.penalty,
            tol=_model_class_tuple.tol,
            C=_model_class_tuple.c,
            max_iter=_model_class_tuple.max_iter,
            solver=_model_class_tuple.solver,
            fit_intercept=_model_class_tuple.fit_intercept,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class == "AR":
        vo_model_obj = get_vo_model(
            model_class,
            p=_model_class_tuple.p,
            method=_model_class_tuple.method,
            penalty=_model_class_tuple.penalty,
            C=_model_class_tuple.c,
            missing=_model_class_tuple.missing,
        )
        vo_score = vo_model_obj.model.score(
            metric=vo_metric_name[0],
            start=_model_class_tuple.p,
            npredictions=_model_class_tuple.npredictions,
        )
    elif model_class == "MA":
        vo_model_obj = get_vo_model(
            model_class,
            q=_model_class_tuple.q,
            penalty=_model_class_tuple.penalty,
            C=_model_class_tuple.c,
            missing=_model_class_tuple.missing,
        )
        vo_score = vo_model_obj.model.score(
            metric=vo_metric_name[0],
            start=_model_class_tuple.q,
            npredictions=_model_class_tuple.npredictions,
        )
    elif model_class in ["ARMA", "ARIMA"]:
        vo_model_obj = get_vo_model(
            model_class,
            order=_model_class_tuple.order,
            tol=_model_class_tuple.tol,
            max_iter=_model_class_tuple.max_iter,
            init=_model_class_tuple.init,
            missing=_model_class_tuple.missing,
        )
        vo_score = vo_model_obj.model.score(
            metric=vo_metric_name[0],
            start=_model_class_tuple.order[0],
            npredictions=_model_class_tuple.npredictions,
        )
    elif model_class == "LinearRegression":
        vo_model_obj = get_vo_model(
            model_class,
            tol=_model_class_tuple.tol,
            max_iter=_model_class_tuple.max_iter,
            solver=_model_class_tuple.solver,
            fit_intercept=_model_class_tuple.fit_intercept,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class == "ElasticNet":
        vo_model_obj = get_vo_model(
            model_class,
            tol=_model_class_tuple.tol,
            c=_model_class_tuple.c,
            max_iter=_model_class_tuple.max_iter,
            solver=_model_class_tuple.solver,
            l1_ratio=_model_class_tuple.l1_ratio,
            fit_intercept=_model_class_tuple.fit_intercept,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    elif model_class in ["Ridge", "Lasso"]:
        vo_model_obj = get_vo_model(
            model_class,
            tol=_model_class_tuple.tol,
            c=_model_class_tuple.c,
            max_iter=_model_class_tuple.max_iter,
            solver=_model_class_tuple.solver,
            fit_intercept=_model_class_tuple.fit_intercept,
        )
        vo_score = vo_model_obj.model.score(metric=vo_metric_name[0])
    else:
        pytest.skip(f"Invalid parameters {_model_class_tuple} for {model_class}")

    if model_class in [
        "RandomForestClassifier",
        "DecisionTreeClassifier",
        "DummyTreeClassifier",
        "XGBClassifier",
    ]:
        vo_model_obj.pred_vdf.drop(
            columns=["survived_pred"]
        )  # this is added if parameters runs in loop
    elif model_class in [
        "AR",
        "MA",
        "ARMA",
        "ARIMA",
    ]:
        vo_model_obj.pred_vdf.drop(
            columns=["prediction"]
        )  # this is added if parameters runs in loop
    else:
        vo_model_obj.pred_vdf.drop(
            columns=["quality_pred"]
        )  # this is added if parameters runs in loop

    # python
    if model_class in ["RandomForestRegressor"]:
        py_model_obj = get_py_model(
            model_class,
            n_estimators=_model_class_tuple.n_estimators,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            sample=_model_class_tuple.sample,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
        )
        metrics_map = _metrics(model_class, model_obj=py_model_obj)
        py_score = metrics_map[py_metric_name]
    elif model_class in ["RandomForestClassifier"]:
        py_model_obj = get_py_model(
            model_class,
            n_estimators=_model_class_tuple.n_estimators,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            sample=_model_class_tuple.sample,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
        )
        _metrics = _metrics(model_class, model_obj=py_model_obj)
        py_score = _metrics[py_metric_name]
    elif model_class in ["DecisionTreeRegressor"]:
        py_model_obj = get_py_model(
            model_class,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
        )
        metrics_map = _metrics(model_class, model_obj=py_model_obj)
        py_score = metrics_map[py_metric_name]
    elif model_class in ["DecisionTreeClassifier"]:
        py_model_obj = get_py_model(
            model_class,
            max_features=_model_class_tuple.max_features,
            max_leaf_nodes=_model_class_tuple.max_leaf_nodes,
            max_depth=_model_class_tuple.max_depth,
            min_samples_leaf=_model_class_tuple.min_samples_leaf,
        )
        _metrics = _metrics(model_class, model_obj=py_model_obj)
        py_score = _metrics[py_metric_name]
    elif model_class in ["XGBRegressor"]:
        py_model_obj = get_py_model(
            model_class,
            n_estimators=_model_class_tuple.max_ntree,
            max_depth=_model_class_tuple.max_depth,
            max_bin=_model_class_tuple.nbins,
            learning_rate=_model_class_tuple.learning_rate,
            gamma=_model_class_tuple.min_split_loss,
            reg_alpha=_model_class_tuple.weight_reg,
            reg_lambda=_model_class_tuple.weight_reg,
            subsample=_model_class_tuple.sample,
            colsample_bytree=_model_class_tuple.col_sample_by_tree,
            colsample_bynode=_model_class_tuple.col_sample_by_node,
        )
        metrics_map = _metrics(model_class, model_obj=py_model_obj)
        py_score = metrics_map[py_metric_name]
    elif model_class in ["XGBClassifier"]:
        py_model_obj = get_py_model(
            model_class,
            n_estimators=_model_class_tuple.max_ntree,
            max_depth=_model_class_tuple.max_depth,
            max_bin=_model_class_tuple.nbins,
            learning_rate=_model_class_tuple.learning_rate,
            gamma=_model_class_tuple.min_split_loss,
            reg_alpha=_model_class_tuple.weight_reg,
            reg_lambda=_model_class_tuple.weight_reg,
            subsample=_model_class_tuple.sample,
            colsample_bytree=_model_class_tuple.col_sample_by_tree,
            colsample_bynode=_model_class_tuple.col_sample_by_node,
        )
        _metrics = _metrics(model_class, model_obj=py_model_obj)
        py_score = _metrics[py_metric_name]
    elif model_class in ["DummyTreeRegressor", "DummyTreeClassifier"]:
        py_model_obj = get_py_model(model_class)
        metrics_map = _metrics(model_class, model_obj=py_model_obj)
        py_score = metrics_map[py_metric_name]
    elif model_class in ["LinearSVR"]:
        metrics_map = _metrics(model_class, fit_intercept=True)
        py_score = metrics_map[py_metric_name]
    elif model_class in ["PoissonRegressor"]:
        metrics_map = _metrics(model_class, fit_intercept=True)
        py_score = metrics_map[py_metric_name]
    elif model_class in [
        "AR",
        "MA",
        "ARMA",
        "ARIMA",
    ]:
        if model_class == "AR":
            _order = (_model_class_tuple.p, 0, 0)
        elif model_class == "MA":
            _order = (0, 0, _model_class_tuple.q)
        else:
            _order = _model_class_tuple.order

        py_model_obj = get_py_model(model_class, order=_order)
        metrics_map = _metrics(model_class, model_obj=py_model_obj)
        py_score = metrics_map[py_metric_name]
    else:
        metrics_map = _metrics(
            model_class, fit_intercept=_model_class_tuple.fit_intercept
        )
        py_score = metrics_map[py_metric_name]

    return vo_score, py_score


def get_model_params(model_class):
    """
    getter function to get VAST model parameters
    """
    params_map = {
        **dict.fromkeys(
            ["LinearRegression"],
            {"tol": 1e-06, "max_iter": 100, "solver": "newton", "fit_intercept": True},
        ),
        **dict.fromkeys(
            ["Ridge"],
            {
                "tol": 1e-06,
                "C": 1.0,
                "max_iter": 100,
                "solver": "newton",
                "fit_intercept": True,
            },
        ),
        **dict.fromkeys(
            ["Lasso"],
            {
                "tol": 1e-06,
                "C": 1.0,
                "max_iter": 100,
                "solver": "cgd",
                "fit_intercept": True,
            },
        ),
        **dict.fromkeys(
            ["ElasticNet"],
            {
                "tol": 1e-06,
                "C": 1.0,
                "max_iter": 100,
                "solver": "cgd",
                "l1_ratio": 0.5,
                "fit_intercept": True,
            },
        ),
        **dict.fromkeys(
            ["RandomForestRegressor", "RandomForestClassifier"],
            {
                "n_estimators": 10,
                "max_features": 2,
                "max_leaf_nodes": 10,
                "sample": 0.632,
                "max_depth": 10,
                "min_samples_leaf": 1,
                "min_info_gain": 0.0,
                "nbins": 32,
            },
        ),
        **dict.fromkeys(
            ["DecisionTreeRegressor", "DecisionTreeClassifier"],
            {
                "max_features": 2,
                "max_leaf_nodes": 10,
                "max_depth": 10,
                "min_samples_leaf": 1,
                "min_info_gain": 0.0,
                "nbins": 32,
            },
        ),
        **dict.fromkeys(
            ["XGBRegressor", "XGBClassifier"],
            {
                "max_ntree": 10,
                "max_depth": 10,
                "nbins": 150,
                "split_proposal_method": "'global'",
                "tol": 0.001,
                "learning_rate": 0.1,
                "min_split_loss": 0.0,
                "weight_reg": 0.0,
                "sample": 1.0,
                "col_sample_by_tree": 1.0,
                "col_sample_by_node": 1.0,
            },
        ),
        **dict.fromkeys(["DummyTreeRegressor", "DummyTreeClassifier"], {}),
        **dict.fromkeys(
            ["LinearSVR"],
            {
                "tol": 1e-04,
                "C": 1.0,
                "intercept_scaling": 1.0,
                "intercept_mode": "regularized",
                "acceptable_error_margin": 0.1,
                "max_iter": 100,
            },
        ),
        **dict.fromkeys(
            ["PoissonRegressor"],
            {
                "penalty": "l2",
                "tol": 1e-06,
                "C": 1,
                "max_iter": 100,
                "solver": "newton",
                "fit_intercept": True,
            },
        ),
        **dict.fromkeys(
            ["AR"],
            {
                "p": 3,
                "method": "ols",
                "penalty": "none",
                "C": 1.0,
                "missing": "linear_interpolation",
                "subtract_mean": False,
            },
        ),
        **dict.fromkeys(
            ["MA"],
            {"q": 1, "penalty": "none", "C": 1.0, "missing": "linear_interpolation"},
        ),
        **dict.fromkeys(
            ["ARMA"],
            {
                "order": (2, 1),
                "tol": 1e-06,
                "max_iter": 100,
                "init": "zero",
                "missing": "linear_interpolation",
            },
        ),
        **dict.fromkeys(
            ["ARIMA"],
            {
                "order": (2, 1, 1),
                "tol": 1e-06,
                "max_iter": 100,
                "init": "zero",
                "missing": "linear_interpolation",
            },
        ),
        **dict.fromkeys(
            ["KMeans"],
            {"n_cluster": 8, "init": "kmeanspp", "max_iter": 300, "tol": 0.0001},
        ),
    }
    return params_map.get(
        model_class,
        None,
    )


def get_VAST_model_attributes(model_class):
    """
    getter function to get VAST model attributes
    """
    VAST_attributes_map = {
        **dict.fromkeys(
            [
                "RandomForestRegressor",
                "RandomForestClassifier",
                "DecisionTreeRegressor",
                "DecisionTreeClassifier",
                "DummyTreeRegressor",
                "DummyTreeClassifier",
                "XGBRegressor",
                "XGBClassifier",
            ],
            {
                "attr_name": [
                    "tree_count",
                    "rejected_row_count",
                    "accepted_row_count",
                    "call_string",
                    "details",
                ],
                "attr_fields": [
                    "tree_count",
                    "rejected_row_count",
                    "accepted_row_count",
                    "call_string",
                    "predictor, type",
                ],
                "#_of_rows": [1, 1, 1, 1, 3],
            },
        ),
        **dict.fromkeys(
            ["LinearSVR"],
            {
                "attr_name": [
                    "details",
                    "accepted_row_count",
                    "rejected_row_count",
                    "iteration_count",
                    "call_string",
                ],
                "attr_fields": [
                    "predictor, coefficient",
                    "accepted_row_count",
                    "rejected_row_count",
                    "iteration_count",
                    "call_string",
                ],
                "#_of_rows": [4, 1, 1, 1, 1],
            },
        ),
        **dict.fromkeys(
            ["PoissonRegressor"],
            {
                "attr_name": [
                    "details",
                    "regularization",
                    "iteration_count",
                    "rejected_row_count",
                    "accepted_row_count",
                    "call_string",
                ],
                "attr_fields": [
                    "predictor, coefficient, std_err, z_value, p_value",
                    "type, lambda",
                    "iteration_count",
                    "rejected_row_count",
                    "accepted_row_count",
                    "call_string",
                ],
                "#_of_rows": [4, 1, 1, 1, 1, 1],
            },
        ),
        **dict.fromkeys(
            ["AR"],
            {
                "attr_name": [
                    "coefficients",
                    "mean",
                    "lag_order",
                    "num_predictors",
                    "lambda",
                    "mean_squared_error",
                    "rejected_row_count",
                    "accepted_row_count",
                    "predictor_columns",
                    "timestamp_column",
                    "missing_method",
                    "call_string",
                ],
                "attr_fields": [
                    "parameter, value",
                    "predictor, value",
                    "lag_order",
                    "num_predictors",
                    "lambda",
                    "predictor, value",
                    "rejected_row_count",
                    "accepted_row_count",
                    "predictor_columns",
                    "timestamp_column",
                    "missing_method",
                    "call_string",
                ],
                "#_of_rows": [4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            },
        ),
        **dict.fromkeys(
            ["MA"],
            {
                "attr_name": [
                    "coefficients",
                    "mean",
                    "lag_order",
                    "num_predictors",
                    "lambda",
                    "mean_squared_error",
                    "rejected_row_count",
                    "accepted_row_count",
                    "predictor_columns",
                    "timestamp_column",
                    "missing_method",
                    "call_string",
                ],
                "attr_fields": [
                    "parameter, value",
                    "predictor, value",
                    "lag_order",
                    "num_predictors",
                    "lambda",
                    "predictor, value",
                    "rejected_row_count",
                    "accepted_row_count",
                    "predictor_columns",
                    "timestamp_column",
                    "missing_method",
                    "call_string",
                ],
                "#_of_rows": [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            },
        ),
        **dict.fromkeys(
            ["ARMA", "ARIMA"],
            {
                "attr_name": [
                    "coefficients",
                    "p",
                    "d",
                    "q",
                    "mean",
                    "regularization",
                    "lambda",
                    "mean_squared_error",
                    "rejected_row_count",
                    "accepted_row_count",
                    "timeseries_name",
                    "timestamp_name",
                    "missing_method",
                    "call_string",
                ],
                "attr_fields": [
                    "parameter, value",
                    "p",
                    "d",
                    "q",
                    "mean",
                    "regularization",
                    "lambda",
                    "mean_squared_error",
                    "rejected_row_count",
                    "accepted_row_count",
                    "timeseries_name",
                    "timestamp_name",
                    "missing_method",
                    "call_string",
                ],
                "#_of_rows": [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            },
        ),
        **dict.fromkeys(
            ["KMeans"],
            {
                "attr_name": ["centers", "metrics"],
                "attr_fields": [
                    "sepallengthcm, sepalwidthcm, petallengthcm, petalwidthcm",
                    "metrics",
                ],
                "#_of_rows": [8, 1],
            },
        ),
    }
    if model_class == "XGBRegressor":
        VAST_attributes_map[model_class]["attr_name"].append("initial_prediction")
        VAST_attributes_map[model_class]["attr_fields"].append("initial_prediction")
        VAST_attributes_map[model_class]["#_of_rows"].append(1)
    elif model_class == "XGBClassifier":
        VAST_attributes_map[model_class]["attr_name"].append("initial_prediction")
        VAST_attributes_map[model_class]["attr_fields"].append("response_label, value")
        VAST_attributes_map[model_class]["#_of_rows"].append(2)

    return VAST_attributes_map.get(
        model_class,
        {
            "attr_name": [
                "details",
                "regularization",
                "iteration_count",
                "rejected_row_count",
                "accepted_row_count",
                "call_string",
            ],
            "attr_fields": [
                "predictor, coefficient, std_err, t_value, p_value",
                "type, lambda",
                "iteration_count",
                "rejected_row_count",
                "accepted_row_count",
                "call_string",
            ],
            "#_of_rows": [4, 1, 1, 1, 1, 1],
        },
    )


def get_set_params(model_class):
    """
    getter function to get VAST params attributes
    """
    set_params_map = {
        **dict.fromkeys(
            ["RandomForestRegressor", "RandomForestClassifier"],
            {"n_estimators": 100, "max_depth": 50, "nbins": 100},
        ),
        **dict.fromkeys(
            ["DecisionTreeRegressor", "DecisionTreeClassifier"],
            {"max_depth": 50, "nbins": 100},
        ),
        **dict.fromkeys(
            ["XGBRegressor", "XGBClassifier"], {"max_depth": 50, "nbins": 100}
        ),
        **dict.fromkeys(["DummyTreeRegressor", "DummyTreeClassifier"], {}),
        **dict.fromkeys(
            ["LinearSVR"], {"intercept_mode": "unregularized", "max_iter": 500}
        ),
        **dict.fromkeys(
            ["ElasticNet"],
            {"l1_ratio": 0.01, "C": 0.12, "solver": "newton", "max_iter": 500},
        ),
        **dict.fromkeys(
            ["AR"], {"p": 10, "C": 0.12, "penalty": "l2", "missing": "drop"}
        ),
        **dict.fromkeys(
            ["MA"], {"q": 10, "C": 0.12, "penalty": "l2", "missing": "drop"}
        ),
        **dict.fromkeys(
            ["ARMA"], {"order": (2, 4, 2), "tol": 1, "init": "hr", "missing": "drop"}
        ),
        **dict.fromkeys(
            ["ARIMA"], {"order": (2, 2), "tol": 1, "init": "hr", "missing": "drop"}
        ),
        **dict.fromkeys(["KMeans"], {"n_cluster": 5, "init": "random", "tol": 1}),
    }
    return set_params_map.get(model_class, {"solver": "cgd", "max_iter": 500})


@pytest.fixture(name="get_pred_column")
def get_pred_column_fixture(model_class):
    """
    getter fixture to get prediction column
    """
    pred_col_map = {
        **dict.fromkeys(REGRESSION_MODELS, "quality_pred"),
        **dict.fromkeys(CLASSIFICATION_MODELS, "survived_pred"),
        **dict.fromkeys(TIMESERIES_MODELS, "prediction"),
        **dict.fromkeys(["KMeans"], f"{model_class}_cluster_ids"),
    }
    return pred_col_map.get(model_class, None)


pytestmark = pytest.mark.parametrize(
    "model_class",
    [
        "RandomForestRegressor",
        "RandomForestClassifier",
        "DecisionTreeRegressor",
        "DecisionTreeClassifier",
        # "DummyTreeRegressor",
        # "DummyTreeClassifier",
        "XGBRegressor",
        "XGBClassifier",
        "Ridge",
        "Lasso",
        "ElasticNet",
        "LinearRegression",
        # "LinearSVR",
        "PoissonRegressor",
        "AR",
        "MA",
        "ARMA",
        "ARIMA",
        # *****cluster models ************
        "KMeans",
    ],
)


@pytest.fixture(name="get_models")
def get_models_fixture(model_class, get_vo_model, get_py_model):
    """
    test function - get_models
    """
    _get_models = namedtuple("_get_models", ["vpy", "py"])(
        get_vo_model(model_class), get_py_model(model_class)
    )

    yield _get_models


class TestBaseModelMethods:
    """
    test class for linear models
    """

    def test_contour(self, model_class, get_vo_model):
        """
        test function - contour
        """
        X = get_xy(model_class)["X"]
        if model_class in [
            "AR",
            "MA",
            "ARMA",
            "ARIMA",
        ]:
            pytest.skip(f"contour function is not available for {model_class} model")

        vo_res = get_vo_model(
            model_class,
            X=X[:2],
        ).model.contour()

        assert isinstance(vo_res, (plt.Axes, plotly.graph_objs.Figure))

    def test_deploysql(self, get_models, model_class):
        """
        test function - deploySQL
        """
        pred_fun_name = get_predict_function(model_class)
        columns = ", ".join(f'"{col}"' for col in get_models.py.X.columns)

        vo_pred_sql = get_models.vpy.model.deploySQL()
        pred_sql = _get_deploysql(model_class).format(
            pred_fun_name=pred_fun_name,
            columns=columns,
            schema_name=get_models.vpy.schema_name,
            model_name=get_models.vpy.model_name,
        )

        assert vo_pred_sql == pred_sql

    def test_drop(self, get_models):
        """
        test function - drop
        """
        model_sql = f"SELECT model_name FROM models WHERE schema_name='{get_models.vpy.schema_name}' and model_name = '{get_models.vpy.model_name}'"

        current_cursor().execute(model_sql)
        assert current_cursor().fetchone()[0] == get_models.vpy.model_name

        get_models.vpy.model.drop()
        current_cursor().execute(model_sql)
        assert current_cursor().fetchone() is None

    @pytest.mark.parametrize("kind", ["pmml", "VAST", "VAST_models", None])
    def test_export_models(self, model_class, get_models, kind):
        """
        test function - export_models
        """
        export_path = f"/tmp/exports/{model_class}_{kind}"
        obj = get_models.vpy

        if os.path.isdir(export_path) and export_path.startswith("/tmp/exports/"):
            print(f"Deleting directory {export_path}")
            shutil.rmtree(export_path)

        try:
            assert VASTModel.export_models(
                name=f"{obj.schema_name}.{obj.model_name}",
                path=export_path,
                kind=kind,
            )
        except QueryError:
            with pytest.raises(QueryError) as exception_info:
                VASTModel.export_models(
                    name=f"{obj.schema_name}.{obj.model_name}",
                    path=export_path,
                    kind=kind,
                )

            assert (
                f"Exporting a model of type {get_train_function(model_class)} to PMML is not yet supported"
                in exception_info.value.message
            )

    def test_get_attributes(self, get_models, model_class):
        """
        test function - get_attributes
        """
        assert get_models.vpy.model.get_attributes() == get_model_attributes(
            model_class
        )

    @pytest.mark.parametrize(
        "match_index_attr, expected", [("valid_colum", 2), ("invalid_colum", None)]
    )
    def test_get_match_index(self, get_models, match_index_attr, expected, model_class):
        """
        test function - get_match_index
        """
        if model_class in TIMESERIES_MODELS:
            x = get_models.py.X.columns[0]
            col_list = [x]
            expected = 0 if match_index_attr == "valid_colum" else expected
        else:
            x = get_models.py.X.columns[2]
            col_list = get_models.py.X.columns

        if match_index_attr == "valid_colum":
            vo_res = get_models.vpy.model.get_match_index(x=x, col_list=col_list)
        else:
            vo_res = get_models.vpy.model.get_match_index(
                x=match_index_attr, col_list=col_list
            )

        assert vo_res == expected

    def test_get_params(self, get_models, model_class):
        """
        test function - get_params
        """
        expected_model_params = get_model_params(model_class)
        actual_model_params = get_models.vpy.model.get_params()

        assert expected_model_params == pytest.approx(actual_model_params)

    def test_get_plotting_lib(self, get_models):
        """
        test function - get_plotting_lib
        """
        plotting_lib = get_models.vpy.model.get_plotting_lib(
            class_name="RegressionPlot"
        )[0].RegressionPlot.__module__
        assert (
            "matplotlib" in plotting_lib
            or "plotly" in plotting_lib
        )

    @pytest.mark.parametrize("attributes", ["attr_name", "attr_fields", "#_of_rows"])
    def test_get_VAST_attributes(self, get_models, model_class, attributes):
        """
        test function - get_VAST_attributes
        """
        model_attributes = get_models.vpy.model.get_VAST_attributes()

        attr_map = get_VAST_model_attributes(model_class)
        expected = attr_map[attributes]

        assert model_attributes[attributes] == expected

    @pytest.mark.parametrize("kind", ["pmml", "VAST", "VAST_models", None])
    def test_import_models(self, schema_loader, model_class, get_models, kind):
        """
        test function - import_models
        """
        export_path = f"/tmp/imports/{model_class}_{kind}"
        obj = get_models.vpy

        if os.path.isdir(export_path) and export_path.startswith("/tmp/imports/"):
            print(f"Deleting directory {export_path}")
            shutil.rmtree(export_path)

        try:
            VASTModel.export_models(
                name=f"{obj.schema_name}.{obj.model_name}",
                path=export_path,
                kind=kind,
            )
            obj.model.drop()
            assert VASTModel.import_models(
                path=f"{export_path}/vo_model_{model_class}/",
                schema=schema_loader,
                kind=kind,
            )
            obj.model.drop()
        except QueryError:
            with pytest.raises(QueryError) as exception_info:
                VASTModel.export_models(
                    name=f"{obj.schema_name}.{obj.model_name}",
                    path=export_path,
                    kind=kind,
                )

            assert (
                f"Exporting a model of type {get_train_function(model_class)} to PMML is not yet supported"
                in exception_info.value.message
            )

    @pytest.mark.parametrize("overwrite", [True, False])
    def test_overwrite(self, model_class, get_vo_model, overwrite):
        """
        test function - overwrite existing model
        """
        obj = get_vo_model(model_class)
        try:
            get_vo_model(model_class, overwrite_model=overwrite)
        except NameError:
            with pytest.raises(NameError) as exception_info:
                get_vo_model(model_class, overwrite_model=overwrite)
            assert exception_info.match(f"The model '{obj.model_name}' already exists!")
        obj.model.drop()

    @pytest.mark.parametrize(
        "plotting_library",
        [
            # "plotly",
            "matplotlib",
        ],
    )
    def test_plot(self, model_class, get_vo_model, plotting_library):
        """
        test function - plot
        """
        vo.set_option("plotting_lib", plotting_library)
        X = get_xy(model_class)["X"]
        try:
            vo_res = get_vo_model(
                model_class,
                X=X if model_class in TIMESERIES_MODELS else X[:2],
            )[0].plot()
        except NotImplementedError:
            pytest.skip(
                f"plot function is not implemented for {model_class} model class - NotImplementedError"
            )

        if plotting_library == "matplotlib":
            assert isinstance(vo_res, plt.Axes)
        elif plotting_library == "plotly":
            assert isinstance(vo_res, plotly.graph_objs.Figure)
        # assert isinstance(vo_res, (plt.Axes, plotly.graph_objs.Figure))

    def test_predict(self, get_models, model_class, get_pred_column):
        """
        test function - predict
        """
        vo_res = get_models.vpy.pred_vdf[[get_pred_column]].to_numpy().mean()
        py_res = get_models.py.pred.mean()

        assert vo_res == pytest.approx(
            py_res, rel=rel_abs_tol_map[model_class]["predict"]["rel"]
        )

    def test_register(self, get_models, model_class):
        """
        test function - register model
        """
        assert get_models.vpy.model.register(f"{model_class}_app")

    def test_set_params(self, get_models, model_class):
        """
        test function - set_params
        """
        params = get_set_params(model_class)
        get_models.vpy.model.set_params(params)

        assert {
            k: get_models.vpy.model.get_params()[k] for k in params
        } == pytest.approx(params)

    def test_to_binary(self, get_models):
        """
        test function - to_binary
        """
        assert get_models.vpy.model.to_binary(path="/tmp/")

    def test_to_memmodel(self, get_models, model_class):
        """
        test function - to_mmmodel
        """
        if model_class in TIMESERIES_MODELS:
            pytest.skip(
                f"to_memmodel function is not available for {model_class} model"
            )

        pdf = get_models.py.X

        # cast Decimal.decimal datatype to float (if exists)
        for col in pdf.columns:
            pdf[col] = pdf[col].astype(float)

        mmodel = get_models.vpy.model.to_memmodel()
        mm_res = mmodel.predict(pdf).tolist()
        py_res = get_models.vpy.model.to_python()(pdf).tolist()

        assert mm_res == pytest.approx(py_res, rel=REL_TOLERANCE)

    def test_to_python(self, get_models, model_class, get_pred_column):
        """
        test function - to_python
        """
        if model_class in TIMESERIES_MODELS:
            pytest.skip(f"to_python function is not available for {model_class} model")

        pdf = get_models.py.X
        # cast Decimal.decimal datatype to float (if exists)
        for col in pdf.columns:
            pdf[col] = pdf[col].astype(float)

        py_res = get_models.vpy.model.to_python()(pdf)[10]
        vo_res = get_models.vpy.pred_vdf[[get_pred_column]].to_numpy()[10]

        py_res = [np.exp(py_res) if model_class == "PoissonRegressor" else py_res]

        assert vo_res == pytest.approx(
            py_res, rel=rel_abs_tol_map[model_class]["to_python"]["rel"]
        )

    def test_to_sql(self, model_class, get_to_sql):
        """
        test function - to_sql
        """
        current_cursor().execute(get_to_sql)
        prediction = current_cursor().fetchone()
        assert prediction[0] == pytest.approx(
            np.exp(prediction[1])
            if model_class == "PoissonRegressor"
            else prediction[1]
        )

    @pytest.mark.parametrize(
        "key_name",
        [
            "index",
            "importance",
            "sign",
        ],
    )
    @pytest.mark.skip(
        reason="This test has started failing for index-DecisionTreeClassifier and index-XGBRegressor since 1/9/24"
    )
    def test_features_importance(self, get_vo_model, model_class, key_name):
        """
        test function - features_importance
        """
        feature_importances_map = {"sign": [1, 1, 1]}
        _X = None

        if model_class in [
            "RandomForestClassifier",
            "DecisionTreeClassifier",
            "DummyTreeClassifier",
            "XGBClassifier",
        ]:
            feature_importances_map["index"] = [
                "sex",
                "fare",
                "age",
            ]
            if model_class in ["RandomForestClassifier"]:
                # feature_importances_map["index"] = [
                #     "sex",
                #     "fare",
                #     "age",
                # ]
                feature_importances_map["importance"] = [74.4, 12.88, 12.72]
            elif model_class in ["DecisionTreeClassifier"]:
                # feature_importances_map["index"] = [
                #     "sex",
                #     "age",
                #     "fare",
                # ]
                feature_importances_map["importance"] = [76.4, 12.41, 11.19]
            elif model_class in ["XGBClassifier"]:
                # feature_importances_map["index"] = [
                #     "sex",
                #     "fare",
                #     "age",
                # ]
                feature_importances_map["importance"] = [97.88, 1.39, 0.73]
            elif model_class in ["DummyTreeClassifier"]:
                feature_importances_map["index"] = [
                    "fare",
                    "sex",
                    "age",
                ]
                feature_importances_map["importance"] = [38.9, 36.61, 24.49]
        elif model_class in [
            "RandomForestRegressor",
            "DecisionTreeRegressor",
            "XGBRegressor",
        ]:
            feature_importances_map["index"] = [
                "alcohol",
                "citric_acid",
                "residual_sugar",
            ]
            if model_class in ["RandomForestRegressor"]:
                feature_importances_map["importance"] = [82.67, 12.91, 4.42]
            elif model_class in ["DecisionTreeRegressor"]:
                feature_importances_map["importance"] = [83.65, 11.37, 4.98]
            elif model_class in ["XGBRegressor"]:
                feature_importances_map["index"] = [
                    "alcohol",
                    "residual_sugar",
                    "citric_acid",
                ]
                feature_importances_map["importance"] = [64.86, 17.58, 17.57]
        elif model_class == "AR":
            feature_importances_map["index"] = [
                '""passengers""[t-1]',
                '""passengers""[t-2]',
                '""passengers""[t-3]',
            ]
            feature_importances_map["importance"] = [
                0.62945595267205,
                0.27631678771967194,
                0.09422725960827791,
            ]
            feature_importances_map["sign"] = [1.0, -1.0, 1.0]
        elif model_class == "MA":
            pytest.skip("Features Importance can not be computed for Moving Averages")
        elif model_class in ["ARMA", "ARIMA"]:
            feature_importances_map["index"] = [
                '""passengers""[t-1]',
                '""passengers""[t-2]',
            ]
            feature_importances_map["importance"] = [
                0.6018412076652686,
                0.3981587923347315,
            ]
            feature_importances_map["sign"] = (
                [1.0, 1.0] if model_class == "ARMA" else [1.0, -1.0]
            )
        else:
            feature_importances_map["index"] = [
                "alcohol",
                "residual_sugar",
                "citric_acid",
            ]
            if model_class in ["DummyTreeRegressor"]:
                # feature_importances_map["index"] = [
                #     "alcohol",
                #     "residual_sugar",
                #     "citric_acid",
                # ]
                feature_importances_map["importance"] = [37.61, 36.56, 25.83]
            elif model_class == "Ridge":
                # feature_importances_map["index"] = ['alcohol', 'residual_sugar', 'citric_acid']
                feature_importances_map["importance"] = [52.3, 32.63, 15.07]
            elif model_class == "LinearRegression":
                # feature_importances_map["index"] = ['alcohol', 'residual_sugar', 'citric_acid']
                feature_importances_map["importance"] = [52.25, 32.58, 15.17]
            elif model_class == "LinearSVR":
                # feature_importances_map["index"] = ['alcohol', 'residual_sugar', 'citric_acid']
                feature_importances_map["importance"] = [52.68, 33.27, 14.05]
            elif model_class == "PoissonRegressor":
                # feature_importances_map["index"] = ['alcohol', 'residual_sugar', 'citric_acid']
                feature_importances_map["importance"] = [51.94, 32.48, 15.58]
            elif model_class in ["Lasso", "ElasticNet"]:
                _X = feature_importances_map["index"] = [
                    "total_sulfur_dioxide",
                    "residual_sugar",
                    "alcohol",
                ]
                feature_importances_map["importance"] = [100, 0, 0]
                feature_importances_map["sign"] = [-1, 0, 0]

        f_imp = get_vo_model(model_class, X=_X).model.features_importance(show=False)
        # print(f_imp[key_name])

        assert feature_importances_map[key_name] == pytest.approx(
            f_imp[key_name], rel=1e-0
        )
