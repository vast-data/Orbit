"""
SPDX-License-Identifier: Apache-2.0
"""

import os
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


def infer_trino_type(series: pd.Series, column_name: str) -> str:
    """
    Infer Trino data type from pandas Series.

    Parameters
    ----------
    series : pd.Series
        Pandas series to analyze
    column_name : str
        Name of the column (for error messages)

    Returns
    -------
    str
        Trino data type string
    """
    # Remove null values for type inference
    non_null = series.dropna()

    if len(non_null) == 0:
        return "VARCHAR"

    dtype = series.dtype

    # Boolean
    if dtype == "bool":
        return "BOOLEAN"

    # Integer types (but be careful with NaN causing float conversion)
    if dtype in ["int8", "int16", "int32", "int64"]:
        # Check if values fit in INTEGER range
        if non_null.min() >= -2147483648 and non_null.max() <= 2147483647:
            return "INTEGER"
        return "BIGINT"

    # Float types - check if they're actually integers with NaN
    if dtype in ["float16", "float32", "float64"]:
        # Check if all non-null values are integers
        if (non_null % 1 == 0).all():
            # It's integer data stored as float (due to NaN)
            if non_null.min() >= -2147483648 and non_null.max() <= 2147483647:
                return "INTEGER"
            return "BIGINT"

        # True floating point
        if dtype in ["float16", "float32"]:
            return "REAL"
        return "DOUBLE"

    # Datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        # Check if it has time component
        if (non_null.dt.hour != 0).any() or (non_null.dt.minute != 0).any():
            return "TIMESTAMP"
        return "DATE"

    # Object type - need to infer from values
    if dtype == "object":
        # Try to parse as datetime (suppress warnings)
        try:
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed = pd.to_datetime(non_null.head(100), errors="coerce")

            # If most values parsed successfully, it's a date column
            if parsed.notna().sum() / len(parsed) > 0.8:
                # Check first valid value for time component
                first_valid = (
                    parsed.dropna().iloc[0] if len(parsed.dropna()) > 0 else None
                )
                if first_valid and (
                    first_valid.hour != 0
                    or first_valid.minute != 0
                    or first_valid.second != 0
                ):
                    return "TIMESTAMP"
                return "DATE"
        except:
            pass

        # Check if it's numeric
        try:
            numeric = pd.to_numeric(non_null.head(100), errors="coerce")
            valid_numeric = numeric.dropna()

            # If most values parsed successfully, it's numeric
            if len(valid_numeric) / len(numeric) > 0.8:
                if (valid_numeric % 1 == 0).all():
                    # Integer
                    if (
                        valid_numeric.min() >= -2147483648
                        and valid_numeric.max() <= 2147483647
                    ):
                        return "INTEGER"
                    return "BIGINT"
                return "DOUBLE"
        except:
            pass

        # Determine VARCHAR length
        max_len = non_null.astype(str).str.len().max()
        if max_len <= 50:
            return "VARCHAR(50)"
        elif max_len <= 255:
            return f"VARCHAR({min(max_len + 50, 255)})"
        elif max_len <= 65535:
            return f"VARCHAR({min(max_len + 100, 65535)})"
        return "VARCHAR"

    # Default
    return "VARCHAR"


def clean_column_name(col: str) -> str:
    """
    Clean column names for database compatibility.

    Parameters
    ----------
    col : str
        Original column name

    Returns
    -------
    str
        Cleaned column name
    """
    col = col.strip()
    # Remove Unicode smart quotes
    col = col.replace("\u201c", "").replace("\u201d", "")  # " "
    col = col.replace("\u2018", "").replace("\u2019", "")  # ' '
    # Remove regular quotes
    col = col.replace('"', "").replace("'", "")
    col = col.strip()

    # Replace spaces and special characters with underscore
    col = col.replace(" ", "_").replace("-", "_").replace(".", "_")

    # Ensure it starts with a letter or underscore
    if col and not col[0].isalpha() and col[0] != "_":
        col = "_" + col

    return col if col else "column"


def read_csv(
    path: str,
    schema: Optional[str] = None,
    table_name: Optional[str] = None,
    catalog: Optional[str] = None,
    dtype: Optional[dict] = None,
    parse_nrows: int = 1000,
    insert: bool = False,
    temporary_table: bool = False,
    sep: Optional[str] = None,
    header: bool = True,
    header_names: Optional[list] = None,
    na_rep: str = "",
    infer_types: bool = True,
    genSQL: bool = False,
) -> Union[VastFrame, List[VastFrame], list[str]]:
    """
    Read CSV file(s) and create table in database via Trino.

    Supports wildcard patterns to load multiple CSV files into the same table.

    Parameters
    ----------
    path : str
        Path to the CSV file(s). Supports wildcards (e.g., 'data/*.csv', 'file_*.csv')
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
    parse_nrows : int, optional
        Number of rows to use for type inference (default: 1000)
    insert : bool, optional
        If True, insert into existing table. If False, create new table
    temporary_table : bool, optional
        If True, create temporary table
    sep : str, optional
        Column separator. If None, auto-detected
    header : bool, optional
        Whether CSV has header row (default: True)
    header_names : list, optional
        Custom column names (overrides CSV header)
    na_rep : str, optional
        String representing missing values (default: '')
    infer_types : bool, optional
        Whether to infer types from data (default: True)
    genSQL : bool, optional
        If True, return SQL statements without executing

    Returns
    -------
    VastFrame or List[VastFrame] or list[str]
        If genSQL=False and single file: VastFrame object
        If genSQL=False and multiple files: List of VastFrame objects
        If genSQL=True: List of SQL statements

    Examples
    --------
    Single file:

    .. code-block:: python

        from vastorbit.core.parsers.csv import read_csv

        vdf = read_csv('data.csv')

    Multiple files with wildcard:

    .. code-block:: python

        # Load all CSV files in a directory into one table
        vdf = read_csv('data/*.csv', table_name='combined_data')

        # Load files matching pattern
        vdf = read_csv('sales_2024_*.csv', table_name='sales_2024')
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
                "Example: read_csv('*.csv', table_name='my_table')"
            )

        # Load first file to create table and infer schema
        first_file = files[0]
        print(f"Loading {len(files)} files matching pattern: {path}")
        print(f"Inferring schema from: {first_file}")

        # Load first file (creates table)
        vdf = _read_single_csv(
            path=first_file,
            schema=schema,
            table_name=table_name,
            catalog=catalog,
            dtype=dtype,
            parse_nrows=parse_nrows,
            insert=insert,
            temporary_table=temporary_table,
            sep=sep,
            header=header,
            header_names=header_names,
            na_rep=na_rep,
            infer_types=infer_types,
            genSQL=genSQL,
        )

        if genSQL:
            # For genSQL, just return statements for first file
            return vdf

        # Get the dtype from first file for consistency
        if not dtype:
            # Read first file to get column types
            df_first = pd.read_csv(
                first_file, nrows=parse_nrows, sep=sep if sep else ","
            )
            if header:
                df_first.columns = [clean_column_name(col) for col in df_first.columns]
            if header_names:
                df_first.columns = [clean_column_name(col) for col in header_names]

            dtype = {}
            for col in df_first.columns:
                dtype[col] = infer_trino_type(df_first[col], col)

        # Load remaining files (insert mode)
        for file_path in files[1:]:
            print(f"Loading: {file_path}")
            _read_single_csv(
                path=file_path,
                schema=schema,
                table_name=table_name,
                catalog=catalog,
                dtype=dtype,
                parse_nrows=parse_nrows,
                insert=True,  # Always insert for subsequent files
                temporary_table=temporary_table,
                sep=sep,
                header=header,
                header_names=header_names,
                na_rep=na_rep,
                infer_types=False,  # Use dtype from first file
                genSQL=False,
            )

        print(f"Successfully loaded {len(files)} files into {vdf.current_relation()}")
        return vdf

    else:
        # Single file - use existing logic
        return _read_single_csv(
            path=path,
            schema=schema,
            table_name=table_name,
            catalog=catalog,
            dtype=dtype,
            parse_nrows=parse_nrows,
            insert=insert,
            temporary_table=temporary_table,
            sep=sep,
            header=header,
            header_names=header_names,
            na_rep=na_rep,
            infer_types=infer_types,
            genSQL=genSQL,
        )


def _read_single_csv(
    path: str,
    schema: Optional[str] = None,
    table_name: Optional[str] = None,
    catalog: Optional[str] = None,
    dtype: Optional[dict] = None,
    parse_nrows: int = 1000,
    insert: bool = False,
    temporary_table: bool = False,
    sep: Optional[str] = None,
    header: bool = True,
    header_names: Optional[list] = None,
    na_rep: str = "",
    infer_types: bool = True,
    genSQL: bool = False,
) -> Union[VastFrame, list[str]]:
    """
    Internal function to read a single CSV file.
    This contains all the original read_csv logic.
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
        # Clean table name
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
        except:
            table_exists = False

        if table_exists and not insert:
            raise NameError(f"The table {full_table_name} already exists!")

        if not table_exists and insert:
            raise MissingRelation(f"The table {full_table_name} doesn't exist!")

    # Read CSV file
    read_kwargs = {}
    if sep:
        read_kwargs["sep"] = sep
    if not header:
        read_kwargs["header"] = None
    if na_rep:
        read_kwargs["na_values"] = [na_rep]

    # Read sample for type inference
    if infer_types and not dtype:
        df_sample = pd.read_csv(path, nrows=parse_nrows, **read_kwargs)
    else:
        df_sample = pd.read_csv(path, nrows=10, **read_kwargs)

    # Clean column names
    if header:
        df_sample.columns = [clean_column_name(col) for col in df_sample.columns]

    # Apply custom header names
    if header_names:
        header_names_clean = [clean_column_name(col) for col in header_names]
        if len(header_names_clean) != len(df_sample.columns):
            raise ValueError(
                f"header_names length ({len(header_names_clean)}) doesn't match "
                f"number of columns ({len(df_sample.columns)})"
            )
        df_sample.columns = header_names_clean

    # Infer or use provided data types
    if not dtype:
        # Read full file for type inference to ensure consistency
        df_full_for_inference = pd.read_csv(path, **read_kwargs)

        if header:
            df_full_for_inference.columns = [
                clean_column_name(col) for col in df_full_for_inference.columns
            ]

        if header_names:
            df_full_for_inference.columns = header_names_clean

        dtype = {}
        for col in df_full_for_inference.columns:
            dtype[col] = infer_trino_type(df_full_for_inference[col], col)
    else:
        # Ensure all columns in dtype are in dataframe
        missing_cols = set(dtype.keys()) - set(df_sample.columns)
        if missing_cols:
            raise ValueError(f"Columns in dtype not found in CSV: {missing_cols}")

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

    # 2. Load CSV to memory catalog
    # Read full CSV
    df_full = pd.read_csv(path, **read_kwargs)

    if header:
        df_full.columns = [clean_column_name(col) for col in df_full.columns]

    if header_names:
        df_full.columns = header_names_clean

    # Convert datetime columns
    for col, col_type in dtype.items():
        if col not in df_full.columns:
            continue

        col_type_upper = col_type.upper()
        if "DATE" in col_type_upper or "TIMESTAMP" in col_type_upper:
            df_full[col] = pd.to_datetime(df_full[col], errors="coerce")

    if genSQL:
        # Just return the CREATE TABLE SQL
        insert_sql = f"""
            -- Load CSV data from {path}
            -- Note: Execute this via read_csv() without genSQL=True
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
        for i in range(0, len(df_full), batch_size):
            batch = df_full.iloc[i : i + batch_size]

            values_list = []
            for _, row in batch.iterrows():
                values = []
                for col in dtype.keys():
                    if col not in df_full.columns:
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
                        except:
                            values.append("NULL")
                    elif "TIMESTAMP" in col_type:
                        try:
                            ts_str = pd.Timestamp(val).strftime("%Y-%m-%d %H:%M:%S")
                            values.append(f"TIMESTAMP '{ts_str}'")
                        except:
                            values.append("NULL")
                    elif "TIME" in col_type and "TIMESTAMP" not in col_type:
                        values.append(f"TIME '{str(val)}'")
                    # Integer types
                    elif "INTEGER" in col_type or "BIGINT" in col_type:
                        try:
                            # Try to convert to int
                            if isinstance(val, (int, np.integer)):
                                values.append(str(val))
                            elif isinstance(val, (float, np.floating)):
                                values.append(str(int(val)))
                            elif isinstance(val, str):
                                # String value for integer column - try to parse
                                values.append(str(int(float(val))))
                            else:
                                values.append(str(int(val)))
                        except (ValueError, TypeError):
                            # Can't convert to int - use NULL
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
                        # Everything else becomes a string
                        if isinstance(val, str):
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        else:
                            # Convert to string
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
        _executeSQL(
            copy_sql, title=f"Loading {len(df_full)} rows into {full_table_name}"
        )

        # Cleanup
        cursor.execute(f"DROP TABLE IF EXISTS memory.default.{memory_table}")

        return VastFrame(table_name, schema=schema)

    except Exception as e:
        # Cleanup on error
        try:
            cursor.execute(f"DROP TABLE IF EXISTS memory.default.{memory_table}")
        except:
            pass

        if not insert:
            try:
                drop(full_table_name, method="table")
            except:
                pass

        raise e


@save_vastorbit_logs
def pcsv(
    path: str,
    sep: str = ",",
    header: bool = True,
    header_names: Optional[list] = None,
    na_rep: Optional[str] = None,
    parse_nrows: int = 1000,
) -> dict[str, str]:
    """
    Parse a CSV file and return inferred column types.

    Supports wildcard patterns - will analyze first matching file.

    Parameters
    ----------
    path : str
        Path to the CSV file(s). Supports wildcards (e.g., '*.csv')
    sep : str, optional
        Column separator (default: ',')
    header : bool, optional
        Whether CSV has header row (default: True)
    header_names : list, optional
        Custom column names
    na_rep : str, optional
        String representing missing values
    parse_nrows : int, optional
        Number of rows to use for type inference (default: 1000)

    Returns
    -------
    dict
        Dictionary mapping column names to Trino types

    Examples
    --------
    .. code-block:: python

        from vastorbit.core.parsers.csv import pcsv

        # Inspect single CSV
        types = pcsv('data.csv')

        # Inspect first matching CSV
        types = pcsv('sales_*.csv')
    """
    # Expand wildcards
    if "*" in path or "?" in path:
        files = sorted(glob.glob(path))
        if not files:
            raise FileNotFoundError(f"No files found matching pattern: {path}")
        path = files[0]
        print(f"Analyzing first file: {path}")

    # Read sample
    read_kwargs = {"sep": sep, "nrows": parse_nrows}
    if not header:
        read_kwargs["header"] = None
    if na_rep:
        read_kwargs["na_values"] = [na_rep]

    df = pd.read_csv(path, **read_kwargs)

    # Clean column names
    if header:
        df.columns = [clean_column_name(col) for col in df.columns]

    if header_names:
        header_names_clean = [clean_column_name(col) for col in header_names]
        if len(header_names_clean) == len(df.columns):
            df.columns = header_names_clean

    # Infer types
    dtype = {}
    for col in df.columns:
        dtype[col] = infer_trino_type(df[col], col)

    return dtype
