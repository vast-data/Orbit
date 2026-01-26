.. _user_guide.data_ingestion:

===============
Data Ingestion
===============

Load data into VAST database from multiple sources.

____

Supported Formats
-----------------

VastOrbit currently supports ingestion of the following formats:

- **CSV** – Comma-separated values files
- **JSON** – JSON documents and arrays
- **pandas DataFrame** – In-memory pandas DataFrames

.. note::

   Additional formats (Parquet, ORC, Avro) will be supported in future releases.

____

Ingest CSV Files
----------------

Use :py:func:`~vastorbit.read_csv` to load CSV files into VAST:

**Basic ingestion:**

.. code-block:: python

    import vastorbit as vo

    vo.read_csv(
        "data.csv",
        schema="default",
        table_name="my_table",
    )

**Preview CSV structure:**

Before ingesting, check columns and data types with :py:func:`~vastorbit.pcsv`:

.. ipython:: python

    from vastorbit.datasets import load_titanic

    titanic = load_titanic()
    
    # Export subset to CSV
    titanic[0:50].to_csv("titanic_subset.csv")

.. ipython:: python

    vo.pcsv(
        path="titanic_subset.csv",
        sep=",",
        na_rep="",
    )

**Ingest with custom options:**

.. code-block:: python

    vo.read_csv(
        "titanic_subset.csv",
        schema="default",
        table_name="titanic_subset",
        sep=",",
        parse_nrows=1000,  # Sample for type inference
    )

**Insert into existing table:**

.. code-block:: python

    # Export more data
    titanic[50:100].to_csv("titanic_more_data.csv")

    # Insert into existing table
    vo.read_csv(
        "titanic_more_data.csv",
        schema="default",
        table_name="titanic_subset",
        insert=True,
    )

.. tip::

   Use :py:func:`~vastorbit.insert_into` for more control over data insertion.

**Common parameters:**

- ``sep`` – Column separator (default: ``,``)
- ``parse_nrows`` – Number of rows to sample for type inference
- ``insert`` – Insert into existing table (default: ``False``)
- ``table_name`` – Target table name (default: filename)
- ``schema`` – Target schema (default: ``default``)
- ``dtype`` – Dictionary of column types (optional)

____

Ingest JSON Files
-----------------

Use :py:func:`~vastorbit.read_json` to load JSON files:

**Preview JSON structure:**

.. code-block:: python

    # Check JSON structure
    vo.pjson("data.json")

**Basic ingestion:**

.. code-block:: python

    from vastorbit.datasets import load_iris

    iris = load_iris()
    
    # Export to JSON
    iris.to_json("iris.json")
    
    # Ingest JSON
    vo.read_json(
        path="iris.json",
        table_name="iris_ingest",
        schema="default",
    )

**Select specific fields:**

.. code-block:: python

    vo.read_json(
        path="data.json",
        table_name="my_table",
        usecols=["field1", "field2", "field3"],
    )

**Common parameters:**

- ``usecols`` – List of JSON fields to ingest (others ignored)
- ``start_point`` – Key in JSON where parsing begins
- ``flatten_maps`` – Flatten nested JSON objects (default: ``True``)
- ``table_name`` – Target table name
- ``schema`` – Target schema

____

Ingest pandas DataFrames
-------------------------

Load in-memory pandas DataFrames directly into VAST:

.. code-block:: python

    import pandas as pd
    import vastorbit as vo

    # Create pandas DataFrame
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'Chicago']
    })

    # Ingest into VAST
    vo.read_pandas(
        df,
        schema="default",
        table_name="users",
    )

**Insert into existing table:**

.. code-block:: python

    # Create more data
    df_new = pd.DataFrame({
        'name': ['David', 'Eve'],
        'age': [28, 32],
        'city': ['Boston', 'Seattle']
    })

    # Append to existing table
    vo.read_pandas(
        df_new,
        schema="default",
        table_name="users",
        insert=True,
    )

.. warning::

   Ensure pandas DataFrame column types match the target table schema when using ``insert=True``.

____

Automatic Type Inference
-------------------------

When ``dtype`` is not specified, VastOrbit automatically infers column types:

.. code-block:: python

    # Automatic inference
    vo.read_csv("data.csv", table_name="auto_types")

    # Manual specification
    vo.read_csv(
        "data.csv",
        table_name="manual_types",
        dtype={
            "id": "INTEGER",
            "name": "VARCHAR(100)",
            "price": "DECIMAL(10,2)",
            "created_at": "TIMESTAMP",
        }
    )

.. tip::

   Specifying ``dtype`` improves ingestion speed and ensures correct data types.

____

Generate SQL Without Execution
-------------------------------

Preview the CREATE TABLE statement before execution:

.. code-block:: python

    vo.read_csv(
        "data.csv",
        schema="default",
        table_name="preview_table",
        genSQL=True,  # Show SQL without executing
    )

____

Best Practices
--------------

**1. Type specification for large files:**

.. code-block:: python

    # Better performance with explicit types
    vo.read_csv(
        "large_file.csv",
        dtype={"col1": "INTEGER", "col2": "VARCHAR(50)"},
        parse_nrows=10000,  # Sample first 10k rows
    )

**2. Check structure before ingestion:**

.. code-block:: python

    # Preview CSV
    vo.pcsv("data.csv")
    
    # Preview JSON
    vo.pjson("data.json")

**3. Handle errors gracefully:**

.. code-block:: python

    try:
        vo.read_csv("data.csv", table_name="my_table")
    except Exception as e:
        print(f"Ingestion failed: {e}")

**4. Use appropriate schema:**

.. code-block:: python

    # Production data
    vo.read_csv("prod_data.csv", schema="production")
    
    # Development data
    vo.read_csv("test_data.csv", schema="staging")

____

Coming Soon
-----------

The following formats will be supported in upcoming releases:

- Parquet
- ORC  
- Avro
- Shapefile (SHP)

.. seealso::

   - :py:func:`~vastorbit.read_csv` – CSV ingestion reference
   - :py:func:`~vastorbit.read_json` – JSON ingestion reference
   - :py:func:`~vastorbit.read_pandas` – pandas ingestion reference
   - :ref:`user_guide.introduction.vdf` – Working with VastFrames