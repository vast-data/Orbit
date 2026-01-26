.. _user_guide:

============
User Guide
============

.. include:: logo_include.rst

.. raw:: html

    <div style="text-align: center; margin: 30px 0;">
        <div style="font-size: 24px; font-weight: 600; color: #2F71BD; margin-bottom: 10px;">
            Complete Guide to VastOrbit
        </div>
        <div style="font-size: 16px; color: #666;">
            From data ingestion to machine learning at scale
        </div>
    </div>

Welcome to the VastOrbit User Guide! This comprehensive tutorial series takes you from basics to advanced topics, teaching you how to leverage VAST Data Platform for data science at scale.

**What You'll Learn:**

- Connect to VAST DataBase and query data across multiple sources
- Perform in-database analytics without moving data
- Build hybrid ML workflows with sklearn/Spark
- Create interactive visualizations with federated queries
- Deploy production-ready data pipelines

.. tip::
   
   **New Users**: Start with **Introduction** to understand VastOrbit fundamentals, then progress through each section sequentially. Each guide includes hands-on examples you can run immediately.

____

Learning Path
-------------

Follow this structured path to master VastOrbit. Total time: ~4.5 hours.

.. grid:: 1 1 2 2
    :gutter: 3

    .. grid-item::
    
      .. card:: 📚 1. Introduction
          :link: user_guide.introduction
          :link-type: ref
          :text-align: center
          :class-card: custom-card-8
          :class-footer: user_guide_footer
          
          ⏱️ **36 minutes**
          
          +++
          
          Master VastOrbit fundamentals including **VastFrame** (pandas-like API) and **VastColumn** operations. Learn how to connect to VAST DataBase and execute your first queries.
          
          **Key Topics:**
          
          - Connection setup and authentication
          - VastFrame creation and basic operations  
          - Column selection and filtering
          - Lazy evaluation and query optimization
          
          :bdg-primary:`VastFrame` :bdg-primary:`VastColumn` :bdg-primary:`Connections`
          
          +++
          Start Learning →

    .. grid-item::
    
      .. card:: 📥 2. Data Ingestion
          :link: user_guide.data_ingestion
          :link-type: ref
          :text-align: center
          :class-card: custom-card-8
          :class-footer: user_guide_footer
          
          ⏱️ **20 minutes**
          
          +++
          
          Load data from multiple sources into VAST DataBase. Query files directly (Parquet, CSV, JSON) without loading. Access external databases via Trino's federated queries.
          
          **Key Topics:**
          
          - Loading from VAST tables
          - Querying files in S3/DataStore
          - Importing from PostgreSQL, MongoDB
          - Streaming data from Kafka
          
          :bdg-primary:`ETL` :bdg-primary:`Data Loading` :bdg-primary:`Federated Queries`
          
          +++
          Start Learning →

    .. grid-item::
    
      .. card:: 🔍 3. Data Exploration
          :link: user_guide.data_exploration
          :link-type: ref
          :text-align: center
          :class-card: custom-card-8
          :class-footer: user_guide_footer
          
          ⏱️ **34 minutes**
          
          +++
          
          Discover patterns and insights through interactive visualizations. Create charts that execute in-database with automatic sampling for large datasets.
          
          **Key Topics:**
          
          - Descriptive statistics and profiling
          - Interactive plotting (Plotly, Highcharts)
          - Correlation analysis
          - Distribution visualization
          
          :bdg-primary:`Visualization` :bdg-primary:`EDA` :bdg-primary:`Charts`
          
          +++
          Start Learning →

    .. grid-item::
    
      .. card:: 🛠️ 4. Data Preparation
          :link: user_guide.data_preparation
          :link-type: ref
          :text-align: center
          :class-card: custom-card-8
          :class-footer: user_guide_footer
          
          ⏱️ **52 minutes**
          
          +++
          
          Transform raw data into analysis-ready datasets. All operations execute in-database for maximum performance on large datasets.
          
          **Key Topics:**
          
          - Data cleaning and missing value handling
          - Feature engineering and transformation
          - Aggregation and pivoting
          - Window functions and time-series ops
          
          :bdg-primary:`Data Cleaning` :bdg-primary:`Feature Engineering` :bdg-primary:`Transformations`
          
          +++
          Start Learning →

    .. grid-item::
    
      .. card:: 🤖 5. Machine Learning
          :link: user_guide.machine_learning
          :link-type: ref
          :text-align: center
          :class-card: custom-card-8
          :class-footer: user_guide_footer
          
          ⏱️ **38 minutes**
          
          +++
          
          Build hybrid ML workflows: train models with sklearn/Spark, deploy for blazing-fast in-database inference. Scale to billions of rows without data movement.
          
          **Key Topics:**
          
          - Training with sklearn and Spark
          - In-database inference at scale
          - Model evaluation and metrics
          - Hyperparameter tuning
          
          :bdg-primary:`Machine Learning` :bdg-primary:`sklearn` :bdg-primary:`Spark MLlib`
          
          +++
          Start Learning →

    .. grid-item::
    
      .. card:: 🚀 6. Full Stack
          :link: user_guide.full_stack
          :link-type: ref
          :text-align: center
          :class-card: custom-card-8
          :class-footer: user_guide_footer
          
          ⏱️ **87 minutes**
          
          +++
          
          Advanced topics for production deployments. User-defined functions, geospatial analysis, streaming pipelines, and integration with the broader data ecosystem.
          
          **Key Topics:**
          
          - User-defined functions (UDFs)
          - Geospatial analytics with GeoPandas
          - Real-time streaming with Kafka
          - Production deployment patterns
          
          :bdg-primary:`UDFs` :bdg-primary:`GeoPandas` :bdg-primary:`Production` :bdg-primary:`Advanced`
          
          +++
          Start Learning →

____

Quick Navigation
----------------

**By Topic:**

.. grid:: 2 2 3 3
    :gutter: 2

    .. grid-item::
    
        **Data Access**
        
        - :ref:`user_guide.introduction` - Connections
        - :ref:`user_guide.data_ingestion` - Loading data
        
    .. grid-item::
    
        **Analysis**
        
        - :ref:`user_guide.data_exploration` - Visualization
        - :ref:`user_guide.data_preparation` - Transformations
        
    .. grid-item::
    
        **Advanced**
        
        - :ref:`user_guide.machine_learning` - ML workflows
        - :ref:`user_guide.full_stack` - Production patterns

**Prerequisites:**

- Basic Python knowledge (pandas familiarity helpful)
- Access to a VAST Cluster (5.0.0-sp10+)
- Python 3.12+ installed
- Familiarity with SQL concepts (helpful but not required)

**Format:**

Each guide includes:

✓ **Hands-on Examples** - Copy-paste code that runs immediately  
✓ **Best Practices** - Production-ready patterns  
✓ **Common Pitfalls** - What to avoid and why  
✓ **Performance Tips** - Optimize queries for VAST  

____

Example: Your First VastOrbit Query
------------------------------------

Here's a taste of what you'll learn:

.. code-block:: python

    import vastorbit as vo
    
    # 1. Connect to VAST
    vo.new_connection({
        'host': 'vast-cluster.example.com',
        'port': 8080,
        'catalog': 'vast_catalog'
    })
    
    # 2. Load data (from VAST table or S3 file)
    customers = vo.VastFrame('customers')
    transactions = vo.VastFrame.from_parquet('s3://data-lake/transactions/')
    
    # 3. Analyze with pandas-like syntax (executes in VAST!)
    result = customers.join(transactions, on='customer_id')
    summary = result.groupby('region').agg({
        'revenue': 'sum',
        'customer_count': 'count'
    })
    
    # 4. Visualize
    summary.bar(columns=['region', 'revenue'])

**What makes this special?**

- 🚀 All operations execute **in-database** - no data movement
- 🌐 **Federated query** - join VAST table + S3 file seamlessly  
- 📊 **Smart sampling** - visualizations work on billions of rows
- ⚡ **VAST SQL Engine** - coming soon for 10-100x performance boost

.. seealso::

   - :ref:`getting_started` - Installation and setup
   - :ref:`api` - Complete API reference
   - :ref:`examples` - More code examples
   - :ref:`chart_gallery` - Visualization gallery

.. note::

   **Questions?** Join our community at **vastsupport.slack.com** or check the :ref:`api` for detailed documentation.

____

Continue Learning
-----------------

Ready to start? Begin with the **Introduction** guide:

.. button-ref:: user_guide.introduction
    :color: primary
    :outline:
    
    Start with Introduction →

Or jump to a specific topic that interests you!

.. toctree::
  :hidden:
  :maxdepth: 1
  
  user_guide_introduction
  user_guide_data_ingestion
  user_guide_data_exploration
  user_guide_data_preparation
  user_guide_machine_learning
  user_guide_full_stack