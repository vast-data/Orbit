.. _getting_started:

=================
Getting Started
=================

.. include:: logo_include.rst

Welcome to VastOrbit, the Python library that unlocks the full potential of the VAST Data Platform. Created by Badr Ouali (creator of VerticaPy), VastOrbit is designed to give VAST DataBase users endless possibilities for data analytics and AI development.

Overview
--------

VastOrbit unlocks the **endless possibilities** of the VAST Data Platform for data science and AI development. Currently leveraging Trino's powerful federated query capabilities, VastOrbit will soon integrate with the **VAST native SQL Query Engine** for even greater performance by directly exploiting VAST's compressed columnar file format.

**The VAST Advantage:**

VastOrbit is designed to maximize VAST's unique capabilities:

- **Compressed Columnar Format**: VAST stores data in an optimized columnar format with aggressive compression
- **Current**: Trino provides federated access across any data source
- **Coming Soon**: VAST SQL Query Engine will directly leverage compressed formats for 10-100x performance gains
- **Zero Data Movement**: All operations execute where data lives - in VAST DataBase or on files

**Endless Possibilities with VastOrbit:**

- **Query Anywhere**: VAST tables, data lakes (S3/DataStore), external databases, Kafka streams - unified Python API
- **Any File Format**: Parquet, CSV, JSON, ORC, Avro - query directly without loading
- **Federated Analytics**: Join VAST tables with S3 files, PostgreSQL, MongoDB in single queries
- **Hybrid ML**: Train with sklearn/Spark, deploy for ultra-fast in-database inference
- **400+ Functions**: Comprehensive analytics toolkit spanning all data science needs
- **Future-Proof**: Seamless migration path to VAST SQL Query Engine for maximum performance

What is VAST DataBase?
^^^^^^^^^^^^^^^^^^^^^^^

The VAST DataBase is a unified transactional and analytical database designed for the AI era. It combines:

- **Transactional Capabilities**: ACID-compliant operations for data integrity
- **Analytical Power**: Columnar storage optimized for analytics and ML workloads  
- **Real-Time Performance**: Single-millisecond latency with linear scaling to exabytes
- **Unified Architecture**: No separate OLTP and OLAP systems - one database for all workloads
- **File & Table Unification**: Query structured tables and unstructured files seamlessly

Learn more at the `VAST Data Platform documentation <https://www.vastdata.com/platform/database>`_.

Installation Guide
------------------

Prerequisites
^^^^^^^^^^^^^

Before installing VastOrbit, ensure you have:

**System Requirements:**

- Python 3.12 or higher
- Linux or macOS operating system
- Network access to your VAST Cluster

**VAST Infrastructure:**

- VAST Cluster running release 5.0.0-sp10 or later
- Virtual IP pool configured with DNS service
- Access credentials (AWS-style access and secret keys)
- Trino query engine configured on your VAST cluster
- Hive metastore for external table access (optional for file queries)

.. note::
   
   If your VAST Cluster is running an older release, contact customer.support@vastdata.com for upgrade assistance.

Installing VastOrbit
^^^^^^^^^^^^^^^^^^^^

Install VastOrbit using pip:

.. code-block:: bash

   pip install vastorbit

For development installations with all dependencies:

.. code-block:: bash

   pip install vastorbit[dev]

Installing Jupyter Lab (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For interactive data science workflows, install Jupyter Lab:

.. code-block:: bash

   pip install jupyterlab

   # Launch Jupyter Lab
   jupyter lab

Verifying Installation
^^^^^^^^^^^^^^^^^^^^^^

Verify your installation by importing VastOrbit:

.. code-block:: python

   import vastorbit as vo
   print(vo.__version__)

Quick Start
-----------

5-Minute Tutorial
^^^^^^^^^^^^^^^^^

Here's a quick example to get you started with VastOrbit:

**1. Connect to VAST DataBase**

.. code-block:: python

   import vastorbit as vo

   # Connect using Trino
   vo.new_connection({
       'host': 'your-vast-cluster.com',
       'port': 8080,  # Trino port
       'catalog': 'your_catalog',
       'schema': 'your_schema',
       'user': 'your_username',
       'http_scheme': 'https'
   })

**2. Load Data - Tables or Files**

.. code-block:: python

   # Option 1: Load from VAST DataBase table
   vdf = vo.VastFrame('customer_data')

   # Option 2: Query Parquet files in S3/DataStore
   vdf = vo.VastFrame.from_parquet('s3://bucket/path/to/data/')

   # Option 3: Query CSV files
   vdf = vo.VastFrame.from_csv('s3://bucket/data.csv')

   # Preview the data
   vdf.head(10)

**3. Perform In-Database Analytics**

.. code-block:: python

   # Get summary statistics (executed in VAST DataBase)
   vdf.describe()

   # Filter data (predicate pushdown to database)
   filtered = vdf[vdf['amount'] > 1000]

   # Aggregate with groupby (executed in-database)
   result = vdf.groupby(
      'region',
      [
         'SUM(revenue) AS sum_revenue', 
         'COUNT(customers) AS count_customers',
         'AVG(transaction) AS mean_transaction'
      ]
   })

**4. Federated Query Across Sources**

.. code-block:: python

   # Join VAST table with S3 parquet files in one query!
   customer_vdf = vo.VastFrame('vast_catalog.customers')
   transactions_vdf = vo.VastFrame.from_parquet('s3://data-lake/transactions/')
   
   # Trino handles the federated join
   result = customer_vdf.join(
       transactions_vdf, 
       on='customer_id',
       how='inner'
   )

**5. Machine Learning Workflow**

.. code-block:: python

   # Train model with sklearn (local or Spark)
   from sklearn.ensemble import RandomForestClassifier
   import pandas as pd

   # Extract training data to pandas
   train_df = vdf.to_pandas()
   
   # Train with sklearn
   model = RandomForestClassifier()
   model.fit(train_df[['feature1', 'feature2']], train_df['target'])

   # Deploy for in-database inference using VastOrbit
   from vastorbit.machine_learning import InMemoryModel
   
   vo_model = InMemoryModel(model)
   # Predictions execute in VAST DataBase - no data movement!
   predictions = vo_model.predict(vdf)

**6. Visualize Results**

.. code-block:: python

   # Create interactive scatter plot
   vdf.scatter(
       columns=['feature1', 'target'],
       max_nb_points=10000
   )

What's Next?
------------

Now that you have VastOrbit installed and running, explore these resources:

.. grid:: 2

    .. grid-item-card:: 📚 User Guide
        :link: user_guide
        :link-type: ref

        Learn VastFrame operations, data manipulation, and federated queries

    .. grid-item-card:: 🔌 Connection Guide
        :link: connection
        :link-type: ref

        Master Trino connections and query multiple data sources

    .. grid-item-card:: 🤖 Machine Learning
        :link: api.machine_learning
        :link-type: ref

        Train with sklearn/Spark, deploy for in-database inference

    .. grid-item-card:: 📊 Visualization
        :link: chart_gallery
        :link-type: ref

        Create interactive charts from any data source

Architecture Overview
---------------------

Understanding VastOrbit's Execution Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

VastOrbit intelligently executes operations where they're most efficient. Today using Trino, tomorrow using VAST's native SQL Query Engine for maximum performance:

.. code-block:: text

   ┌─────────────────────────────────────────┐
   │         Your Python Code                │
   │    (pandas/sklearn-like syntax)         │
   └─────────────────┬───────────────────────┘
                     │
   ┌─────────────────▼───────────────────────┐
   │           VastOrbit API                 │
   │  • Query planning & optimization        │
   │  • Intelligent execution routing        │
   └─────────────────┬───────────────────────┘
                     │
         ┌───────────┴────────────┐
         ▼                        ▼
   ┌──────────────┐     ┌──────────────────┐
   │  **TODAY**   │     │   **FUTURE**     │
   │    Trino     │     │  VAST SQL Query  │
   │ (Federated)  │────▶│     Engine       │
   └──────┬───────┘     └────────┬─────────┘
          │                      │
          ▼                      ▼
   ┌────────────────────────────────────────┐
   │         VAST Data Platform             │
   │  • Compressed columnar storage         │
   │  • VAST DataBase tables                │
   │  • S3/DataStore files                  │
   │  • Real-time ingestion                 │
   └────────────────────────────────────────┘

**Today - Trino Query Engine:**

✓ Federated access to 30+ data sources  
✓ Join VAST tables with external databases  
✓ Query files (Parquet, CSV, JSON) directly  
✓ Production-ready performance  

**Coming Soon - VAST SQL Query Engine:**

🚀 **10-100x Performance Improvement** by directly reading VAST's compressed columnar format  
🚀 **Native Integration** with VAST Catalog and metadata  
🚀 **Optimized Pushdown** for filters, aggregations, and joins  
🚀 **Seamless Transition** - same VastOrbit code, dramatically faster execution  

The VAST SQL Query Engine will unlock the full power of VAST's storage format, delivering unprecedented performance for analytics and AI workloads while maintaining VastOrbit's endless possibilities for data access.

Machine Learning Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

VastOrbit uses a hybrid approach for maximum flexibility:

.. code-block:: text

   TRAINING (sklearn/Spark)
   ┌─────────────────────────────────────┐
   │  VastFrame.to_pandas()              │
   │         ↓                           │
   │  sklearn.fit(X, y)                  │
   │    or                               │
   │  Spark MLlib training               │
   │         ↓                           │
   │  Trained Model                      │
   └─────────────────────────────────────┘
   
   INFERENCE (In-Database)
   ┌─────────────────────────────────────┐
   │  VastOrbit.InMemoryModel(model)     │
   │         ↓                           │
   │  model.predict(VastFrame)           │
   │         ↓                           │
   │  Predictions in VAST DataBase       │
   │  (No data movement!)                │
   └─────────────────────────────────────┘

**Why This Architecture?**

- **Training Flexibility**: Use familiar sklearn or scale with Spark
- **Inference Performance**: Execute on full dataset in-database
- **No Data Movement**: Predictions run where data lives
- **Model Portability**: Import models trained anywhere

Key Concepts
^^^^^^^^^^^^

**VastFrame**: The core data structure representing data in VAST DataBase, data lakes, or files. Operations on VastFrame execute in-database or on files - data never moves to Python.

**Federated Queries**: Trino enables querying across multiple data sources (VAST tables, S3 files, PostgreSQL, etc.) in a single query.

**Lazy Evaluation**: Queries are optimized before execution, enabling intelligent query planning and predicate pushdown.

**Hybrid ML**: Train models wherever you want (sklearn locally, Spark distributed), deploy for in-database inference at scale.

System Requirements Summary
----------------------------

+------------------+------------------------------------------------------+
| Component        | Requirement                                          |
+==================+======================================================+
| Python           | 3.12 or higher                                       |
+------------------+------------------------------------------------------+
| Operating System | Linux, macOS                                         |
+------------------+------------------------------------------------------+
| VAST Cluster     | Release 5.0.0-sp10 or later                          |
+------------------+------------------------------------------------------+
| Query Engine     | Trino (configured on VAST cluster)                   |
+------------------+------------------------------------------------------+
| Metastore        | Hive metastore (for file/external table access)      |
+------------------+------------------------------------------------------+
| Network Access   | Connection to VAST cluster endpoint                  |
+------------------+------------------------------------------------------+
| Authentication   | AWS-style access and secret keys                     |
+------------------+------------------------------------------------------+

Getting Help
------------

If you encounter issues during installation or usage:

**Documentation Resources:**

- `VAST Data Platform Docs <https://docs.vastdata.com>`_
- `VastOrbit GitHub Repository <https://github.com/vast-data/vastorbit>`_
- `Trino Documentation <https://trino.io/docs/current/>`_

**Community Support:**

- Open an issue on `GitHub <https://github.com/vast-data/vastorbit/issues>`_
- Contact VAST Data support: vastsupport.slack.com

**Examples and Tutorials:**

- Check out the :ref:`examples` section for hands-on tutorials
- Browse the :ref:`api` reference for detailed function documentation

Next Steps
----------

Continue your journey with VastOrbit:

1. :ref:`connection` - Learn how to connect to VAST and configure Trino
2. :ref:`user_guide` - Master VastFrame and federated queries
3. :ref:`examples` - Follow step-by-step tutorials
4. :ref:`api.machine_learning` - Build hybrid ML workflows
5. :ref:`chart_gallery` - Create stunning visualizations

.. note::

   VastOrbit gives you endless possibilities - query databases, data lakes, files, and more. All from familiar pandas-like Python syntax!