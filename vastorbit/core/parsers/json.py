"""
SPDX-License-Identifier: Apache-2.0
"""

import os
import json
import glob
from typing import Optional, Union, List

import pandas as pd
import numpy as np

import vastorbit._config.config as conf
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_schema_table, quote_ident
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit.connection import current_cursor
from vastorbit.errors import MissingRelation

from vastorbit.core.vastframe.base import VastFrame

from vastorbit.sql.create import create_table
from vastorbit.sql.drop import drop

# Import type inference from CSV module
from vastorbit.core.parsers.csv import infer_trino_type, clean_column_name


@save_vastorbit_logs
def read_json(
    path: str,
    schema: Optional[str] = None,
    table_name: Optional[str] = None,
    catalog: Optional[str] = None,
    dtype: Optional[dict] = None,
    orient: str = "records",
    lines: bool = False,
    insert: bool = False,
    temporary_table: bool = False,
    flatten: bool = True,
    genSQL: bool = False,
) -> Union[VastFrame, List[VastFrame], list[str]]:
    """
    Read JSON file(s) and create table in database via Trino.

    Supports wildcard patterns to load multiple JSON files into the same table.

    Parameters
    ----------
    path : str
        Path to the JSON file(s). Supports wildcards (e.g., ``'data/*.json'``, ``'file_*.json'``)
    schema : str, optional
        Target schema. Supports formats:
        - 'schema_name' (uses default catalog from config)
        - 'catalog.schema_name' (catalog and schema)
        If None, uses 'memory.default'
    table_name : str, optional
        Target table name. If None, generates from filename
        For wildcards, you must provide a table_name
    catalog : str, optional
        Target catalog (overrides catalog from schema parameter)
        Examples: 'hive', 'postgresql', 'vast', 'memory'
    dtype : dict, optional
        Column definitions {column_name: trino_type}
        If None, types are inferred from data
    orient : str, optional
        JSON orientation format (default: 'records')
        Options: 'records', 'index', 'columns', 'values', 'split'
    lines : bool, optional
        If True, read JSON lines format (one JSON object per line)
    insert : bool, optional
        If True, insert into existing table. If False, create new table
    temporary_table : bool, optional
        If True, create temporary table
    flatten : bool, optional
        If True, flatten nested JSON structures (default: True)
    genSQL : bool, optional
        If True, return SQL statements without executing

    Returns
    -------
    VastFrame or List[VastFrame] or list[str]
        If genSQL=False and single file: VastFrame object
        If genSQL=False and multiple files: VastFrame object
        If genSQL=True: List of SQL statements

    Examples
    --------
    Single file:

    .. code-block:: python

        from vastorbit.core.parsers.json import read_json

        # Load to memory.default (temporary)
        vdf = read_json('data.json')

        # Load to specific schema
        vdf = read_json('data.json', schema='public')

    Multiple files with wildcard:

    .. code-block:: python

        # Load all JSON files in a directory into one table
        vdf = read_json('data/*.json', table_name='combined_data')

        # Load files matching pattern
        vdf = read_json('events_2024_*.json', table_name='events_2024')

        # Load JSON lines files
        vdf = read_json('logs/*.jsonl', table_name='logs', lines=True)

    Notes
    -----
    - Complex nested structures are flattened or stored as JSON strings
    - Arrays are converted to JSON strings
    - NULL values are handled properly
    - Memory catalog is used for staging
    """
    # Expand wildcards
    if "*" in path or "?" in path:
        files = sorted(glob.glob(path))
        if not files:
            raise FileNotFoundError(f"No files found matching pattern: {path}")

        # For wildcards, table_name must be provided
        if not table_name:
            raise ValueError(
                "table_name must be provided when using wildcard patterns. "
                "Example: read_json('*.json', table_name='my_table')"
            )

        # Load first file to create table and infer schema
        first_file = files[0]
        print(f"Loading {len(files)} files matching pattern: {path}")
        print(f"Inferring schema from: {first_file}")

        # Load first file (creates table)
        vdf = _read_single_json(
            path=first_file,
            schema=schema,
            table_name=table_name,
            catalog=catalog,
            dtype=dtype,
            orient=orient,
            lines=lines,
            insert=insert,
            temporary_table=temporary_table,
            flatten=flatten,
            genSQL=genSQL,
        )

        if genSQL:
            # For genSQL, just return statements for first file
            return vdf

        # Get the dtype from first file for consistency
        if not dtype:
            # Read first file to get column types
            df_first = _read_json_to_dataframe(first_file, orient, lines, flatten)
            df_first.columns = [clean_column_name(col) for col in df_first.columns]

            # Handle complex types
            for col in df_first.columns:
                if df_first[col].apply(lambda x: isinstance(x, (dict, list))).any():
                    df_first[col] = df_first[col].apply(
                        lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
                    )

            dtype = {}
            for col in df_first.columns:
                dtype[col] = infer_trino_type(df_first[col], col)

        # Load remaining files (insert mode)
        for file_path in files[1:]:
            print(f"Loading: {file_path}")
            _read_single_json(
                path=file_path,
                schema=schema,
                table_name=table_name,
                catalog=catalog,
                dtype=dtype,
                orient=orient,
                lines=lines,
                insert=True,  # Always insert for subsequent files
                temporary_table=temporary_table,
                flatten=flatten,
                genSQL=False,
            )

        print(f"Successfully loaded {len(files)} files into {vdf.current_relation()}")
        return vdf

    else:
        # Single file - use existing logic
        return _read_single_json(
            path=path,
            schema=schema,
            table_name=table_name,
            catalog=catalog,
            dtype=dtype,
            orient=orient,
            lines=lines,
            insert=insert,
            temporary_table=temporary_table,
            flatten=flatten,
            genSQL=genSQL,
        )


def _read_json_to_dataframe(
    path: str,
    orient: str = "records",
    lines: bool = False,
    flatten: bool = True,
) -> pd.DataFrame:
    """
    Helper function to read JSON file into DataFrame.

    Parameters
    ----------
    path : str
        Path to JSON file
    orient : str
        JSON orientation
    lines : bool
        Whether it's JSON lines format
    flatten : bool
        Whether to flatten nested structures

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame
    """
    try:
        if lines:
            # JSON lines format (one object per line)
            df = pd.read_json(path, lines=True, orient="records")
        else:
            # Standard JSON
            df = pd.read_json(path, orient=orient)
    except ValueError as e:
        # Try alternative reading methods
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.json_normalize(data) if flatten else pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.json_normalize([data]) if flatten else pd.DataFrame([data])
            else:
                raise ValueError(f"Unsupported JSON structure: {type(data)}") from e
        except Exception as e2:
            raise ValueError(f"Failed to read JSON file: {e2}") from e2

    # Flatten nested structures if requested
    if flatten and not lines:
        try:
            # Try to normalize nested structures
            if orient == "records" or isinstance(df.iloc[0].to_dict(), dict):
                df = pd.json_normalize(df.to_dict("records"))
        except Exception:
            pass  # Keep original structure if normalization fails

    return df


def _read_single_json(
    path: str,
    schema: Optional[str] = None,
    table_name: Optional[str] = None,
    catalog: Optional[str] = None,
    dtype: Optional[dict] = None,
    orient: str = "records",
    lines: bool = False,
    insert: bool = False,
    temporary_table: bool = False,
    flatten: bool = True,
    genSQL: bool = False,
) -> Union[VastFrame, list[str]]:
    """
    Internal function to read a single JSON file.
    This contains all the original read_json logic.
    """
    # Parse schema and catalog
    if schema and "." in schema:
        # Schema contains catalog: 'catalog.schema'
        parts = schema.split(".")
        if len(parts) == 2:
            catalog = parts[0]
            schema = parts[1]
        else:
            raise ValueError(
                f"Invalid schema format: {schema}. Use 'schema' or 'catalog.schema'"
            )

    # Set defaults
    if not catalog and not schema:
        # Default to memory catalog
        catalog = "memory"
        schema = "default"
    elif not catalog:
        # No catalog specified, use temp_schema config
        schema = schema or conf.get_option("temp_schema")
        # Catalog will be inferred from connection
        catalog = None

    if not table_name:
        # Generate table name from filename
        filename = os.path.basename(path)
        table_name = os.path.splitext(filename)[0]
        table_name = clean_column_name(table_name)

    table_name_quoted = quote_ident(table_name)

    # Build full table name
    if catalog:
        full_table_name = f"{catalog}.{schema}.{table_name_quoted}"
    else:
        full_table_name = format_schema_table(schema, table_name)

    # Check if table exists
    if not genSQL:
        cursor = current_cursor()
        try:
            cursor.execute(f"SELECT 1 FROM {full_table_name} LIMIT 1")
            table_exists = True
        except Exception:
            table_exists = False

        if table_exists and not insert:
            raise NameError(f"The table {full_table_name} already exists!")

        if not table_exists and insert:
            raise MissingRelation(f"The table {full_table_name} doesn't exist!")

    # Read JSON file
    df = _read_json_to_dataframe(path, orient, lines, flatten)

    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]

    # Handle complex data types (convert to JSON strings)
    for col in df.columns:
        # Check if column contains complex types (dicts, lists)
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )

    # Infer or use provided data types
    if not dtype:
        dtype = {}
        for col in df.columns:
            dtype[col] = infer_trino_type(df[col], col)
    else:
        # When inserting, we need to handle column mismatches gracefully
        if insert:
            # Add missing columns with NULL values
            missing_in_df = set(dtype.keys()) - set(df.columns)
            for col in missing_in_df:
                df[col] = None

            # Remove extra columns not in dtype
            extra_in_df = set(df.columns) - set(dtype.keys())
            if extra_in_df:
                print(f"Warning: Dropping columns not in schema: {extra_in_df}")
                df = df.drop(columns=list(extra_in_df))

            # Reorder columns to match dtype
            df = df[list(dtype.keys())]
        else:
            # For create mode, ensure all columns in dtype are in dataframe
            missing_cols = set(dtype.keys()) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Columns in dtype not found in JSON: {missing_cols}")

    # Convert datetime columns
    for col, col_type in dtype.items():
        if col not in df.columns:
            continue

        col_type_upper = col_type.upper()
        if "DATE" in col_type_upper or "TIMESTAMP" in col_type_upper:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Create memory table name
    memory_table = f"temp_{table_name}_{os.getpid()}"

    # Generate SQL statements
    sql_statements = []

    # 1. CREATE TABLE statement
    if not insert:
        create_sql = create_table(
            table_name=table_name_quoted,
            dtype=dtype,
            schema=schema,
            temporary_table=temporary_table,
            genSQL=True,
        )
        sql_statements.append(create_sql)

    if genSQL:
        # Just return the CREATE TABLE SQL
        insert_sql = f"""
            -- Load JSON data from {path}
            -- Note: Execute this via read_json() without genSQL=True
            INSERT INTO {full_table_name}
            SELECT * FROM memory.default.{memory_table};
        """
        sql_statements.append(insert_sql)
        return sql_statements

    # Execute the load
    cursor = current_cursor()

    try:
        # Create memory table
        columns_def = ", ".join([f'"{col}" {dtype[col]}' for col in dtype.keys()])
        create_memory_sql = (
            f"CREATE TABLE memory.default.{memory_table} ({columns_def})"
        )
        cursor.execute(create_memory_sql)

        # Insert data in batches
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i : i + batch_size]

            values_list = []
            for _, row in batch.iterrows():
                values = []
                for col in dtype.keys():
                    if col not in df.columns:
                        values.append("NULL")
                        continue

                    val = row[col]
                    col_type = dtype[col].upper()

                    # Handle NULL/NaN first
                    if pd.isna(val) or val is None:
                        values.append("NULL")
                    # Date types
                    elif "DATE" in col_type and "TIME" not in col_type:
                        try:
                            date_str = pd.Timestamp(val).strftime("%Y-%m-%d")
                            values.append(f"DATE '{date_str}'")
                        except Exception:
                            values.append("NULL")
                    elif "TIMESTAMP" in col_type:
                        try:
                            ts_str = pd.Timestamp(val).strftime("%Y-%m-%d %H:%M:%S")
                            values.append(f"TIMESTAMP '{ts_str}'")
                        except Exception:
                            values.append("NULL")
                    elif "TIME" in col_type and "TIMESTAMP" not in col_type:
                        values.append(f"TIME '{str(val)}'")
                    # Integer types
                    elif "INTEGER" in col_type or "BIGINT" in col_type:
                        try:
                            if isinstance(val, (int, np.integer)):
                                values.append(str(val))
                            elif isinstance(val, (float, np.floating)):
                                values.append(str(int(val)))
                            elif isinstance(val, str):
                                values.append(str(int(float(val))))
                            else:
                                values.append(str(int(val)))
                        except (ValueError, TypeError):
                            values.append("NULL")
                    # Float types
                    elif "DOUBLE" in col_type or "REAL" in col_type:
                        try:
                            if isinstance(val, (int, float, np.integer, np.floating)):
                                values.append(f"CAST({val} AS {col_type})")
                            elif isinstance(val, str):
                                values.append(f"CAST({float(val)} AS {col_type})")
                            else:
                                values.append(f"CAST({val} AS {col_type})")
                        except (ValueError, TypeError):
                            values.append("NULL")
                    # Boolean
                    elif "BOOLEAN" in col_type:
                        if isinstance(val, bool):
                            values.append("TRUE" if val else "FALSE")
                        elif isinstance(val, str):
                            values.append(
                                "TRUE"
                                if val.lower() in ["true", "t", "1", "yes"]
                                else "FALSE"
                            )
                        else:
                            values.append("TRUE" if val else "FALSE")
                    # String/VARCHAR types
                    else:
                        if isinstance(val, str):
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        else:
                            escaped = str(val).replace("'", "''")
                            values.append(f"'{escaped}'")

                values_list.append(f"({', '.join(values)})")

            if values_list:
                insert_sql = f"INSERT INTO memory.default.{memory_table} VALUES {', '.join(values_list)}"
                cursor.execute(insert_sql)

        # Create target table if needed
        if not insert:
            create_sql = create_table(
                table_name=table_name_quoted,
                dtype=dtype,
                schema=schema,
                temporary_table=temporary_table,
            )

        # Copy from memory to VAST
        copy_sql = f"""
            INSERT INTO {full_table_name}
            SELECT * FROM memory.default.{memory_table}
        """
        _executeSQL(copy_sql, title=f"Loading {len(df)} rows into {full_table_name}")

        # Cleanup
        cursor.execute(f"DROP TABLE IF EXISTS memory.default.{memory_table}")

        return VastFrame(table_name, schema=schema)

    except Exception as e:
        # Cleanup on error
        try:
            cursor.execute(f"DROP TABLE IF EXISTS memory.default.{memory_table}")
        except Exception:
            pass

        if not insert:
            try:
                drop(full_table_name, method="table")
            except Exception:
                pass

        raise e


@save_vastorbit_logs
def pjson(path: str, lines: bool = False) -> dict[str, str]:
    """
    Parse a JSON file and return inferred column types.

    Supports wildcard patterns - will analyze first matching file.

    This is a simplified version that returns type information
    without creating tables. Useful for inspecting JSON structure.

    Parameters
    ----------
    path : str
        Path to the JSON file(s). Supports wildcards (e.g., ``'*.json'``)
    lines : bool, optional
        If True, read JSON lines format (default: False)

    Returns
    -------
    dict
        Dictionary mapping column names to Trino types

    Examples
    --------
    .. code-block:: python

        from vastorbit.core.parsers.json import pjson

        # Inspect single JSON
        types = pjson('data.json')
        print(types)
        # {'id': 'INTEGER', 'name': 'VARCHAR(50)', 'metadata': 'VARCHAR'}

        # Inspect first matching JSON
        types = pjson('events_*.json')

        # Inspect JSON lines
        types = pjson('data.jsonl', lines=True)
    """
    # Expand wildcards
    if "*" in path or "?" in path:
        files = sorted(glob.glob(path))
        if not files:
            raise FileNotFoundError(f"No files found matching pattern: {path}")
        path = files[0]
        print(f"Analyzing first file: {path}")

    # Read JSON
    df = _read_json_to_dataframe(path, orient="records", lines=lines, flatten=True)

    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]

    # Handle complex types
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )

    # Infer types
    dtype = {}
    for col in df.columns:
        dtype[col] = infer_trino_type(df[col], col)

    return dtype
