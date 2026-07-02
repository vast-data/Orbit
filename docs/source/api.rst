.. _api:

=============
API Reference
=============

.. include:: logo_include.rst

.. raw:: html

    <div style="text-align: center; margin: 10px 0;">
        <div style="font-size: 24px; font-weight: 600; color: #2F71BD; margin-bottom: 10px;">
            VAST Orbit API Documentation
        </div>
        <div style="font-size: 16px; color: #666;">
            Version 0.1.x
        </div>
    </div>

Welcome to the VAST Orbit API Reference. This comprehensive guide covers all public objects, functions, and methods available in VAST Orbit for data science at scale on the VAST AI OS.

.. tip::
   
   **New to VAST Orbit?** Start with :ref:`getting_started` for installation and quick examples, then explore the :ref:`user_guide` for in-depth tutorials.

____

Core Components
---------------

Essential modules for connecting to VAST and working with data.

.. grid:: 2 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item::
    
      .. card:: |i-connect| Connection
          :link: api.connect
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          :class-footer: user_guide_footer
          
          Connect to VAST DataBase. Manage connections, catalogs, and authentication.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-frame| VastFrame
          :link: api.vastframe
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          :class-footer: user_guide_footer
          
          The main data structure - pandas-like API for VAST DataBase. 400+ functions for data manipulation.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-files| Parsers
          :link: api.parsers
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          :class-footer: user_guide_footer
          
          Load data from files (Parquet, CSV, JSON), databases, and streaming sources into VAST.
          
          +++
          View Documentation →

____

Machine Learning & Analytics
-----------------------------

Tools for building, training, and deploying ML models at scale.

.. grid:: 2 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item::
    
      .. card:: |i-ml| Machine Learning
          :link: api.machine_learning
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Train models with sklearn/Spark. Deploy for in-database inference. 10 supported algorithms.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-stats| Stats
          :link: api.stats
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Statistical functions for hypothesis testing, distributions, and advanced analytics.
          
          +++
          View Documentation →

____

Visualization & Exploration
----------------------------

Create interactive charts and explore data visually.

.. grid:: 2 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item::
    
      .. card:: |i-charts| Plotting
          :link: api.plotting
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Comprehensive charting library supporting Plotly and Matplotlib backends.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-notebook| Jupyter Extensions
          :link: api.jupyter
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Interactive widgets, magic commands, and enhanced notebook functionality for VAST Orbit.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-datasets| Datasets
          :link: api.datasets
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Built-in sample datasets (Titanic, Iris, Amazon) for learning and testing.
          
          +++
          View Documentation →

____

Data Management
---------------

Utilities for managing data in VAST DataBase.

.. grid:: 2 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item::
    
      .. card:: |i-functions| Utilities
          :link: api.utilities
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Helper functions for data ingestion, schema management, and table operations.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-indb| SQL
          :link: api.sql
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Execute raw SQL queries against VAST DataBase with federated query support.
          
          +++
          View Documentation →

    .. grid-item::
    
      .. card:: |i-sample| TableSample
          :link: api.tablesample
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Work with data samples for exploratory analysis and rapid prototyping.
          
          +++
          View Documentation →

____

Advanced Topics
---------------

.. grid:: 2 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item::
    
      .. card:: |i-error| Error Handling
          :link: api.error
          :link-type: ref
          :text-align: center
          :class-card: custom-card
          
          Exception types and error handling patterns in VAST Orbit.
          
          +++
          View Documentation →

____

Quick Reference
---------------

**Most Used Functions:**

.. code-block:: python

    import vastorbit as vo
    
    # Connection
    vo.new_connection({...})
    vo.current_connection()
    
    # Data Loading
    vdf = vo.VastFrame('table_name')
    vdf = vo.VastFrame('SELECT * FROM ...')
    
    # Analysis
    vdf.describe()
    vdf.agg(func="max", columns)
    vdf.scatter(['x', 'y'])
    
    # Machine Learning
    from vastorbit.machine_learning import RandomForest
    model = RandomForest()
    model.fit(vdf, 'target', ['feature1', 'feature2'])
    predictions = model.predict(vdf)

**Key Modules:**

- ``vastorbit.VastFrame`` - Main data structure
- ``vastorbit.machine_learning`` - ML algorithms
- ``vastorbit.plot`` - Visualization functions
- ``vastorbit.sql`` - SQL execution utilities
- ``vastorbit.stats`` - Statistical functions

.. note::

   **API Stability**: VAST Orbit is currently in pre-release (0.1.x). APIs may change before the 1.0.0 release. After 1.0.0, VAST Orbit will follow semantic versioning with stable public APIs. Breaking changes will be announced in advance and deprecated gradually.

.. seealso::

   - :ref:`getting_started` - Installation and setup guide
   - :ref:`user_guide` - Comprehensive tutorials
   - :ref:`examples` - Hands-on code examples
   - :ref:`chart_gallery` - Visualization gallery

____

Full API Documentation
----------------------

Detailed documentation for every module, class, and function.

.. toctree::
  :maxdepth: 2
  
  connect
  datasets
  error
  geospatial
  jupyter
  machine_learning
  parsers
  plotting
  sql
  stats
  tablesample
  utilities
  vastframe