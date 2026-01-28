.. _statistics:

==================
VastOrbit Statistics
==================

.. include:: logo_include.rst

This page provides detailed statistics about VastOrbit's capabilities for in-database data science on VAST.

.. note::

    VastOrbit brings Python data science to VAST Database with complete in-database execution - data preparation, exploration, analytics, and ML at any scale.

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
   * - ML Algorithms
     - 10 (embedded + sklearn import)
   * - Supported Python Versions
     - 3.12+
   * - Supported Platforms
     - Linux, macOS
   * - Target Database
     - VAST Database
   * - Data Sources
     - VAST tables, files, external databases

Functional Coverage
-------------------

Data Preparation
^^^^^^^^^^^^^^^^

- **Cleaning**: fillna, dropna, drop_duplicates - all in VAST
- **Transformation**: normalize, scale, encode - in-database execution
- **Feature Engineering**: 80+ functions for column operations
- **Type Handling**: Comprehensive casting and conversions
- **Missing Values**: Multiple strategies executed in VAST
- **Outlier Detection**: Statistical methods at scale

Data Exploration
^^^^^^^^^^^^^^^^

- **Charts**: Histograms, scatter plots, correlation matrices
- **Distributions**: KDE, box plots, violin plots
- **Statistical Profiling**: 60+ functions (mean, median, variance, quantiles)
- **Correlation Analysis**: Pearson, Spearman, Kendall
- **Pattern Discovery**: Automatic anomaly detection
- **Intelligent Sampling**: Visualize billions of rows instantly

Analytics Functions
^^^^^^^^^^^^^^^^^^^

- **DataFrame Operations**: 200+ functions for transformation and aggregation
- **Aggregations**: All standard plus custom aggregations in VAST
- **Window Functions**: Ranking, analytical, aggregate windows
- **Join Operations**: All SQL join types across sources
- **Pivot/Unpivot**: Multi-dimensional reshaping
- **Time Series**: Specialized temporal analysis
- **Geospatial**: Location-based analytics
- **Text Analytics**: String manipulation and pattern matching
- **JSON/Array**: Complex nested data operations

Data Source Access
------------------

VAST Database
^^^^^^^^^^^^^

- **VAST Tables**: Native in-database processing
- **Columnar Storage**: Optimized analytics execution
- **DASE Architecture**: Leverages disaggregated compute/storage
- **Sub-ms Latency**: Flash-native performance

File Access
^^^^^^^^^^^

- **Parquet**: Direct querying without load
- **CSV/TSV**: In-place analysis
- **JSON**: Nested data exploration
- **ORC, Avro**: Additional formats
- **Compressed Files**: Gzip, Snappy, LZ4, Zstandard

Multi-Source
^^^^^^^^^^^^

- **External Databases**: PostgreSQL, MySQL, MongoDB, 30+ more
- **Data Lakes**: S3, Azure Blob, GCS
- **Table Formats**: Iceberg, Delta Lake, Hudi
- **Streaming**: Kafka integration
- **Unified API**: Query all sources with pandas syntax

Machine Learning
----------------

Embedded Models (10)
^^^^^^^^^^^^^^^^^^^^

Train and deploy directly with VastOrbit:

1. **Linear Models**
   - LinearRegression
   - LogisticRegression
   - Ridge, Lasso

2. **Tree Models**
   - DecisionTree
   - RandomForest
   - XGBoost

3. **Ensemble Methods**
   - GradientBoosting
   - AdaBoost

4. **Clustering**
   - KMeans

5. **Other**
   - SVM
   - NaiveBayes

Model Import
^^^^^^^^^^^^

- **sklearn Models**: Import trained sklearn models
- **Automatic Deployment**: Convert to in-database inference
- **Custom Models**: sklearn-compatible estimators
- **Serialization**: Pickle, joblib support

ML Workflow
^^^^^^^^^^^

- **Sampling**: Automatic intelligent sampling for training
- **Feature Prep**: Transform features in VAST before training
- **In-Database Inference**: Score billions of rows in VAST
- **Batch Predictions**: Production-scale scoring
- **Model Versioning**: Track and deploy versions

Visualization
-------------

Chart Types
^^^^^^^^^^^

**Statistical Charts:**
- Histograms with intelligent binning
- Box plots and violin plots
- Density and KDE plots
- Q-Q and probability plots

**Exploration:**
- Scatter plots and correlation matrices
- Heatmaps for multi-dimensional data
- Distribution comparisons
- Pattern visualization

**Time Series:**
- Line plots and trend analysis
- Candlestick charts
- Seasonal decomposition

**ML Visualization:**
- ROC curves and AUC
- Confusion matrices
- Feature importance
- Lift charts

**Geospatial:**
- Map visualizations
- Location clustering

Rendering Backends
^^^^^^^^^^^^^^^^^^

- **Plotly**: Interactive web-ready charts
- **Matplotlib**: Publication-quality static plots
- **Highcharts**: Enterprise interactive visualizations

Intelligent Sampling
^^^^^^^^^^^^^^^^^^^^

- **Automatic**: Samples large datasets for instant visualization
- **Distribution-Preserving**: Maintains statistical characteristics
- **Configurable**: User-defined sample sizes
- **Performance**: Visualize exabyte-scale data interactively
- **Smart Algorithms**: Stratified, reservoir sampling

Performance
-----------

In-Database Execution
^^^^^^^^^^^^^^^^^^^^^

- **Zero Data Movement**: All processing in VAST
- **Predicate Pushdown**: Filters executed in-database
- **Projection Pushdown**: Only required columns retrieved
- **Lazy Evaluation**: Optimized before execution
- **Partition Pruning**: Intelligent file filtering

Scalability
^^^^^^^^^^^

- **Data Volume**: Petabyte to exabyte scale
- **Processing Speed**: Leverages VAST's flash performance
- **Concurrency**: Multi-user analytics
- **ML Inference**: Score billions of rows in minutes
- **Chart Generation**: Sub-second visualization

VAST Optimizations
^^^^^^^^^^^^^^^^^^

- **Columnar Format**: Optimized analytics queries
- **DASE Architecture**: Efficient compute/storage separation
- **Flash Storage**: Sub-millisecond latency
- **Linear Scaling**: Performance scales with data

Code Quality
------------

Development Standards
^^^^^^^^^^^^^^^^^^^^^

- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **PEP 8**: Consistent formatting
- **Modern Python**: Python 3.12+ features

Platform Compatibility
----------------------

VAST Database
^^^^^^^^^^^^^

- **Minimum Version**: 5.0.0-sp10
- **Recommended**: Latest stable release
- **Tested**: 5.0.x, 5.1.x series

Python
^^^^^^

- **Supported**: 3.12+
- **Recommended**: 3.12 or 3.13

Operating Systems
^^^^^^^^^^^^^^^^^

- **Linux**: Ubuntu 20.04+, RHEL 8+, CentOS 8+, Debian 11+
- **macOS**: 12 (Monterey) and later
- **Windows**: Use WSL2

Key Capabilities
----------------

Data Preparation in VAST
^^^^^^^^^^^^^^^^^^^^^^^^^

- Clean data at any scale
- Transform and normalize in-database
- Feature engineering without data movement
- Handle missing values efficiently
- Profile data quality

Interactive Exploration
^^^^^^^^^^^^^^^^^^^^^^^

- Generate charts with intelligent sampling
- Analyze distributions and correlations
- Discover patterns and anomalies
- Statistical profiling
- Multi-dimensional visualization

In-Database Analytics
^^^^^^^^^^^^^^^^^^^^^

- 400+ functions executing in VAST
- pandas-like syntax
- Zero data movement
- Petabyte-scale processing
- Production-ready workflows

Multi-Source Queries
^^^^^^^^^^^^^^^^^^^^

- Query VAST tables and files
- Access external databases
- Join across sources
- Unified Python API

In-Database ML
^^^^^^^^^^^^^^

- Embedded model algorithms
- sklearn model import
- Production inference in VAST
- Batch scoring at scale

Roadmap
-------

Near Term (v1.0)
^^^^^^^^^^^^^^^^

- Production-ready release
- Enhanced AutoML
- Additional ML algorithms
- Streaming integration

Medium Term
^^^^^^^^^^^

- Advanced time series forecasting
- Vector operations for AI
- Enhanced geospatial analytics
- Real-time inference

Long Term
^^^^^^^^^

- Distributed training
- Graph analytics
- Multi-modal data processing
- AI workflow automation

Use Cases
---------

**Data Preparation:**
- Clean and transform data in VAST
- Feature engineering at scale
- Data quality validation
- Preprocessing for ML

**Data Exploration:**
- Interactive charts and profiling
- Pattern discovery
- Statistical analysis
- Multi-source exploration

**AI/ML Development:**
- Train models with embedded algorithms
- Deploy for in-database inference
- Production-scale predictions
- Real-time scoring

**Analytics:**
- In-database aggregations
- Cross-source reporting
- Historical trend analysis
- Business intelligence

For More Information
--------------------

- `GitHub Repository <https://github.com/vastdata-dev/vastorbit>`_
- `VAST Database <https://www.vastdata.com/platform/database>`_

.. seealso::

   - :ref:`getting_started` - Installation and quick start
   - :ref:`api` - Complete API reference
   - :ref:`examples` - Example workflows
   - :ref:`machine_learning` - ML guide