"""
SPDX-License-Identifier: Apache-2.0
"""

from itertools import chain
import pytest


class TestRead:
    """
    test class for read functions test
    """

    @pytest.mark.parametrize("exclude_columns", [["pclass", "age"], None])
    def test_get_columns(self, titanic_vd, exclude_columns):
        """
        test function - get_columns
        """
        titanic_pdf = titanic_vd.to_pandas()

        vo_col_names = [
            col.replace('"', "")
            for col in titanic_vd.get_columns(exclude_columns=exclude_columns)
        ]

        exclude_columns = exclude_columns if exclude_columns else [None]
        py_col_names = [
            col for col in list(titanic_pdf.columns) if col not in exclude_columns
        ]

        assert vo_col_names == py_col_names

    @pytest.mark.parametrize(
        "function_type, columns, limit",
        [
            ("VastFrame", "age", None),
            ("VastFrame", "age", 10),
            ("VastColumn", "ticket", 2),
            ("VastColumn", "ticket", None),
        ],
    )
    @pytest.mark.parametrize("func", ["head", "tail"])
    def test_head_tail(self, titanic_vd, func, function_type, columns, limit):
        """
        test function - head
        """
        titanic_pdf = titanic_vd.to_pandas()

        vdf = titanic_vd.sort({"age": "desc", "name": "asc"})
        pdf = titanic_pdf.sort_values(
            by=["age", "name"], ascending=[False, True]
        ).reset_index(drop=True)

        if function_type == "VastFrame":
            if limit:
                vo_res = getattr(vdf, func)(limit=limit)
                py_res = getattr(pdf, func)(n=limit)
            else:
                vo_res = getattr(vdf, func)()
                py_res = getattr(pdf, func)()

            assert len(vo_res.to_vdf()) == len(py_res)
        else:
            if limit:
                vo_res = list(
                    chain(*getattr(vdf[columns], func)(limit=limit).to_list())
                )
                py_res = getattr(pdf[columns], func)(n=limit).values.tolist()
            else:
                vo_res = list(chain(*getattr(vdf[columns], func)().to_list()))
                py_res = getattr(pdf[columns], func)().values.tolist()

            assert vo_res == py_res

    @pytest.mark.parametrize(
        "function_type, limit, offset, columns, select_column",
        [
            ("VastFrame", 2, 5, None, "name"),
            ("VastFrame", 2, None, None, "name"),
            ("VastFrame", None, 6, None, "name"),
            ("VastFrame", None, None, None, "name"),
            ("VastFrame", 4, 20, ["ticket", "home.dest"], None),
            ("VastFrame", 4, None, ["ticket", "home.dest"], None),
            ("VastFrame", None, 7, ["ticket"], None),
            ("VastColumn", 2, 5, "ticket", "name"),
            ("VastColumn", 2, None, "ticket", "name"),
            ("VastColumn", None, 5, "ticket", "name"),
            ("VastColumn", None, None, "ticket", "name"),
        ],
    )
    def test_iloc(
        self, titanic_vd, function_type, limit, offset, columns, select_column
    ):
        """
        test function - iloc
        """
        titanic_pdf = titanic_vd.to_pandas()

        vdf = titanic_vd.sort({"age": "desc", "name": "asc"})
        pdf = titanic_pdf.sort_values(
            by=["age", "name"], ascending=[False, True]
        ).reset_index(drop=True)
        pdf.index = pdf.index + 1

        if function_type == "VastFrame":
            if limit and offset and columns is None:
                vo_res = vdf.iloc(limit=limit, offset=offset)[select_column]
                py_res = list(
                    chain(
                        *pdf.iloc[offset : offset + limit][
                            [select_column]
                        ].values.tolist()
                    )
                )
            elif limit and offset is None and columns is None:
                vo_res = vdf.iloc(limit=limit)[select_column]
                py_res = list(chain(*pdf.iloc[:limit][[select_column]].values.tolist()))
            elif limit is None and offset and columns is None:
                vo_res = vdf.iloc(offset=offset)[select_column]
                py_res = list(
                    chain(
                        *pdf.iloc[offset : offset + 5][[select_column]].values.tolist()
                    )
                )
            elif columns:
                limit = limit if limit else 5
                offset = offset if offset else 0
                vo_res = list(
                    chain(
                        *vdf.iloc(
                            limit=limit,
                            offset=offset,
                            columns=columns,
                        ).to_list()
                    )
                )
                py_res = list(
                    chain(*pdf.iloc[offset : offset + limit][columns].values.tolist())
                )
            else:
                vo_res = vdf.iloc()[select_column]
                py_res = list(chain(*pdf.iloc[:5][[select_column]].values.tolist()))
        else:
            if limit and offset:
                vo_res = list(
                    chain(*vdf[columns].iloc(limit=limit, offset=offset).to_list())
                )
                py_res = pdf[columns].iloc[offset : offset + limit].values.tolist()
            elif limit and offset is None:
                vo_res = list(chain(*vdf[columns].iloc(limit=limit).to_list()))
                py_res = pdf[columns].iloc[:limit].values.tolist()
            elif limit is None and offset:
                vo_res = list(chain(*vdf[columns].iloc(offset=offset).to_list()))
                py_res = pdf[columns].iloc[offset : offset + 5].values.tolist()
            else:
                vo_res = list(chain(*vdf[columns].iloc().to_list()))
                py_res = pdf[columns].iloc[:5].values.tolist()

        assert vo_res == py_res

    def test_shape(self, titanic_vd):
        """
        test function - shape
        """
        titanic_pdf = titanic_vd.to_pandas()

        assert titanic_vd.shape() == titanic_pdf.shape

    @pytest.mark.parametrize(
        "_columns",
        ["name", ["name", "ticket"]],
    )
    def test_select(self, titanic_vd, _columns):
        """
        test function - select
        """
        titanic_pdf = titanic_vd.to_pandas()
        py_res = titanic_pdf[_columns].values.tolist()
        if isinstance(_columns, list):
            py_res = list(chain(*py_res))

        vo_res = list(chain(*titanic_vd.select(columns=_columns).to_list()))

        vo_res.sort()
        py_res.sort()

        assert vo_res == py_res

    @pytest.mark.parametrize(
        "n, column",
        [(4, "fare"), (None, "fare")],
    )
    @pytest.mark.parametrize("func", ["nlargest", "nsmallest"])
    def test_nlargest_nsmallest(self, titanic_vd, func, n, column):
        """
        test function - nlargest
        """
        titanic_pdf = titanic_vd.to_pandas()
        titanic_pdf[column] = titanic_pdf[column].astype(float)

        if n:
            vo_res = getattr(titanic_vd[column], func)(n=n)[column]
            py_res = getattr(titanic_pdf[column], func)(n=n).values.tolist()
        else:
            vo_res = getattr(titanic_vd[column], func)()[column]
            py_res = getattr(titanic_pdf[column], func)(n=10).values.tolist()

        assert vo_res == py_res
