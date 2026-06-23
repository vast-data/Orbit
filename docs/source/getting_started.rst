.. _getting_started:

===============
Getting Started
===============

.. include:: logo_include.rst

VAST Orbit is the open-source Python library for in-database data science on the
VAST Data Platform. This guide takes you from an empty environment to your first
in-database query: install the library, connect to VAST, and prepare,
explore, and model your data without ever moving it.

Overview
--------

Everything you would normally do in a notebook — clean and shape data, explore it
with charts, run analytics, and train and score models — VAST Orbit does directly
inside VAST, with the pandas- and scikit-learn-style API you already know. Because
the work executes where the data lives, the same code runs unchanged whether you are
holding a few megabytes or many petabytes, and nothing leaves the platform except the
results you ask for.

What is VAST Database?
^^^^^^^^^^^^^^^^^^^^^^^

VAST Database is a unified transactional and analytical database built for AI. It
combines ACID transactions with analytics in a single system, stores data in a
columnar format tuned for data-science workloads, and delivers flash-native,
sub-millisecond latency that scales linearly from gigabytes to exabytes. Crucially,
it lets you query tables and files through the same interface — which is exactly what
lets VAST Orbit treat your whole estate as one surface. Learn more in the
`VAST Database documentation <https://www.vastdata.com/platform/database>`__.

Installation
------------

Prerequisites
^^^^^^^^^^^^^

You will need Python 3.12 or newer on Linux or macOS, network access to your VAST
cluster, and a VAST deployment running **VAST 4.5 or later** with access credentials
and a configured virtual IP pool.

Installing VAST Orbit
^^^^^^^^^^^^^^^^^^^^^^

Install the library with pip:

.. code-block:: bash

   pip install vastorbit

For a development setup that includes the test and docs tooling:

.. code-block:: bash

   pip install vastorbit[dev]

If you work in notebooks, Jupyter Lab pairs well with VAST Orbit's interactive charts:

.. code-block:: bash

   pip install jupyterlab
   jupyter lab

Verify the installation by importing the package and printing its version:

.. code-block:: python

   import vastorbit as vo
   print(vo.__version__)

.. note::

   Version 0.1.x is a beta; a production-ready 1.0.0 is on the way.

Quick start
-----------

The fastest way to understand VAST Orbit is to run a short workflow end to end. Each
step below executes inside VAST.

**1. Connect to VAST Database**

.. code-block:: python

   import vastorbit as vo

   vo.new_connection({
       "host": "your-vast-cluster.com",
       "port": 8080,
       "catalog": "your_catalog",
       "schema": "your_schema",
       "user": "your_username",
       "http_scheme": "https",
   })

.. note::

   Today VAST Orbit connects through Trino; VAST's own query engine is coming and
   will become the default. Because the API is the same, your code won't change when
   it does.

**2. Load data**

A :py:class:`~VastFrame` is a handle to data in VAST — creating one does not pull
anything into Python.

.. code-block:: python

   # A VAST table, addressed as catalog.schema.table
   vdf = vo.VastFrame("vast_catalog.analytics.customer_data")

   # Parquet in the data lake is exposed through the hive catalog, so you just
   # reference it as a table - Trino reads it in place, with no load step
   vdf = vo.VastFrame("hive.default.transactions")

   # CSV or JSON files that need ingesting use the read_* helpers
   vdf = vo.read_csv("s3://bucket/data.csv")
   vdf = vo.read_json("s3://bucket/data.json")

   vdf.head(10)

**3. Prepare the data — in VAST**

.. code-block:: python

   vdf = vdf.fillna({"income": 0, "age": vdf["age"].avg()})
   vdf = vdf.drop_duplicates()
   vdf["income_normalized"] = vdf.normalize("income")
   vdf.describe()

**4. Explore with charts**

Charts are drawn from intelligent samples, so they are instant even on very large
tables.

.. code-block:: python

   vdf["age"].hist(nbins=20)
   vdf.scatter(["income", "spending"])
   vdf.corr()

**5. Run analytics — in VAST**

.. code-block:: python

   filtered = vdf[vdf["amount"] > 1000]

   result = vdf.groupby(
       ["region"],
       [
           "sum(revenue) AS total_revenue",
           "count(*) AS num_customers",
           "avg(transaction) AS avg_transaction",
       ],
   )

**6. Join across sources**

.. code-block:: python

   customers = vo.VastFrame("vast_catalog.analytics.customers")
   transactions = vo.VastFrame("hive.lake.transactions")   # parquet via hive catalog

   result = customers.join(transactions, on="customer_id", how="inner")

**7. Train and deploy a model**

.. code-block:: python

   from vastorbit.machine_learning.vast import RandomForestClassifier

   model = RandomForestClassifier()
   model.fit(vdf, ["feature1", "feature2"], "target")

   predictions = model.predict(vdf)   # in-database inference, no data movement

What's next?
------------

.. grid:: 2
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item-card:: |i-guide| User Guide
        :link: user_guide
        :link-type: ref

        Learn data preparation and in-database analytics in depth.

    .. grid-item-card:: |i-charts| Chart Gallery
        :link: chart_gallery
        :link-type: ref

        See the interactive visualizations you can create.

    .. grid-item-card:: |i-ml| Machine Learning
        :link: api.machine_learning
        :link-type: ref

        Train models and deploy them for inference in VAST.

    .. grid-item-card:: |i-connect| Connection Guide
        :link: connection
        :link-type: ref

        Configure connections, catalogs, and authentication.

Architecture
------------

VAST Orbit sits between your Python and VAST: you write familiar pandas-style code,
the library translates it into queries, and VAST executes them where the data lives.
Nothing is copied into Python — preparation, analytics, chart sampling, and model
inference all happen in the database, and only the results come back.

.. code-block:: text

   Your Python code (pandas-style)
            |
            v
   VAST Orbit  (query translation)
            |
            v
   +--------------------------------+
   |          VAST Database         |
   |  - Data preparation            |
   |  - Analytics                   |
   |  - ML inference                |
   |  - Chart sampling              |
   |        Zero data movement      |
   +--------------------------------+

For machine learning, the workflow is hybrid by design: you train with the embedded
algorithms or import a model you built locally with scikit-learn, and then deploy it
so that scoring runs as SQL inside VAST — across billions of rows, with no export and
no separate serving layer.

Key concepts
------------

A **VastFrame** is the core structure: a handle to data in VAST whose operations all
execute in the database rather than in Python. **In-database processing** means that
preparation, analytics, and ML run where the data sits. **Intelligent sampling** is
how charts stay instant — visualizations are drawn from representative samples rather
than from every row. And **multi-source access** means a single VastFrame API reaches
VAST tables, data-lake files, and external databases alike.

System requirements
-------------------

+------------------+------------------------------------------------------+
| Component        | Requirement                                          |
+==================+======================================================+
| Python           | 3.12 or higher                                       |
+------------------+------------------------------------------------------+
| OS               | Linux, macOS                                         |
+------------------+------------------------------------------------------+
| VAST             | 4.5 or later                                         |
+------------------+------------------------------------------------------+
| Network          | Access to VAST cluster                               |
+------------------+------------------------------------------------------+

Getting help
------------

For questions and discussion, the VAST Slack at
`vastsupport.slack.com <https://vastsupport.slack.com>`__ is the best place to start.
To report a bug or request a feature, open an issue at
`github.com/vastdata-dev/vastorbit/issues <https://github.com/vastdata-dev/vastorbit/issues>`__.
And to go deeper, the :ref:`examples` and the :ref:`api` reference cover the full
library.

.. note::

   VAST Orbit brings Python data science to the VAST Data Platform: prepare, explore,
   analyze, and build AI - all with in-database execution at any scale.