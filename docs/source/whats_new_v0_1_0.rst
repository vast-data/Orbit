.. _whats_new_v0_1_0:

=====================
Version 0.1.0 (Beta)
=====================

.. include:: logo_include.rst

.. raw:: html

    <div style="text-align: center; margin: 30px 0;">
        <div style="font-size: 24px; font-weight: 600; color: #2F71BD; margin-bottom: 10px;">
            🎉 First Beta Release
        </div>
        <div style="font-size: 16px; color: #666;">
            February 2026 - Beta Release
        </div>
    </div>

Welcome to the first release of **VAST Orbit** - Python data science for VAST Database!

.. important::

   **Beta Status**: VAST Orbit 0.1.0 is in beta. Production-ready version 1.0.0 coming soon. API may change based on feedback. Report issues at **`vastsupport.slack.com <https://vastsupport.slack.com>`__**.

____

Release Highlights
------------------

|i-start| **Python Data Science for VAST**

VAST Orbit 0.1.0 brings complete data science workflows to VAST Database - prepare, explore, analyze, and build ML models with in-database execution.

**Core Features:**

- **Data Preparation in VAST** - Clean, transform, engineer features at any scale
- **Interactive Exploration** - Charts and visualizations with intelligent sampling
- **400+ Functions** - Complete analytics toolkit executing in VAST
- **10 ML Algorithms** - Embedded models for training and inference
- **Multi-Source Access** - Query VAST tables, files, and external databases
- **Zero Data Movement** - All processing in VAST Database

____

What's Included
---------------

**Data Preparation:**

- ``fillna``, ``dropna``, ``drop_duplicates`` - cleaning in VAST
- ``normalize``, ``scale``, ``encode`` - transformations in-database
- Feature engineering at petabyte scale
- Statistical profiling and quality checks

**Interactive Exploration:**

- Histograms, scatter plots, correlation matrices
- Box plots, violin plots, KDE
- Intelligent sampling for instant visualization
- Statistical analysis (mean, median, variance, quantiles)

**Analytics:**

- 400+ functions executing in VAST
- pandas-like DataFrame operations
- Aggregations, joins, window functions
- Time series and geospatial analysis

**Machine Learning:**

- 10 embedded models (RandomForest, GradientBoosting, LinearRegression, etc.)
- sklearn model import support
- In-database inference at scale
- Production-ready deployment

**Core Modules:**

- ``vastorbit.VastFrame`` - pandas-like DataFrame for VAST
- ``vastorbit.machine_learning.vast`` - ML algorithms
- ``vastorbit.plot`` - Visualization library
- ``vastorbit.sql`` - SQL execution utilities
- ``vastorbit.stats`` - Statistical functions

**Supported Platforms:**

- Python 3.12+
- Linux and macOS
- VAST Database 5.0.0-sp10 or later

**Example Usage:**

.. code-block:: python

    import vastorbit as vo
    
    # Connect to VAST Database
    vo.new_connection({
        'host': 'vast-cluster.com',
        'catalog': 'vast_catalog'
    })
    
    # Query data
    vdf = vo.VastFrame('sales_data')
    
    # Data preparation - all in VAST
    vdf = vdf.fillna({'revenue': 0})
    vdf = vdf.drop_duplicates()
    
    # Explore with charts
    vdf['revenue'].hist(nbins=20)
    vdf.scatter(['sales', 'revenue'])
    
    # Analyze
    summary = vdf.groupby(['region'], ['sum(revenue) AS total'])
    
    # Train ML model
    from vastorbit.machine_learning.vast import RandomForestClassifier
    model = RandomForestClassifier(n_estimators = 4)
    model.fit(vdf, ['feature1', 'feature2'], 'target')
    
    # In-database inference
    predictions = model.predict(vdf)

____

Key Capabilities
----------------

**In-Database Data Preparation:**

 - |check| Clean and transform data directly in VAST  
 - |check| Handle missing values, outliers, duplicates  
 - |check| Feature engineering at any scale  
 - |check| Statistical profiling and validation  

**Interactive Exploration:**

 - |check| Generate charts with intelligent sampling  
 - |check| Analyze distributions and correlations  
 - |check| Discover patterns and anomalies  
 - |check| Visualize billions of rows instantly  

**Multi-Source Analytics:**

 - |check| Query VAST tables and files  
 - |check| Access external databases (PostgreSQL, MySQL, MongoDB)  
 - |check| Join across sources  
 - |check| Unified Python API  

**In-Database ML:**

 - |check| 10 embedded algorithms ready to use  
 - |check| Import sklearn models  
 - |check| In-database inference in VAST  
 - |check| Production-scale scoring  

____

Beta Limitations
----------------

As a beta release:

- API may change before 1.0.0
- Documentation actively expanding
- Some advanced features in development
- Feedback welcome for improvements

____

Getting Started
---------------

**Installation:**

.. code-block:: bash

    pip install vastorbit

**Documentation:**

- :ref:`getting_started` - Installation and setup
- :ref:`user_guide` - Data preparation and analytics
- :ref:`chart_gallery` - Visualization examples
- :ref:`api.machine_learning` - ML workflows
- :ref:`api` - Complete API reference
- :ref:`examples` - Hands-on tutorials

**Support:**

- Slack: `vastsupport.slack.com <https://vastsupport.slack.com>`__
- GitHub: https://github.com/vastdata-dev/vastorbit

____

Roadmap to 1.0.0
----------------

**Production Release Plans:**

- API stabilization based on beta feedback
- Expanded documentation and tutorials
- Additional ML algorithms
- Enhanced data preparation functions
- Advanced visualization capabilities
- Performance optimizations
- Production hardening

We're excited to hear your feedback as we work toward 1.0.0!

____

Thank You
---------

Thank you for being an early adopter of VAST Orbit. Your feedback shapes the future of data science on VAST Database.

**Get Involved:**

- Report issues on GitHub
- Join discussions on Slack
- Share your use cases
- Contribute ideas for new features

Happy analyzing with VAST! |i-start|