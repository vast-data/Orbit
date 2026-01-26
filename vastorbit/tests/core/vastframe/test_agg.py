"""
SPDX-License-Identifier: Apache-2.0
"""

from contextlib import nullcontext as does_not_raise
import pytest
import numpy as np
from scipy.stats import median_abs_deviation, jarque_bera
from vastorbit.errors import MissingColumn
from vastorbit.tests.core.vastframe import REL_TOLERANCE, ABS_TOLERANCE
from vastorbit.tests import functions, AggregateFun


class TestAgg:
    """
    test class for aggregate function test
    """

    @pytest.mark.parametrize(
        "dataset, columns, expr, rollup, having, raise_err, expected",
        [
            (
                "market_vd",
                ["Form", "Name"],
                ["AVG(Price) AS avg_price", "STDDEV(Price) AS std"],
                None,
                None,
                does_not_raise(),
                (159, 4),
            ),
            (
                "market_vd",
                ["Form", "Name"],
                ["AVG(Price) AS avg_price", "STDDEV(Price) AS std"],
                True,
                None,
                does_not_raise(),
                (197, 4),
            ),
            (
                "market_vd",
                ["Form", "Name"],
                ["AVG(Price) AS avg_price", "STDDEV(Price) AS std"],
                True,
                "AVG(Price) > 2",
                does_not_raise(),
                (73, 4),
            ),
            (
                "market_vd",
                ["Form", "Name"],
                ["AVG(Price) AS avg_price", "STDDEV(Price) AS std"],
                [False, True],
                None,
                does_not_raise(),
                (196, 4),
            ),
            (
                "titanic_vd",
                [("pclass", "sex"), "embarked"],
                ["AVG(survived) AS avg_survived"],
                [True, False],
                None,
                does_not_raise(),
                (33, 4),
            ),
            (
                "market_vd",
                ["For", "Name"],
                ["AVG(Price) AS avg_price", "STDDEV(Price) AS std"],
                None,
                None,
                pytest.raises(MissingColumn),
                "The Virtual Column 'For' doesn't exist.\nDid you mean '\"form\"' ?",
            ),
        ],
    )
    def test_groupby(
        self, request, dataset, columns, expr, rollup, having, raise_err, expected
    ):
        """
        test function - groupby
        """
        data = request.getfixturevalue(dataset)
        # exc_info = None
        with raise_err:
            if rollup and having:
                vo_res = data.groupby(
                    columns=columns, expr=expr, rollup=rollup, having=having
                ).shape()
            elif rollup and having is None:
                vo_res = data.groupby(
                    columns=columns, expr=expr, rollup=rollup
                ).shape()
            elif having and rollup is None:
                vo_res = data.groupby(
                    columns=columns,
                    expr=expr,
                ).shape()
            else:
                vo_res = data.groupby(
                    columns=columns,
                    expr=expr,
                ).shape()

        assert (
            getattr(raise_err, "excinfo").match(expected)
            if hasattr(raise_err, "excinfo")
            else vo_res == expected
        )

    @pytest.mark.parametrize(
        "vo_func, py_func, _rel_tol, _abs_tols, expected",
        [
            ("aad", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            (
                "approx_median",
                None,
                REL_TOLERANCE,
                ABS_TOLERANCE,
                [[3.0, 0.0, 28.0, 0.0, 0.0, 14.4542, 160.5], [28.0, 14.4542, 3.0, 0.0]],
            ),
            (
                "approx_10%",
                None,
                REL_TOLERANCE,
                ABS_TOLERANCE,
                [[1.0, 0.0, 14.5, 0.0, 0.0, 7.5892, 37.7], [14.5, 7.5892, 1.0, 0.0]],
            ),
            (
                "approx_90%",
                None,
                REL_TOLERANCE,
                ABS_TOLERANCE,
                [
                    [3.0, 1.0, 50.18782608695652, 1.0, 2.0, 77.22874209106986, 297.0],
                    [50.0, 79.13, 3.0, 1.0],
                ],
            ),
            # ("approx_unique", None, None, REL_TOLERANCE, ABS_TOLERANCE, [[3.0, 2.0, 1233.0, 2.0, 96.0, 7.0, 8.0, 888.0, 275.0, 181.0, 3.0, 26.0, 118.0, 355.0], [96.0, 275.0, 3.0, 2.0]]),  # fail due to randomness in output
            ("count", "count", REL_TOLERANCE, ABS_TOLERANCE, None),
            ("cvar", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            # ("dtype", None, REL_TOLERANCE, ABS_TOLERANCE, [['int', 'int', 'varchar(164)', 'varchar(20)', 'numeric(6,3)', 'int', 'int', 'varchar(36)', 'numeric(10,5)', 'varchar(30)', 'varchar(20)', 'varchar(100)', 'int', 'varchar(100)'], ['numeric(6,3)', 'numeric(10,5)', 'int', 'int']]),  # fail due to randomness in output
            ("iqr", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("kurtosis", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("jb", None, 1e-00, ABS_TOLERANCE, None),
            ("mad", None, 1e-00, 1e-00, None),
            ("max", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("mean", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("median", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("min", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("mode", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("percent", None, 1e-04, ABS_TOLERANCE, None),
            ("10%", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("90%", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            # ('prod', None, REL_TOLERANCE, ABS_TOLERANCE, None),  # fail getting inf for pclass column
            ("range", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("sem", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("skewness", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("sum", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("std", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("top1", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("top1_percent", None, 1e-04, ABS_TOLERANCE, None),
            ("unique", None, REL_TOLERANCE, ABS_TOLERANCE, None),
            ("var", None, REL_TOLERANCE, ABS_TOLERANCE, None),
        ],
    )
    @pytest.mark.parametrize(
        "input_type, columns",
        [
            ("VastFrame", []),
            ("VastFrame_column", ["age"]),
            ("VastColumn", ["age"]),
            ("VastColumn", ["age", "fare", "pclass", "survived"]),
        ],
    )
    @pytest.mark.parametrize("agg_func_type", ["agg", "aggregate"])
    def test_aggregate(
        self,
        titanic_vd,
        agg_func_type,
        vo_func,
        py_func,
        columns,
        expected,
        _rel_tol,
        _abs_tols,
        input_type,
    ):
        """
        test function - aggregate
        """
        numeric_columns = [
            "pclass",
            "survived",
            "age",
            "sibsp",
            "parch",
            "fare",
            "body",
        ]

        titanic_pdf = titanic_vd.to_pandas()
        titanic_pdf["age"] = titanic_pdf["age"].astype(float)
        titanic_pdf["fare"] = titanic_pdf["fare"].astype(float)

        # vastorbit
        if input_type == "VastFrame":
            if vo_func in ["top1", "top1_percent"]:
                vo_res = (
                    getattr(titanic_vd[numeric_columns], agg_func_type)(func=vo_func)
                    .transpose()
                    .to_list()[0]
                )
            elif vo_func in ["aad"]:
                res = getattr(titanic_vd[numeric_columns], agg_func_type)(func=vo_func)
                vo_res_map = dict(zip(res["index"], res[vo_func]))
                vo_res = {k.replace('"', ""): v for k, v in vo_res_map.items()}
            else:
                vo_res = (
                    getattr(titanic_vd, agg_func_type)(func=vo_func)
                    .transpose()
                    .to_list()[0]
                )
        elif input_type == "VastFrame_column":
            vo_res = (
                getattr(titanic_vd, agg_func_type)(func=vo_func, columns=columns)
                .transpose()
                .to_list()[0]
            )
        else:
            vo_res = (
                getattr(titanic_vd[columns], agg_func_type)(func=vo_func)
                .transpose()
                .to_list()[0]
            )

        # Python
        py_res = []
        if py_func:
            if input_type == "VastFrame":
                py_data = titanic_pdf
                py_res = getattr(titanic_pdf, agg_func_type)(func=py_func).tolist()
            else:
                py_res = getattr(titanic_pdf[columns], agg_func_type)(
                    func=py_func
                ).tolist()
        else:
            if expected:
                if input_type == "VastFrame":
                    py_res = expected[0]
                else:
                    py_res = [expected[1][0]] if len(columns) == 1 else expected[1]
            else:
                _py_func = AggregateFun(*functions[vo_func]).py
                if input_type == "VastFrame" and vo_func not in [
                    "top1",
                    "top1_percent",
                    "jb",
                ]:
                    py_data = (
                        titanic_pdf[numeric_columns]
                        if vo_func in ["cvar", "jb", "mad"]
                        else titanic_pdf
                    )
                    if vo_func in ["aad"]:
                        py_res = dict(eval(_py_func))
                    else:
                        py_res = eval(_py_func).tolist()
                else:
                    # py_res = eval(_py_func) if vo_func in ["top2"] else eval(_py_func).tolist()
                    if vo_func in ["top1", "top1_percent", "jb"]:
                        for column in columns if columns else numeric_columns:
                            py_data = titanic_pdf[column]
                            py_res.append(eval(f"{_py_func}"))
                        py_res = [None if np.isnan(v) else v for v in py_res]
                    else:
                        py_data = titanic_pdf[columns]
                        py_res = eval(_py_func).tolist()

        if vo_func in ["mode"]:
            py_res = [None if np.isnan(v) else v for v in py_res[0]]

        print(
            f"Function name: {vo_func} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )
        assert vo_res == pytest.approx(py_res, rel=_rel_tol, abs=_abs_tols)

    @pytest.mark.parametrize(
        "func_name, _rel_tol, _abs_tol",
        [
            ("aad", REL_TOLERANCE, ABS_TOLERANCE),
            ("mean", REL_TOLERANCE, ABS_TOLERANCE),
            ("avg", REL_TOLERANCE, ABS_TOLERANCE),
            ("count", REL_TOLERANCE, ABS_TOLERANCE),
            ("kurt", REL_TOLERANCE, ABS_TOLERANCE),
            ("kurtosis", REL_TOLERANCE, ABS_TOLERANCE),
            ("mad", 1e-00, 1e-00),
            ("max", REL_TOLERANCE, ABS_TOLERANCE),
            ("median", REL_TOLERANCE, ABS_TOLERANCE),
            ("min", REL_TOLERANCE, ABS_TOLERANCE),
            # ("prod", REL_TOLERANCE, ABS_TOLERANCE),  # fail getting inf for pclass column
            # # ("product", REL_TOLERANCE, ABS_TOLERANCE),  # fail getting inf for pclass column
            ("quantile", REL_TOLERANCE, ABS_TOLERANCE),
            ("sem", REL_TOLERANCE, ABS_TOLERANCE),
            ("skew", REL_TOLERANCE, ABS_TOLERANCE),
            ("skewness", REL_TOLERANCE, ABS_TOLERANCE),
            ("std", REL_TOLERANCE, ABS_TOLERANCE),
            ("stddev", REL_TOLERANCE, ABS_TOLERANCE),
            ("sum", REL_TOLERANCE, ABS_TOLERANCE),
            ("var", REL_TOLERANCE, ABS_TOLERANCE),
            ("variance", REL_TOLERANCE, ABS_TOLERANCE),
            ("nunique", REL_TOLERANCE, ABS_TOLERANCE),
        ],
    )
    @pytest.mark.parametrize(
        "function_type, columns",
        [
            ("VastFrame", []),
            ("VastFrame_columns", ["age"]),
            ("VastColumn", ["age", "fare", "pclass", "survived"]),
        ],
    )
    def test_vdf_vcol(
        self,
        titanic_vd,
        func_name,
        columns,
        _rel_tol,
        _abs_tol,
        function_type,
    ):
        """
        test function - VastFrame and VastColumn
        """
        numeric_columns = [
            "pclass",
            "survived",
            "age",
            "sibsp",
            "parch",
            "fare",
            "body",
        ]

        titanic_pdf = titanic_vd.to_pandas()
        titanic_pdf["age"] = titanic_pdf["age"].astype(float)
        titanic_pdf["fare"] = titanic_pdf["fare"].astype(float)
        # data = titanic_pdf[columns[0]]
        vo_func, py_func = (
            AggregateFun(*functions[func_name]).vpy,
            AggregateFun(*functions[func_name]).py,
        )

        # vastorbit
        vo_func_name = (
            vo_func
            if vo_func.count(".") == 0
            else vo_func.split(".")[1].split("(")[0]
        )

        if function_type == "VastFrame":
            vo_data = titanic_vd
            if vo_func_name in ["aad"]:
                res = eval(vo_func)
                vo_res_map = dict(zip(res["index"], res[vo_func_name]))
                vo_res = {k.replace('"', ""): v for k, v in vo_res_map.items()}
            else:
                vo_res = eval(vo_func).transpose().to_list()[0]
        elif function_type == "VastFrame_columns":
            vo_data = titanic_vd
            vo_res = (
                eval(
                    vo_func.replace(")", "columns=columns)")
                    if "()" in vo_func
                    else vo_func.replace(")", ", columns=columns)")
                )
                .transpose()
                .to_list()[0]
            )
        else:
            vo_data = titanic_vd[columns]
            vo_res = eval(vo_func).transpose().to_list()[0]

        # Python
        if function_type == "VastFrame":
            if vo_func_name in ["mad", "sem"]:
                py_data = titanic_pdf[numeric_columns]
                py_res = eval(py_func).tolist()
            elif vo_func_name in ["aad"]:
                py_data = titanic_pdf
                py_res = dict(eval(py_func))
            else:
                py_data = titanic_pdf
                py_res = eval(py_func).tolist()
        else:
            py_data = titanic_pdf[columns]
            py_res = eval(py_func).tolist()

        print(
            f"Function name: {vo_func} \ncolumns: {columns} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )
        assert vo_res == pytest.approx(
            py_res[0] if func_name == "quantile" else py_res, rel=_rel_tol, abs=_abs_tol
        )

    @pytest.mark.parametrize(
        "func_name, vo_func, py_func",
        [
            (
                "all",
                "vo_data.all(columns = columns)['bool_and'][0]",
                "py_data.all()",
            ),
            (
                "any",
                "vo_data.any(columns = columns)['bool_or'][0]",
                "py_data.any()",
            ),
            (
                "count_percent",
                "vo_data.count_percent(columns = columns, sort_result=True, desc=False)['percent'][0]",
                "py_data.notnull().mean()*100",
            ),
            (
                "duplicated",
                "vo_data.duplicated(columns = columns, count=False, limit=30)['occurrence']",  # tablesample doesn't support sorting with null value
                "py_data.groupby(['survived']).size().reset_index(name='occurrence')['occurrence'].tolist()",
            ),
        ],
    )
    def test_vdf(self, titanic_vd, func_name, vo_func, py_func):
        """
        test function - VastFrame groupby
        """
        columns = ["survived"]
        titanic_pdf = titanic_vd.to_pandas()
        titanic_pdf["age"] = titanic_pdf["age"].astype(float)
        titanic_pdf["fare"] = titanic_pdf["fare"].astype(float)

        # vastorbit
        vo_data = titanic_vd
        vo_res = eval(vo_func)

        # Python
        py_data = (
            titanic_pdf[[columns[0]]]
            if func_name == "duplicated"
            else titanic_pdf[columns[0]]
        )
        py_res = eval(py_func)

        print(
            f"Function name: {vo_func} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )
        if func_name in ["all", "any"]:
            assert bool(vo_res) == bool(py_res)
        else:
            assert vo_res == pytest.approx(py_res, abs=1e-3)

    @pytest.mark.parametrize(
        "func_name",
        ["value_counts", "topk", "distinct"],
    )
    @pytest.mark.parametrize("columns", ["pclass"])
    def test_VastColumn(self, titanic_vd, columns, func_name):
        """
        test function - VastColumn groupby
        """
        titanic_pdf = titanic_vd.to_pandas()

        vo_func, py_func = (
            AggregateFun(*functions[func_name]).vpy,
            AggregateFun(*functions[func_name]).py,
        )

        # vastorbit
        vo_data = titanic_vd[columns]
        if func_name == "value_counts":
            vo_res = eval(vo_func).transpose().to_list()[0][4:]
        elif func_name == "distinct":
            vo_res = eval(vo_func)
        else:
            vo_res = eval(vo_func).transpose().to_list()[0]

        # Python
        py_data = titanic_pdf[columns]
        py_res = eval(py_func).tolist()

        # Sorting
        vo_res.sort()
        py_res.sort()

        print(
            f"Function name: {vo_func} \nvastorbit Result: {vo_res} \nPython Result :{py_res}\n"
        )
        assert vo_res == pytest.approx(py_res, abs=1e-3)
