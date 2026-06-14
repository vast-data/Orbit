"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional, Union, TYPE_CHECKING

from vastorbit._typing import NoneType, SQLColumns, SQLExpression
from vastorbit._utils._object import create_new_vdf
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident
from vastorbit._utils._sql._merge import gen_coalesce, group_similar_names
from vastorbit._utils._gen import gen_col_name
from vastorbit.errors import EmptyParameter

from vastorbit.core.vastframe._join_union_sort import vDFJoinUnionSort

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFPivot(vDFJoinUnionSort):

    @save_vastorbit_logs
    def merge_similar_names(self, skip_word: Union[str, list[str]]) -> "VastFrame":
        """
        Merges  columns with  similar names.  The function  generates
        a COALESCE  statement that  merges the columns into a  single
        column that excludes  the input words. Note that the order of
        the variables in the COALESCE statement is based on the order
        of the 'get_columns' method.

        Parameters
        ----------
        skip_word: str | list, optional
            List  of words to  exclude  from  the provided column  names.
            For example,     if      two      columns      are     named
            'age.information.phone'  and  'age.phone' AND  ``skip_word``  is
            set  to  ``['.information']``,  then  the  two  columns are
            merged  together  with  the   following  COALESCE  statement:
            ``COALESCE("age.phone", "age.information.phone") AS "age.phone"``

        Returns
        -------
        VastFrame
            An object containing the merged element.

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

        For this example, let's generate a dataset
        which has two columns that are duplicates
        with slight change in spelling and some
        missing values:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "user.id": [12, None, 13],
                    "id": [12, 11, None],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_merge_similar_names_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_merge_similar_names_1.html

        In order to remove the redundant column, we
        can combine them using ``merge_similar_names``:

        .. code-block:: python

            vdf.merge_similar_names(skip_word = "user.")

        .. ipython:: python
            :suppress:

            result = vdf.merge_similar_names(skip_word = "user.")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_merge_similar_names.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_merge_similar_names.html

        .. note::

            This function is particularly useful when flattening highly
            nested JSON files. Such files may contain redundant features
            and inconsistencies. The function is designed to merge these
            features, ensuring consistent information.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.pivot` : Pivots the VastFrame.
        """
        columns = self.get_columns()
        skip_word = format_type(skip_word, dtype=list)
        group_dict = group_similar_names(columns, skip_word=skip_word)
        sql = f"SELECT {gen_coalesce(group_dict)} FROM {self}"
        return create_new_vdf(sql)

    @save_vastorbit_logs
    def narrow(
        self,
        index: SQLColumns,
        columns: Optional[SQLColumns] = None,
        col_name: str = "column",
        val_name: str = "value",
    ) -> "VastFrame":
        """
        Returns the Narrow Table of the VastFrame using the input
        VastColumns.

        Parameters
        ----------
        index: SQLColumns
            Index(es) used to identify the Row.
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all VastColumns
            except the index(es) are used.
        col_name: str, optional
            Alias of the VastColumn  representing the different input
            VastColumns names as categories.
        val_name: str, optional
            Alias of the VastColumn  representing the different input
            VastColumns values.

        Returns
        -------
        VastFrame
            the narrow table object.

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

        For this example, let's generate a dataset
        which has multiple columns:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "id": [12, 11, 13],
                    "state": [12, 11, 13],
                    "size":[100, 120, 140],
                    "score": [9, 9.5, 4],
                    "extra_info": ['Grey', 'Black', 'White'],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_narrow_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_narrow_1.html

        To focus only on the quantities of interest, we can
        utilize the ``narrow`` function:

        .. code-block:: python

            vdf.narrow("id", col_name = "state", val_name = "score")

        .. ipython:: python
            :suppress:

            result = vdf.narrow("id", col_name = "state", val_name = "score")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_narrow.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_narrow.html

        .. note::

            The inverse function of ``pivot`` is ``narrow``. With
            both, you can preprocess the table either vertically
            or horizontally. These functions utilize pure SQL
            statements to perform the job.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.pivot` : Pivots the VastFrame.
        """
        index, columns = format_type(index, columns, dtype=list, na_out=self.numcol())
        index, columns = self.format_colnames(index, columns)
        for idx in index:
            if idx in columns:
                columns.remove(idx)
        query = []
        all_are_num, all_are_date = True, True
        for column in columns:
            if not self[column].isnum():
                all_are_num = False
            if not self[column].isdate():
                all_are_date = False
        for column in columns:
            conv = ""
            if not all_are_num and not all_are_date:
                conv_b = "CAST("
                conv_e = " AS VARCHAR)"
            elif self[column].category() == "int":
                conv_b = "CAST("
                conv_e = " AS INT)"
            column_str = column.replace("'", "''")[1:-1]
            query += [f"""
                (SELECT 
                    {', '.join(index)}, 
                    '{column_str}' AS {col_name}, 
                    {conv_b}{column}{conv_e} AS {val_name} 
                FROM {self})"""]
        query = " UNION ALL ".join(query)
        return create_new_vdf(query)

    melt = narrow

    @save_vastorbit_logs
    def pivot(
        self,
        index: str,
        columns: str,
        values: str,
        aggr: str = "sum",
        prefix: Optional[str] = None,
    ) -> "VastFrame":
        """
        Returns the Pivot of the VastFrame using the
        input aggregation.

        Parameters
        ----------
        index: str
            :py:class:`~VastColumn` used to group the
            elements.
        columns: str
            The :py:class:`~VastColumn` used to compute
            the different categories, which then act as
            the columns in the pivot table.
        values: str
            The VastColumn whose values populate the
            new :py:class:`~VastFrame`.
        aggr: str, optional
            Aggregation to use on 'values'.  To use complex
            aggregations, you must use braces: ``{}``. For
            example, to aggregate using the aggregation:
            ``x -> MAX(x) - MIN(x)``, write ``MAX({}) - MIN({})``.
        prefix: str, optional
            The prefix for the pivot table's column names.

        Returns
        -------
        VastFrame
            the pivot table object.

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

        For this example, let's generate a dummy dataset
        representing sales of two items for different dates:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "date": [
                        "2014-01-01",
                        "2014-01-02",
                        "2014-01-01",
                        "2014-01-02",
                    ],
                    "cat": ["A", "A", "B", "B"],
                    "sale": [100, 120, 120, 110],
                }
            )

        .. ipython:: python
            :suppress:

            result = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_pivot_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_pivot_1.html

        To better view the data, we can create a
        pivot table:

        .. code-block:: python

            vdf.pivot(
                index = "date",
                columns = "cat",
                values = "sale",
                aggr = "avg",
            )

        .. ipython:: python
            :suppress:

            result = vdf.pivot(
                index = "date",
                columns = "cat",
                values = "sale",
                aggr = "avg",
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_pivot.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPivot_pivot.html

        .. note::

            The inverse function of ``pivot`` is ``narrow``. With
            both, you can preprocess the table either vertically
            or horizontally. These functions utilize pure SQL
            statements to perform the job.

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.narrow` :
                Narrow Table for a :py:class:`~VastFrame`.
        """
        if isinstance(prefix, NoneType):
            prefix = ""
        index, columns, values = self.format_colnames(index, columns, values)
        aggr = aggr.upper()
        if "{}" not in aggr:
            aggr += "({})"
        new_cols = self[columns].distinct()
        new_cols_trans = []
        ctype = self[columns].ctype().upper()
        if ctype == "FLOAT":
            ctype = "DOUBLE"
        for col in new_cols:
            if isinstance(col, NoneType):
                new_cols_trans += [
                    aggr.replace(
                        "{}",
                        f"(CASE WHEN {columns} IS NULL THEN {values} ELSE NULL END)",
                    )
                    + f'AS "{prefix}NULL"'
                ]
            else:
                new_cols_trans += [
                    aggr.replace(
                        "{}",
                        f"(CASE WHEN {columns} = CAST('{col}' AS {ctype}) THEN {values} ELSE NULL END)",
                    )
                    + f'AS "{prefix}{col}"'
                ]
        return create_new_vdf(
            f"""
            SELECT 
                {index},
                {", ".join(new_cols_trans)}
            FROM {self}
            GROUP BY 1""",
        )
