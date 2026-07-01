"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import decimal
import pickle
import os
from typing import Literal, Optional, Union, TYPE_CHECKING
from collections.abc import Iterable

import numpy as np
import pandas as pd

import vastorbit._config.config as conf
from vastorbit._typing import NoneType, SQLColumns, SQLExpression
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident
from vastorbit._utils._sql._random import _current_random
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit.errors import ParsingError


from vastorbit.core.vastframe._sys import vDFSystem

if conf.get_import_success("geopandas"):
    from geopandas import GeoDataFrame
    from shapely import wkt
else:
    GeoDataFrame = None
    wkt = None

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame

pickle.DEFAULT_PROTOCOL = 4


class vDFInOut(vDFSystem):
    def copy(self) -> "VastFrame":
        """
        Returns a deep copy of the :py:class:`~VastFrame`.

        Returns
        -------
        VastFrame
            The copy of the :py:class:`~VastFrame`.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's create a copy of data
        :py:class:`~VastFrame`
        and name it data_copy

        .. code-block:: python

            data_copy = data.copy()
            display(data_copy)

        .. ipython:: python
            :suppress:

            data_copy = data.copy()
            res = data_copy
            html_file = open("figures/core_VastFrame_io1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io1.html

        .. note::

            This function creates a deep copy of the
            :py:class:`~VastFrame`. It enables you to
            make modifications without altering the
            main :py:class:`~VastFrame`.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_pickle` :
                Saves the :py:class:`~VastFrame` to a
                Python pickle file.
        """
        return copy.deepcopy(self)

    @save_vastorbit_logs
    def load(self, offset: int = -1) -> "VastFrame":
        """
        Loads a previous structure of the
        :py:class:`~VastFrame`.

        Parameters
        ----------
        offset: int, optional
            Offset of the saving. For example,
            setting to -1 loads the last saving.

        Returns
        -------
        VastFrame
            VastFrame of the loading.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's save the current structure.

        .. code-block:: python

            data.save()

        Let's perform some operations on the
        ``VastFrame``.

        .. code-block:: python

            data.filter("age < 30")
            data.normalize()

        .. ipython:: python
            :suppress:

            data.save()
            data.filter("age < 30")
            res = data.normalize()
            html_file = open("figures/core_VastFrame_io_load1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_load1.html

        .. note::
            You can observe that 699 element(s) were
            filtered out from the VastFrame.

        Now, let's load the last saved
        :py:class:`~VastFrame`.

        .. code-block:: python

            data.load()

        .. ipython:: python
            :suppress:

            res = data.load()
            html_file = open("figures/core_VastFrame_io_load2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_load2.html

        .. note::

            You can observe that the last saved state of
            :py:class:`~VastFrame` having 1234 elements
            has been loaded.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.save` :
                Saves the current :py:class:`~VastFrame`
                structure.
        """
        save = self._vars["saving"][offset]
        vdf = pickle.loads(save)
        return vdf

    @save_vastorbit_logs
    def save(self) -> "VastFrame":
        """
        Saves the current structure of the
        :py:class:`~VastFrame`.
        This function is useful for loading
        previous transformations.

        Returns
        -------
        VastFrame
            self

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's save the current structure.

        .. code-block:: python

            data.save()

        Let's perform some operations on the
        ``VastFrame``.

        .. code-block:: python

            data.filter("age < 30")
            data.normalize()

        .. ipython:: python
            :suppress:

            data.save()
            data.filter("age < 30")
            res = data.normalize()
            html_file = open("figures/core_VastFrame_io_save1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_save1.html

        .. note::
            You can observe that 699 element(s) were
            filtered out from the :py:class:`~VastFrame`.

        Now, let's load the last saved
        :py:class:`~VastFrame`.

        .. code-block:: python

            data.load()

        .. ipython:: python
            :suppress:

            res = data.load()
            html_file = open("figures/core_VastFrame_io_save2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_save2.html

        .. note::

            You can observe that the last saved state of
            :py:class:`~VastFrame` having 1234 elements
            has been loaded.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.load` :
                Loads a saved :py:class:`~VastFrame`
                structure.
        """
        vdf = self.copy()
        self._vars["saving"] += [pickle.dumps(vdf)]
        return self

    @save_vastorbit_logs
    def to_csv(
        self,
        path: Optional[str] = None,
        sep: str = ",",
        na_rep: Optional[str] = None,
        quotechar: str = '"',
        usecols: Optional[SQLColumns] = None,
        header: bool = True,
        new_header: Optional[list] = None,
        order_by: Union[None, SQLColumns, dict] = None,
        n_files: int = 1,
    ) -> Union[None, str, list[str]]:
        """
        Creates  a CSV  file  or  folder of CSV
        files of  the  current :py:class:`~VastFrame`
        relation.

        Parameters
        ----------
        path: str, optional
            File / Folder system path.

            .. warning::

                Be  careful: if a CSV file with
                the same name exists, it will be
                overwritten.
        sep: str, optional
            Column separator.
        na_rep: str, optional
            Missing values representation.
        quotechar: str, optional
            Char that will enclose the ``str``
            values.
        usecols: SQLColumns, optional
            :py:class:`~VastColumn` to select from
            the final :py:class:`~VastFrame` relation.
            If empty, all :py:class:`~VastColumn` are
            selected.
        header: bool, optional
            If set to ``False``, no header is
            written in the CSV file.
        new_header: list, optional
            List of columns used to replace
            :py:class:`~VastColumn` name in
            the CSV.
        order_by: SQLColumns | dict, optional
            List of the :py:class:`~VastColumn`
            used to sort  the data, using asc
            order or a ``dictionary`` of all
            sorting methods. For example, to
            sort by "column1" ASC and "column2"
            DESC, write:
            ``{"column1": "asc", "column2": "desc"}``
        n_files: int, optional
            Integer greater than or equal to 1,
            the number of CSV files to generate.
            If ``n_files > 1``, you must also set
            ``order_by`` to sort the data, ideally
            with a column with unique values (e.g.
            ID). Greater values of ``n_files``
            decrease memory usage, but increase
            execution time.

        Returns
        -------
        str or list
            JSON str or list (``n_files > 1``) if
            ``path`` is not defined; otherwise,
            nothing.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's do some transformations.

        .. code-block:: python

            data.get_dummies()
            data.normalize()

        .. ipython:: python
            :suppress:
            :okwarning:

            data.get_dummies()
            res = data.normalize()
            html_file = open("figures/core_VastFrame_io_tocsv1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_tocsv1.html

        Let's create the CSV file of the current
        :py:class:`~VastFrame`.

        .. ipython:: python

            data[0:2].to_csv()

        Let's create 2 CSV files and
        sort the elements by "name".

        .. ipython:: python

            data[0:2].to_csv(n_files = 2, order_by = "name")

        .. note::

            In this sample, we only export the first
            two rows to avoid display problems.

        .. note::

            vastorbit simplifies CSV export, which can
            be useful for exporting data to another
            environment.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db` :
                Saves the current structure of
                :py:class:`~VastFrame` to the
                VAST DataBase.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_json` :
                Creates a JSON file of the current
                :py:class:`~VastFrame` structure.
        """
        order_by, usecols, new_header = format_type(
            order_by, usecols, new_header, dtype=list
        )
        if n_files < 1:
            raise ValueError("Parameter 'n_files' must be greater or equal to 1.")
        if (n_files != 1) and not order_by:
            raise ValueError(
                "If you want to store the VastFrame in many CSV files, "
                "you have to sort your data by using at least one column. "
                "If the column hasn't unique values, the final result can "
                "not be guaranteed."
            )
        columns = self.get_columns() if not usecols else quote_ident(usecols)
        for col in columns:
            if self[col].category() in ("complex"):
                raise TypeError(
                    f"Impossible to export virtual column {col} as"
                    " it includes complex data types. "
                    "Use 'astype' method to cast them before using "
                    "this function."
                )
        if (new_header) and len(new_header) != len(columns):
            raise ParsingError("The header has an incorrect number of columns")
        total = self.shape()[0]
        current_nb_rows_written, file_id = 0, 0
        limit = int(total / n_files) + 1
        order_by = self._get_sort_syntax(order_by)
        if not order_by:
            order_by = self._get_last_order_by()
        if n_files > 1 and path:
            os.makedirs(path)
        csv_files = []
        while current_nb_rows_written < total:
            if new_header:
                csv_file = sep.join(
                    [
                        quotechar + column.replace('"', "") + quotechar
                        for column in new_header
                    ]
                )
            elif header:
                csv_file = sep.join(
                    [
                        quotechar + column.replace('"', "") + quotechar
                        for column in columns
                    ]
                )
            result = _executeSQL(
                query=f"""
                    SELECT 
                        /*+LABEL('VastFrame.to_csv')*/ 
                        {', '.join(columns)} 
                    FROM {self}
                    {order_by} 
                    OFFSET {current_nb_rows_written}
                    LIMIT {limit} 
                    """,
                title="Reading the data.",
                method="fetchall",
            )
            for row in result:
                tmp_row = []
                for item in row:
                    if isinstance(item, str):
                        tmp_row += [
                            quotechar
                            + item.replace(quotechar, quotechar * 2)
                            + quotechar
                        ]
                    elif isinstance(item, NoneType):
                        tmp_row += ["" if isinstance(na_rep, NoneType) else na_rep]
                    else:
                        tmp_row += [str(item)]
                csv_file += "\n" + sep.join(tmp_row)
            current_nb_rows_written += limit
            file_id += 1
            if n_files == 1 and path:
                with open(path, "w+", encoding="utf-8") as f:
                    f.write(csv_file)
            elif path:
                with open(f"{path}/{file_id}.csv", "w+", encoding="utf-8") as f:
                    f.write(csv_file)
            else:
                csv_files += [csv_file]
        if not path:
            if n_files == 1:
                return csv_files[0]
            else:
                return csv_files

    @save_vastorbit_logs
    def to_db(
        self,
        name: str,
        usecols: Optional[SQLColumns] = None,
        relation_type: Literal["view", "table", "insert"] = "view",
        inplace: bool = False,
        db_filter: SQLExpression = "",
        nb_split: int = 0,
        order_by: Union[None, SQLColumns, dict] = None,
    ) -> "VastFrame":
        """
        Saves the :py:class:`~VastFrame`
        current relation to the VAST
        database.

        Parameters
        ----------
        name: str
            Name of the relation. To save the
            relation in a specific schema,
            you can write ``'"my_schema"."my_relation"'``.
            Use  double  quotes '"' to avoid
            errors due to special characters.
        usecols: SQLColumns, optional
            :py:class:`~VastColumn` to select from the
            final :py:class:`~VastFrame` relation. If
            empty, all :py:class:`~VastColumn` are
            selected.
        relation_type: str, optional
            Type of the relation.

             - view:
                View.
             - table:
                Table.
             - insert:
                Inserts into an existing table.
        inplace: bool, optional
            If set to ``True``, the
            :py:class:`~VastFrame` is replaced
            with the new relation.
        db_filter: SQLExpression, optional
            Filter used before  creating the
            relation in the DB. It can be a
            ``list`` of conditions or an
            expression. This parameter is
            useful for creating train and
            test sets on TS.
        nb_split: int, optional
            If this parameter is greater than
            0, it adds a new column ``'_vastorbit_split_'``
            to the final relation. This column
            contains values in ``[0;nb_split - 1]``
            where each category represents ``1 / nb_split``
            of the entire distribution.
        order_by: SQLColumns | dict, optional
            List of the :py:class:`~VastColumn` used to
            sort the data, using asc order or a
            ``dictionary`` of all sorting methods.
            For example, to sort by "column1"
            ASC and "column2" DESC, write:
            ``{"column1": "asc", "column2": "desc"}``

        Returns
        -------
        VastFrame
            self

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's do some transformations.

        .. code-block:: python

            data.get_dummies()
            data.normalize()

        .. ipython:: python
            :suppress:
            :okwarning:

            data.get_dummies()
            res = data.normalize()
            html_file = open("figures/core_VastFrame_io_todb1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_todb1.html

        Let's save the result in the Database.

        .. code-block:: python

            data.to_db(
                name = '"default"."data_normalized"',
                usecols = ["fare", "sex", "survived"],
                relation_type = "table",
            )
            vo.VastFrame('"default"."data_normalized"')

        .. ipython:: python
            :suppress:
            :okexcept:

            data.to_db(
                name = '"default"."data_normalized"',
                usecols = ["fare", "sex", "survived"],
                relation_type = "table",
            )
            res = vo.VastFrame('"default"."data_normalized"')
            html_file = open("figures/core_VastFrame_io_todb2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_todb2.html

        Let's add a split column in the final relation.

        .. code-block:: python

            data.to_db(
                name = '"default"."data_norm_split"',
                usecols = ["fare", "sex", "survived"],
                relation_type = "table",
                nb_split = 3,
            )
            vo.VastFrame('"default"."data_norm_split"')

        .. ipython:: python
            :suppress:
            :okexcept:

            data.to_db(
                name = '"default"."data_norm_split"',
                usecols = ["fare", "sex", "survived"],
                relation_type = "table",
                nb_split = 3,
            )
            res = vo.VastFrame('"default"."data_norm_split"')
            html_file = open("figures/core_VastFrame_io_todb3.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_todb3.html

        Let's use conditions to filter data.

        .. code-block:: python

            data.to_db(
                name = '"default"."data_norm_filter"',
                usecols = ["fare", "sex", "survived"],
                relation_type = "table",
                db_filter = "sex = 'female'",
            )
            vo.VastFrame('"default"."data_norm_filter"')

        .. ipython:: python
            :suppress:
            :okexcept:

            data.to_db(
                name = '"default"."data_norm_filter"',
                usecols = ["fare", "sex", "survived"],
                relation_type = "table",
                db_filter = "sex = 'female'",
            )
            res = vo.VastFrame('"default"."data_norm_filter"')
            html_file = open("figures/core_VastFrame_io_todb4.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_todb4.html

        .. note::

            The ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db` method enables
            you to save the :py:class:`~VastFrame` into
            various types of relations, including views,
            temporary tables, and regular tables. It also
            allows for inserting elements into an existing
            table, as well as ordering the data using the
            ``order_by`` parameter.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_csv` :
                Creates a CSV file of the current
                :py:class:`~VastFrame` structure.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_json` :
                Creates a JSON file of the current
                :py:class:`~VastFrame` structure.
        """
        relation_type = relation_type.lower()
        usecols, order_by = format_type(usecols, order_by, dtype=list)
        usecols = self.format_colnames(usecols)
        order_by = self._get_sort_syntax(order_by)
        if not order_by:
            order_by = self._get_last_order_by()
        if not usecols:
            usecols = self.get_columns()
            select = "*"
        elif usecols:
            select = ", ".join(quote_ident(usecols))
        else:
            select = []
            for column in usecols:
                ctype, _col = self[column].ctype(), quote_ident(column)
                select += [f"CAST({column} AS {ctype})"]
            select = ", ".join(select)
        insert_usecols = ", ".join(quote_ident(usecols))
        random_func = _current_random(nb_split)
        nb_split = f", {random_func} AS _vastorbit_split_" if (nb_split > 0) else ""
        if isinstance(db_filter, Iterable) and not isinstance(db_filter, str):
            db_filter = " AND ".join([f"({elem})" for elem in db_filter])
        db_filter = f" WHERE {db_filter}" if (db_filter) else ""
        if relation_type == "insert":
            insert_usecols_str = (
                f" ({insert_usecols})" if not nb_split and select != "*" else ""
            )
            query = f"""
                INSERT INTO {name}{insert_usecols_str} 
                    SELECT 
                        {select}{nb_split} 
                    FROM {self}
                    {db_filter}
                    {order_by}"""
            title = f"Inserting data in {name}."
            history_message = (
                "[Insert]: The VastFrame was inserted into the " f"table '{name}'."
            )
        else:
            query = f"""
                CREATE 
                    {relation_type.upper()}
                    {name}
                AS 
                SELECT 
                    /*+LABEL('VastFrame.to_db')*/ 
                    {select}{nb_split} 
                FROM {self}
                {db_filter}
                {order_by}"""
            title = f"Creating a new {relation_type} to save the VastFrame."
            history_message = (
                "[Save]: The VastFrame was saved into a "
                f"{relation_type} named '{name}'."
            )
        _executeSQL(
            query=query,
            title=title,
        )
        if relation_type == "insert":
            _executeSQL(query="COMMIT;", title="Commit.")
        self._add_to_history(history_message)
        if inplace:
            history = self._vars["history"]
            catalog_vars = {}
            for column in usecols:
                catalog_vars[column] = self[column]._catalog
            self.__init__(name)
            self._vars["history"] = history
            for column in usecols:
                self[column]._catalog = catalog_vars[column]
        return self

    @save_vastorbit_logs
    def to_geopandas(self, geometry: str) -> "GeoDataFrame":
        """
        Converts the :py:class:`~VastFrame`
        to a Geopandas ``DataFrame``.

        .. warning::

            The data will be loaded
            in memory.

        Parameters
        ----------
        geometry: str
            ``Geometry`` object used to create
            the ``GeoDataFrame``. It can also
            be a Geography object, which will
            be casted to ``Geometry``.

        Returns
        -------
        geopandas.GeoDataFrame
            The ``geopandas.GeoDataFrame`` of
            the current :py:class:`~VastFrame`
            relation.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the World dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_world()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_world.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_world()

        Let's convert the :py:class:`~VastFrame`
        to a Geopandas ``DataFrame``.

        .. code-block:: python

            data.to_geopandas(geometry = "geometry")

        .. ipython:: python
            :suppress:

            res = data.to_geopandas(geometry = "geometry")
            html_file = open("figures/core_VastFrame_io_gp.html", "w")
            html_file.write(res.to_html(max_rows = 2, justify = "center"))
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_gp.html

        .. warning::

            Exporting to an in-memory object can take time
            if the data is massive. It is recommended to
            downsample the data before using such a function.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db` :
                Saves the current structure of
                :py:class:`~VastFrame` to the
                VAST DataBase.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_json` :
                Creates a JSON file of the current
                :py:class:`~VastFrame` structure.
        """
        if not conf.get_import_success("geopandas"):
            raise ImportError(
                "The geopandas module doesn't seem to be installed in your "
                "environment.\nTo be able to use this method, you'll have to "
                "install it.\n[Tips] Run: 'pip3 install geopandas' in your "
                "terminal to install the module."
            )
        columns = self.get_columns(exclude_columns=[geometry])
        columns = ", ".join(columns + [f"ST_AsText({geometry}) AS {geometry}"])
        query = f"""
            SELECT 
                /*+LABEL('VastFrame.to_geopandas')*/ {columns} 
            FROM {self}
            {self._get_last_order_by()}"""
        cursor = _executeSQL(
            query, title="Getting the VastFrame values.", method="cursor"
        )
        column_names = [
            col.name if hasattr(col, "name") else col[0] for col in cursor.description
        ]
        data = cursor.fetchall()
        df = pd.DataFrame(data)
        df.columns = column_names
        if len(geometry) > 2 and geometry[0] == geometry[-1] == '"':
            geometry = geometry[1:-1]
        df[geometry] = df[geometry].apply(wkt.loads)
        df = GeoDataFrame(df, geometry=geometry)
        return df

    @save_vastorbit_logs
    def to_json(
        self,
        path: Optional[str] = None,
        usecols: Optional[SQLColumns] = None,
        order_by: Union[None, SQLColumns, dict] = None,
        n_files: int = 1,
    ) -> Union[None, str, list[str]]:
        """
        Creates  a JSON file or folder of JSON
        files of the  current :py:class:`~VastFrame`
        relation.

        Parameters
        ----------
        path: str, optional
            File / Folder system path.

            .. warning::

                Be careful: if a JSON file with
                the same name exists, it is
                overwritten.
        usecols: SQLColumns, optional
            VastColumns to select from the final
            :py:class:`~VastFrame` relation. If
            empty, all :py:class:`~VastColumn`
            are selected.
        order_by: str | dict | list, optional
            List of the :py:class:`~VastColumn`
            used to sort the data, using asc order
            or ``dictionary`` of all sorting methods.
            For example, to sort by "column1" ASC
            and "column2" DESC, write:
            ``{"column1": "asc", "column2": "desc"}``
        n_files: int, optional
            Integer greater than or equal to 1,
            the number of CSV files to generate.
            If ``n_files > 1``, you must also set
            ``order_by`` to sort the data, ideally
            with a column with unique values
            (e.g. ID). Greater values of ``n_files``
            decrease memory usage, but increase
            execution time.

        Returns
        -------
        str or list
            JSON str or list (``n_files > 1``) if
            ``path`` is not defined; otherwise,
            nothing.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's do some transformations.

        .. code-block:: python

            data.get_dummies()
            data.normalize()

        .. ipython:: python
            :suppress:
            :okwarning:

            data.get_dummies()
            res = data.normalize()
            html_file = open("figures/core_VastFrame_io_tojson1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_tojson1.html

        Let's create the JSON file of the
        current :py:class:`~VastFrame`.

        .. ipython:: python

            data[0:2].to_json()

        Let's create 2 JSON files and sort
        the elements by "name".

        .. ipython:: python

            data[0:2].to_json(
                n_files = 2,
                order_by = "name",
            )

        .. note::

            In this sample, we only export the first
            two rows to avoid display problems.

        .. note::

            vastorbit simplifies JSON export, which
            can be useful for exporting data to
            another environment.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db` :
                Saves the current structure of
                :py:class:`~VastFrame` to the
                VAST DataBase.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_csv` :
                Creates a CSV file of the current
                :py:class:`~VastFrame` structure.
        """
        order_by, usecols = format_type(order_by, usecols, dtype=list)
        if n_files < 1:
            raise ValueError("Parameter 'n_files' must be greater or equal to 1.")
        if (n_files != 1) and not order_by:
            raise ValueError(
                "If you want to store the VastFrame in many JSON files, you "
                "have to sort your data by using at least one column. If "
                "the column hasn't unique values, the final result can not "
                "be guaranteed."
            )
        columns = self.get_columns() if not usecols else quote_ident(usecols)
        transformations = []
        for col in columns:
            if self[col].category() == "complex":
                transformations += [f"JSON_FORMAT(CAST({col} AS JSON)) AS {col}"]
            else:
                transformations += [col]
        total = self.shape()[0]
        current_nb_rows_written, file_id = 0, 0
        limit = int(total / n_files) + 1
        order_by = self._get_sort_syntax(order_by)
        if not order_by:
            order_by = self._get_last_order_by()
        if n_files > 1 and path:
            os.makedirs(path, exist_ok=True)  # Added exist_ok=True
        json_files = []
        while current_nb_rows_written < total:
            result = _executeSQL(
                query=f"""
                    SELECT 
                        /*+LABEL('VastFrame.to_json')*/ 
                        {', '.join(transformations)} 
                    FROM {self}
                    {order_by} 
                    OFFSET {current_nb_rows_written}
                    LIMIT {limit} 
                    """,
                title="Reading the data.",
                method="fetchall",
            )

            # Break if no results returned
            if not result or len(result) == 0:
                break

            json_file = "[\n"
            for row in result:
                tmp_row = []
                for i, item in enumerate(row):
                    if isinstance(item, (float, int, decimal.Decimal)):
                        tmp_row += [f"{quote_ident(columns[i])}: {item}"]
                    elif not isinstance(item, NoneType):
                        tmp_row += [f'{quote_ident(columns[i])}: "{item}"']
                json_file += "{" + ", ".join(tmp_row) + "},\n"

            # Update counter with actual rows returned
            actual_rows_returned = len(result)
            current_nb_rows_written += actual_rows_returned
            file_id += 1

            json_file = json_file[0:-2] + "\n]"

            if n_files == 1 and path:
                with open(path, "w+", encoding="utf-8") as f:
                    f.write(json_file)
            elif path:
                with open(f"{path}/{file_id}.json", "w+", encoding="utf-8") as f:
                    f.write(json_file)
            else:
                json_files += [json_file]

        if not path:
            if n_files == 1:
                return json_files[0]
            else:
                return json_files

    @save_vastorbit_logs
    def to_list(self) -> list:
        """
        Converts the :py:class:`~VastFrame`
        to a Python ``list``.

        .. warning::

            The data will be loaded in memory.

        Returns
        -------
        List
            The list of the current
            :py:class:`~VastFrame`
            relation.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's convert the :py:class:`~VastFrame`
        to a Python ``list``.

        .. ipython:: python

            data[0:2].to_list()

        .. note::

            In this sample, we only export the first
            two rows to avoid display problems.

        .. warning::

            Exporting to an in-memory object can take time
            if the data is massive. It is recommended to
            downsample the data before using such a function.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_numpy` :
                Exports the :py:class:`~VastFrame` to
                a ``numpy.array``.
        """
        res = _executeSQL(
            query=f"""
                SELECT 
                    /*+LABEL('VastFrame.to_list')*/ * 
                FROM {self}
                {self._get_last_order_by()}""",
            title="Getting the VastFrame values.",
            method="fetchall",
        )
        final_result = []
        for row in res:
            final_result += [
                [
                    float(item) if isinstance(item, decimal.Decimal) else item
                    for item in row
                ]
            ]
        return final_result

    @save_vastorbit_logs
    def to_numpy(self) -> np.ndarray:
        """
        Converts the :py:class:`~VastFrame`
        to a ``numpy.array``.

        .. warning::

            The data will be loaded in
            memory.

        Returns
        -------
        numpy.array
            The ``numpy.array`` of the
            current :py:class:`~VastFrame`
            relation.

        Examples
        ---------

        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's convert the VastFrame to a
        ``numpy.array``.

        .. ipython:: python

            data[0:2].to_numpy()

        .. note::

            In this sample, we only export the first
            two rows to avoid display problems.

        .. warning::

            Exporting to an in-memory object can take time
            if the data is massive. It is recommended to
            downsample the data before using such a function.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_pandas` :
                Exports the :py:class:`~VastFrame`
                to a ``pandas.DataFrame``.
        """
        return np.array(self.to_list())

    @save_vastorbit_logs
    def to_pandas(self) -> pd.DataFrame:
        """
        Converts the VastFrame to a
        ``pandas.DataFrame``.

        .. warning::

            The data will be loaded in
            memory.

        Returns
        -------
        pandas.DataFrame
            The ``pandas.DataFrame`` of the
            current :py:class:`~VastFrame`
            relation.

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's convert the :py:class:`~VastFrame`
        to a ``pandas.DataFrame``.

        .. code-block:: python

            data.to_pandas()

        .. ipython:: python
            :suppress:

            res = data.to_pandas()
            html_file = open("figures/core_VastFrame_io_tp.html", "w")
            html_file.write(res.to_html(max_rows = 6, justify = "center"))
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_tp.html

        .. warning::

            Exporting to an in-memory object can take time
            if the data is massive. It is recommended to
            downsample the data before using such a function.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_numpy` :
                Exports the :py:class:`~VastFrame` to a
                ``numpy.array``.
        """
        cursor = _executeSQL(
            query=f"""
                SELECT 
                    /*+LABEL('VastFrame.to_pandas')*/ * 
                FROM {self}{self._get_last_order_by()}""",
            title="Getting the VastFrame values.",
            method="cursor",
        )
        column_names = [column.name for column in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data)
        if not df.empty:
            df.columns = column_names
        else:
            df.reindex(columns=column_names)
        return df

    @save_vastorbit_logs
    def to_pickle(self, name: str) -> "VastFrame":
        """
        Saves the :py:class:`~VastFrame`
        to a Python pickle file.

        Parameters
        ----------
        name: str
            Name of the file.

            .. warning::

                Be careful: if a file
                with the same name exists,
                it is overwritten.

        Returns
        -------
        VastFrame
            self

        Examples
        ---------
        We import :py:mod:`vastorbit`:

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

        For this example, we will use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. note::

            vastorbit offers a wide range of sample
            datasets that are ideal for training
            and testing purposes. You can explore
            the full list of available datasets in
            the :ref:`api.datasets`, which provides
            detailed information on each dataset and
            how to use them effectively. These datasets
            are invaluable resources for honing your
            data analysis and machine learning skills
            within the vastorbit environment.

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        Let's save the :py:class:`~VastFrame`
        to a Python pickle file.

        .. code-block:: python

            data.to_pickle("vdf_data.p")

        Let's unpickle the VastFrame from Python
        pickle file and view it.

        .. code-block:: python

            import pickle

            vdf = pickle.load(open("vdf_data.p", "rb"))
            display(vdf)

        .. ipython:: python
            :suppress:

            data.to_pickle("vdf_data.p")
            import pickle
            res = pickle.load(open("vdf_data.p", "rb"))
            html_file = open("figures/core_VastFrame_io_pickle.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_io_pickle.html

        .. note::

            The structure of the :py:class:`~VastFrame`
            is saved and can be reused in another
            environment. However, the connection cannot
            be saved, and when unpickling the
            :py:class:`~VastFrame`, you will still need
            to connect to the database and have access
            to data with the same structure.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.save` :
                Saves the current :py:class:`~VastFrame`
                structure.
        """
        pickle.dump(self, open(name, "wb"))
        return self
