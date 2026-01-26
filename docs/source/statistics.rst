.. _statistics:

==================
VastOrbit Statistics
==================

.. include:: logo_include.rst

This page provides detailed statistics about VastOrbit's capabilities, coverage, and performance metrics.

.. note::

    VastOrbit is designed specifically for the VAST Data Platform with enhanced capabilities for federated queries, advanced analytics, AI development, and endless data access possibilities.

Library Metrics
---------------

Core Statistics
^^^^^^^^^^^^^^^

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Metric
     - Value
   * - Total Functions
     - 400+
   * - ML Inference Algorithms
     - 10
   * - Supported Python Versions
     - 3.12+
   * - Supported Platforms
     - Linux, macOS
   * - Query Engines
     - Trino (federated)
   * - Data Sources
     - Unlimited (via Trino connectors)

Functional Coverage
-------------------

Data Manipulation
^^^^^^^^^^^^^^^^^

- **DataFrame Operations**: 200+ functions for data transformation, filtering, and aggregation
- **Column Operations**: 80+ functions for column-level manipulations
- **Join Operations**: All SQL join types including cross-catalog federated joins
- **Window Functions**: Complete suite of ranking, analytical, and aggregate window functions
- **Pivot/Unpivot**: Multi-dimensional data reshaping capabilities
- **Data Type Conversions**: Comprehensive casting and transformation functions

Analytics Functions
^^^^^^^^^^^^^^^^^^^

- **Statistical Functions**: 60+ functions (mean, median, variance, quantiles, correlations, etc.)
- **Aggregation Functions**: All standard SQL aggregates plus custom aggregations
- **Time Series**: Specialized functions for temporal data analysis
- **Geospatial**: Location-based analytics and distance calculations (via Trino geospatial functions)
- **Text Analytics**: String manipulation, pattern matching, and text processing
- **JSON/Array**: Complex data type operations for nested structures

Data Source Connectivity
-------------------------

Via Trino Federated Queries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

VastOrbit can query any data source supported by Trino:

**Databases:**
- VAST DataBase (primary)

**Data Lakes & Files:**
- S3 (Parquet, ORC, Avro, CSV, JSON)
- VAST DataStore
- Azure Blob Storage
- Google Cloud Storage
- HDFS

**Streaming:**
- Apache Kafka

**Other:**
- Hive metastore tables
- Delta Lake, Iceberg, Hudi
- Google Sheets
- REST APIs (via custom connectors)

Machine Learning Capabilities
------------------------------

Inference Algorithms (10)
^^^^^^^^^^^^^^^^^^^^^^^^^

VastOrbit supports in-database inference for models trained with sklearn or Spark:

**Supported for Inference:**

1. **Linear Models**
   - Linear Regression
   - Logistic Regression
   - Ridge/Lasso

2. **Tree-Based Models**
   - Decision Trees
   - Random Forests
   - Gradient Boosting

3. **Ensemble Methods**
   - XGBoost models
   - LightGBM models

4. **Clustering**
   - K-Means inference

5. **Other**
   - SVM models
   - Naive Bayes

Training Integration
^^^^^^^^^^^^^^^^^^^^

- **sklearn**: Full compatibility - train locally, deploy for in-database inference
- **Spark MLlib**: Import Spark-trained models for inference
- **Custom Models**: Support for custom sklearn-compatible estimators
- **Model Serialization**: Pickle, joblib support

ML Workflow Features
^^^^^^^^^^^^^^^^^^^^

- **In-Database Scoring**: Predictions execute in VAST DataBase - no data movement
- **Batch Predictions**: Score millions/billions of rows efficiently
- **Feature Engineering**: Transform features in-database before inference
- **Model Versioning**: Track and deploy different model versions
- **A/B Testing**: Compare model performance on live data

Visualization Capabilities
---------------------------

Chart Types
^^^^^^^^^^^

- **Statistical**: Histograms, box plots, violin plots, density plots
- **Correlation**: Scatter plots, correlation matrices, heatmaps
- **Time Series**: Line plots, candlestick charts, trend analysis
- **ML**: ROC curves, confusion matrices, feature importance, lift charts
- **Geospatial**: Map visualizations (via geopandas)
- **Distribution**: KDE plots, Q-Q plots, probability plots

Backends
^^^^^^^^

- **Plotly**: Interactive, web-ready visualizations
- **Matplotlib**: Publication-quality static charts
- **Highcharts**: Enterprise-grade interactive charts

Smart Sampling
^^^^^^^^^^^^^^

- **Intelligent Sampling**: Automatically samples large datasets for visualization
- **Statistical Preservation**: Maintains data distribution characteristics
- **Configurable Limits**: User-defined sample sizes
- **Performance Optimization**: Visualize exabyte-scale data interactively

Performance Metrics
-------------------

Query Optimization
^^^^^^^^^^^^^^^^^^

- **Predicate Pushdown**: Filters executed in-database or at file level
- **Projection Pushdown**: Only required columns retrieved
- **Lazy Evaluation**: Queries optimized before execution
- **Trino CBO**: Cost-based query optimization
- **Partition Pruning**: Intelligent partition elimination for file queries

Scalability
^^^^^^^^^^^

- **Data Volume**: Unlimited
- **File Size**: Efficiently handles petabyte-scale file collections
- **Concurrency**: Leverages Trino's multi-user concurrency
- **Query Performance**: Sub-second to seconds for most analytical queries
- **ML Inference**: Score billions of rows in minutes

Federated Query Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Cross-Source Joins**: Optimized joins across different data sources
- **Data Locality**: Trino minimizes data movement between sources
- **Parallel Execution**: Distributed query processing
- **Catalog Caching**: Metadata caching for faster query planning

Code Quality
------------

Development Standards
^^^^^^^^^^^^^^^^^^^^^

- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings for all public APIs
- **PEP 8 Compliance**: Consistent code formatting
- **Modern Python**: Leverages Python 3.12+ features

Platform Compatibility
----------------------

Query Engines
^^^^^^^^^^^^^

- **Trino**: Full support for federated queries (current)
- **VAST SQL Query Engine**: Coming soon with 10-100x performance gains
  
  - Direct read of VAST's compressed columnar format
  - Native VAST Catalog integration
  - Optimized for VAST storage architecture
  - Seamless migration - same VastOrbit code, dramatically faster execution

VAST Cluster Versions
^^^^^^^^^^^^^^^^^^^^^

- **Minimum**: 5.0.0-sp10
- **Recommended**: Latest stable release
- **Tested**: 5.0.x, 5.1.x series

Python Versions
^^^^^^^^^^^^^^^

- **Supported**: 3.12+
- **Recommended**: 3.12 or 3.13
- **Earlier**: Not supported

Operating Systems
^^^^^^^^^^^^^^^^^

- **Linux**: Ubuntu 20.04+, RHEL 8+, CentOS 8+, Debian 11+
- **macOS**: 12 (Monterey) and later
- **Windows**: Not currently supported (use WSL2)

File Formats Supported
----------------------

Via Trino Connectors
^^^^^^^^^^^^^^^^^^^^

**Structured:**
- Native VAST Format (recommended for analytics)
- Parquet
- ORC
- Avro

**Semi-Structured:**
- JSON (including JSON Lines)
- CSV/TSV
- XML (via custom connectors)

**Compressed:**
- Gzip
- Snappy
- LZ4
- Zstandard

**Table Formats:**
- Apache Iceberg
- Delta Lake
- Apache Hudi
- Hive tables

Unique VastOrbit Features
--------------------------

Compared to VerticaPy
^^^^^^^^^^^^^^^^^^^^^

VastOrbit builds on VerticaPy's foundation with significant enhancements:

**Enhanced Capabilities:**

1. **Federated Queries**: Query across multiple data sources (databases, lakes, files) in one query
2. **File-First Support**: Direct querying of Parquet, CSV, JSON without loading to database
3. **Broader Ecosystem**: Access any Trino-supported data source
4. **AI Development**: Built specifically for modern AI workflows on VAST
5. **Hybrid ML**: Flexible train anywhere, infer in-database architecture
6. **Data Lake Integration**: Seamless S3/DataStore file querying

**VAST-Specific:**

- Optimized for VAST's DASE architecture
- Leverages VAST DataBase's columnar storage
- Integration with VAST Catalog for metadata
- Support for VAST's high-performance file system

Roadmap Highlights
------------------

Near Term
^^^^^^^^^

- Enhanced AutoML capabilities
- Additional ML algorithm support for inference
- Real-time streaming integration (Kafka/Event Broker)
- Advanced time series forecasting

Medium Term
^^^^^^^^^^^

- VAST SQL Query Engine integration
- Native VAST Catalog integration
- Vector database operations for AI/ML
- Enhanced geospatial analytics

Long Term
^^^^^^^^^

- Distributed training capabilities
- Graph analytics support
- Multi-modal data processing
- Enhanced AI workflow automation

Use Cases
---------

**Data Exploration:**
- Interactive analysis of data lakes
- Ad-hoc querying across multiple sources
- Data quality assessment

**AI/ML Development:**
- Feature engineering at scale
- Model deployment for inference
- Real-time predictions on live data

**Analytics:**
- Cross-database reporting
- Unified view of disparate data sources
- Historical trend analysis

**Data Engineering:**
- ETL pipeline development
- Data validation and quality checks
- Schema evolution and migration

For More Information
--------------------

- `GitHub Repository <https://github.com/vast-data/vastorbit>`_
- `VAST Data Platform <https://www.vastdata.com>`_
- `Trino Documentation <https://trino.io/docs/current/>`_

.. seealso::

   - :ref:`getting_started` - Installation and quick start
   - :ref:`api` - Complete API reference
   - :ref:`examples` - Example workflows and tutorials
   - :ref:`machine_learning` - ML inference guide