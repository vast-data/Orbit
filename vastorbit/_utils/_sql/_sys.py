"""
SPDX-License-Identifier: Apache-2.0
"""

import time
from typing import Any, Literal, Optional

import vastorbit._config.config as conf
from vastorbit.connection.global_connection import get_global_connection
from vastorbit._typing import NoneType
from vastorbit._utils._sql._display import print_query, print_time
from vastorbit._utils._sql._format import (
    clean_query,
    erase_label,
    format_type,
    replace_label,
)
from vastorbit.connection.connect import current_cursor


def _executeSQL(
    query: str,
    title: Optional[str] = None,
    data: Optional[list] = None,
    method: Literal[
        "cursor", "fetchrow", "fetchall", "fetchfirstelem", "copy"
    ] = "cursor",
    path: Optional[str] = None,
    print_time_sql: bool = True,
    _clean_query: bool = True,
) -> Any:
    """
    Executes and returns the
    result of the input query.

    Parameters
    ----------
    query: str
        SQL Query.
    title: str, optional
        Query Title. It will be displayed
        with the query if the option is
        activated.
    data: list, optional
        It represents the data we want to
        ingest in the database.
    method: str, optional
        Method to use when executing the
        query.

         - cursor:
            Executes the query and returns
            the cursor.
         - fetchrow:
            Executes the query and returns
            the first row.
         - fetchall:
            Executes the query and returns
            the entire result.
         - fetchfirstelem:
            Executes the query and returns
            the first element.
         - copy:
            Ingests the data and returns
            the cursor.
    path: str, optional
        Only used when ``method = 'copy'``.
        Path to the file to ingest.
    print_time_sql: bool, optional
        If set to ``True``, and the associated
        option is activated, it prints the
        SQL query and the time of execution.

    Returns
    -------
    The result depends on the input method;
    it can be the cursor or the result of
    the query.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._sys import _executeSQL

        # Generating a SQL query.
        query = "SELECT 1, 2, 3"

        # Executing the query and returning the cursor.
        _executeSQL(query, method = 'cursor')

        # Executing the query and returning the first row.
        _executeSQL(query, method = 'fetchrow')

        # Executing the query and returning the first element.
        _executeSQL(query, method = 'fetchfirstelem')

        # Executing the query and returning the entire result.
        _executeSQL(query, method = 'fetchall')

    .. note::

        In case of insertion or ingestion, you
        can use the 'copy' ``method`` to simplify
        the process.

    .. note::

        This function is one of the most crucial
        functions in the entire API. All queries
        pass through it before being executed.

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    data = format_type(data, dtype=list)
    # Replacing the label
    separator = conf.get_option("label_separator")
    suffix = conf.get_option("label_suffix")
    if isinstance(suffix, NoneType):
        separator = None
    if isinstance(suffix, str) and isinstance(separator, NoneType):
        separator = "__"  # Default separator
    query = replace_label(query, separator=separator, suffix=suffix)

    # Cleaning the query

    if _clean_query:
        query = clean_query(query)

    cursor = current_cursor()
    if (
        conf.get_option("sql_on") or (conf.get_option("verbosity") == 3)
    ) and print_time_sql:
        print_query(query, title)
    start_time = time.time()
    if data:
        cursor.executemany(query, data)
    elif method == "copy":
        with open(path, "r", encoding="utf-8") as f:
            cursor.copy(query, f)
    else:
        cursor.execute(query)
    elapsed_time = time.time() - start_time
    if (
        conf.get_option("time_on") or (conf.get_option("verbosity") == 3)
    ) and print_time_sql:
        print_time(elapsed_time)
    if method == "fetchrow":
        return cursor.fetchone()
    elif method == "fetchfirstelem":
        return cursor.fetchone()[0]
    elif method == "fetchall":
        return cursor.fetchall()
    return cursor


def purge_memory(
    schema: str = "default",
    catalog: str = "memory",
    like: Optional[str] = None,
    raise_on_error: bool = False,
) -> int:
    """
    Drops staging tables left behind in Trino's ``memory`` connector.

    VastOrbit ingestion helpers (for example :py:func:`~vastorbit.read_csv`)
    stage data in the ``memory`` connector before copying it into VAST. When a
    load raises before its cleanup step, the staging table survives and either
    fills the connector's memory budget (``MEMORY_LIMIT_EXCEEDED``) or collides
    with the next load (``table ... already exists``). Call this at the start of
    a session, notebook, or documentation build to reset that state.

    Parameters
    ----------
    schema: str, optional
        Schema inside the memory connector to purge. Default: ``"default"``.
    catalog: str, optional
        Catalog name of the memory connector. Default: ``"memory"``.
    like: str, optional
        SQL ``LIKE`` pattern. When set, only tables whose name matches the
        pattern are dropped (for example ``"_vastorbit_tmp_%"`` to spare
        user-created tables). When ``None``, every table in ``schema`` is dropped.
    raise_on_error: bool, optional
        When ``True``, the first failed ``DROP`` is re-raised. When ``False``
        (default), failures are swallowed so a single locked or vanished table
        never aborts the purge.

    Returns
    -------
    int
        Number of tables successfully dropped.

    Examples
    --------
    .. code-block:: python

        from vastorbit._utils._sql._sys import purge_memory

        purge_memory()                      # full reset before an example
        purge_memory(like="_vastorbit_tmp_%")   # only VastOrbit's own staging
    """
    # 1. Enumerate the staging tables currently in the memory connector.
    list_sql = (
        f"SELECT table_name "
        f"FROM {catalog}.information_schema.tables "
        f"WHERE table_schema = '{schema}'"
    )
    if like is not None:
        list_sql += f" AND table_name LIKE '{like}'"

    rows = _executeSQL(
        list_sql,
        title="Listing memory-connector staging tables",
        method="fetchall",
    )
    tables = [row[0] for row in rows] if rows else []

    # 2. Drop each table independently so one failure never blocks the rest.
    dropped = 0
    for table in tables:
        drop_sql = f'DROP TABLE IF EXISTS {catalog}.{schema}."{table}"'
        try:
            _executeSQL(drop_sql, title=f"Dropping {catalog}.{schema}.{table}")
            dropped += 1
        except Exception:
            if raise_on_error:
                raise
    return dropped
