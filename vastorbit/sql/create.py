"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from vastorbit.connection.errors import QueryError

from vastorbit._utils._sql._format import format_schema_table, quote_ident
from vastorbit._utils._sql._sys import _executeSQL


def create_schema(
    schema: str,
    raise_error: bool = False,
) -> bool:
    """
    Creates a new schema.

    Parameters
    ----------
    schema: str
        Schema name.
    raise_error: bool, optional
        If the schema couldn't be created, the
        function raises an error.

    Returns
    -------
    bool
        True  if  the schema was  successfully
        created, False otherwise.

    Examples
    --------
    Create a new schema:

    .. ipython:: python

        from vastorbit.sql import create_schema

        create_schema(schema = "employees_test")

    .. ipython:: python
        :suppress:

        from vastorbit.sql import drop

        drop("employees_test")

    .. seealso::
        | :py:func:`~vastorbit.create_table` : Creates a table.
    """
    try:
        _executeSQL(f"CREATE SCHEMA {schema};", title="Creating the new schema.")
        return True
    except QueryError:
        if raise_error:
            raise
        return False


def create_table(
    table_name: str,
    dtype: dict,
    schema: Optional[str] = None,
    temporary_table: bool = False,
    genSQL: bool = False,
    raise_error: bool = False,
) -> bool:
    """
    Creates a new table using the input columns'
    names and data types.

    Parameters
    ----------
    table_name: str
        The final table name.
    dtype: dict
        Dictionary  of the user types. Each  key
        represents  a column name and each value
        represents its data type.
        Example: {"age": "int", "name": "varchar"}
    schema: str, optional
        Schema name.
    temporary_table: bool, optional
        If set to True, a temporary table is
        created.
    genSQL: bool, optional
        If set to True, the SQL code for creating
        the final table is generated but not
        executed.
    raise_error: bool, optional
        If  the  relation  couldn't  be  created,
        raises the entire error.

    Returns
    -------
    bool
        True   if  the  table  was   successfully
        created, False otherwise.

    Examples
    --------
    The ``create_table`` function offers multiple options.

    Let's import the function.

    .. ipython:: python

        from vastorbit.sql import create_table

    You can generate the SQL needed to create the table.

    .. ipython:: python

        create_table(
            table_name = "employees",
            schema = "default",
            dtype = {"name": "VARCHAR(60)", "salary": "FLOAT"},
            genSQL = True,
        )

    Or create the table.

    .. ipython:: python

        create_table(
            table_name = "employees",
            schema = "default",
            dtype = {"name": "VARCHAR(60)", "salary": "FLOAT"},
        )

    The table can be utilized as a VastFrame.

    .. code-block:: python

        import vastorbit as vo

        vo.VastFrame("default.employees")

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame, drop

        html_file = open("SPHINX_DIRECTORY/figures/sql_create_create_table.html", "w")
        html_file.write(VastFrame(input_relation = '"default"."employees"')._repr_html_())
        html_file.close()

        drop("default.employees")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_create_create_table.html

    .. seealso::
        | :py:func:`~vastorbit.create_schema` : Creates a schema.
    """
    if schema:
        input_relation = format_schema_table(schema, table_name)
    else:
        input_relation = quote_ident(table_name)
    temp = "TEMPORARY " if temporary_table else ""
    dtype_str = [f"{quote_ident(column)} {dtype[column]}" for column in dtype]
    dtype_str = ", ".join(dtype_str)
    query = f"CREATE {temp}TABLE {input_relation}({dtype_str});"
    if genSQL:
        return query
    try:
        _executeSQL(query, title="Creating the new table.")
        return True
    except QueryError:
        if raise_error:
            raise
        return False
