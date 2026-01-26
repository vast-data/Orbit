"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional

from vastorbit.connection.errors import MissingRelation, QueryError

from vastorbit._utils._sql._format import (
    format_schema_table,
    schema_relation,
)
from vastorbit._utils._sql._sys import _executeSQL


def drop(
    name: Optional[str] = None,
    method: Literal["auto", "table", "view", "schema"] = "auto",
    raise_error: bool = False,
) -> bool:
    """
    Drops the input relation. This can be a view, table, or schema.

    Parameters
    ----------
    name: str, optional
        Relation name. If empty, the function drops
        all vastorbit temporary elements.
    method: str, optional
        Method used to drop.

         - auto:
            identifies the table or view to drop.
            It never drops an entire schema unless
            the method is set to 'schema'.
         - table:
            drops the input table.
         - view:
            drops the input view.
         - schema:
            drops the input schema.

    raise_error: bool, optional
        If the object couldn't be dropped, this
        function raises an error.

    Returns
    -------
    bool
        True if the relation was dropped,
        False otherwise.

    Examples
    --------
    Create a table:

    .. code-block:: python

        from vastorbit.sql import create_table

        create_table(
            table_name = "table_example",
            schema = "public",
            dtype = {"name": "VARCHAR(60)"},
        )

    Drop the table:

    .. code-block:: python

        from vastorbit.sql import drop

        drop(name = "public.table_example")

    .. warning::

        Dropping an element permanently removes it from
        the database. Please exercise caution, as this
        action is irreversible.

    .. seealso::
        | :py:func:`~vastorbit.create_table` : Creates a table.
    """
    schema, relation = schema_relation(name)
    schema, relation = schema[1:-1], relation[1:-1]

    if not name:
        method = "temp"

    if method == "auto":
        # Check if it's a table
        result = _executeSQL(
            query=f"""
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = '{schema}' 
                AND table_name = '{relation}'
                AND table_type = 'BASE TABLE'
            """,
            print_time_sql=False,
            method="fetchone",
        )
        if result:
            return drop(name=name, method="table", raise_error=raise_error)

        # Check if it's a view
        result = _executeSQL(
            query=f"""
            SELECT 1
            FROM information_schema.views
            WHERE table_schema = '{schema}' 
                AND table_name = '{relation}'
            """,
            print_time_sql=False,
            method="fetchone",
        )
        if result:
            return drop(name=name, method="view", raise_error=raise_error)

        # Not found
        if raise_error:
            raise MissingRelation(f"No relation named '{name}' was detected.")
        return False

    query = ""

    if method == "table":
        query = f"DROP TABLE IF EXISTS {name}"

    elif method == "view":
        query = f"DROP VIEW IF EXISTS {name}"

    elif method == "schema":
        query = f"DROP SCHEMA IF EXISTS {name} CASCADE"

    elif method == "temp":
        # Drop temporary tables
        sql = f"""
        SELECT table_schema, table_name 
        FROM information_schema.tables
        WHERE LOWER(table_name) LIKE '%_vastorbit_tmp_%'
            AND table_type = 'BASE TABLE'
        """
        all_tables = _executeSQL(sql, print_time_sql=False, method="fetchall")

        for elem in all_tables:
            table = format_schema_table(
                elem[0].replace('"', '""'), elem[1].replace('"', '""')
            )
            drop(table, method="table")

        # Drop temporary views
        sql = f"""
        SELECT table_schema, table_name 
        FROM information_schema.views
        WHERE LOWER(table_name) LIKE '%_vastorbit_tmp_%'
        """
        all_views = _executeSQL(sql, print_time_sql=False, method="fetchall")

        for elem in all_views:
            view = format_schema_table(
                elem[0].replace('"', '""'), elem[1].replace('"', '""')
            )
            drop(view, method="view")

        return True

    if query:
        try:
            _executeSQL(query, title="Deleting the relation.")
            return True
        except QueryError:
            if raise_error:
                raise
            return False

    return True
