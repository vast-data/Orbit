.. _index:

***********************************
Welcome to VAST Orbit Documentation
***********************************

.. include:: logo_include.rst

**Python API for In-Database Analytics and AI with VAST**

VAST Orbit unlocks the **endless possibilities** of VAST Database for data science and AI. Perform all your data preparation, exploration, and machine learning directly in VAST Database - no data movement required. Query across databases, data lakes, and files with familiar pandas-like syntax. Train ML models and deploy for blazing-fast in-database inference at any scale.

.. grid:: 2 2 2 2
    :gutter: 3

    .. grid-item-card:: |i-start| Getting Started
        :link: getting_started
        :link-type: ref
        :text-align: center

        Installation, quick start, and your first query in 5 minutes.

    .. grid-item-card:: |i-connect| Connection Guide
        :link: connection
        :link-type: ref
        :text-align: center

        Connect to VAST Database and configure your environment.

    .. grid-item-card:: |i-guide| User Guide
        :link: user_guide
        :link-type: ref
        :text-align: center

        Master VastFrame operations and in-database analytics.

    .. grid-item-card:: |i-ml| Machine Learning
        :link: api.machine_learning
        :link-type: ref
        :text-align: center

        Train models and deploy for in-database inference at scale.

    .. grid-item-card:: |i-charts| Chart Gallery
        :link: chart_gallery
        :link-type: ref
        :text-align: center

        Interactive visualizations with intelligent sampling.

    .. grid-item-card:: |i-api| API Reference
        :link: api
        :link-type: ref
        :text-align: center

        Complete API documentation with 400+ functions.

    .. grid-item-card:: |i-examples| Examples
        :link: examples
        :link-type: ref
        :text-align: center

        Hands-on tutorials for analytics and ML workflows.

    .. grid-item-card:: |i-about| About Us
        :link: about_us
        :link-type: ref
        :text-align: center

        Meet the creator and learn VAST Orbit's vision.

What is VAST Orbit?
==================

VAST Orbit is a Python library that brings the full power of VAST Database to data scientists and AI developers:

**In-Database Data Preparation:**
- Clean, transform, and prepare data directly in VAST
- Handle missing values, normalize, encode features
- All preprocessing executes in VAST - no data movement
- Scale from megabytes to petabytes with the same code

**Interactive Exploration:**
- Generate charts and visualizations with intelligent sampling
- Analyze distributions, correlations, and patterns
- Explore data interactively without moving it to Python
- pandas-like syntax for familiar workflows

**Multi-Source Analytics:**
- Query VAST tables, data lake files, and external databases
- Join across tables, Parquet files, PostgreSQL, MongoDB
- All in one query, executing in VAST

**In-Database ML:**
- Train models with VAST Orbit's embedded algorithms
- Deploy for in-database inference in VAST
- Score billions of rows without data movement
- 10 ML algorithms available (RandomForest, XGBoost, LinearRegression, etc.)

**400+ Functions:**
- pandas-like DataFrame operations
- Advanced analytics and statistics
- Geospatial and time series analysis
- Text processing and JSON handling

Key Features
============

.. grid:: 1 1 2 2

    .. grid-item-card:: |i-prep| Data Preparation
        :text-align: center

        Clean, transform, and engineer features directly in VAST - handle missing values, outliers, and encoding at any scale.

    .. grid-item-card:: |i-explore| Interactive Exploration
        :text-align: center

        Generate charts, analyze distributions, and discover patterns with intelligent sampling - all without moving data.

    .. grid-item-card:: |i-indb| In-Database Processing
        :text-align: center

        All operations execute in VAST Database - aggregations, joins, and analytics with zero data movement.

    .. grid-item-card:: |i-multisource| Multi-Source Access
        :text-align: center

        Query VAST tables alongside S3 files, PostgreSQL, MongoDB, and 30+ data sources - all in one query.

    .. grid-item-card:: |i-files| Direct File Queries
        :text-align: center

        Query Parquet, CSV, JSON files directly without loading. No "COPY" required - just point and query.

    .. grid-item-card:: |i-inml| In-Database ML
        :text-align: center

        Train with VAST Orbit's embedded models or import sklearn, deploy for in-database inference at production scale in VAST.

Quick Example
=============

Data preparation, exploration, and ML in just a few lines:

.. code-block:: python

    import vastorbit as vo

    # Connect to VAST Database
    vo.new_connection({
        'host': 'vast-cluster.example.com',
        'port': 8080,
        'catalog': 'vast_catalog'
    })

    # Query VAST table - executes in-database
    customers = vo.VastFrame('vast_catalog.crm.customers')

    # Data preparation - all in VAST
    customers = customers.fillna({'income': 0, 'age': customers['age'].avg()})
    customers = customers.drop_duplicates()
    customers['income_normalized'] = customers.normalize('income')
    
    # Explore with charts - intelligent sampling
    customers['age'].hist(nbins=20)
    customers.scatter(['income', 'spending'])
    
    # Query S3 Parquet files
    transactions = vo.VastFrame('hive.default.transactions')

    # Join across sources - all in VAST!
    result = customers.join(
        transactions,
        on='customer_id',
        how='inner'
    )
    
    # Analyze with pandas-like syntax - executes in VAST
    summary = result.groupby(['region'], ['sum(revenue)', 'avg(customer_lifetime_value)'])

    # Train ML model with VAST Orbit - samples and trains automatically
    from vastorbit.machine_learning.vast import RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(result, ['age', 'tenure'], 'churn')

    # Deploy for in-database inference in VAST - no data movement!
    predictions = model.predict(result)  # Executes in VAST Database!

Architecture
============

VAST Orbit brings Python to VAST Database for in-database analytics and AI:

.. code-block:: text

    Python Code (pandas/sklearn syntax)
            ↓
    VAST Orbit API (intelligent query translation)
            ↓
    ┌────────────────────────────────────────┐
    │      VAST Database                     │
    │  • In-Database Execution               │
    │  • Zero Data Movement                  │
    │  • Compressed Columnar Storage         │
    │  • Multi-Source Federation             │
    │  • Real-time Ingestion                 │
    └────────────────────────────────────────┘

**In-Database Processing**: All operations execute where your data lives  
**Multi-Source Access**: Query tables, files, and external databases  
**Zero Movement**: Data stays in VAST - only results come to Python  

Why VAST Database?
==================

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

Install VAST Orbit Beta using pip:

.. code-block:: bash

    pip install vastorbit

Requirements:

- Python 3.12+
- VAST Database 5.0.0-sp10+
- Network access to VAST cluster

**Note**: Version 0.1.0 is in beta. Production-ready version 1.0.0 coming soon.

See :ref:`getting_started` for detailed installation instructions.

What Makes VAST Orbit Special?
==============================

VAST Orbit brings Python data science to VAST Database with true in-database execution:

**Core Capabilities:**

1. **In-Database Data Preparation**: Clean, transform, and engineer features directly in VAST - handle missing values, encode categoricals, normalize at scale
2. **Interactive Exploration**: Generate charts, analyze distributions, discover patterns - all with intelligent sampling from VAST
3. **Multi-Source Queries**: Join VAST tables with files, PostgreSQL, MongoDB - all in one query
4. **Direct File Access**: Query Parquet/CSV/JSON without loading to database tables
5. **In-Database ML**: Train with VAST Orbit's embedded models or import your own, deploy for inference at scale in VAST
6. **400+ Functions**: Comprehensive analytics toolkit with pandas-like API

**The VAST Orbit Advantage:**

- **Zero Data Movement**: Compute where data lives, at VAST scale
- **Familiar Syntax**: pandas and sklearn APIs you already know
- **Production Ready**: Deploy from notebook to production without code changes
- **Limitless Scale**: Query gigabytes to petabytes with the same code

VAST Orbit gives you endless possibilities for analytics and AI on VAST Database.

Documentation Sections
======================

.. grid:: 2

    .. grid-item::

        **Getting Started**

        - :ref:`getting_started` - Installation and quick start
        - :ref:`connection` - Connecting to VAST Database
        - :ref:`whats_new` - Latest features and changes

    .. grid-item::

        **Core Concepts**

        - :ref:`user_guide` - VastFrame and in-database operations
        - :ref:`examples` - Hands-on tutorials
        - :ref:`contribution_guidelines` - Contributing

    .. grid-item::

        **Advanced Topics**

        - :ref:`api.machine_learning` - In-database ML workflows
        - :ref:`chart_gallery` - Visualization examples
        - :ref:`statistics` - Library metrics

    .. grid-item::

        **Reference**

        - :ref:`api` - Complete API documentation
        - :ref:`about_us` - Creator and team

Use Cases
=========

**Data Preparation:**
- Clean and transform data directly in VAST
- Handle missing values, duplicates, outliers
- Feature engineering at scale
- All preprocessing in-database - no data movement

**Data Exploration:**
- Interactive charts and visualizations
- Statistical analysis and profiling
- Pattern discovery and correlation analysis
- Explore petabytes as easily as gigabytes

**AI/ML Development:**
- Prepare features in VAST with embedded transformations
- Train with VAST Orbit's models or import your own
- Deploy for in-database inference at scale
- Real-time predictions on live data

**Multi-Source Analytics:**
- Query across VAST tables, files, and databases
- Ad-hoc analysis without ETL
- Data quality validation in VAST

Community & Support
===================

**Get Help:**

- |i-docs| Documentation: This site
- |i-chat| GitHub: https://github.com/vastdata-dev/vastorbit
- |i-email| Support: `vastsupport.slack.com <https://vastsupport.slack.com>`_

**Resources:**

- `VAST Platform Docs <https://docs.vastdata.com>`_
- `VAST Database Guide <https://docs.vastdata.com/database>`_

**Contributing:**

We welcome contributions! See :ref:`contribution_guidelines`.

What's New
==========

**Version 0.1.0 Beta** (Latest)

- Beta release for VAST Database
- In-database processing for all operations
- Hybrid ML: local training + in-database inference
- 400+ functions for comprehensive analytics
- Direct file querying (Parquet, CSV, JSON)
- 10 ML inference algorithms

Production-ready **Version 1.0.0** coming soon.

See :ref:`whats_new` for complete changelog.

Next Steps
==========

Ready to unlock endless possibilities with VAST? Here's your path:

1. **Install**: Follow :ref:`getting_started`
2. **Connect**: Set up VAST connection in :ref:`connection`
3. **Query**: Learn in-database operations in :ref:`user_guide`
4. **Try Examples**: Work through tutorials in :ref:`examples`
5. **Build ML**: Create in-database workflows in :ref:`api.machine_learning`
6. **Visualize**: Generate charts in :ref:`chart_gallery`

.. note::

    VAST Orbit brings Python data science to VAST Database. Query anywhere, analyze everything, build AI at any scale - all with in-database execution and zero data movement.

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