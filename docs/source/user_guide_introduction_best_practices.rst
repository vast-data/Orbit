.. _user_guide.introduction.best_practices:

===============
Best Practices
===============

Optimize your VAST Orbit workflow for maximum performance and efficiency.

____

Restrict to Essential Columns
------------------------------

VAST Orbit executes queries directly in the VAST database. Limiting operations to essential columns significantly improves performance, especially with large datasets.

**Load specific columns:**

.. code-block:: python

    from vastorbit.datasets import load_titanic
    import vastorbit as vo

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

Use the ``usecols`` parameter to load only required columns:

.. code-block:: python
    
    import vastorbit as vo

    titanic = vo.VastFrame(
        "titanic",
        usecols=["survived", "pclass", "age", "parch", "sibsp"],
    )
    titanic.head(100)

.. ipython:: python
    :suppress:

    import vastorbit as vo
    titanic = vo.VastFrame(
        "titanic",
        usecols=["survived", "pclass", "age", "parch", "sibsp"],
    )
    res = titanic.head(100)
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_load_titanic_selective.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_load_titanic_selective.html

**Inspect generated SQL:**

.. note:: 
   
   Enable SQL output with :py:func:`~vastorbit.set_option` to see generated queries.

.. ipython:: python
    
    # Turn on SQL generation
    vo.set_option("sql_on", True)

    titanic.avg()
    
    # Turn off SQL generation
    vo.set_option("sql_on", False)

**Restrict operations to specific columns:**

.. code-block:: python

    titanic.avg(columns=["age", "survived"])

.. ipython:: python
    :suppress:

    res = titanic.avg(columns=["age", "survived"])
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_avg.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_avg.html

**Exclude columns:**

.. ipython:: python

    titanic.numcol(exclude_columns=["parch", "sibsp"])

.. note:: 

    Use :py:func:`~vastorbit.VastFrame.get_columns` to list all columns.

**Combine with other operations:**

.. code-block:: python

    titanic.corr(columns=titanic.numcol(exclude_columns=["parch", "sibsp"]))

.. ipython:: python
    :suppress:

    vo.set_option("plotting_lib", "plotly")
    fig = titanic.corr(columns=titanic.numcol(exclude_columns=["parch", "sibsp"]))
    fig.write_html("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_corr.html")

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_corr.html

.. tip::

   For datasets > 1TB, selecting essential columns can reduce query time by 10-100x.

____

Save Complex Relations
----------------------

VastFrame works like a SQL view. Heavy transformations (joins, window functions, complex operations) can slow down each method call. Save complex relations as tables to improve performance.

**Example transformation chain:**

.. code-block:: python

    titanic = vo.VastFrame("titanic")
    titanic["sex"].label_encode()["boat"].fillna(method="0ifnull")["name"].str_extract(
        ' ([A-Za-z]+)\.').eval("family_size", expr="parch + sibsp + 1").drop(
        columns=["cabin", "body", "ticket", "home.dest"])["fare"].fill_outliers().fillna()

.. ipython:: python
    :suppress:

    titanic = vo.VastFrame("titanic")
    titanic["sex"].label_encode()["boat"].fillna(method="0ifnull")["name"].str_extract(' ([A-Za-z]+)\.').eval("family_size", expr="parch + sibsp + 1").drop(columns=["cabin", "body", "ticket", "home.dest"])["fare"].fill_outliers().fillna()

.. ipython:: python

    print(titanic.current_relation())

**View query plan:**

.. ipython:: python

    print(titanic.explain())

**Save as table:**

.. code-block:: python

    vo.drop("titanic_clean", method="table")
    
    titanic.to_db(
        "titanic_clean",
        relation_type="table",
        inplace=True,
    )

.. ipython:: python
    :suppress:

    vo.drop("titanic_clean", method="table")
    titanic.to_db(
        "titanic_clean",
        relation_type="table",
        inplace=True,
    )

.. ipython:: python
    
    print(titanic.current_relation())

.. warning::

   For very large datasets, save tables only after thorough exploration to avoid unnecessary storage.

____

Use Built-in Help
-----------------

Quick reference for any function:

.. ipython:: python

    help(vo.connect)

____

Close Connections
-----------------

Close connections when finished to reduce database concurrency:

.. code-block:: python

    # Connect
    vo.connect("vast_connection")
    
    # Do work...
    
    # Close when done
    vo.close_connection()

.. important::

   Always close connections in multi-user environments.

____

Consider Time Complexity
------------------------

Some methods are computationally expensive. For example, Kendall correlation uses cross joins (O(n²)) vs Pearson (O(n)).

**Performance comparison:**

.. ipython:: python

    import time

    titanic = vo.VastFrame("titanic")
    
    start_time = time.time()
    x = titanic.corr(method="pearson", show=False)
    print(f"Pearson: {time.time() - start_time:.2f}s")
    
    start_time = time.time()
    x = titanic.corr(method="kendall", show=False)
    print(f"Kendall: {time.time() - start_time:.2f}s")

.. tip::

   Choose methods appropriate for your dataset size. Use Pearson for large datasets unless Kendall is required.

____

Limit Plot Elements
-------------------

Keep visualizations readable by limiting categories:

**Too many categories:**

.. code-block:: python

    titanic.bar(["name", "survived"])  # 1000+ categories - unreadable

.. ipython:: python
    :suppress:

    fig = titanic.bar(["name", "survived"], width=900)
    fig.write_html("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_bar_plot.html")

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_bar_plot.html

**Optimal categories:**

.. code-block:: python

    titanic.hist(["pclass", "survived"])  # 3 categories - clear

.. ipython:: python
    :suppress:

    fig = titanic.hist(["pclass", "survived"])
    fig.write_html("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_hist_plot.html")

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_titanic_hist_plot.html

**Check cardinality:**

.. code-block:: python

    titanic.nunique()

.. ipython:: python
    :suppress:

    res = titanic.nunique()
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_nunique.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_nunique.html

____

Filter Unnecessary Data
-----------------------

Filtering reduces computation and improves performance:

**Filter rows:**

.. code-block:: python

    titanic.filter("boat IS NOT NULL")

.. ipython:: python
    :suppress:

    res = titanic.filter("boat IS NOT NULL")
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_filter.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_filter.html

**Drop columns:**

.. code-block:: python

    titanic.drop(["name", "body"])

.. ipython:: python
    :suppress:

    res = titanic.drop(["name", "body"])
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_drop_name_body.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_drop_name_body.html

**Verify relation:**

.. ipython:: python

    print(titanic.current_relation())

____

Optimize Resource Usage
------------------------

Control query concurrency for large datasets with many columns.

**Generate test dataset:**

.. code-block:: python

    from vastorbit.datasets import gen_dataset

    vo.drop("test_dataset", method="table")
    
    features_ranges = {}
    for i in range(20):
        features_ranges[f"x{i}"] = {"type": float, "range": [0, 1]}
    
    vdf = gen_dataset(
        features_ranges,
        nrows=100000,
    ).to_db(
        "test_dataset", 
        relation_type="table", 
        inplace=True,
    )
    vdf.head(100)

.. ipython:: python
    :suppress:

    from vastorbit.datasets import gen_dataset

    vo.drop("test_dataset", method="table")
    features_ranges = {}
    for i in range(20):
        features_ranges[f"x{i}"] = {"type": float, "range": [0, 1]}
    vo.drop("test_dataset", method="table")
    vdf = gen_dataset(
        features_ranges,
        nrows=100000,
    ).to_db(
        "test_dataset", 
        relation_type="table", 
        inplace=True,
    )
    res = vdf.head(100)
    html_file = open("SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_gen_dataset.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/user_guide_introduction_best_practices_gen_dataset.html

**Enable monitoring:**

.. ipython:: python

    vo.set_option("sql_on", True)
    vo.set_option("cache", False)

**Single query (all columns):**

.. ipython:: python

    display(vdf.avg(ncols_block=20))

**Split into batches:**

.. ipython:: python

    display(vdf.avg(ncols_block=5))  # 4 queries of 5 columns each

**Parallel execution:**

.. code-block:: python

    vdf.avg(ncols_block=5, processes=4)  # 4 concurrent workers

.. tip::

   Use ``ncols_block`` and ``processes`` to balance query load on shared databases.