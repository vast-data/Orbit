.. _about_us:

About Us
========

.. include:: logo_include.rst

Why Choose VastOrbit?
---------------------

Unlock Endless Possibilities for Data Analytics and AI on VAST Data Platform

.. tab-set::

   .. tab-item:: Endless Possibilities

      Query Anywhere, Analyze Everything - Unlock VAST's Full Potential

      VastOrbit gives you **endless possibilities** by removing all barriers between different data sources. Built for the VAST Data Platform, it leverages both current (Trino) and future (VAST SQL Query Engine) technologies to deliver unmatched flexibility and performance.

      **Data Sources - No Limits:**
      - VAST DataBase tables (transactional + analytical)
      - Data lakes (S3, VAST DataStore)
      - Files (Parquet, CSV, JSON, ORC, Avro)
      - External databases (PostgreSQL, MySQL, MongoDB, 30+ more)
      - Streaming data (Kafka, Pulsar)
      - **All accessible through one Python API**

      **Performance Evolution:**
      - **Today**: Work with Trino federated queries
      - **Tomorrow**: 10-100x faster with VAST SQL Query Engine directly reading compressed columnar format
      - **Always**: Zero data movement - execute where data lives

      **What This Means:**
      - Write one Python query to join VAST tables + S3 Parquet + PostgreSQL
      - Access petabyte-scale data lakes without moving a single byte
      - Future-proof architecture - seamless transition to VAST SQL Engine
      - Compressed columnar format exploitation for maximum performance
      - Real-time and historical data in unified queries

      With VastOrbit and VAST Data Platform, you truly have endless possibilities for data science and AI development.

      `Learn More About VAST DataBase <https://www.vastdata.com/platform/database>`_

   .. tab-item:: Federated Analytics

      Join Data Across Any Source - Today and Tomorrow

      Traditional data science requires consolidating data into one system. VastOrbit eliminates this bottleneck using Trino's federated capabilities today, with a seamless path to VAST's native SQL Query Engine for 10-100x performance gains.

      **Cross-Source Operations:**
      - Join VAST tables with S3 Parquet files
      - Combine PostgreSQL data with data lake files
      - Merge streaming Kafka data with historical tables
      - Aggregate across multiple databases simultaneously
      - **All in a single Python query**

      **The VAST Advantage:**
      - **Current**: Trino federates across 30+ data sources
      - **Future**: VAST SQL Engine directly reads compressed columnar format
      - **Result**: Same code, dramatically faster execution
      - Compressed format exploitation for analytics
      - Native integration with VAST Catalog

      **Benefits:**
      - Eliminate ETL pipelines for analytics
      - Query data without copying or moving it
      - Maintain single source of truth for each dataset
      - Reduce storage costs and data duplication
      - Accelerate time-to-insight
      - Future-proof with automatic VAST SQL Engine optimization

      **Example Use Cases:**
      - Customer 360 view combining CRM, transactions, and clickstream data
      - Real-time fraud detection joining live transactions with historical patterns
      - Supply chain analytics across ERP, warehouse, and logistics systems

      VastOrbit's federated analytics unlock VAST's endless possibilities for unified data access.

   .. tab-item:: Hybrid ML Workflow

      Train Anywhere, Infer at Scale on VAST

      VastOrbit pioneers a hybrid approach combining training flexibility with inference performance, optimized for VAST's compressed storage format:

      **Training:**
      - Use sklearn locally on sampled data
      - Scale training with Spark on full datasets
      - Leverage any Python ML library you prefer
      - Develop and iterate quickly

      **Inference:**
      - Deploy models for in-database execution
      - Score billions of rows without data movement
      - Achieve production-scale performance
      - Maintain data security and governance

      **Supported Models:**
      - Linear models (regression, logistic regression)
      - Tree-based models (decision trees, random forests, XGBoost)
      - Ensemble methods
      - Clustering algorithms (K-Means)
      - Custom sklearn-compatible models

      This architecture gives you the best of both worlds: the flexibility of Python ML libraries and the performance of in-database execution.

   .. tab-item:: AI Development Platform

      Built for Modern AI Workflows on VAST

      VastOrbit is designed from the ground up for AI development on the VAST Data Platform, with optimizations for both current (Trino) and future (VAST SQL Engine) execution:

      **400+ Functions:**
      - Comprehensive data manipulation
      - Advanced analytics and statistics
      - Feature engineering at scale
      - Text and geospatial processing

      **10 ML Inference Algorithms:**
      - Production-ready model deployment
      - Real-time scoring capabilities
      - Batch prediction processing
      - Model performance monitoring

      **Integration with AI Stack:**
      - Seamless sklearn compatibility
      - Spark MLlib model import
      - Jupyter notebook first-class support
      - Visualization for model explainability

      **VAST-Specific Advantages:**
      - Leverage VAST's sub-millisecond latency
      - Scale linearly with data growth
      - Access live and historical data simultaneously
      - Build real-time AI applications

      VastOrbit transforms VAST DataBase into your AI development platform.

The Team
--------

.. grid:: 2 2 3 3

    .. grid-item::
    
        .. card:: Badr Ouali
          :img-top: _static/website/about_us/team/member1.jpg
          :link: https://www.linkedin.com/in/badr-ouali/
          :text-align: center
          :class-card: member-pics-card

          DB Systems Engineer

    .. grid-item::

        .. card:: Fouad Teban
          :img-top: _static/website/about_us/team/member2.jpg
          :link: https://www.linkedin.com/in/fouadteban/
          :text-align: center
          :class-card: member-pics-card

          Field Engineering Lead

    .. grid-item::

        .. card:: Christian Neundorf
          :img-top: _static/website/about_us/team/member3.jpg
          :link: https://www.linkedin.com/in/christian-neundorf-552a6721/
          :text-align: center
          :class-card: member-pics-card

          Senior Systems Engineer

    .. grid-item::

        .. card:: Chris Snow
          :img-top: _static/website/about_us/team/member4.jpg
          :link: https://www.linkedin.com/in/csnowuk/
          :text-align: center
          :class-card: member-pics-card

          Product Manager

    .. grid-item::

        .. card:: Kiran Kumar
          :img-top: _static/website/about_us/team/member5.jpg
          :link: https://www.linkedin.com/in/kiranmavatoor/
          :text-align: center
          :class-card: member-pics-card

          Principal Systems Engineer

The Story Behind VastOrbit
---------------------------

From VerticaPy to VastOrbit: Evolution of In-Database Data Science

.. tab-set::

   .. tab-item:: The Vision

      **The Problem:**

      Modern data science faces a fundamental challenge: data keeps growing, but traditional tools force you to choose between:
      
      - **Small Data Analysis**: Load data into Python/pandas - fast and flexible, but limited to memory
      - **Big Data Processing**: Use Spark/Hadoop - scalable but complex, slow iteration
      - **Database Analytics**: Write SQL - powerful but limited flexibility

      None of these approaches handle today's reality: data lives in multiple places (databases, data lakes, files) and modern AI requires accessing all of it.

      **The VAST Revolution:**

      VAST Data Platform changed the game:
      - Unified transactional and analytical database
      - All-flash performance at data lake economics
      - Linear scaling from gigabytes to exabytes
      - DASE architecture eliminates bottlenecks

      But data scientists still needed a way to leverage this power with familiar Python tools.

      **VastOrbit's Solution:**

      Give VAST users endless possibilities:
      - Query any data source through one API
      - Leverage Trino for federated analytics
      - Train ML models with sklearn/Spark
      - Deploy for in-database inference at scale
      - Work with familiar pandas-like syntax

      The vision: Make the VAST Data Platform accessible to every data scientist.

   .. tab-item:: The Journey

      **2017-2022: VerticaPy Era**

      Badr Ouali created VerticaPy to solve a specific problem: bring Python data science to Vertica's columnar database. VerticaPy pioneered:
      - pandas-like API for in-database analytics
      - sklearn-compatible ML models
      - Visualization directly from database
      - Zero data movement philosophy

      VerticaPy proved the concept: Python can be a powerful interface for in-database analytics.

      **2019-2025: VAST Emergence**

      VAST Data disrupted the market:
      - Revolutionary DASE architecture
      - All-flash Universal Storage
      - VAST DataBase combining OLTP and OLAP
      - Integration with Trino for SQL anywhere

      The question arose: Could Python unlock VAST's full potential?

      **2026-Present: VastOrbit**

      VastOrbit represents the evolution of in-database data science:
      - Built specifically for VAST Data Platform
      - Leverages Trino's federated query capabilities
      - Extends beyond database to files and data lakes
      - Hybrid ML: train anywhere, infer in-database
      - 400+ functions for comprehensive analytics

      **Key Innovations:**
      - Query federation across any Trino-supported source
      - Direct file access (Parquet, CSV, JSON) without loading
      - sklearn integration for model training
      - In-database inference at scale
      - Endless possibilities for data access

   .. tab-item:: Philosophy

      **Endless Possibilities**

      VastOrbit is built on the principle that data scientists shouldn't be limited by where data lives or what tools they use.

      **Core Principles:**

      1. **Query Anywhere**: If Trino can reach it, VastOrbit can query it
      2. **Zero Data Movement**: Process data where it lives
      3. **Familiar Tools**: Use pandas and sklearn patterns you know
      4. **Hybrid Flexibility**: Train with any tool, infer in-database
      5. **Federation First**: Join data across sources seamlessly

      **What This Means:**

      - A data scientist shouldn't care if data is in a database, data lake, or files
      - Training a model locally and deploying it at scale should be seamless
      - Querying petabytes should feel like querying megabytes
      - Python code should translate to optimized SQL automatically
      - Every data source is accessible through one API

      **The Result:**

      VastOrbit doesn't just bring tools to data - it erases the boundaries between different data sources, giving you a unified Python interface to your entire data ecosystem.

   .. tab-item:: Technical Evolution

      **From Database-Only to Federated Analytics**

      **VerticaPy Foundations (2017-2022):**
      - In-database execution for Vertica
      - SQL generation from Python operations
      - ML model training in-database
      - Visualization with intelligent sampling

      **VastOrbit Innovations (2026-Present):**

      1. **Federated Query Support:**
         - Trino integration for cross-source queries
         - Catalog abstraction for multiple data sources
         - Intelligent query routing

      2. **File-First Capabilities:**
         - Direct Parquet/CSV/JSON querying
         - Hive metastore integration
         - S3/DataStore file access
         - No "load first" requirement

      3. **Hybrid ML Architecture:**
         - Separate training (sklearn/Spark) from inference (in-DB)
         - Model serialization and deployment
         - In-database scoring at scale
         - Support for 10 model types

      4. **Enhanced Analytics:**
         - 400+ functions (focused on VAST/Trino capabilities)
         - Geospatial via Trino functions
         - Advanced time series operations
         - JSON/complex type handling

      5. **VAST Optimization:**
         - Leverages VAST's columnar storage
         - Optimized for DASE architecture
         - Integration with VAST Catalog
         - Support for VAST-specific features

VastOrbit Statistics
--------------------

* **400+ Functions**: Comprehensive data manipulation and analytics
* **10 ML Inference Algorithms**: Production-ready model deployment
* **Unlimited Data Sources**: Query anywhere via Trino federation
* **Python 3.12+**: Modern Python features
* **Exabyte Scale**: No practical limits with VAST infrastructure
* **Sub-ms Latency**: VAST's flash-native performance

`View Detailed Statistics <../documentation/statistics.html>`_

Comparison: VastOrbit vs VerticaPy
-----------------------------------

Built on the same philosophy, evolved for different platforms:

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - Feature
     - VerticaPy
     - VastOrbit
   * - Target Platform
     - Vertica Database
     - VAST Data Platform
   * - Query Engine
     - Vertica SQL
     - Trino (federated)
   * - Data Sources
     - Vertica tables only
     - Databases, files, data lakes, streams
   * - Functions
     - 600+
     - 400+ (focused on VAST/Trino)
   * - ML Training
     - In-database
     - sklearn/Spark (external)
   * - ML Inference
     - In-database
     - In-database
   * - File Querying
     - Requires COPY
     - Direct (Parquet, CSV, JSON)
   * - Federated Queries
     - Limited
     - Core capability
   * - Use Case
     - Vertica-centric analytics
     - Multi-source AI/ML

Both libraries share the vision of bringing Python to databases, but VastOrbit expands to give users endless possibilities across the entire data ecosystem.

Technology Stack
----------------

VastOrbit leverages cutting-edge technologies:

**Core Platform:**
- **VAST DataBase**: Unified transactional and analytical database
- **Trino**: Distributed SQL query engine for federation
- **DASE Architecture**: Disaggregated compute and storage

**Python Ecosystem:**
- **sklearn**: ML training compatibility
- **Pandas**: API patterns and data structures
- **PyArrow**: Efficient data transfer
- **Plotly/Matplotlib/Highcharts**: Visualization backends

**Data Access:**
- **Hive Metastore**: File and table metadata
- **S3 Protocol**: Data lake access
- **JDBC/ODBC**: Database connectivity

Community & Support
-------------------

**Get Involved:**

- **GitHub**: `github.com/vast-data/vastorbit <https://github.com/vast-data/vastorbit>`_
- **Documentation**: This site
- **Support**: vastsupport.slack.com

**Enterprise Support:**

VAST Data provides enterprise-grade support for VastOrbit as part of the VAST Data Platform offering.

.. note::

   VastOrbit gives VAST DataBase users endless possibilities. Created by the maker of VerticaPy, refined for the VAST Data Platform, designed for modern AI workloads.