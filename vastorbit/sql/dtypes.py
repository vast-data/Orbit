"""
SPDX-License-Identifier: Apache-2.0
"""

import uuid

from typing import Optional, Union, List, Tuple

import vastorbit._config.config as conf
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._format import format_type, quote_ident

from vastorbit.connection import current_cursor


def trino_dtype(
    type_name: str, display_size: int = 0, precision: int = 0, scale: int = 0
) -> str:
    """
    Takes as input the Trino type information
    and returns its corresponding data type string.

    Parameters
    ----------
    type_name: str
        Type Name.
    display_size: int, optional
        Display Size.
    precision: int, optional
        Type Precision.
    scale: int, optional
        Scale.

    Returns
    -------
    str
        The final type.

    Examples
    --------
    Let's import the function before proceeding.

    .. ipython:: python

        from vastorbit.sql import trino_dtype

    Let's format a varchar data type.

    .. ipython:: python

        trino_dtype('varchar', 666)

    Let's format a decimal data type.

    .. ipython:: python

        trino_dtype('decimal', precision = 5, scale = 4)

    .. note::

        This function is designed for formatting the cursor-guessed
        data type. Ensuring the optimal performance of the
        ``get_data_types`` function is crucial.

    .. seealso::

        | :py:func:`~vastorbit.get_data_types` : Gets a SQL query data types.
    """
    res = type_name.lower()

    # Types that don't have precision/scale
    no_precision_types = (
        "array",
        "boolean",
        "date",
        "integer",
        "bigint",
        "smallint",
        "tinyint",
        "map",
        "row",
        "uuid",
        "timestamp",
        "time",
        "real",
        "double",
        "json",
    )

    _has_precision_scale = not any(res.startswith(t) for t in no_precision_types)

    return res


# Keep backward compatibility alias
vast_python_dtype = trino_dtype


def get_data_types(
    expr: Optional[str] = None,
    column: Optional[str] = None,
    table_name: Optional[str] = None,
    schema: Optional[str] = None,
    catalog: Optional[str] = None,
    usecols: Optional[List[str]] = None,
) -> Union[str, List[Tuple[str, str]]]:
    """
    Returns customized relation columns and the
    respective data types. This process may create
    a temporary table or use DESCRIBE for metadata.

    If table_name is defined, the expression is
    ignored and the function returns the table/
    view column names and data types.

    Parameters
    ----------
    expr: str, optional
        An expression in pure SQL. If empty, the
        parameter 'table_name' must be defined.
    column: str, optional
        If not empty, the function returns only
        the data type of the input column if it
        is in the relation.
    table_name: str, optional
        Input table Name.
    schema: str, optional
        Table schema.
    catalog: str, optional
        Table catalog (Trino-specific).
    usecols: list, optional
        List of columns to consider. This
        parameter cannot be used if 'column' is
        defined.

    Returns
    -------
    str or list of tuples
        If column is specified, returns the data type string.
        Otherwise, returns a list of (column_name, data_type) tuples.

    Examples
    --------
    Let's import the function before proceeding.

    .. ipython:: python

        from vastorbit.sql import get_data_types

    You can easily retrieve all the types of the columns
    in your SQL query by using this function.

    .. ipython:: python

        get_data_types(
            "SELECT "
            "pclass, embarked, AVG(survived) "
            "FROM titanic "
            "GROUP BY 1, 2"
        )

    You can also retrieve the type of a specific column.

    .. ipython:: python

        get_data_types(
            "SELECT "
            "pclass, embarked, AVG(survived) "
            "FROM titanic "
            "GROUP BY 1, 2",
            column = "pclass",
        )

    .. note::

        This function is employed to determine the column types
        in a SQL query. For tables and views, it uses Trino's
        DESCRIBE or information_schema. For SQL queries, it uses
        the cursor description after executing a LIMIT 0 query.

    .. seealso::

        | :py:func:`~vastorbit.trino_dtype` : Formats the input data type.
    """
    if not schema:
        schema = conf.get_option("temp_schema")

    usecols = format_type(usecols, dtype=list)

    if not expr and not table_name:
        raise ValueError(
            "Missing parameter: 'expr' and 'table_name' cannot both be empty."
        )

    if column and usecols:
        raise ValueError("Parameters 'column' and 'usecols' cannot both be defined.")

    if expr and table_name:
        warning_message = (
            "As parameter 'table_name' is defined, "
            "parameter 'expression' is ignored."
        )
        print_message(warning_message, "warning")

    # If we have a table name, use DESCRIBE or information_schema
    if table_name:
        return _get_table_types(
            table_name=table_name,
            schema=schema,
            catalog=catalog,
            column=column,
            usecols=usecols,
        )

    # For SQL expressions, use cursor description
    return _get_expression_types(
        expr=expr,
        column=column,
        usecols=usecols,
    )


def _get_table_types(
    table_name: str,
    schema: Optional[str] = None,
    catalog: Optional[str] = None,
    column: Optional[str] = None,
    usecols: Optional[List[str]] = None,
) -> Union[str, List[Tuple[str, str]]]:
    """
    Get data types for a table using Trino's DESCRIBE or information_schema.
    """
    cursor = current_cursor()

    # Build the full table reference
    table_ref = table_name
    if schema:
        table_ref = f"{schema}.{table_ref}"
    if catalog:
        table_ref = f"{catalog}.{table_ref}"

    try:
        # Try using DESCRIBE first (more direct)
        cursor.execute(f"DESCRIBE {table_ref}")
        all_columns = cursor.fetchall()

        # Trino DESCRIBE returns: (column_name, data_type, extra, comment)
        ctype = [(col[0], col[1]) for col in all_columns]

        # Filter by usecols if provided
        if usecols:
            usecols_lower = [c.lower() for c in usecols]
            ctype = [
                (name, dtype) for name, dtype in ctype if name.lower() in usecols_lower
            ]

        # Filter by specific column if provided
        if column:
            for name, dtype in ctype:
                if name.lower() == column.lower():
                    return dtype
            raise ValueError(f"Column '{column}' not found in table '{table_ref}'")

        return ctype

    except Exception as e:
        # Fallback to information_schema
        try:
            return _get_table_types_from_information_schema(
                table_name=table_name,
                schema=schema,
                catalog=catalog,
                column=column,
                usecols=usecols,
            )
        except Exception as e2:
            raise ValueError(
                f"Failed to get table types for '{table_ref}': {str(e)}. "
                f"Also failed with information_schema: {str(e2)}"
            ) from e2


def _get_table_types_from_information_schema(
    table_name: str,
    schema: Optional[str] = None,
    catalog: Optional[str] = None,
    column: Optional[str] = None,
    usecols: Optional[List[str]] = None,
) -> Union[str, List[Tuple[str, str]]]:
    """
    Get data types using information_schema.columns.
    """
    cursor = current_cursor()

    # Build the query
    where_clauses = [f"table_name = '{table_name}'"]

    if schema:
        where_clauses.append(f"table_schema = '{schema}'")

    if catalog:
        where_clauses.append(f"table_catalog = '{catalog}'")

    if column:
        where_clauses.append(f"column_name = '{column}'")

    if usecols:
        usecols_quoted = [f"'{c}'" for c in usecols]
        where_clauses.append(f"column_name IN ({', '.join(usecols_quoted)})")

    query = f"""
        SELECT 
            column_name,
            data_type
        FROM information_schema.columns
        WHERE {' AND '.join(where_clauses)}
        ORDER BY ordinal_position
    """

    cursor.execute(query)
    results = cursor.fetchall()

    if not results:
        raise ValueError(f"No columns found for table '{table_name}'")

    if column:
        return results[0][1] if results else None

    return [(row[0], row[1]) for row in results]


def _get_expression_types(
    expr: str,
    column: Optional[str] = None,
    usecols: Optional[List[str]] = None,
) -> Union[str, List[Tuple[str, str]]]:
    """
    Get data types for a SQL expression.
    """
    cursor = current_cursor()

    # Project only the requested columns.
    if column:
        select_clause = quote_ident(column)
    elif usecols:
        select_clause = ", ".join([quote_ident(c) for c in usecols])
    else:
        select_clause = "*"

    inner = f"SELECT {select_clause} FROM ({expr}) AS x"

    # --- Preferred path: PREPARE + DESCRIBE OUTPUT (analysis only) ----------
    stmt_name = "vo_dtype_" + uuid.uuid4().hex
    try:
        cursor.execute(f"PREPARE {stmt_name} FROM {inner}")
        try:
            cursor.execute(f"DESCRIBE OUTPUT {stmt_name}")
            rows = cursor.fetchall()
        finally:
            try:
                cursor.execute(f"DEALLOCATE PREPARE {stmt_name}")
            except Exception:
                pass

        # DESCRIBE OUTPUT columns:
        # (Column Name, Catalog, Schema, Table, Type, Type Size, Aliased)
        ctype = []
        for row in rows:
            col_name = row[0]
            type_str = row[4] if len(row) > 4 and row[4] is not None else None
            # Trino emits a single empty sentinel row for no-output statements.
            if not col_name and not type_str:
                continue
            ctype.append((col_name, trino_dtype(type_name=str(type_str or "unknown"))))

        if ctype:
            if column:
                return ctype[0][1]
            return ctype
        # No usable rows -> fall through to the LIMIT 0 path below.
    except Exception:
        # DESCRIBE OUTPUT unsupported or failed -> fall back below.
        pass

    # --- Fallback: LIMIT 0 + cursor description -----------------------------
    query = f"{inner} LIMIT 0"

    try:
        cursor.execute(query)
        description = cursor.description

        if not description:
            raise ValueError("Query returned no column information")

        # Extract types from cursor description
        # Trino cursor description: (name, type_code, display_size, internal_size,
        #                            precision, scale, null_ok)
        ctype = []
        for desc in description:
            col_name = desc[0]
            # For Trino, the type is usually in desc[1] as a string or type object
            if hasattr(desc[1], "__name__"):
                type_name = desc[1].__name__
            else:
                type_name = str(desc[1])

            # Try to get precision and scale if available
            precision = desc[4] if len(desc) > 4 else 0
            scale = desc[5] if len(desc) > 5 else 0
            display_size = desc[2] if len(desc) > 2 else 0

            formatted_type = trino_dtype(
                type_name=type_name,
                display_size=display_size,
                precision=precision,
                scale=scale,
            )

            ctype.append((col_name, formatted_type))

        if column:
            return ctype[0][1] if ctype else None

        return ctype

    except Exception as e:
        raise ValueError(f"Failed to determine types for expression: {str(e)}") from e
