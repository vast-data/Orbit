.. _whats_new_v0_1_0:

===================
Version 0.1.0 (Beta)
===================

.. include:: logo_include.rst

.. raw:: html

    <div style="text-align: center; margin: 30px 0;">
        <div style="font-size: 24px; font-weight: 600; color: #2F71BD; margin-bottom: 10px;">
            🎉 First Release
        </div>
        <div style="font-size: 16px; color: #666;">
            January 2026 - Beta Release
        </div>
    </div>

Welcome to the first release of **VastOrbit** - the Python API for data science at scale on VAST Data Platform!

.. important::

   **Beta Status**: VastOrbit 0.1.0 is currently in beta. The API may change before the 1.0.0 production release. We welcome your feedback and bug reports at **vastsupport.slack.com**.

____

Release Highlights
------------------

🚀 **First Public Release**

VastOrbit 0.1.0 introduces a comprehensive Python library for data science on VAST Data Platform, bringing pandas-like syntax to petabyte-scale analytics.

**Core Features:**

- **400+ Functions** - Complete data manipulation toolkit
- **Federated Queries** - Query VAST, S3, PostgreSQL, MongoDB in one API  
- **In-Database Execution** - All operations run in VAST DataBase
- **Hybrid ML** - Train with sklearn/Spark, infer in-database
- **Interactive Visualizations** - Plotly, Matplotlib, Highcharts support

____

Query Engine Support
--------------------

**Current: Trino**

VastOrbit 0.1.0 leverages **Trino** as the query engine for federated SQL queries:

✅ Access 30+ data sources through Trino connectors  
✅ Production-ready with full feature support  
✅ Proven at scale with enterprise deployments  
✅ Complete SQL functionality  

**Coming Soon: VAST SQL Query Engine**

Future releases will support the **VAST native SQL Query Engine** for enhanced performance:

⚡ **10-100x performance improvement** over federated engines  
⚡ Direct exploitation of VAST's compressed columnar format  
⚡ Optimized for VAST's DASE architecture  
⚡ **Seamless migration** - same VastOrbit code, dramatically faster execution  

.. tip::

   Your VastOrbit code will work with both Trino and VAST SQL Engine without modification. We're designing for seamless transition as the native engine becomes available.

____

What's Included
---------------

**Core Modules:**

- ``vastorbit.VastFrame`` - pandas-like DataFrame for VAST DataBase
- ``vastorbit.machine_learning`` - 10 ML algorithms for in-database inference
- ``vastorbit.plot`` - Interactive visualization library
- ``vastorbit.sql`` - Direct SQL execution utilities
- ``vastorbit.stats`` - Statistical analysis functions

**Supported Platforms:**

- Python 3.12+
- Linux and macOS
- VAST Cluster 5.0.0-sp10 or later

**Example Usage:**

.. code-block:: python

    import vastorbit as vo
    
    # Connect to VAST via Trino
    vo.new_connection({
        'host': 'vast-cluster.com',
        'catalog': 'vast_catalog'
    })
    
    # Query data
    vdf = vo.VastFrame('sales_data')
    
    # Analyze with pandas-like syntax
    summary = vdf.groupby(['region'], ['sum(revenue) AS total_revenue'])
    
    # Visualize
    summary.bar(['region', 'total_revenue'])

____

Known Limitations
-----------------

As a beta release, please note:

- API may change before 1.0.0 release
- VAST SQL Query Engine not yet available (Trino only)
- Limited to Trino-supported operations
- Documentation is actively being expanded

____

Getting Started
---------------

**Installation:**

.. code-block:: bash

    pip install vastorbit

**Documentation:**

- :ref:`getting_started` - Installation and setup
- :ref:`user_guide` - Comprehensive tutorials
- :ref:`api` - Complete API reference
- :ref:`examples` - Hands-on code examples

**Support:**

- Slack: vastsupport.slack.com
- GitHub: https://github.com/vast-data/vastorbit

____

What's Next
-----------

**Roadmap to 1.0.0:**

- API stabilization based on beta feedback
- VAST SQL Query Engine integration
- Expanded documentation and examples
- Additional ML algorithms
- Performance optimizations
- Production hardening

We're excited to hear your feedback as we work toward the 1.0.0 production release!

____

Thank You
---------

Thank you for being an early adopter of VastOrbit. Your feedback shapes the future of data science on VAST Data Platform.

**Get Involved:**

- Report issues on GitHub
- Join discussions on Slack
- Share your use cases
- Contribute ideas for new features

Happy analyzing! 🚀