"""
SPDX-License-Identifier: Apache-2.0
"""

import math
from itertools import chain
import pytest
import pandas as pd
from sklearn import model_selection
from scipy.stats import median_abs_deviation, chi2_contingency
from vastorbit import errors

# Utilities
from vastorbit.core.tablesample.base import TableSample
from vastorbit.tests.machine_learning.vast.conftest import (
    get_vo_model_fixture,
    calculate_regression_metrics,
)


class TestMachineLearning:
    """
    test class for Machine Learning functions test
    """

    @pytest.mark.parametrize("use_gcd", [True, False])
    def test_add_duplicates(self, use_gcd):
        """
        test function - add_duplicates
        """
        cities = TableSample(
            {
                "cities": ["Boston", "New York City", "San Francisco"],
                "weight": [2, 4, 6],
            }
        ).to_vdf()

        result = (
            cities.add_duplicates("weight", use_gcd=use_gcd)
            .groupby("cities", "COUNT(*) AS cnt")
            .sort("cnt")
        )

        if use_gcd:
            cities["weight"] = cities["weight"] / math.gcd(
                *list(chain(*cities[["weight"]].to_list()))
            )

        result1 = cities.to_list()
        result2 = result.to_list()

        result1.sort()
        result2.sort()

        assert result1 == result2

    @pytest.mark.parametrize(
        "columns, max_cardinality, nbins, tcdt, drop_transf_cols",
        [
            ("age", 20, 15, False, True),
            ("age", 20, 10, False, False),
            ("age", 25, 10, False, False),
            ("age", 20, 10, True, False),
        ],
    )
    def test_cdt(
        self, titanic_vd_fun, columns, max_cardinality, nbins, tcdt, drop_transf_cols
    ):
        """
        test function - cdt - complete disjunctive table
        """
        titanic_vd_fun_fillna = titanic_vd_fun.copy()
        titanic_vd_fun_fillna["age"].fillna(30)

        titanic_pdf = titanic_vd_fun_fillna.to_pandas()
        titanic_pdf[columns] = titanic_pdf[columns].astype("float")
        titanic_vd_fun_copy = titanic_vd_fun_fillna.copy()

        def _get_columns(df):
            col_names = [
                col.replace('"', "")
                for col in df.get_columns()
                if col.replace('"', "").startswith("age_")
            ]

            return col_names

        vo_raw = titanic_vd_fun_fillna.cdt(
            columns=columns, drop_transf_cols=drop_transf_cols, tcdt=tcdt
        )
        vo_res = vo_raw.aggregate(columns=_get_columns(vo_raw), func=["sum"]).to_list()

        vo_cdt_raw = (
            titanic_vd_fun_fillna[columns]
            .discretize(nbins=nbins)
            .one_hot_encode(
                columns,
                max_cardinality=max(max_cardinality, nbins) + 2,
                drop_first=False,
            )
        )
        if tcdt:
            for elem in _get_columns(vo_cdt_raw):
                sum_cat = vo_cdt_raw[elem].sum()
                vo_cdt_raw[elem].apply(f"{{}} / {sum_cat} - 1")
        vo_cdt_res = vo_cdt_raw.aggregate(
            columns=_get_columns(vo_cdt_raw), func=["sum"]
        ).to_list()

        assert (
            columns not in _get_columns(vo_raw)
            if drop_transf_cols
            else vo_res == vo_cdt_res
        )

        # as there is no way to control h(interval  size) value in cdt function to compare result with pandas.
        # so first comparing results of vpy cdt with cdt(using discretize and one_hot_encode).

        h = 10
        vo_cdt_h = (
            titanic_vd_fun_copy[columns]
            .discretize(h=h, nbins=nbins)
            .one_hot_encode(
                columns,
                max_cardinality=max(max_cardinality, nbins) + 2,
                drop_first=False,
            )
        )
        vo_cdt_h_res = vo_cdt_h.aggregate(
            columns=_get_columns(vo_cdt_h), func=["sum"]
        ).to_list()

        # python
        bins = range(0, int(max(titanic_pdf[columns])) + 20, h)
        titanic_pdf[f"{columns}_cut"] = pd.cut(
            titanic_pdf[columns],
            bins=bins,
            right=False,
        )
        py_raw = pd.get_dummies(
            titanic_pdf, columns=[f"{columns}_cut"], drop_first=False
        )

        py_col_names = [col for col in list(py_raw.columns) if col.startswith("age_")]
        py_res = list(py_raw[py_col_names].sum().values)

        assert list(chain(*vo_cdt_h_res)) == py_res

    @pytest.mark.parametrize(
        "response, columns, nbins, method",
        [
            ("survived", ["sex", "pclass"], 16, "same_width"),
        ],
    )
    def test_chaid(self, titanic_vd_fun, response, columns, nbins, method):
        """
        test function - chaid
        """
        titanic_pdf = titanic_vd_fun.to_pandas()
        vo_tree = titanic_vd_fun.chaid(
            response=response, columns=columns, nbins=nbins, method=method
        ).tree_
        vo_col2_cats = vo_tree["children"]["female"]["children"].keys()

        for col1_cat in titanic_pdf[columns[0]].unique():
            for col2_cat, vo_col2_cat in zip(
                titanic_pdf[columns[1]].unique(), vo_col2_cats
            ):
                subset_pdf = titanic_pdf.loc[titanic_pdf[columns[0]].isin([col1_cat])]

                sub_grp_pdf1 = subset_pdf.groupby([columns[1], response])[
                    columns[1]
                ].count()
                sub_grp_pdf2 = subset_pdf.groupby([columns[1]])[[columns[1]]].count()
                merge_pdf = pd.merge(
                    sub_grp_pdf1, sub_grp_pdf2, left_index=True, right_index=True
                )
                merge_pdf["prob"] = merge_pdf["pclass_x"] / merge_pdf["pclass_y"]

                contingency_table = pd.crosstab(
                    subset_pdf[response], subset_pdf[columns[1]]
                ).to_numpy()
                py_chi2, py_p_val, py_dof, _ = chi2_contingency(contingency_table)

                vo_chi2_res = vo_tree["children"][col1_cat]["chi2"]
                py_chi2_res = py_chi2

                vo_prob_res = vo_tree["children"][col1_cat]["children"][vo_col2_cat][
                    "prediction"
                ]
                py_prob_res = merge_pdf[
                    merge_pdf.index.get_level_values(0) == col2_cat
                ]["prob"].tolist()

                assert pytest.approx(vo_chi2_res, 1e-02) == pytest.approx(
                    py_chi2_res, 1e-02
                )

                py_prob_res.sort()
                py_prob_res.sort()

                # TO DO: Make more robust
                assert 0 < vo_prob_res[0] < 1
                assert 0 < py_prob_res[0] < 1

    @pytest.mark.parametrize(
        "columns, max_cardinality, expected",
        [
            (["age", "pclass"], 20, ["age", "pclass"]),
            (
                None,
                None,
                [
                    "pclass",
                    "survived",
                    "sex",
                    "age",
                    "sibsp",
                    "parch",
                    "fare",
                    "embarked",
                    "body",
                ],
            ),
        ],
    )
    def test_chaid_columns(self, titanic_vd_fun, columns, max_cardinality, expected):
        """
        test function - chaid_columns
        """
        if columns:
            _vo_res = titanic_vd_fun.chaid_columns(
                columns=columns, max_cardinality=max_cardinality
            )
        else:
            _vo_res = titanic_vd_fun.chaid_columns()
        vo_res = [col.replace('"', "") for col in _vo_res]

        assert vo_res == expected

    @pytest.mark.parametrize(
        "columns, name, threshold, robust",
        [
            ("age", "outliers", 2.5, False),
            ("age", "outliers", 2, True),
        ],
    )
    def test_outliers(self, titanic_vd_fun, columns, name, threshold, robust):
        """
        test function - outliers
        """
        titanic_pdf = titanic_vd_fun.to_pandas()
        titanic_pdf[columns] = titanic_pdf[columns].astype("float")

        titanic_vd_fun.outliers(
            columns=columns, name=name, threshold=threshold, robust=robust
        )
        vo_res = list(chain(*titanic_vd_fun[[name]].to_list()))

        py_data = titanic_pdf[columns]
        if robust:
            titanic_pdf[name] = (
                (
                    abs(py_data - py_data.median())
                    / (1.4826 * median_abs_deviation(py_data, nan_policy="omit"))
                )
                > threshold
            ).astype(int)
        else:
            titanic_pdf[name] = (
                ((py_data - py_data.mean()) / py_data.std()) > threshold
            ).astype(int)
        py_res = titanic_pdf[name].tolist()
        py_res.sort()
        vo_res.sort()

        assert len(vo_res) == len(py_res)

    @pytest.mark.parametrize(
        "response, columns, nbins, method",
        [
            ("survived", "pclass", 16, "same_width"),
        ],
    )
    def test_pivot_table_chi2(
        self,
        titanic_vd_fun,
        response,
        columns,
        nbins,
        method,
    ):
        """
        test function - pivot_table_chi2
        """
        titanic_pdf = titanic_vd_fun.to_pandas()
        (
            vo_chi2,
            vo_p_val,
            vo_dof,
            vo_categories,
            vo_is_numerical,
        ) = titanic_vd_fun.pivot_table_chi2(
            response=response, columns=[columns]
        ).to_list()[
            0
        ]
        contingency_table = pd.crosstab(
            titanic_pdf[response], titanic_pdf[columns]
        ).to_numpy()
        py_chi2, py_p_val, py_dof, _ = chi2_contingency(contingency_table)

        assert (
            (vo_chi2 == pytest.approx(py_chi2))
            and (vo_p_val == pytest.approx(py_p_val))
            and (vo_dof == pytest.approx(py_dof))
        )

    @pytest.mark.parametrize(
        "columns, r",
        [
            (["sepal_length", "sepal_width"], 2),
            (["sepal_length", "sepal_width", "petal_length"], 3),
        ],
    )
    def test_polynomial_comb(self, iris_vd_fun, columns, r):
        """
        test function - polynomial_comb
        """
        iris_pdf = iris_vd_fun.to_pandas()

        col_name = "_".join(columns)
        vo_res = iris_vd_fun.polynomial_comb(columns=columns, r=r)

        if r == 3:
            iris_pdf[col_name] = (
                iris_pdf[columns[0]] * iris_pdf[columns[1]] * iris_pdf[columns[2]]
            )
        else:
            iris_pdf[col_name] = iris_pdf[columns[0]] * iris_pdf[columns[1]]

        assert vo_res[col_name].sum() == pytest.approx(float(iris_pdf[col_name].sum()))

    def test_recommend(self, market_vd):
        """
        test function - recommend
        """
        # need to check on which library needs to use for comparison. spark uses alternating least squares (ALS)
        assert market_vd.recommend("Name", "Form").shape() == (126, 4)

    def test_score(self, titanic_vd_fun):
        """
        test function - test_score
        """
        vo_res = titanic_vd_fun.score(y_true="age", y_score="fare", metric="r2")

        assert vo_res == pytest.approx(-13.843044361084836)

        vo_res = titanic_vd_fun.score(y_true="age", y_score="fare", metric="mse")

        assert vo_res == pytest.approx(3070.2953742915315)

    @pytest.mark.parametrize(
        "session_threshold, name, expected",
        [
            ("1 time", "slot", "Unsupported interval unit: TIME"),
            ("10 minutes", "slot", (11844, 4)),
            ("1 hour", "slot", (11844, 4)),
        ],
    )
    def test_sessionize(self, smart_meters_vd, session_threshold, name, expected):
        """
        test function - sessionize
        """

        smart_meters_copy = smart_meters_vd.copy()
        try:
            smart_meters_copy.sessionize(
                ts="time", by=["id"], session_threshold=session_threshold, name=name
            )
            assert smart_meters_copy.shape() == expected
        except ValueError as exception_info:
            assert expected in exception_info.args[0]

    def test_train_test_split(self, titanic_vd_fun):
        """
        test function - train_test_split
        """
        titanic_pdf = titanic_vd_fun.to_pandas()
        vo_train, vo_test = titanic_vd_fun.train_test_split(
            test_size=0.25, order_by={"name": "asc"}, random_state=1
        )

        py_train, py_test = model_selection.train_test_split(
            titanic_pdf, test_size=0.25, random_state=1
        )

        assert len(vo_train) == pytest.approx(len(py_train), 1e-01) and len(
            vo_test
        ) == pytest.approx(len(py_test), 1e-01)
