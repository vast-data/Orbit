"""
SPDX-License-Identifier: Apache-2.0
"""

import os
import json
import glob
from typing import Optional

import pandas as pd

import vastorbit._config.config as conf
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit.connection import current_cursor

from vastorbit.core.vastframe.base import VastFrame

from vastorbit.sql.create import create_table
from vastorbit.sql.drop import drop

"""
General Functions.
"""


def _load_csv_via_memory(
    csv_path: str, memory_table: str, dtype: dict, skip_columns: Optional[list] = None
) -> int:
    """
    Load CSV file into Trino memory catalog.

    This is equivalent to the COPY command for CSV files.
    Data is loaded to memory catalog first, then can be copied to VAST.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file
    memory_table : str
        Name of the temporary memory table
    dtype : dict
        Column definitions {column_name: trino_type}
    skip_columns : list, optional
        Columns to skip

    Returns
    -------
    int
        Number of rows loaded
    """
    cursor = current_cursor()

    # Read CSV
    df = pd.read_csv(csv_path)

    # Clean column names - handle both regular quotes and Unicode smart quotes
    # Unicode: " (U+201C), " (U+201D), ' (U+2018), ' (U+2019)
    # Regular: " (U+0022), ' (U+0027)
    def clean_column_name(col):
        col = col.strip()
        # Remove Unicode smart quotes
        col = col.replace("\u201c", "").replace("\u201d", "")  # " "
        col = col.replace("\u2018", "").replace("\u2019", "")  # ' '
        # Remove regular quotes
        col = col.replace('"', "").replace("'", "")
        return col.strip()

    df.columns = [clean_column_name(col) for col in df.columns]

    # Create case-insensitive column mapping
    # Map lowercase column names to actual column names in dataframe
    df_cols_lower = {col.lower(): col for col in df.columns}

    # Filter columns based on dtype and skip_columns
    skip_columns = skip_columns or []
    skip_columns_lower = [col.lower() for col in skip_columns]

    # Match dtype keys with actual dataframe columns (case-insensitive)
    column_mapping = {}
    for dtype_col in dtype.keys():
        dtype_col_lower = dtype_col.lower()
        if (
            dtype_col_lower in df_cols_lower
            and dtype_col_lower not in skip_columns_lower
        ):
            # Map the dtype column name to the actual dataframe column name
            column_mapping[dtype_col] = df_cols_lower[dtype_col_lower]

    if not column_mapping:
        # Print debug info
        print(f"DEBUG: dtype keys: {list(dtype.keys())}")
        print(f"DEBUG: CSV columns (after cleaning): {list(df.columns)}")
        print(f"DEBUG: CSV columns (lowercase): {list(df_cols_lower.keys())}")
        raise ValueError(
            f"No matching columns found between dtype {list(dtype.keys())} and CSV columns {list(df.columns)}"
        )

    available_cols = list(column_mapping.keys())

    # Convert date/timestamp columns
    for dtype_col, df_col in column_mapping.items():
        col_type = dtype[dtype_col].upper()
        if "DATE" in col_type and df_col in df.columns:
            # Convert to datetime, then format as DATE
            df[df_col] = pd.to_datetime(df[df_col], errors="coerce")
        elif "TIMESTAMP" in col_type and df_col in df.columns:
            # Convert to datetime for timestamp columns
            df[df_col] = pd.to_datetime(df[df_col], errors="coerce")

    # Create table in memory catalog
    columns_def = ", ".join([f'"{col}" {dtype[col]}' for col in available_cols])
    create_sql = f"CREATE TABLE memory.default.{memory_table} ({columns_def})"
    cursor.execute(create_sql)

    # Insert data in batches
    batch_size = 1000
    total_rows = len(df)

    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i : i + batch_size]

        values_list = []
        for _, row in batch.iterrows():
            values = []
            for dtype_col in available_cols:
                df_col = column_mapping[dtype_col]
                val = row[df_col]
                col_type = dtype[dtype_col].upper()

                if pd.isna(val):
                    values.append("NULL")
                elif "DATE" in col_type and "TIME" not in col_type:
                    # Format as DATE: DATE '2024-01-15'
                    if pd.notna(val):
                        date_str = pd.Timestamp(val).strftime("%Y-%m-%d")
                        values.append(f"DATE '{date_str}'")
                    else:
                        values.append("NULL")
                elif "TIMESTAMP" in col_type:
                    # Format as TIMESTAMP: TIMESTAMP '2024-01-15 12:30:45'
                    if pd.notna(val):
                        ts_str = pd.Timestamp(val).strftime("%Y-%m-%d %H:%M:%S")
                        values.append(f"TIMESTAMP '{ts_str}'")
                    else:
                        values.append("NULL")
                elif "TIME" in col_type and "TIMESTAMP" not in col_type:
                    # Format as TIME: TIME '12:30:45'
                    if pd.notna(val):
                        time_str = str(val)
                        values.append(f"TIME '{time_str}'")
                    else:
                        values.append("NULL")
                elif "INT" in col_type:
                    # Integer columns are often loaded as float64 by pandas
                    # (so NaN can be represented); emit a clean integer literal
                    # rather than e.g. "5.0", which Trino parses as a decimal.
                    if pd.notna(val):
                        values.append(str(int(float(val))))
                    else:
                        values.append("NULL")
                elif isinstance(val, str):
                    # Escape single quotes for VARCHAR
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                else:
                    values.append(str(val))

            values_list.append(f"({', '.join(values)})")

        if values_list:
            insert_sql = f"INSERT INTO memory.default.{memory_table} VALUES {', '.join(values_list)}"
            cursor.execute(insert_sql)

    return total_rows


def _load_json_via_memory(json_pattern: str, memory_table: str, dtype: dict) -> int:
    """
    Load JSON file(s) into Trino memory catalog.

    This is equivalent to the COPY command for JSON files.

    Parameters
    ----------
    json_pattern : str
        Path to JSON file or pattern with wildcards
    memory_table : str
        Name of the temporary memory table
    dtype : dict
        Column definitions (complex types stored as VARCHAR/JSON strings)

    Returns
    -------
    int
        Number of rows loaded
    """
    cursor = current_cursor()

    # Find all matching JSON files
    json_files = glob.glob(json_pattern) if "*" in json_pattern else [json_pattern]

    if not json_files:
        raise FileNotFoundError(f"No JSON files found matching: {json_pattern}")

    # Read and combine all JSON files
    all_data = []
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data.append(data)

    if not all_data:
        return 0

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Create table in memory catalog
    # For complex types, store as VARCHAR and preserve JSON structure
    columns_def = ", ".join(
        [f'"{col}" {dtype.get(col, "VARCHAR")}' for col in df.columns]
    )
    create_sql = f"CREATE TABLE memory.default.{memory_table} ({columns_def})"
    cursor.execute(create_sql)

    # Insert data
    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            val = row[col]
            col_type = dtype.get(col, "VARCHAR").upper()

            # Complex types (dict, list) → JSON string (checked first because
            # pd.isna on a list returns an element-wise array, not a scalar).
            if isinstance(val, (dict, list)):
                escaped = json.dumps(val).replace("'", "''")
                values.append(f"'{escaped}'")
            elif pd.isna(val):
                values.append("NULL")
            elif "INT" in col_type:
                try:
                    values.append(str(int(float(val))))
                except (TypeError, ValueError):
                    values.append("NULL")
            elif "DATE" in col_type and "TIME" not in col_type:
                try:
                    values.append(f"DATE '{pd.Timestamp(val).strftime('%Y-%m-%d')}'")
                except (TypeError, ValueError):
                    values.append("NULL")
            elif "TIMESTAMP" in col_type:
                try:
                    values.append(
                        f"TIMESTAMP '{pd.Timestamp(val).strftime('%Y-%m-%d %H:%M:%S')}'"
                    )
                except (TypeError, ValueError):
                    values.append("NULL")
            elif "TIME" in col_type:
                time_str = str(val).replace("'", "''")
                values.append(f"TIME '{time_str}'")
            elif any(t in col_type for t in ("DOUBLE", "REAL", "DECIMAL", "FLOAT")):
                try:
                    values.append(str(float(val)))
                except (TypeError, ValueError):
                    values.append("NULL")
            else:
                escaped = str(val).replace("'", "''")
                values.append(f"'{escaped}'")

        insert_sql = (
            f"INSERT INTO memory.default.{memory_table} VALUES ({', '.join(values)})"
        )
        cursor.execute(insert_sql)

    return len(df)


def load_dataset(
    schema: Optional[str],
    name: str,
    dtype: dict,
    copy_cols: Optional[list] = None,
    dataset_name: Optional[str] = None,
    catalog: Optional[str] = None,
) -> VastFrame:
    """
    Ingest a dataset into VASTDB via Trino.

    Trino Implementation Strategy:
    1. Check if table already exists → return VastFrame
    2. If not exists:
       a. Load CSV/JSON to memory catalog (temporary staging)
       b. Create target table in specified catalog.schema
       c. Copy data from memory to target
       d. Cleanup memory table

    Parameters
    ----------
    schema : str, optional
        Target schema. Supports formats:
        - 'schema_name' (uses default catalog)
        - 'catalog.schema_name' (catalog and schema)
        If None, uses 'memory.default'
    name : str
        Table name for the dataset
    dtype : dict
        Column definitions {column_name: trino_type}
    copy_cols : list, optional
        Columns to copy
    dataset_name : str, optional
        Dataset filename (without extension)
    catalog : str, optional
        Target catalog (overrides catalog from schema parameter)
        Examples: 'hive', 'postgresql', 'vast', 'memory'

    Returns
    -------
    VastFrame
        VastFrame object pointing to the loaded table

    Notes
    -----
    - CSV files are loaded from: <module_dir>/data/<dataset_name>.csv
    - JSON files are loaded from: <module_dir>/data/<dataset_name>/*.json
    - Memory catalog is used as temporary staging area
    - All operations are transactional (cleanup on failure)
    - Default destination is memory.default if no schema specified
    """
    copy_cols = format_type(copy_cols, dtype=list)

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
        # Default to memory catalog (temporary)
        catalog = "memory"
        schema = "default"
    elif not catalog:
        # No catalog specified, use temp_schema config
        schema = schema or conf.get_option("temp_schema")
        # Catalog will be inferred from connection
        catalog = None

    # Try to return existing table
    try:
        return VastFrame(name, schema=schema)
    except Exception:
        pass

    # Table doesn't exist - create and load it
    name_quoted = quote_ident(name)
    cursor = current_cursor()

    # Generate unique memory table name
    memory_table = f"temp_{dataset_name}_{os.getpid()}"

    try:
        # Determine file path and type
        base_path = os.path.dirname(__file__)
        is_json = dataset_name in ("laliga",)

        if is_json:
            file_path = os.path.join(base_path, "data", dataset_name, "*.json")
        else:
            file_path = os.path.join(base_path, "data", f"{dataset_name}.csv")

        # Extract skip columns
        skip_columns = []
        if copy_cols:
            for col in copy_cols:
                if isinstance(col, str) and "FILLER" in col.upper():
                    # Extract column name before FILLER
                    skip_columns.append(col.split()[0])

        # Load data to memory catalog
        if is_json:
            row_count = _load_json_via_memory(file_path, memory_table, dtype)
        else:
            row_count = _load_csv_via_memory(
                file_path, memory_table, dtype, skip_columns
            )

        # Build full table name
        if catalog:
            full_table_name = f"{catalog}.{schema}.{name_quoted}"
        else:
            full_table_name = f"{schema}.{name_quoted}"

        # Create target table
        create_table(table_name=name_quoted, dtype=dtype, schema=schema)

        # Copy from memory to target. Select the declared columns explicitly
        # (in dtype order) rather than SELECT *, because the memory table may
        # contain extra columns or a different ordering than the target table
        # (e.g. JSON sources expose every key, not just the typed ones).
        select_cols = ", ".join(quote_ident(col) for col in dtype)
        insert_sql = f"""
            INSERT INTO {full_table_name}
            SELECT {select_cols} FROM memory.default.{memory_table}
        """
        _executeSQL(
            insert_sql, title=f"Loading {row_count} rows into {full_table_name}"
        )

        # Cleanup memory table
        try:
            cursor.execute(f"DROP TABLE IF EXISTS memory.default.{memory_table}")
        except Exception:
            pass  # Ignore cleanup errors

        # Return VastFrame
        return VastFrame(name, schema=schema)

    except Exception as e:
        # Cleanup on error
        try:
            cursor.execute(f"DROP TABLE IF EXISTS memory.default.{memory_table}")
        except Exception:
            pass

        # Build full table name for cleanup
        if catalog:
            full_table_name = f"{catalog}.{schema}.{name_quoted}"
        else:
            full_table_name = f"{schema}.{name_quoted}"

        try:
            drop(full_table_name, method="table")
        except Exception:
            pass

        raise e


"""
Datasets for basic Data Exploration.
"""


@save_vastorbit_logs
def load_market(schema: Optional[str] = None, name: str = "market") -> VastFrame:
    """
    Ingests the market dataset into the database.

    This dataset is ideal for data exploration.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. Supports formats:
        - 'schema_name' (uses default catalog)
        - 'catalog.schema_name' (e.g., 'vast.public', 'hive.default')
        If None, uses 'memory.default' (temporary)
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The market VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_market

        vdf = load_market()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_market

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_market.html", "w")
        html_file.write(
            load_market()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_market.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={"Form": "VARCHAR(32)", "Name": "VARCHAR(32)", "Price": "DOUBLE"},
        dataset_name="market",
    )


"""
Datasets for Classification.
"""


@save_vastorbit_logs
def load_iris(schema: Optional[str] = None, name: str = "iris") -> VastFrame:
    """
    Ingests the iris dataset into the VAST database.

    This dataset is ideal for classification and clustering models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The iris VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_iris

        vdf = load_iris()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_iris

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_iris.html", "w")
        html_file.write(
            load_iris()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_iris.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "SepalLengthCm": "DECIMAL(5,2)",
            "SepalWidthCm": "DECIMAL(5,2)",
            "PetalLengthCm": "DECIMAL(5,2)",
            "PetalWidthCm": "DECIMAL(5,2)",
            "Species": "VARCHAR(30)",
        },
        copy_cols=[
            "Id FILLER Integer",
            "SepalLengthCm",
            "SepalWidthCm",
            "PetalLengthCm",
            "PetalWidthCm",
            "Species",
        ],
        dataset_name="iris",
    )


@save_vastorbit_logs
def load_titanic(schema: Optional[str] = None, name: str = "titanic") -> VastFrame:
    """
    Ingests the titanic dataset into the VAST database.

    This dataset is ideal for classification models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The titanic VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_titanic

        vdf = load_titanic()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_titanic

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html", "w")
        html_file.write(
            load_titanic()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "pclass": "INTEGER",
            "survived": "INTEGER",
            "name": "VARCHAR(164)",
            "sex": "VARCHAR(20)",
            "age": "DOUBLE",
            "sibsp": "INTEGER",
            "parch": "INTEGER",
            "ticket": "VARCHAR(36)",
            "fare": "DOUBLE",
            "cabin": "VARCHAR(30)",
            "embarked": "VARCHAR(20)",
            "boat": "VARCHAR(100)",
            "body": "INTEGER",
            "home.dest": "VARCHAR(100)",
        },
        dataset_name="titanic",
    )


@save_vastorbit_logs
def load_africa_education(
    schema: Optional[str] = None, name: str = "africa_education"
) -> VastFrame:
    """
    Ingests the Africa Education dataset into the VAST database.
    This dataset is ideal for testing geospatial functions.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The Africa Education VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_africa_education

        vdf = load_africa_education()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_africa_education

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_africa_education.html", "w")
        html_file.write(
            load_winequality()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_africa_education.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        # Match Query types exactly from error message
        dtype={
            "PABSENT": "INTEGER",
            "SPUPPR16": "VARCHAR(9)",
            "zpmealsc": "VARCHAR(19)",
            "PREPEAT": "VARCHAR(10)",
            "zpses": "DECIMAL(3,1)",
            "SPUPPR06": "VARCHAR(9)",
            "zraloct": "DECIMAL(11,7)",
            "COUNTRY": "VARCHAR(3)",
            "XSEX": "VARCHAR(6)",
            "lon": "DECIMAL(8,6)",
            "zralocp": "DECIMAL(11,7)",
            "district": "VARCHAR(23)",
            "SCHOOL": "INTEGER",
            "ZRALEVP": "INTEGER",
            "SPUPPR13": "VARCHAR(9)",
            "ZRALEVT": "DECIMAL(2,1)",
            "SPUPPR09": "VARCHAR(9)",
            "SPUPPR10": "VARCHAR(9)",
            "zpsit": "VARCHAR(27)",
            "PNURSERY": "VARCHAR(19)",
            "STCHPR08": "VARCHAR(9)",
            "country_long": "VARCHAR(12)",
            "XQPROFES": "VARCHAR(9)",
            "PTRAVEL2": "VARCHAR(13)",
            "PTRAVEL": "VARCHAR(11)",
            "lat": "DECIMAL(11,9)",
            "PLIGHT": "VARCHAR(12)",
            "REGION": "VARCHAR(3)",
            "PUPIL": "INTEGER",
            "PMOTHER": "VARCHAR(34)",
            "STYPE": "VARCHAR(10)",
            "SPUPPR07": "VARCHAR(9)",
            "SPUPPR14": "VARCHAR(9)",
            "PMALIVE": "BOOLEAN",
            "zmalocp": "DECIMAL(11,7)",
            "STCHPR06": "VARCHAR(9)",
            "XNUMYRS": "DECIMAL(3,1)",
            "PFATHER": "VARCHAR(34)",
            "zsdist": "DECIMAL(4,1)",
            "PSEX": "VARCHAR(4)",
            "SLOCAT": "VARCHAR(10)",
            "ZMALEVP": "DECIMAL(2,1)",
            "province": "VARCHAR(22)",
            "zphmwkhl": "VARCHAR(28)",
            "SPUPPR04": "VARCHAR(9)",
            "SPUPPR11": "VARCHAR(9)",
            "STCHPR07": "VARCHAR(9)",
            "SQACADEM": "VARCHAR(11)",
            "STCHPR04": "VARCHAR(9)",
            "SINS2006": "DECIMAL(3,1)",
            "numstu": "INTEGER",
            "ZMALEVT": "DECIMAL(2,1)",
            "PFALIVE": "VARCHAR(10)",
            "STCHPR09": "VARCHAR(9)",
            "SPUPPR15": "VARCHAR(9)",
            "PENGLISH": "VARCHAR(16)",
            "SPUPPR12": "VARCHAR(9)",
            "zpsibs": "INTEGER",
            "XAGE": "DECIMAL(3,1)",
            "SPUPPR08": "VARCHAR(9)",
            "PAGE": "INTEGER",
            "schoolname": "VARCHAR(52)",
        },
        dataset_name="africa_education",
    )


@save_vastorbit_logs
def load_winequality(
    schema: Optional[str] = None, name: str = "winequality"
) -> VastFrame:
    """
    Ingests the winequality dataset into the VAST database.

    This dataset is ideal for regression and classification models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The winequality VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_winequality

        vdf = load_winequality()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_winequality

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html", "w")
        html_file.write(
            load_winequality()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "fixed_acidity": "DECIMAL(6,3)",
            "volatile_acidity": "DECIMAL(7,4)",
            "citric_acid": "DECIMAL(6,3)",
            "residual_sugar": "DECIMAL(7,3)",
            "chlorides": "DOUBLE",
            "free_sulfur_dioxide": "DECIMAL(7,2)",
            "total_sulfur_dioxide": "DECIMAL(7,2)",
            "density": "DOUBLE",
            "pH": "DECIMAL(6,3)",
            "sulphates": "DECIMAL(6,3)",
            "alcohol": "DOUBLE",
            "quality": "INTEGER",
            "good": "INTEGER",
            "color": "VARCHAR(20)",
        },
        dataset_name="winequality",
    )


"""
Datasets for Time Series.
"""


@save_vastorbit_logs
def load_airline_passengers(
    schema: Optional[str] = None, name: str = "airline_passengers"
) -> VastFrame:
    """
    Ingests the airline passengers dataset into the VAST database.

    This dataset is ideal for time series and regression models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The airline passengers VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_airline_passengers

        vdf = load_airline_passengers()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_airline_passengers

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html", "w")
        html_file.write(
            load_airline_passengers()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={"date": "DATE", "passengers": "INTEGER"},
        dataset_name="airline_passengers",
    )


@save_vastorbit_logs
def load_amazon(schema: Optional[str] = None, name: str = "amazon") -> VastFrame:
    """
    Ingests the amazon dataset into the VAST database.

    This dataset is ideal for time series and regression models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The amazon VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_amazon

        vdf = load_amazon()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_amazon

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_amazon.html", "w")
        html_file.write(
            load_amazon()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_amazon.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={"date": "DATE", "state": "VARCHAR(32)", "number": "INTEGER"},
        dataset_name="amazon",
    )


@save_vastorbit_logs
def load_commodities(
    schema: Optional[str] = None, name: str = "commodities"
) -> VastFrame:
    """
    Ingests the commodities dataset into the VAST database.

    This dataset is ideal for time series and regression models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The commodities VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_commodities

        vdf = load_commodities()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_commodities

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_commodities.html", "w")
        html_file.write(
            load_commodities()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_commodities.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "date": "DATE",
            "Gold": "DOUBLE",
            "Oil": "DOUBLE",
            "Spread": "DOUBLE",
            "Vix": "DOUBLE",
            "Dol_Eur": "DOUBLE",
            "SP500": "DOUBLE",
        },
        dataset_name="commodities",
    )


@save_vastorbit_logs
def load_gapminder(schema: Optional[str] = None, name: str = "gapminder") -> VastFrame:
    """
    Ingests the gapminder dataset into the VAST database.

    This dataset is ideal for time series and regression models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The gapminder VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_gapminder

        vdf = load_gapminder()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_gapminder

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_gapminder.html", "w")
        html_file.write(
            load_gapminder()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_gapminder.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "country": "VARCHAR(96)",
            "year": "INTEGER",
            "pop": "INTEGER",
            "continent": "VARCHAR(52)",
            "lifeExp": "DOUBLE",
            "gdpPercap": "DOUBLE",
        },
        dataset_name="gapminder",
    )


@save_vastorbit_logs
def load_pop_growth(
    schema: Optional[str] = None, name: str = "pop_growth"
) -> VastFrame:
    """
    Ingests the population growth dataset into the VAST database.

    This dataset is ideal for time series and geospatial models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The pop growth VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_pop_growth

        vdf = load_pop_growth()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_pop_growth

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_pop_growth.html", "w")
        html_file.write(
            load_pop_growth()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_pop_growth.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "year": "INTEGER",
            "continent": "VARCHAR(100)",
            "country": "VARCHAR(100)",
            "city": "VARCHAR(100)",
            "population": "DOUBLE",
            "lat": "DOUBLE",
            "lon": "DOUBLE",
        },
        dataset_name="pop_growth",
    )


@save_vastorbit_logs
def load_smart_meters(
    schema: Optional[str] = None, name: str = "smart_meters"
) -> VastFrame:
    """
    Ingests the smart meters dataset into the VAST database.

    This dataset is ideal for time series and regression models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The smart meters VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_smart_meters

        vdf = load_smart_meters()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_smart_meters

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_smart_meters.html", "w")
        html_file.write(
            load_smart_meters()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_smart_meters.html
    """
    return load_dataset(
        schema=schema,
        name=name,
        dtype={"time": "TIMESTAMP", "val": "DECIMAL(11,7)", "id": "INTEGER"},
        dataset_name="smart_meters",
    )


"""
Datasets for Geospatial.
"""


@save_vastorbit_logs
def load_cities(schema: Optional[str] = None, name: str = "cities") -> VastFrame:
    """
    Ingests the Cities dataset into the VAST database.

    This dataset is ideal for geospatial models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Note: Geometry column contains WKT (Well-Known Text) strings.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The Cities VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_cities

        vdf = load_cities()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_cities

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_cities.html", "w")
        html_file.write(
            load_cities()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_cities.html
    """
    vdf = load_dataset(
        schema=schema,
        name=name,
        dtype={"name": "VARCHAR(82)", "geometry": "VARCHAR"},
        dataset_name="cities",
    )
    vdf["geometry"] = "ST_GeometryFromText(geometry)"
    return vdf


@save_vastorbit_logs
def load_world(schema: Optional[str] = None, name: str = "world") -> VastFrame:
    """
    Ingests the World dataset into the VAST database.

    This dataset is ideal for geospatial models.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Note: Geometry column contains WKT (Well-Known Text) strings.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The World VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_world

        vdf = load_world()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_world

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_world.html", "w")
        html_file.write(
            load_world()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_world.html
    """
    vdf = load_dataset(
        schema=schema,
        name=name,
        dtype={
            "pop_est": "INTEGER",
            "continent": "VARCHAR(32)",
            "name": "VARCHAR(82)",
            "geometry": "VARCHAR",
        },
        dataset_name="world",
    )
    vdf["geometry"] = "ST_GeometryFromText(geometry)"
    return vdf


"""
Datasets for Complex Data Analysis.
"""


@save_vastorbit_logs
def load_laliga(schema: Optional[str] = None, name: str = "laliga") -> VastFrame:
    """
    Ingests the LaLiga dataset into the VAST database.

    This dataset is ideal for testing complex data types.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Note: Complex nested types (ROW, ARRAY) are stored as JSON strings
    for compatibility with Trino's type system.

    Parameters
    ----------
    schema : str, optional
        Schema of the new relation. If empty, the temporary schema is used.
    name : str, optional
        Name of the new relation.

    Returns
    -------
    VastFrame
        The LaLiga VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_laliga

        vdf = load_laliga()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_laliga

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_laliga.html", "w")
        html_file.write(
            load_laliga()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_laliga.html
    """
    # Complex types simplified to VARCHAR for JSON storage
    # In production, you may want to use Trino's ROW/ARRAY types
    return load_dataset(
        schema=schema,
        name=name,
        dtype={
            "away_score": "INTEGER",
            "away_team": "VARCHAR",  # Stores JSON string
            "competition": "VARCHAR",  # Stores JSON string
            "competition_stage": "VARCHAR",  # Stores JSON string
            "home_score": "INTEGER",
            "home_team": "VARCHAR",  # Stores JSON string
            "kick_off": "TIME",
            "last_updated": "DATE",
            "match_date": "DATE",
            "match_id": "INTEGER",
            "match_status": "VARCHAR",
            "match_week": "INTEGER",
            "metadata": "VARCHAR",  # Stores JSON string
            "season": "VARCHAR",  # Stores JSON string
        },
        dataset_name="laliga",
    )
