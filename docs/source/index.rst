.. _index:

***********************************
Welcome to VastOrbit Documentation
***********************************

.. include:: logo_include.rst

**Python API for Federated Analytics and AI Development**

VastOrbit, unlocks the **endless possibilities** of the VAST Data Platform for data science and AI. Currently powered by Trino for federated queries, VastOrbit will soon leverage the **VAST SQL Query Engine** for 10-100x performance gains by directly exploiting VAST's compressed columnar storage format. Query anywhere - databases, data lakes, files - with familiar pandas-like syntax. Train ML models with sklearn or Spark, deploy for blazing-fast in-database inference.

.. grid:: 2 2 2 2
    :gutter: 3

    .. grid-item-card:: 🚀 Getting Started
        :link: getting_started
        :link-type: ref
        :text-align: center

        Installation, quick start, and your first federated query in 5 minutes.

    .. grid-item-card:: 🔌 Connection Guide
        :link: connection
        :link-type: ref
        :text-align: center

        Connect to VAST via Trino, access multiple catalogs, configure authentication.

    .. grid-item-card:: 📚 User Guide
        :link: user_guide
        :link-type: ref
        :text-align: center

        Master VastFrame operations and federated queries across data sources.

    .. grid-item-card:: 🤖 Machine Learning
        :link: machine_learning
        :link-type: ref
        :text-align: center

        Train with sklearn/Spark, deploy for in-database inference at scale.

    .. grid-item-card:: 📊 Chart Gallery
        :link: chart_gallery
        :link-type: ref
        :text-align: center

        Interactive visualizations from any data source with intelligent sampling.

    .. grid-item-card:: 💻 API Reference
        :link: api
        :link-type: ref
        :text-align: center

        Complete API documentation with 400+ functions.

    .. grid-item-card:: 🎯 Examples
        :link: examples
        :link-type: ref
        :text-align: center

        Hands-on tutorials for federated analytics and hybrid ML workflows.

    .. grid-item-card:: ℹ️ About Us
        :link: about_us
        :link-type: ref
        :text-align: center

        Meet the creator and learn VastOrbit's vision.

What is VastOrbit?
==================

VastOrbit is a Python library that unlocks the full potential of the VAST Data Platform by providing:

**Endless Data Access:**
- Query VAST DataBase tables
- Access data lake files (Parquet, CSV, JSON)
- Connect to external databases (PostgreSQL, MySQL, MongoDB, etc.)
- Stream from Kafka/Pulsar
- Join across all sources in one query

**Hybrid ML Workflow:**
- Train models with sklearn or Spark
- Deploy for in-database inference
- Score billions of rows without data movement
- 10 supported model types

**400+ Functions:**
- pandas-like DataFrame operations
- Advanced analytics and statistics
- Geospatial and time series analysis
- Text processing and JSON handling

Key Features
============

.. grid:: 1 1 2 2

    .. grid-item-card:: 🌐 Federated Queries
        :text-align: center

        Leverage Trino to query across VAST tables, S3 files, PostgreSQL, and 30+ data sources - all in one Python query.

    .. grid-item-card:: 📁 File-First Support
        :text-align: center

        Query Parquet, CSV, JSON files directly without loading. No "COPY" required - just point and query.

    .. grid-item-card:: ⚡ In-Database Execution
        :text-align: center

        All operations execute in VAST DataBase or on files - zero data movement to Python.

    .. grid-item-card:: 🤖 Hybrid ML
        :text-align: center

        Train anywhere (sklearn, Spark), deploy for in-database inference at production scale.

    .. grid-item-card:: 🎨 Familiar API
        :text-align: center

        pandas-like DataFrames and sklearn-compatible models make adoption seamless.

    .. grid-item-card:: 📈 Unlimited Scale
        :text-align: center

        Leverage VAST's exabyte-scale infrastructure - query gigabytes or petabytes with same code.

Quick Example
=============

Federated analytics in just a few lines:

.. code-block:: python

    import vastorbit as vo

    # Connect to VAST via Trino
    vo.new_connection({
        'host': 'vast-cluster.example.com',
        'port': 8080,
        'catalog': 'vast_catalog'
    })

    # Query VAST table
    customers = vo.VastFrame('vast_catalog.crm.customers')

    # Query S3 Parquet files
    transactions = vo.VastFrame('hive.default.transactions')

    # Federated join across sources!
    result = customers.join(
        transactions,
        on='customer_id',
        how='inner'
    )

    # Analyze with pandas-like syntax
    summary = result.groupby('region').agg({
        'revenue': 'sum',
        'customer_lifetime_value': 'mean'
    })

    # Train ML model
    from sklearn.ensemble import RandomForestClassifier
    train_data = result.to_pandas().sample(10000)
    model = RandomForestClassifier()
    model.fit(train_data[['age', 'tenure']], train_data['churn'])

    # Deploy for in-database inference - no data movement!
    from vastorbit.machine_learning import InferenceModel
    vo_model = InferenceModel(model)
    predictions = vo_model.predict(result)  # Executes in VAST!

Architecture
============

VastOrbit connects Python to the VAST Data Platform - today through Trino, tomorrow through VAST SQL Query Engine:

.. code-block:: text

    Python Code (pandas/sklearn syntax)
            ↓
    VastOrbit API (intelligent query routing)
            ↓
        TODAY              →        FUTURE
      ┌─────────┐                  ┌──────────────┐
      │  Trino  │───────────--───▶ │  VAST SQL    │
      │         │  (Cross-Engine)  │  Query Engine│
      └────┬────┘                  └──────┬───────┘
           │                              │
           ▼                              ▼
    ┌────────────────────────────────────────┐
    │      VAST Data Platform                │
    │  • Compressed Columnar Storage         │
    │  • VAST DataBase Tables                │
    │  • S3/DataStore Files                  │
    │  • Real-time Ingestion                 │
    └────────────────────────────────────────┘

**Today - Trino**: Federated queries across 30+ data sources  
**Tomorrow - VAST SQL Engine**: 10-100x faster with compressed format exploitation  
**Always - Same Code**: Seamless transition, maximum performance  

**Endless Data Access**: 
- VAST tables, S3 files, PostgreSQL, MongoDB, Kafka streams
- All through one unified Python API
- Zero data movement architecture  

Why VAST Data Platform?
========================

VAST revolutionizes data infrastructure for AI:

**Unified Database**: Transactional + Analytical in one system (no separate OLTP/OLAP)

**DASE Architecture**:
- Single-millisecond latency at exabyte scale
- Linear performance scaling
- All-flash economics

**AI-Ready**: Native vector support, streaming analytics, real-time event processing

**File & Table Unification**: Query structured tables and unstructured files seamlessly

Learn more at `VAST Data Platform <https://www.vastdata.com/platform/database>`_.

Installation
============

Install VastOrbit using pip:

.. code-block:: bash

    pip install vastorbit

Requirements:

- Python 3.12+
- VAST Cluster 5.0.0-sp10+
- Trino query engine configured
- Network access to VAST cluster

See :ref:`getting_started` for detailed installation instructions.

What Makes VastOrbit Special?
==============================

VastOrbit builds on VerticaPy's proven foundation with major enhancements for VAST:

**Endless Possibilities:**

1. **Federated Queries**: Join VAST tables with S3 files, PostgreSQL, MongoDB - all in one query
2. **File-First**: Query Parquet/CSV/JSON directly without loading to database
3. **Hybrid ML**: Train with sklearn/Spark, infer in-database at scale
4. **400+ Functions**: Comprehensive analytics toolkit
5. **Trino Integration**: Access 30+ data sources through one API

**vs VerticaPy:**

- VerticaPy: Vertica-only, in-database training
- VastOrbit: Multi-source federation, hybrid ML, file querying, AI-ready

Both share the vision of bringing Python to databases, but VastOrbit gives you truly endless possibilities.

Documentation Sections
======================

.. grid:: 2

    .. grid-item::

        **Getting Started**

        - :ref:`getting_started` - Installation and quick start
        - :ref:`connection` - Connecting to VAST and configuring Trino
        - :ref:`whats_new` - Latest features and changes

    .. grid-item::

        **Core Concepts**

        - :ref:`user_guide` - VastFrame and federated queries
        - :ref:`examples` - Hands-on tutorials
        - :ref:`contribution_guidelines` - Contributing

    .. grid-item::

        **Advanced Topics**

        - :ref:`machine_learning` - Hybrid ML workflows
        - :ref:`chart_gallery` - Visualization examples
        - :ref:`statistics` - Library metrics

    .. grid-item::

        **Reference**

        - :ref:`api` - Complete API documentation
        - :ref:`connectors` - Data source connectors
        - :ref:`about_us` - Creator and team

Use Cases
=========

**Data Exploration:**
- Federated analytics across data silos
- Ad-hoc querying of data lakes
- Interactive analysis without data movement

**AI/ML Development:**
- Train models on sampled data locally
- Deploy for production inference at scale
- Real-time predictions on live data

**Data Engineering:**
- ETL-free analytics across sources
- Data quality validation
- Schema discovery and evolution

Community & Support
===================

**Get Help:**

- 📖 Documentation: This site
- 💬 GitHub: https://github.com/vast-data/vastorbit
- 📧 Support: vastsupport.slack.com

**Resources:**

- `VAST Platform Docs <https://docs.vastdata.com>`_
- `Trino Documentation <https://trino.io/docs/current/>`_

**Contributing:**

We welcome contributions! See :ref:`contribution_guidelines`.

What's New
==========

**Version 0.1.0** (Latest)

- Production-ready for VAST Data Platform
- Trino federated query integration
- Hybrid ML: sklearn/Spark training + in-database inference
- 400+ functions for comprehensive analytics
- Direct file querying (Parquet, CSV, JSON)
- 10 ML inference algorithms

See :ref:`whats_new` for complete changelog.

Next Steps
==========

Ready to unlock endless possibilities? Here's your path:

1. **Install**: Follow :ref:`getting_started`
2. **Connect**: Set up Trino connection in :ref:`connection`
3. **Query**: Learn federated queries in :ref:`user_guide`
4. **Try Examples**: Work through tutorials in :ref:`examples`
5. **Build ML**: Create hybrid workflows in :ref:`machine_learning`
6. **Visualize**: Generate charts in :ref:`chart_gallery`

.. note::

    VastOrbit gives VAST users endless possibilities. Query anywhere, analyze everything, build AI at any scale - all with familiar Python syntax.

.. toctree::
    :hidden:
    :maxdepth: 1
    :titlesonly:

    getting_started
    connection
    whats_new
    contribution_guidelines
    examples
    api
    chart_gallery
    user_guide
    statistics
    about_us