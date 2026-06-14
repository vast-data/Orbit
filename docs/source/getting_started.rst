.. _getting_started:

=================
Getting Started
=================

.. include:: logo_include.rst

Welcome to VAST Orbit, the Python library for in-database data science on VAST Database. Prepare data, explore interactively, and build ML models - all with zero data movement.

Overview
--------

VAST Orbit brings complete data science workflows to VAST Database with in-database execution at any scale.

**In-Database Data Science:**

- **Data Preparation**: Clean, transform, engineer features directly in VAST
- **Interactive Exploration**: Generate charts and visualize billions of rows
- **Advanced Analytics**: 400+ functions executing in VAST
- **Machine Learning**: Train and deploy models for in-database inference
- **Multi-Source Access**: Query VAST tables, files, and external databases
- **Zero Data Movement**: All processing where data lives

What is VAST Database?
^^^^^^^^^^^^^^^^^^^^^^^

VAST Database is a unified transactional and analytical database designed for AI:

- **Unified Architecture**: ACID transactions + analytics in one system
- **Columnar Storage**: Optimized for data science workloads
- **Sub-ms Latency**: Flash-native performance at exabyte scale
- **Linear Scaling**: From gigabytes to exabytes seamlessly
- **File & Table Access**: Query tables and files with same API

Learn more at the `VAST Database documentation <https://www.vastdata.com/platform/database>`_.

Installation
------------

Prerequisites
^^^^^^^^^^^^^

**System Requirements:**

- Python 3.12 or higher
- Linux or macOS
- Network access to VAST cluster

**VAST Infrastructure:**

- VAST Database 5.0.0-sp10 or later
- Access credentials
- Virtual IP pool configured

Installing VAST Orbit
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install vastorbit

For development:

.. code-block:: bash

   pip install vastorbit[dev]

Installing Jupyter Lab (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For interactive workflows:

.. code-block:: bash

   pip install jupyterlab
   jupyter lab

Verify Installation
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import vastorbit as vo
   print(vo.__version__)

.. note::
   
   Version 0.1.0 is in beta. Production-ready 1.0.0 coming soon.

Quick Start
-----------

5-Minute Tutorial
^^^^^^^^^^^^^^^^^

**1. Connect to VAST Database**

.. code-block:: python

   import vastorbit as vo

   vo.new_connection({
       'host': 'your-vast-cluster.com',
       'port': 8080,
       'catalog': 'your_catalog',
       'schema': 'your_schema',
       'user': 'your_username',
       'http_scheme': 'https'
   })

**2. Load Data**

.. code-block:: python

   # From VAST table
   vdf = vo.VastFrame('customer_data')

   # From Parquet files
   vdf = vo.VastFrame.from_parquet('s3://bucket/path/')

   # From CSV files
   vdf = vo.VastFrame.from_csv('s3://bucket/data.csv')

   # Preview
   vdf.head(10)

**3. Data Preparation - In VAST**

.. code-block:: python

   # Clean data - all executes in VAST
   vdf = vdf.fillna({'income': 0, 'age': vdf['age'].avg()})
   vdf = vdf.drop_duplicates()
   
   # Transform
   vdf['income_normalized'] = vdf.normalize('income')
   
   # Profile
   vdf.describe()

**4. Explore with Charts**

.. code-block:: python

   # Histogram with intelligent sampling
   vdf['age'].hist(nbins=20)
   
   # Scatter plot
   vdf.scatter(['income', 'spending'])
   
   # Correlation matrix
   vdf.corr()

**5. Analytics - In VAST**

.. code-block:: python

   # Filter (executes in VAST)
   filtered = vdf[vdf['amount'] > 1000]

   # Aggregate
   result = vdf.groupby(
      ['region'],
      [
         'sum(revenue) AS total_revenue', 
         'count(*) AS num_customers',
         'avg(transaction) AS avg_transaction'
      ]
   )

**6. Join Across Sources**

.. code-block:: python

   # Join VAST table with files
   customers = vo.VastFrame('vast_catalog.customers')
   transactions = vo.VastFrame.from_parquet('s3://lake/transactions/')
   
   result = customers.join(
       transactions, 
       on='customer_id',
       how='inner'
   )

**7. Machine Learning**

.. code-block:: python

   # Train with VAST Orbit's embedded model
   from vastorbit.machine_learning.vast import RandomForestClassifier
   
   model = RandomForestClassifier()
   model.fit(vdf, ['feature1', 'feature2'], 'target')

   # In-database inference - no data movement!
   predictions = model.predict(vdf)

What's Next?
------------

.. grid:: 2

    .. grid-item-card:: |i-guide| User Guide
        :link: user_guide
        :link-type: ref

        Learn data preparation and in-database analytics

    .. grid-item-card:: |i-charts| Chart Gallery
        :link: chart_gallery
        :link-type: ref

        Create interactive visualizations

    .. grid-item-card:: |i-ml| Machine Learning
        :link: api.machine_learning
        :link-type: ref

        Train and deploy ML models in VAST

    .. grid-item-card:: |i-connect| Connection Guide
        :link: connection
        :link-type: ref

        Configure connections and access

Architecture
------------

In-Database Execution
^^^^^^^^^^^^^^^^^^^^^

VAST Orbit executes all operations in VAST Database:

.. code-block:: text

   Your Python Code
   (pandas-like syntax)
          ↓
   VAST Orbit API
   (query translation)
          ↓
   ┌────────────────────────────────┐
   │     VAST Database              │
   │  • Data Preparation            │
   │  • Analytics                   │
   │  • ML Inference                │
   │  • Chart Sampling              │
   │                                │
   │  Zero Data Movement            │
   └────────────────────────────────┘

**Key Benefits:**

- All operations execute in VAST
- Data stays in database
- Process petabytes like megabytes
- Production-ready from notebook

Machine Learning Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hybrid workflow for flexibility and scale:

.. code-block:: text

   TRAINING
   ┌─────────────────────────────────┐
   │  VAST Orbit Embedded Models     │
   │    or                           │
   │  Import sklearn models          │
   │         ↓                       │
   │  Automatic sampling for training│
   └─────────────────────────────────┘
   
   INFERENCE (In-Database)
   ┌─────────────────────────────────┐
   │  model.predict(VastFrame)       │
   │         ↓                       │
   │  Executes in VAST Database      │
   │  (Billions of rows, no movement)│
   └─────────────────────────────────┘

Key Concepts
^^^^^^^^^^^^

**VastFrame**: Core data structure representing data in VAST. All operations execute in-database.

**In-Database Processing**: Data preparation, analytics, and ML execute in VAST, not Python.

**Intelligent Sampling**: Charts visualize billions of rows using smart sampling algorithms.

**Multi-Source**: Access VAST tables, files, and external databases with unified API.

System Requirements
-------------------

+------------------+------------------------------------------------------+
| Component        | Requirement                                          |
+==================+======================================================+
| Python           | 3.12 or higher                                       |
+------------------+------------------------------------------------------+
| OS               | Linux, macOS                                         |
+------------------+------------------------------------------------------+
| VAST Database    | 5.0.0-sp10 or later                                  |
+------------------+------------------------------------------------------+
| Network          | Access to VAST cluster                               |
+------------------+------------------------------------------------------+

Getting Help
------------

**Documentation:**

- `VAST Database Docs <https://docs.vastdata.com>`_
- `VAST Orbit GitHub <https://github.com/vastdata-dev/vastorbit>`_

**Support:**

- GitHub Issues: `github.com/vastdata-dev/vastorbit/issues <https://github.com/vastdata-dev/vastorbit/issues>`_
- Slack: `vastsupport.slack.com <https://vastsupport.slack.com>`_

**Learn More:**

- :ref:`examples` - Hands-on tutorials
- :ref:`api` - Complete API reference

Next Steps
----------

Continue your journey:

1. :ref:`user_guide` - Master data preparation and analytics
2. :ref:`chart_gallery` - Create visualizations
3. :ref:`api.machine_learning` - Build ML workflows
4. :ref:`examples` - Step-by-step tutorials
5. :ref:`connection` - Advanced connection options

.. note::

   VAST Orbit brings Python data science to VAST Database. Prepare, explore, analyze, and build AI - all with in-database execution at any scale.