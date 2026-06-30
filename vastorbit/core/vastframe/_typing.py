"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional, Union, TYPE_CHECKING

from vastorbit._typing import SQLColumns
from vastorbit._utils._parsers import guess_sep
from vastorbit._utils._sql._cast import to_sql_dtype, to_category
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import clean_query
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.errors import ConversionError

from vastorbit.core.tablesample.base import TableSample

from vastorbit.core.vastframe._read import vDFRead, vDCRead

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFTyping(vDFRead):
    @save_vastorbit_logs
    def astype(self, dtype: dict) -> "VastFrame":
        """
        Converts the VastColumns to the input types.

        Parameters
        ----------
        dtype: dict
            Dictionary of the different types. Each key
            of   the   dictionary  must   represent   a
            VastColumn. The dictionary must be similar
            to the following:

            {"column1": "type1", ... "columnk": "typek"}

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

        Let's check the data types of various VastColumns.

        .. code-block:: python

            data.dtypes()

        .. ipython:: python
            :suppress:

            res = data.dtypes()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_astype1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_astype1.html

        Let's change the data type of few VastColumns.

        .. code-block:: python

            data.astype({"fare": "int", "cabin": "varchar(1)"})

        Let's check the data type of various VastColumns again.

        .. code-block:: python

            data.dtypes()

        .. ipython:: python
            :suppress:

            data.astype({"fare": "int", "cabin": "varchar(1)"})
            res = data.dtypes()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_astype2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_astype2.html
        """
        for column in dtype:
            self[self.format_colnames(column)].astype(dtype=dtype[column])
        return self

    @save_vastorbit_logs
    def bool_to_int(self) -> "VastFrame":
        """
        Converts all booleans VastColumns to integers.

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

        Let's create a small dataset:

        .. code-block:: python

            data = vo.VastFrame(
                {
                    "empid": ['1', '2', '3', '4'],
                    "is_temp": [True, False, False, True],
                }
            )
            data

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {
                    "empid": ['1', '2', '3', '4'],
                    "is_temp": [True, False, False, True],
                }
            )
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_booltoint1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_booltoint1.html

        Let's change the data type from bool to int.

        .. code-block:: python

            data.bool_to_int()

        .. ipython:: python
            :suppress:

            res = data.bool_to_int()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_booltoint2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_booltoint2.html
        """
        columns = self.get_columns()
        for column in columns:
            if self[column].isbool():
                self[column].astype("int")
        return self

    def catcol(self, max_cardinality: int = 12) -> list:
        """
        Returns the VastFrame categorical VastColumns.

        Parameters
        ----------
        max_cardinality: int, optional
            Maximum number of unique values to consider
            integer VastColumns as categorical.

        Returns
        -------
        List
            List of the categorical VastColumns names.

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

        Let's check the categorical VastColumns considering maximum
        cardinality as 10.

        .. ipython:: python

            data.catcol(max_cardinality = 10)

        Let's again check the categorical VastColumns considering
        maximum cardinality as 6.

        .. ipython:: python

            data.catcol(max_cardinality = 6)

        Notice that parch and sibsp are not considered because
        their cardinalities are greater than 6.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.datecol` : Returns all VastColumns with date-type values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.numcol` : Returns all VastColumns with numerical values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.get_columns` : Returns all VastColumns.
        """
        columns = []
        for column in self.get_columns():
            if (self[column].category() == "int") and not self[column].isbool():
                is_cat = _executeSQL(
                    query=f"""
                        SELECT 
                            /*+LABEL('VastFrame.catcol')*/ 
                            (APPROX_DISTINCT({column}) < {max_cardinality}) 
                        FROM {self}""",
                    title="Looking at columns with low cardinality.",
                    method="fetchfirstelem",
                )
            elif self[column].category() == "real":
                is_cat = False
            else:
                is_cat = True
            if is_cat:
                columns += [column]
        return columns

    def datecol(self) -> list:
        """
        Returns a list of the VastColumns of type
        date in the VastFrame.

        Returns
        -------
        List
            List of all VastColumns of type date.

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

        Let's create a small dataset:

        .. code-block:: python

            data = vo.VastFrame(
                {
                    "empid": ['1', '2', '3', '4'],
                    "dob": ['1993-01-01', '1988-01-01', '1992-01-01', '1989-01-01'],
                    "doj": ['2022-01-01', '2023-01-01', '2022-01-01', '2023-01-01'],
                    "emp_cat":[933, 945, 723, 799],
                }
            )
            data

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {
                    "empid": ['1', '2', '3', '4'],
                    "dob": ['1993-01-01', '1988-01-01', '1992-01-01', '1989-01-01'],
                    "doj": ['2022-01-01', '2023-01-01', '2022-01-01', '2023-01-01'],
                    "emp_cat":[933, 945, 723, 799],
                }
            )
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_datecol.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_datecol.html

        Let's set the data type of dob and doj to *date*.

        .. code-block:: python

            data["dob"].astype("date")
            data["doj"].astype("date")

        .. ipython:: python
            :suppress:

            data["dob"].astype("date")
            data["doj"].astype("date")

        Let's retrieve the date type VastColumns in the dataset.

        .. ipython:: python

            data.datecol()

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.catcol` : Returns all VastColumns with categorical values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.numcol` : Returns all VastColumns with numerical values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.get_columns` : Returns all VastColumns.
        """
        columns = []
        cols = self.get_columns()
        for column in cols:
            if self[column].isdate():
                columns += [column]
        return columns

    @save_vastorbit_logs
    def dtypes(self) -> TableSample:
        """
        Returns the different VastColumns types.

        Returns
        -------
        TableSample
            result.

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

        Let's check the data type of various VastColumns.

        .. code-block:: python

            data.dtypes()

        .. ipython:: python
            :suppress:

            res = data.dtypes()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_dtypes.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_dtypes.html
        """
        values = {"index": [], "dtype": []}
        for column in self.get_columns():
            values["index"] += [column]
            values["dtype"] += [self[column].ctype()]
        return TableSample(values)

    def numcol(self, exclude_columns: Optional[SQLColumns] = None) -> list:
        """
        Returns a list of names of the numerical VastColumns
        in the VastFrame.

        Parameters
        ----------
        exclude_columns: SQLColumns, optional
            List  of the  VastColumns names to exclude  from
            the final list.

        Returns
        -------
        List
            List of numerical VastColumns names.

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

        Let's create a small dataset:

        .. code-block:: python

            data = vo.VastFrame(
                {
                    "empid": ['1', '2', '3', '4'],
                    "weight": [140.5, 175, 156.5, 178],
                    "height": [168.5, 175, 178.5, 170],
                    "emp_cat":[933, 945, 723, 799],
                }
            )
            data

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {
                    "empid": ['1', '2', '3', '4'],
                    "weight": [140.5, 175, 156.5, 178],
                    "height": [168.5, 175, 178.5, 170],
                    "emp_cat":[933, 945, 723, 799],
                }
            )
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_numcol.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_numcol.html

        Let's retrieve the numeric type VastColumns in the dataset.

        .. ipython:: python

            data.numcol()

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.catcol` : Returns all VastColumns with categorical values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.datecol` : Returns all VastColumns with date-type values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.get_columns` : Returns all VastColumns.
        """
        columns, cols = [], self.get_columns(exclude_columns=exclude_columns)
        for column in cols:
            if self[column].isnum():
                columns += [column]
        return columns


class vDCTyping(vDCRead):
    @save_vastorbit_logs
    def astype(self, dtype: Union[str, type]) -> "VastFrame":
        """
        Converts the VastColumn to the input type.

        Parameters
        ----------
        dtype: str or Python data type
            New type. One of the following values:

            - 'json' : Converts to a JSON string.
            - 'array': Converts to an array.

        Returns
        -------
        VastFrame
            self._parent

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

        Let's check the data type of fare VastColumn.

        .. ipython:: python

            data["fare"].dtype()

        Let's change the data type of fare to integer.

        .. code-block:: python

            data["fare"].astype(int)

        .. ipython:: python
            :suppress:

            data["fare"].astype(int)

        Let's check the data type of fare VastColumn again.

        .. ipython:: python

            data["fare"].dtype()

        Now, let's see how we can change the data type from
        string to array. Let's create a small dataset.

        .. code-block:: python

            data = vo.VastFrame(
                {
                    "artists": ["Inna, Alexandra, Reea", "Rihanna, Beyonce"]
                }
            )
            data["artists"].astype("array")

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {
                    "artists": ["Inna, Alexandra, Reea", "Rihanna, Beyonce"]
                }
            )
            res = data["artists"].astype("array")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_astypecol1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_astypecol1.html

        Let's change the datatype of artists to json.

        .. code-block:: python

            data["artists"].astype("json")

        .. ipython:: python
            :suppress:

            res = data["artists"].astype("json")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_astypecol2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_astypecol2.html
        """
        dtype = to_sql_dtype(dtype)
        try:
            if (dtype == "array") and self.category() == "text":
                query = f"""
                    SELECT 
                        {self} 
                    FROM {self._parent} 
                    ORDER BY LENGTH({self}) DESC 
                    LIMIT 1"""
                biggest_str = _executeSQL(
                    query,
                    title="getting the biggest string",
                    method="fetchfirstelem",
                )
                biggest_str = biggest_str.strip()
                sep = guess_sep(biggest_str)
                transformation_2 = None
                if dtype == "array":
                    if len(biggest_str) > 2 and (
                        (biggest_str.startswith("(") and biggest_str.endswith(")"))
                        or (biggest_str.startswith("{") and biggest_str.endswith("}"))
                    ):
                        # Need to strip the opening and closing characters
                        transformation_2 = f"""
                            SPLIT(SUBSTR({{}}, 2, LENGTH({{}}) - 2), '{sep}')"""
                    else:
                        transformation_2 = f"""
                            SPLIT({{}}, '{sep}')"""
            elif dtype == "json":
                transformation_2 = "JSON_FORMAT(CAST({} AS JSON))"
                dtype = "varchar"
            else:
                transformation_2 = f"CAST({{}} AS {dtype})"
            transformation_2 = clean_query(transformation_2)
            transformation = (transformation_2.format(self._alias), transformation_2)
            query = f"""
                SELECT 
                    /*+LABEL('VastColumn.astype')*/ 
                    {transformation[0]} AS {self} 
                FROM {self._parent} 
                WHERE {self} IS NOT NULL 
                LIMIT 20"""
            _executeSQL(
                query,
                title="Testing the Type casting.",
            )
            self._transf += [
                (
                    transformation[1],
                    dtype,
                    to_category(ctype=dtype),
                )
            ]
            self._parent._add_to_history(
                f"[AsType]: The VastColumn {self} was converted to {dtype}."
            )
            return self._parent
        except Exception as e:
            raise ConversionError(
                f"{e}\nThe VastColumn {self} can not be converted to {dtype}"
            ) from e

    def category(self) -> str:
        """
        Returns the category of the VastColumn. The category
        will be one of the following:
        date / int / float / text / binary / spatial / uuid
        / undefined

        Returns
        -------
        str
            VastColumn category.

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

        Let's check the category of "fare" and "name" VastColumns.

        .. ipython:: python

            data["fare"].category()

        .. ipython:: python

            data["name"].category()
        """
        return self._transf[-1][2]

    def ctype(self) -> str:
        """
        Returns the VastColumn DB type.

        Returns
        -------
        str
            VastColumn DB type.

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

        Let's check the DB type of "fare" and "name" VastColumns.

        .. ipython:: python

            data["fare"].ctype()

        .. ipython:: python

            data["name"].ctype()
        """
        return self._transf[-1][1].lower()

    dtype = ctype

    def isarray(self) -> bool:
        """
        Returns True if the VastColumn is an array,
        False otherwise.

        Returns
        -------
        bool
            True if the VastColumn is an array.

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

        Let's create a small dataset.

        .. code-block:: python

            data = vo.VastFrame(
                {"artists": ["Inna, Alexandra, Reea", "Rihanna, Beyonce"]}
            )
            data["artists"].astype("array")

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {"artists": ["Inna, Alexandra, Reea", "Rihanna, Beyonce"]}
            )
            res = data["artists"].astype("array")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_isarray.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_isarray.html

        Let's check if data type of "artists" VastColumn is array or not.

        .. ipython:: python

            data["artists"].isarray()
        """
        return self.ctype()[0:5].lower() == "array"

    def isbool(self) -> bool:
        """
        Returns True if the VastColumn is boolean,
        False otherwise.

        Returns
        -------
        bool
            True if the VastColumn is boolean.

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

        Let's create a small dataset:

        .. code-block:: python

            data = vo.VastFrame(
                {
                    "empid": [1, 2, 3, 4],
                    "is_temp": [True, False, False, True],
                }
            )
            data

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {
                    "empid": [1, 2, 3, 4],
                    "is_temp": [True, False, False, True],
                }
            )
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_isbool.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_isbool.html

        Let's check if data type of "is_temp" VastColumn is bool or not.

        .. ipython:: python

            data["is_temp"].isbool()

        Let's check if data type of "empid" VastColumn is bool or not.

        .. ipython:: python

            data["empid"].isbool()
        """
        return self.ctype().startswith("bool")

    def isdate(self) -> bool:
        """
        Returns True if the VastColumn category is date,
        False otherwise.

        Returns
        -------
        bool
            True if the VastColumn category is date.

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

        For this example, we will use the ``amazon`` dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            amazon = vod.load_amazon()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_amazon.html

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
            amazon = vod.load_amazon()

        Let's check if the category of "date" VastColumn is date or not.

        .. ipython:: python

            amazon["date"].isdate()

        Let's check if the category of "state" VastColumn is date or not

        .. ipython:: python

            amazon["state"].isdate()
        """
        return self.category() == "date"

    def isnum(self) -> bool:
        """
        Returns True if the VastColumn is numerical,
        False otherwise.

        Returns
        -------
        bool
            True if the VastColumn is numerical.

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

        Let's create a small dataset:

        .. code-block:: python

            data = vo.VastFrame(
                {
                    "empid": [1, 2, 3, 4],
                    "is_temp": [True, False, False, True],
                }
            )
            data

        .. ipython:: python
            :suppress:

            data = vo.VastFrame(
                {
                    "empid": [1, 2, 3, 4],
                    "is_temp": [True, False, False, True],
                }
            )
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_typing_isbool.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_typing_isbool.html

        Let's check if data type of "empid" VastColumn is numerical or not.

        .. ipython:: python

            data["empid"].isnum()

        """
        return self.category() in ("real", "int")
