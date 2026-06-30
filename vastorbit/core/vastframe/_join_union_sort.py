"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import re
from typing import Literal, Optional, Union, TYPE_CHECKING

from vastorbit._typing import SQLColumns, SQLExpression, SQLRelation
from vastorbit._utils._object import create_new_vdf
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import (
    extract_and_rename_subquery,
    format_type,
    quote_ident,
)
from vastorbit._utils._sql._vast_version import vast_version

from vastorbit.core.vastframe._math import vDFMath

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFJoinUnionSort(vDFMath):
    @save_vastorbit_logs
    def append(
        self,
        input_relation: SQLRelation,
        expr1: Optional[SQLExpression] = None,
        expr2: Optional[SQLExpression] = None,
        union_all: bool = True,
    ) -> "VastFrame":
        """
        Merges the VastFrame with another VastFrame or an input
        relation, and returns a new VastFrame.

        .. warning::

            Appending datasets can potentially increase the structural
            weight; exercise caution when performing this operation.

        Parameters
        ----------
        input_relation: SQLRelation
            Relation to merge with.
        expr1: SQLExpression, optional
            List of pure-SQL expressions from the current
            :py:class:`~VastFrame` to use during merging.
            For example,  ``CASE WHEN "column" > 3 THEN 2 ELSE
            NULL END`` and  ``POWER("column", 2)`` will work.
            If empty, all VastFrame VastColumns are used.
            Aliases are recommended to avoid auto-naming.
        expr2: SQLExpression, optional
            List of pure-SQL  expressions from the input relation to
            use during the merging.
            For example, ``CASE WHEN "column" > 3 THEN 2 ELSE NULL END``
            and ``POWER("column", 2)``  will work.  If empty, all input
            relation columns are  used. Aliases  are  recommended to
            avoid auto-naming.
        union_all: bool, optional
            If  set to True, the  VastFrame is merged with the input
            relation using an 'UNION ALL' instead of an 'UNION'.

        Returns
        -------
        VastFrame
           VastFrame of the Union

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        Let us create two :py:class:`~VastFrame` which we can
        merge for this example:

        .. ipython:: python

                vdf = vo.VastFrame(
                    {
                        "score": [12, 11, 13],
                        "cat": ['A', 'B', 'A'],
                    }
                )

                vdf_2 = vo.VastFrame(
                    {
                        "score": [11, 1, 23],
                        "cat": ['A', 'B', 'B'],
                    }
                )

        We can conveniently append the the first
        :py:class:`~VastFrame` with the second one:

        .. code-block:: python

            vdf.append(vdf_2)

        .. ipython:: python
            :suppress:

            result = vdf.append(vdf_2)
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_append.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_append.html

        We can also apply some SQL expressions on the append
        using ``expr1`` and ``expr2``. Let us try to
        limit the maximum value of the second
        :py:class:`~VastFrame` to 20.

        .. code-block:: python

            vdf.append(
                vdf_2,
                expr1 = [
                    'CASE WHEN "score" > 20 THEN 20 ELSE "score" END AS "score"',
                    '"cat"',
                ],
            )

        .. ipython:: python
            :suppress:

            result = vdf.append(vdf_2, expr1=['CASE WHEN "score" > 20 THEN 20 ELSE "score" END AS "score"', '"cat"'])
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_append_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_append_2.html

        .. note::

            vastorbit offers the flexibility to use UNION ALL or simple UNION
            based on your specific use case. The former includes duplicates,
            while the latter handles them. Refer to ``union_all`` for more
            information.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.join` : Joins the
                :py:class:`~VastFrame` with another one or an
                ``input_relation``.
        """
        expr1, expr2 = format_type(expr1, expr2, dtype=list)
        columns = ", ".join(self.get_columns()) if not expr1 else ", ".join(expr1)
        columns2 = columns if not expr2 else ", ".join(expr2)
        union = "UNION" if not union_all else "UNION ALL"
        query = f"""
            (SELECT 
                {columns} 
             FROM {self}) 
             {union} 
            (SELECT 
                {columns2} 
             FROM {input_relation})"""
        return create_new_vdf(query)

    @save_vastorbit_logs
    def join(
        self,
        input_relation: SQLRelation,
        on: Union[None, tuple, dict, list] = None,
        how: Literal["left", "right", "cross", "full", "self", "inner", None] = "inner",
        expr1: Optional[SQLExpression] = None,
        expr2: Optional[SQLExpression] = None,
        on_interpolate: Optional[dict] = None,
    ) -> "VastFrame":
        """
        Joins the :py:class:`~VastFrame` with another
        one or an ``input_relation``.

        .. warning::

            Joins  can  make  the  VastFrame  structure
            heavier.  It is recommended that you check
            the    current     structure    using    the
            ``current_relation``  method  and  save  it
            with the ``to_db`` method, using the parameters
            ``inplace = True`` and ``relation_type = table``.

        Parameters
        ----------
        input_relation: SQLRelation
            Relation to join with.
        on: tuple | dict | list, optional
            If using a list:
            List of 3-tuples. Each tuple must include
            (key1, key2, operator) — where ``key1`` is
            the key of the :py:class:`~VastFrame`,
            ``key2`` is the key of the ``input_relation``,
            and ``operator`` is one of the following:

            - '=':
                exact match
            - '<':
                key1  < key2
            - '>':
                key1  > key2
            - '<=':
                key1 <= key2
            - '>=':
                key1 >= key2
            - 'llike':
                key1 LIKE '%' || key2 || '%'
            - 'rlike':
                key2 LIKE '%' || key1 || '%'

            Some operators need 5-tuples:
            ``(key1, key2, operator, operator2, x)``
            where  ``operator2`` is  a simple operator
            ``(=, >, <, <=, >=)``, x is a ``float`` or
            an ``integer``, and ``operator`` is one of the
            following:

            - 'lev':
                ``LEVENSHTEIN_DISTANCE(key1, key2) operator2 x``

            If using a dictionary:
            This parameter must include all the different
            keys. It must be similar to the following:
            ``{"relationA_key1": "relationB_key1" ...,"relationA_keyk": "relationB_keyk"}``
            where ``relationA`` is the current :py:class:`~VastFrame`
            and ``relationB`` is the ``input_relation`` or
            the input :py:class:`~VastFrame`.

        how: str, optional
            Join Type.

            - left:
                Left Join.
            - right:
                Right Join.
            - cross:
                Cross Join.
            - full:
                Full Outer Join.
            - inner:
                Inner Join.

        expr1: SQLExpression, optional
            List of the different columns in pure SQL
            to select from the current :py:class:`~VastFrame`,
            optionally as aliases. Aliases are recommended
            to avoid ambiguous names. For example: ``column``
            or ``column AS my_new_alias``.
        expr2: SQLExpression, optional
            List of the different columns in pure SQL
            to select from the current :py:class:`~VastFrame`,
            optionally as aliases. Aliases are recommended
            to avoid ambiguous names. For example: ``column``
            or ``column AS my_new_alias``.
        on_interpolate: dict, optional
            Performs an **interpolated** (time-series "as-of")
            join. It must be a dictionary of the form
            ``{"left_time_col": "right_time_col"}`` mapping the
            time column of the current :py:class:`~VastFrame`
            to the time column of the ``input_relation``. For
            each left-hand row, the most recent right-hand row
            whose time is **less than or equal to** the
            left-hand time is matched
            (last-observation-carried-forward)

            .. note::

                Trino exposes no native interpolated / ASOF
                join, so vastorbit emulates it: both relations
                are interleaved on the time axis and the latest
                right-hand reading is propagated forward with
                ``LAST_VALUE(...) IGNORE NULLS``. When
                ``on_interpolate`` is set, ``expr1`` and
                ``expr2`` must list explicit columns, any
                equality keys passed through ``on`` are used to
                partition the interpolation (e.g. independently
                per sensor or per region), and only
                ``how="left"`` (default) and ``how="inner"``
                are supported.

            For example, to enrich smart-meter consumption with
            the most recent weather reading at or before each
            measurement:

            .. code-block:: python

                consumption.join(
                    weather,
                    how = "left",
                    on_interpolate = {"dateUTC": "dateUTC"},
                    expr1 = ["dateUTC", "meterID", "value"],
                    expr2 = ["humidity", "temperature"],
                )

        Returns
        -------
        VastFrame
            object result of the join.

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        Let us create two :py:class:`~VastFrame` which we
        can JOIN for this example:

        .. ipython:: python

            employees_data = vo.VastFrame(
                {
                    "employee_id": [1, 2, 3, 4],
                    "employee_name": ['Alice', 'Bob', 'Charlie', 'David'],
                    "department_id": [101, 102, 101, 103],
                },
            )

            departments_data = vo.VastFrame(
                {
                    "department_id": [101, 102, 104],
                    "department_name": ['HR', 'Finance', 'Marketing'],
                }
            )

        .. ipython:: python
            :suppress:

            result = employees_data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_table1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_table1.html

        .. ipython:: python
            :suppress:

            result = departments_data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_table2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_table2.html

        Let us look at the different type of JOINs
        available below:

        - INNER JOIN
        - LEFT JOIN
        - RIGHT JOIN
        - FULL JOIN

        After that we will also have a look at:

        - Other operators.
        - Special operators like Levenshtein distance.

        INNER JOIN
        ^^^^^^^^^^^

        We can conveniently JOIN the two :py:class:`~VastFrame`
        using the key column. Let us perform an INNER JOIN.
        INNER JOIN is executed to combine rows from both
        the main table and the ``input_relation`` based on
        a specified condition. Only the rows with matching
        values in the specified column are included in the
        result. If there is no match, those rows are
        excluded from the output.

        .. ipython:: python

            result = employees_data.join(
                input_relation = departments_data,
                on = [("department_id", "department_id", "=")],
                how = "inner",
                expr1 = [
                    "employee_id AS ID",
                    "employee_name AS Name",
                ],
                expr2 = ["department_name AS Dep"],
            )

        .. ipython:: python
            :suppress:

            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join.html

        LEFT JOIN
        ^^^^^^^^^^

        Similarly we can perform a LEFT JOIN which ensures that
        all rows from the main table are included in the
        result, and matching rows from the ``input_relation``
        are included if they exist. If there is no match,
        the columns from the input relation will contain
        ``NULL`` values for the corresponding rows in the
        result.

        .. ipython:: python

            left_join_result = employees_data.join(
                input_relation = departments_data,
                on = [("department_id", "department_id", "=")],
                how = "left",
                expr1 = ["employee_id AS ID", "employee_name AS Name"],
                expr2 = ["department_name AS Dep"],
            )

        .. ipython:: python
            :suppress:

            result = left_join_result
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_left_join.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_left_join.html

        RIGHT JOIN
        ^^^^^^^^^^^

        A RIGHT JOIN is employed to include all rows
        from the ``input_relation`` in the result,
        regardless of whether there are matching values
        in the main table. Rows from the main table are
        included if there are matching values, and for
        non-matching rows, the columns from the main
        table will contain NULL values in the result.

        .. ipython:: python

            right_join_result = employees_data.join(
                input_relation = departments_data,
                on = [("department_id", "department_id", "=")],
                how = "right",
                expr1 = ["employee_id AS ID", "employee_name AS Name"],
                expr2 = ["department_name AS Dep"],
            )

        .. ipython:: python
            :suppress:

            result = right_join_result
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_right_join.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_right_join.html

        FULL JOIN
        ^^^^^^^^^^

        A FULL JOIN is utilized to include all rows
        from both the main table and the ``input_relation``
        in the result. Matching rows are included based
        on the specified condition, and for non-matching
        rows in either table, the columns from the non-matching
        side will contain NULL values in the result.
        This ensures that all rows from both tables are
        represented in the output.

        .. ipython:: python

            full_join_result = employees_data.join(
                input_relation = departments_data,
                on = [("department_id", "department_id", "=")],
                how = "full",
                expr1 = ["employee_id AS ID", "employee_name AS Name"],
                expr2 = ["department_name AS Dep"],
            )

        .. ipython:: python
            :suppress:

            result = full_join_result
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_full_join.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_full_join.html

        OTHER OPERATORS
        ^^^^^^^^^^^^^^^^

        Let us explore some additional features of joins.
        For that let us create another table:

        .. ipython:: python

            additional_departments_data = vo.VastFrame(
                {
                    "department_size": [12, 8, 8, 10],
                    "department": ['HR', 'Fin', 'Mar', 'IT'],
                }
            )

        .. ipython:: python
            :suppress:

            result = additional_departments_data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_table_3.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_table_3.html

        Notice the names are a bit different than the "department_name"
        column in the previous ``department_data`` table. In such cases
        we can utilize the ``llike`` operator:

        .. ipython:: python

            department_join = departments_data.join(
                input_relation = additional_departments_data,
                on = [("department_name", "department", "llike")],
                how = "inner",
                expr1 = ["department_id AS ID", "department_name AS Dep"],
                expr2 = ["department_size AS Size"],
            )

        .. ipython:: python
            :suppress:

            result = full_join_result
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_llike.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_join_llike.html

        .. note::

            vastorbit provides an array of join options and diverse
            operators, delivering an exceptional user experience.

        LEVENSHTEIN DISTANCE
        ^^^^^^^^^^^^^^^^^^^^

        vastorbit also allows you to JOIN tables using the
        Levenshtein distance. It is a string similarity metric
        used to compare the similarity between two strings.
        This method can be particularly useful in scenarios
        where slight spelling mistakes are expected between
        keys of different tables.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.append` : Append a
                :py:class:`~VastFrame` with another one or an
                ``input_relation``.
        """
        on = format_type(on, dtype=dict)
        expr1, expr2 = format_type(expr1, expr2, dtype=list, na_out="*")

        if isinstance(on, tuple):
            on = [on]
        on_list = []
        if isinstance(on, dict):
            on_list += [(key, on[key], "=") for key in on]
        else:
            on_list += copy.deepcopy(on) if on else []

        # Checks
        if on_list:
            self.format_colnames([x[0] for x in on_list])
        object_type = None
        if hasattr(input_relation, "object_type"):
            object_type = input_relation.object_type
        if object_type == "VastFrame" and on_list:
            input_relation.format_colnames([x[1] for x in on_list])

        # Relations
        first_relation = extract_and_rename_subquery(self._genSQL(), alias="x")
        second_relation = extract_and_rename_subquery(f"{input_relation}", alias="y")

        # Interpolated ("as-of" / previous-value) join.
        if on_interpolate:
            return self._interpolate_join(
                first_relation=first_relation,
                second_relation=second_relation,
                on_interpolate=on_interpolate,
                on_list=on_list,
                expr1=expr1,
                expr2=expr2,
                how=how,
            )

        # ON
        on_join = []
        # Supported operators
        all_operators = [
            "=",
            ">",
            ">=",
            "<",
            "<=",
            "llike",
            "rlike",
            "lev",
        ]
        simple_operators = all_operators[0:5]

        for x in on_list:
            key1, key2, op = quote_ident(x[0]), quote_ident(x[1]), x[2]
            if op not in all_operators:
                raise ValueError(
                    f"Incorrect operator: '{op}'.\n"
                    f"Supported operators: {', '.join(all_operators)}.\n"
                )
            if op in ("=", ">", ">=", "<", "<="):
                on_join += [f"x.{key1} {op} y.{key2}"]
            elif op == "llike":
                on_join += [f"x.{key1} LIKE CONCAT('%', y.{key2}, '%')"]
            elif op == "rlike":
                on_join += [f"y.{key2} LIKE CONCAT('%', x.{key1}, '%')"]
            elif op == "lev":
                op2, threshold = x[3], x[4]
                if op2 not in simple_operators:
                    raise ValueError(
                        f"Incorrect operator: '{op2}'.\nCorrect values: {', '.join(simple_operators)}."
                    )
                on_join += [
                    f"levenshtein_distance(x.{key1}, y.{key2}) {op2} {threshold}"
                ]

        # Final
        on_join = " ON " + " AND ".join(on_join) if on_join else ""
        expr = [f"x.{key}" for key in expr1] + [f"y.{key}" for key in expr2]
        expr = "*" if not expr else ", ".join(expr)
        if how:
            how = " " + how.upper() + " "
        query = (
            f"SELECT {expr} FROM {first_relation}{how}JOIN {second_relation} {on_join}"
        )
        return create_new_vdf(query)

    def _interpolate_join(
        self,
        first_relation: str,
        second_relation: str,
        on_interpolate: dict,
        on_list: list,
        expr1,
        expr2,
        how: Optional[str] = "left",
    ) -> "VastFrame":
        """
        Build a Trino-compatible interpolated ("previous value" / as-of) join.

        For each left-hand row the most recent right-hand row whose time is
        ``<=`` the left-hand time is matched.
        """

        def _split(prefix: str, e) -> tuple:
            # "col AS alias" -> ("prefix.col AS alias", "alias")
            # "col"          -> ("prefix.col AS col",   "col")
            parts = re.split(r"\s+as\s+", str(e).strip(), flags=re.IGNORECASE)
            col = parts[0].strip()
            name = parts[-1].strip() if len(parts) > 1 else col
            return f"{prefix}.{col} AS {name}", name

        def _is_star(cols) -> bool:
            return (
                not cols
                or cols == "*"
                or any(str(c).strip() in ("*", "") for c in cols)
            )

        # Explicit columns are required to align the two UNION branches.
        if _is_star(expr1) or _is_star(expr2):
            raise ValueError(
                "Interpolated joins ('on_interpolate') require explicit column "
                "lists in both 'expr1' and 'expr2'."
            )

        how = (how or "left").lower()
        if how not in ("left", "inner"):
            raise ValueError(
                "Interpolated joins ('on_interpolate') support only "
                "how='left' (default) or how='inner'."
            )

        # Time axis (first pair of on_interpolate). Keys are quoted exactly like
        # regular `on` keys for consistency with the rest of join().
        left_time_col, right_time_col = next(iter(on_interpolate.items()))
        left_time = f"x.{quote_ident(left_time_col)}"
        right_time = f"y.{quote_ident(right_time_col)}"

        # Equality keys passed via `on` become interpolation partitions.
        part_pairs = [
            (quote_ident(item[0]), quote_ident(item[1]))
            for item in on_list
            if len(item) >= 3 and item[2] == "="
        ]
        part_names = [f"_vo_k{i}" for i in range(len(part_pairs))]

        # Output columns (raw, like the standard join path).
        left_quals = [_split("x", e) for e in expr1]
        right_quals = [_split("y", e) for e in expr2]
        left_names = [name for _, name in left_quals]
        right_names = [name for _, name in right_quals]

        # --- Left branch (src = 1): real left cols, NULL right cols ----------
        left_select = [f"{left_time} AS _vo_t"]
        left_select += [
            f"x.{k1} AS {pname}" for (k1, _), pname in zip(part_pairs, part_names)
        ]
        left_select += [sql for sql, _ in left_quals]
        left_select += [f"NULL AS {name}" for name in right_names]
        left_select += ["NULL AS _vo_rt", "1 AS _vo_src"]
        left_branch = f"SELECT {', '.join(left_select)} FROM {first_relation}"

        # --- Right branch (src = 0): NULL left cols, real right cols ---------
        right_select = [f"{right_time} AS _vo_t"]
        right_select += [
            f"y.{k2} AS {pname}" for (_, k2), pname in zip(part_pairs, part_names)
        ]
        right_select += [f"NULL AS {name}" for name in left_names]
        right_select += [sql for sql, _ in right_quals]
        right_select += [f"{right_time} AS _vo_rt", "0 AS _vo_src"]
        right_branch = f"SELECT {', '.join(right_select)} FROM {second_relation}"

        # --- Carry the latest right-hand reading forward ---------------------
        # The src tiebreak (right = 0 sorts before left = 1) makes an
        # equal-timestamp right row visible to the left row, matching the
        # "<=" (previous-value) semantics of the original INTERPOLATE join.
        partition = "PARTITION BY " + ", ".join(part_names) + " " if part_names else ""
        over = f"OVER ({partition}ORDER BY _vo_t, _vo_src)"

        filled_select = list(left_names)
        filled_select += [
            f"LAST_VALUE({name}) IGNORE NULLS {over} AS {name}" for name in right_names
        ]
        filled_select += [
            f"LAST_VALUE(_vo_rt) IGNORE NULLS {over} AS _vo_rt",
            "_vo_src",
        ]

        merged = f"({left_branch} UNION ALL {right_branch}) AS _vo_merged"
        filled = f"SELECT {', '.join(filled_select)} FROM {merged}"

        # --- Keep left rows; inner additionally requires a matched right row --
        where = "_vo_src = 1"
        if how == "inner":
            where += " AND _vo_rt IS NOT NULL"
        final_cols = ", ".join(left_names + right_names)
        query = f"SELECT {final_cols} FROM ({filled}) AS _vo_filled WHERE {where}"

        return create_new_vdf(query)

    @save_vastorbit_logs
    def sort(self, columns: Union[SQLColumns, dict]) -> "VastFrame":
        """
        Sorts the :py:class:`~VastFrame` using the input
        :py:class:`~VastColumn`.

        Parameters
        ----------
        columns: SQLColumns | dict
            List  of the  :py:class:`~VastColumn`  used to sort
            the data, using asc order or dictionary of all sorting
            methods. For example, to sort by "column1" ASC and
            "column2" DESC, write:
            ``{"column1": "asc", "column2": "desc"}``

        Returns
        -------
        VastFrame
            self

        Examples
        --------
        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        .. hint::

            By assigning an alias to :py:mod:`vastorbit`,
            we mitigate the risk of code collisions with
            other libraries. This precaution is necessary
            because vastorbit uses commonly known function
            names like "average" and "median", which can
            potentially lead to naming conflicts. The use
            of an alias ensures that the functions from
            :py:mod:`vastorbit` are used as intended
            without interfering with functions from other
            libraries.

        Let us create a :py:class:`~VastFrame` which
        we can sort:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "sales": [10, 11, 9, 20, 6],
                    "cat": ['C', 'B', 'A', 'A', 'B'],
                },
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_sort_data.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_sort_data.html

        We can conveniently sort the :py:class:`~VastFrame`
        using a particular column:

        .. ipython:: python

            vdf.sort({"sales": "asc"})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_sort.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_sort.html

        The same operation can also be performed in descending
        order.

        .. ipython:: python

            vdf.sort({"sales": "desc"})

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_sort_2.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_join_union_sort_sort_2.html

        .. note::

            Sorting the data is crucial to ensure consistent output.
            While VAST forgoes the use of indexes for enhanced
            performance, it does not guarantee a specific order of
            data retrieval.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.append` : Append a
                :py:class:`~VastFrame` with another one or an
                ``input_relation``.
        """
        columns = format_type(columns, dtype=list)
        columns = self.format_colnames(columns)
        max_pos = 0
        for column in self._vars["columns"]:
            max_pos = max(max_pos, len(self[column]._transf) - 1)
        self._vars["order_by"][max_pos] = self._get_sort_syntax(columns)
        return self
