.. _user_guide.introduction.vdf:

==============
The VastFrame
==============

Master the core object for in-database analytics with VAST Orbit.

____

Overview
--------

The :py:mod:`~vastorbit.VastFrame` is the core object of VAST Orbit. It enables Python-based data manipulation without moving data from the VAST database to local memory.

**Key benefits:**

- **In-database processing** – All operations execute in VAST's Trino engine
- **Minimal memory usage** – Only metadata is stored in Python
- **Parallel execution** – Leverage VAST's distributed query engine
- **Lazy evaluation** – Operations are optimized before execution

VastFrames behave like SQL views, formulating operations as queries that execute directly in the database.

____

Creating VastFrames
-------------------

Load the Titanic dataset:

.. code-block:: python

    from vastorbit.datasets import load_titanic

    load_titanic()

.. ipython:: python
    :suppress:

    from vastorbit.datasets import load_titanic
    res = load_titanic()
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_load_titanic.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_load_titanic.html

**From an existing table:**

.. code-block:: python

    import vastorbit as vo

    vo.VastFrame("titanic")

**From a SQL query:**

.. code-block:: python

    vo.VastFrame("SELECT pclass, AVG(survived) AS survived FROM titanic GROUP BY 1")

.. ipython:: python
    :suppress:

    import vastorbit as vo
    res = vo.VastFrame("SELECT pclass, AVG(survived) AS survived FROM titanic GROUP BY 1")
    html_file = open("SPHINX_DIRECTORY/figures/ug_intro_vdf_1.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_intro_vdf_1.html

For more examples, see :py:mod:`~vastorbit.VastFrame`.

____

In-Database vs In-Memory
------------------------

The following examples demonstrate performance advantages of in-database processing.

.. note:: 
    
    These examples show the process without actual computation due to dataset size. When executed, in-database processing is significantly faster.

**Load data into VAST:**

.. code-block:: python

    vo.read_csv(
        "expedia.csv",
        schema="default",
        parse_nrows=20000000,
    )

**Create VastFrame (in-database):**

.. code-block:: python

    import time

    start_time = time.time()
    expedia = vo.VastFrame("expedia")
    print(f"Elapsed time: {time.time() - start_time:.2f}s")

All 4GB of data remains in VAST—no in-memory loading required.

**Compare with pandas (in-memory):**

.. warning::

    Avoid running this on machines with less than 2GB RAM.

.. code-block:: python
    
    import pandas as pd

    start_time = time.time()
    expedia_df = pd.read_csv("expedia.csv")
    print(f"Elapsed time: {time.time() - start_time:.2f}s")

Loading into pandas takes orders of magnitude longer and consumes significant memory.

**Compute correlation matrix (pandas):**

.. code-block:: python

    columns_to_drop = ["date_time", "srch_ci", "srch_co"]
    expedia_df = expedia_df.drop(columns_to_drop, axis=1)
    
    start_time = time.time()
    expedia_df.corr()
    print(f"Elapsed time: {time.time() - start_time:.2f}s")

**Compute correlation matrix (VastFrame):**

.. code-block:: python

    # Remove non-numeric columns
    expedia.drop(columns=["date_time", "srch_ci", "srch_co"])
    
    start_time = time.time()
    expedia.corr(show=False)
    print(f"Elapsed time: {time.time() - start_time:.2f}s")

VAST Orbit caches computed aggregations for instant retrieval:

.. note:: 
    
    Disable caching with: ``vo.set_option("cache", False)``

.. code-block:: python

    start_time = time.time()
    expedia.corr(show=False)
    print(f"Elapsed time: {time.time() - start_time:.2f}s")  # Nearly instant

____

Memory Usage
------------

**pandas DataFrame:**

.. code-block:: python

    expedia_df.info()

Memory usage equals original file size (~4GB).

**VastFrame:**

VastFrame uses only ~37KB! By storing data in VAST and only tracking metadata in Python, memory usage is minimized.

.. tip::

   In-database processing eliminates the need for downsampling, preserving all data insights.

____

VastFrame Structure
-------------------

VastFrames are composed of :py:mod:`VastColumn` objects.

**View all columns:**

.. ipython:: python
    :suppress:

    vo.drop("expedia")
    vo.read_csv(
        "SPHINX_DIRECTORY/source/_static/website/examples/data/booking/expedia.csv",
        schema="default", 
        parse_nrows=20000000,
    )
    expedia = vo.VastFrame("expedia")

.. ipython:: python

    expedia.get_columns()

**Access a column:**

.. note::

    VAST Orbit caches aggregations to avoid recomputation.

.. code-block:: python

    expedia["is_booking"].describe()

.. ipython:: python
    :suppress:

    res = expedia["is_booking"].describe()
    html_file = open("SPHINX_DIRECTORY/figures/ug_intro_vdf_describe.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_intro_vdf_describe.html

**View column catalog:**

Each :py:mod:`~vastorbit.VastColumn` maintains a catalog of user modifications:

.. ipython:: python

    expedia["is_booking"]._catalog

**Enable SQL code generation:**

.. code-block:: python

    vo.set_option("sql_on", True)
    expedia["cnt"].describe()

.. code-block:: sql

    -- Computing aggregations
    SELECT
        APPROX_DISTINCT("cnt")
    FROM (
        SELECT * FROM "expedia"
    ) AS VASTORBIT_SUBTABLE
    LIMIT 1;

.. ipython:: python
    :suppress:

    res = expedia["cnt"].describe()
    html_file = open("SPHINX_DIRECTORY/figures/ug_intro_vdf_describe_cnt.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_intro_vdf_describe_cnt.html

**Enable query timing:**

.. ipython:: python

    vo.set_option("sql_on", False)
    expedia = vo.VastFrame("expedia")
    vo.set_option("time_on", True)
    expedia.corr()

**Cached results are instant:**

.. ipython:: python

    import time
    
    start_time = time.time()
    expedia.corr()
    print(f"Elapsed time: {time.time() - start_time:.2f}s")

**Disable options:**

.. ipython:: python

    vo.set_option("sql_on", False)
    vo.set_option("time_on", False)

____

Query Relations
---------------

**View current relation:**

.. ipython:: python

    print(expedia.current_relation())

**After modifications:**

.. ipython:: python

    expedia["orig_destination_distance"].fillna(method="avg")
    expedia["is_package"].drop()
    print(expedia.current_relation())

Notice the SQL reflects the changes: ``is_package`` removed and ``COALESCE`` added for imputation.

____

VastFrame Attributes
--------------------

VastFrames have two attribute types:

- **Virtual Columns** – :py:mod:`~vastorbit.VastColumn` objects
- **Main attributes** – Stored in ``_vars`` dictionary

.. warning::

   Never modify ``_vars`` manually.

.. ipython:: python

    expedia._vars

____

Data Types
----------

VAST Orbit recognizes four main data types:

- ``int`` – Treated as categorical when low cardinality, otherwise numeric
- ``real`` – Numeric data types
- ``date`` – Date/timestamp types
- ``text`` – Categorical data types

**View data types:**

.. code-block:: python

    expedia.dtypes()

.. ipython:: python
    :suppress:

    res = expedia.dtypes()
    html_file = open("SPHINX_DIRECTORY/figures/ug_intro_vdf_expedia_dtypes.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_intro_vdf_expedia_dtypes.html

**Convert data types:**

.. ipython:: python

    expedia["hotel_market"].astype("varchar")
    expedia["hotel_market"].ctype()

**View column category:**

.. ipython:: python

    expedia["hotel_market"].category()

____

Saving and Loading
------------------

**Save current state:**

.. code-block:: python

    expedia.save()
    expedia.filter("is_booking = 1")

.. ipython:: python
    :suppress:

    expedia.save()
    res = expedia.filter("is_booking = 1")
    html_file = open("SPHINX_DIRECTORY/figures/ug_intro_vdf_expedia_filter.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_intro_vdf_expedia_filter.html

**Restore previous state:**

.. ipython:: python

    expedia = expedia.load()
    print(expedia.shape())

____

Exporting to Database
---------------------

VastFrame modifications don't affect the underlying database. To persist changes, save to a new table.

**Check storage requirements:**

.. code-block:: python

    expedia.expected_store_usage(unit="Gb")

.. ipython:: python
    :suppress:

    res = expedia.expected_store_usage(unit="Gb")
    html_file = open("SPHINX_DIRECTORY/figures/ug_intro_vdf_expedia_storage_gb.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_intro_vdf_expedia_storage_gb.html

**Save to database:**

.. code-block:: python
    
    expedia.to_db(
        "expedia_clean",
        relation_type="table",
    )

.. tip::

   VastFrames behave like views—they're lightweight representations of database queries. Use ``to_db()`` only when you need to materialize results.

.. seealso::

   - :ref:`user_guide.introduction.best_practices` – Performance optimization tips
   - :ref:`api.vastframe` – Complete VastFrame API reference

.. ipython:: python
   :suppress:

   from vastorbit._utils._sql._sys import purge_memory
   purge_memory()