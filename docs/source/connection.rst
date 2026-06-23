.. _connection:

=============
Connection
=============

.. include:: logo_include.rst

**Connecting to VAST Data Platform with VAST Orbit**

VAST Orbit connects to the VAST Data Platform through Trino today, a powerful distributed SQL query engine (VAST's own engine is coming). This connection unlocks access to VAST DataBase tables, data lake files, and any other Trino-supported data source - all through one unified Python API.

.. important::

   In the following sections, placeholders like ``your_host``, ``your_catalog``, ``your_schema``, etc. will be used. Replace them with your actual VAST cluster and Trino connection details.

Connection Overview
-------------------

Today, VAST Orbit reaches your data through **Trino**, and that is what gives a single
Python session reach across so many systems at once. (VAST's own query engine is on
the way and will become the default; because the API stays the same, none of the code
on this page changes when it does.) Through Trino it can read tables in
VAST's unified transactional and analytical database, query Parquet, CSV, and JSON
files sitting in S3 or the VAST DataStore, connect to external databases such as
PostgreSQL, MySQL, and MongoDB (and thirty-plus other sources), tap streaming topics
in Kafka or Pulsar, and address any other catalog configured in Trino.

In practice that federation means you can query VAST tables and S3 files in the same
piece of code, join data across several databases without building an ETL pipeline
first, work with live and historical data side by side, and do all of it with the
familiar pandas-like syntax VAST Orbit provides — the connection details below are
the only setup that stands between you and that.

.. note::

   VAST Orbit uses the `trino-python-client <https://github.com/trinodb/trino-python-client>`__ under the hood, providing full access to Trino's capabilities.

Quick Start Connection
----------------------

The simplest way to connect:

.. code-block:: python

   import vastorbit as vo

   # Connect to VAST via Trino
   vo.new_connection({
       'host': 'your-vast-cluster.com',
       'port': 8080,  # Default Trino port
       'catalog': 'vast_catalog',  # Your VAST catalog name
       'schema': 'your_schema',     # Default schema
       'user': 'your_username'
   })

   # Verify connection
   print(vo.current_connection())

That's it! You're now connected and can query VAST DataBase, files, and any configured Trino catalogs.

Trino Connection Parameters
----------------------------

Complete list of connection options:

+------------------------+--------------------------------------------------------------------+
| Parameter              | Description                                                        |
+========================+====================================================================+
| host                   | Trino coordinator hostname or IP address                           |
|                        | **Required**                                                       |
+------------------------+--------------------------------------------------------------------+
| port                   | Trino coordinator port                                             |
|                        | Default: 8080                                                      |
+------------------------+--------------------------------------------------------------------+
| user                   | Username for authentication                                        |
|                        | Default: OS login username                                         |
+------------------------+--------------------------------------------------------------------+
| catalog                | Default catalog to use (e.g., 'vast_catalog', 'hive')              |
|                        | Can be changed per query                                           |
+------------------------+--------------------------------------------------------------------+
| schema                 | Default schema within the catalog                                  |
|                        | Optional, can be specified in table names                          |
+------------------------+--------------------------------------------------------------------+
| http_scheme            | 'http' or 'https'                                                  |
|                        | Default: 'http'                                                    |
+------------------------+--------------------------------------------------------------------+
| auth                   | Authentication method: None, BasicAuthentication,                  |
|                        | JWTAuthentication, KerberosAuthentication, etc.                    |
|                        | Default: None                                                      |
+------------------------+--------------------------------------------------------------------+
| session_properties     | Dictionary of Trino session properties for query optimization      |
|                        | Example: {'query_max_memory': '10GB'}                              |
+------------------------+--------------------------------------------------------------------+
| source                 | Application name for query tracking                                |
|                        | Default: 'vastorbit'                                               |
+------------------------+--------------------------------------------------------------------+
| max_attempts           | Number of retry attempts for failed queries                        |
|                        | Default: 3                                                         |
+------------------------+--------------------------------------------------------------------+
| request_timeout        | HTTP request timeout in seconds                                    |
|                        | Default: 30                                                        |
+------------------------+--------------------------------------------------------------------+

Connection Methods
------------------

.. tab-set::

   .. tab-item:: Method 1: new_connection (Recommended)

      Create and automatically set an active connection:

      .. code-block:: python

         import vastorbit as vo

         conn_info = {
             'host': 'vast-prod.example.com',
             'port': 8080,
             'catalog': 'vast_catalog',
             'schema': 'analytics',
             'user': 'data_scientist',
             'http_scheme': 'https',
             'session_properties': {
                 'query_max_memory': '50GB',
                 'query_max_execution_time': '1h'
             }
         }

         vo.new_connection(conn_info)

      This connection is now active for all VAST Orbit operations.

   .. tab-item:: Method 2: Environment Variables

      Store connection details in environment variables for security:

      .. code-block:: bash

         # In your shell or .env file
         export TRINO_HOST="vast-cluster.example.com"
         export TRINO_PORT="8080"
         export TRINO_CATALOG="vast_catalog"
         export TRINO_SCHEMA="analytics"
         export TRINO_USER="data_scientist"

      .. code-block:: python

         import vastorbit as vo
         import os

         vo.new_connection({
             'host': os.getenv('TRINO_HOST'),
             'port': int(os.getenv('TRINO_PORT', 8080)),
             'catalog': os.getenv('TRINO_CATALOG'),
             'schema': os.getenv('TRINO_SCHEMA'),
             'user': os.getenv('TRINO_USER')
         })

   .. tab-item:: Method 3: Direct Trino Client

      For advanced use cases, create the Trino connection directly:

      .. code-block:: python

         import vastorbit as vo
         from trino.dbapi import connect

         # Create Trino connection
         conn = connect(
             host='vast-cluster.example.com',
             port=8080,
             user='data_scientist',
             catalog='vast_catalog',
             schema='analytics',
             http_scheme='https'
         )

         # Set as VAST Orbit connection
         vo.set_connection(conn)

Authentication
--------------

Basic Authentication
^^^^^^^^^^^^^^^^^^^^

Username and password:

.. code-block:: python

   import vastorbit as vo
   from trino.auth import BasicAuthentication

   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',
       'user': 'username',
       'http_scheme': 'https',  # HTTPS required for BasicAuth
       'auth': BasicAuthentication('username', 'password')
   })

JWT Token Authentication
^^^^^^^^^^^^^^^^^^^^^^^^

Token-based authentication:

.. code-block:: python

   import vastorbit as vo
   from trino.auth import JWTAuthentication

   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',
       'user': 'username',
       'http_scheme': 'https',
       'auth': JWTAuthentication('your_jwt_token')
   })

Kerberos Authentication
^^^^^^^^^^^^^^^^^^^^^^^

Enterprise SSO:

.. code-block:: python

   import vastorbit as vo
   from trino.auth import KerberosAuthentication

   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',
       'user': 'username',
       'http_scheme': 'https',
       'auth': KerberosAuthentication(
           service_name='trino',
           hostname_override='vast-cluster.example.com'
       )
   })

Multi-Catalog Access
--------------------

VAST Orbit's power comes from accessing multiple catalogs (data sources) through Trino.

Setting Up Catalogs
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import vastorbit as vo

   # Connect with default catalog
   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',  # Default
       'schema': 'analytics'
   })

   # Query VAST DataBase (default catalog)
   vast_data = vo.VastFrame('customer_transactions')

   # Query Hive/S3 files (different catalog)
   files_data = vo.VastFrame('hive.default.parquet_files')

   # Query PostgreSQL (another catalog)
   pg_data = vo.VastFrame('postgresql.public.users')

   # Join across catalogs!
   result = vast_data.join(
       files_data,
       on='transaction_id',
       how='inner'
   )

Catalog Examples
^^^^^^^^^^^^^^^^

**VAST DataBase:**

.. code-block:: python

   vdf = vo.VastFrame('vast_catalog.analytics.sales')

**Hive/S3 Files:**

.. code-block:: python

   vdf = vo.VastFrame('hive.default.events')  # Points to S3 Parquet files

**PostgreSQL:**

.. code-block:: python

   vdf = vo.VastFrame('postgresql.public.customers')

**MongoDB:**

.. code-block:: python

   vdf = vo.VastFrame('mongodb.production.user_profiles')

**Kafka Stream:**

.. code-block:: python

   vdf = vo.VastFrame('kafka.default.clickstream')

Session Properties
------------------

Optimize Trino query execution with session properties:

Memory Settings
^^^^^^^^^^^^^^^

.. code-block:: python

   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',
       'session_properties': {
           # Total memory per query
           'query_max_memory': '100GB',
           # Memory per node
           'query_max_memory_per_node': '20GB',
           # Enable spill to disk if needed
           'spill_enabled': 'true'
       }
   })

Execution Settings
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   session_properties = {
       # Maximum query runtime
       'query_max_execution_time': '2h',
       'query_max_run_time': '3h',
       
       # Join optimization
       'join_distribution_type': 'AUTOMATIC',
       'join_reordering_strategy': 'AUTOMATIC',
       
       # Parallel execution
       'task_concurrency': 16,
       'task_writer_count': 4,
       
       # Enable adaptive query execution
       'adaptive_partial_aggregation': 'true'
   }

VAST-Specific Optimizations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   session_properties = {
       # Pushdown filters to VAST
       'pushdown_filter_enabled': 'true',
       
       # Use VAST's columnar format optimizations
       'orc_use_column_names': 'true',
       
       # Optimize for VAST's storage
       'task_max_writer_count': 8
   }

Connection Management
---------------------

Checking Connection Status
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import vastorbit as vo

   # Get current connection info
   current = vo.current_connection()
   print(f"Connected to: {current}")

   # Check if connected
   if vo.is_connected():
       print("Active connection exists")

Switching Connections
^^^^^^^^^^^^^^^^^^^^^

Work with multiple VAST clusters or environments:

.. code-block:: python

   # Production
   prod = {
       'host': 'vast-prod.example.com',
       'port': 8080,
       'catalog': 'vast_catalog'
   }

   # Development
   dev = {
       'host': 'vast-dev.example.com',
       'port': 8080,
       'catalog': 'vast_catalog'
   }

   # Switch to production
   vo.new_connection(prod)
   # ... do production work ...

   # Switch to development
   vo.new_connection(dev)
   # ... do development work ...

Closing Connections
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Close current connection
   vo.close_connection()

.. important::

   Always close connections when done to free resources on the Trino cluster.

File Access Configuration
--------------------------

Querying Files via Hive Metastore
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To query Parquet, CSV, or JSON files, configure Hive catalog in Trino:

.. code-block:: python

   import vastorbit as vo

   # Connect to Trino
   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'hive',  # Hive catalog for file access
       'schema': 'default'
   })

   # Parquet is read in place: it's exposed through the hive catalog, so you just
   # reference it as a table (catalog.schema.table — the bucket is sometimes part
   # of it). Trino federation reads the files directly; there is no load step.
   vdf = vo.VastFrame('hive.default.events')

   # CSV and JSON files that need ingesting use the read_* helpers
   vdf = vo.read_csv('s3://bucket/data.csv')
   vdf = vo.read_json('s3://bucket/data.json')

Direct File Querying
^^^^^^^^^^^^^^^^^^^^

Create external tables on-the-fly:

.. code-block:: python

   # Point a VastFrame at the location exposed in the hive catalog and query it
   # directly — catalog.schema.table, no temp table to manage yourself.
   vdf = vo.VastFrame('hive.temp.sales_2024')

Troubleshooting
---------------

Common Issues
^^^^^^^^^^^^^

**Connection Refused**

.. code-block:: python

   # Check Trino is running and accessible
   # Verify host and port are correct
   # Ensure network connectivity

   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,  # Verify this is correct
       'catalog': 'vast_catalog',
       'request_timeout': 60  # Increase timeout
   })

**Authentication Failures**

.. code-block:: python

   # Ensure HTTPS for BasicAuth
   from trino.auth import BasicAuthentication

   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',
       'http_scheme': 'https',  # Required!
       'auth': BasicAuthentication('user', 'pass')
   })

**Catalog Not Found**

.. code-block:: python

   # List available catalogs
   catalogs = vo.sql("SHOW CATALOGS")
   print(catalogs)

   # Use correct catalog name
   vo.new_connection({
       'catalog': 'vast_catalog'  # Must match SHOW CATALOGS output
   })

**Slow Queries**

.. code-block:: python

   # Increase memory and optimize settings
   vo.new_connection({
       'host': 'vast-cluster.example.com',
       'port': 8080,
       'catalog': 'vast_catalog',
       'session_properties': {
           'query_max_memory': '100GB',
           'join_distribution_type': 'PARTITIONED',
           'task_concurrency': 32
       }
   })

Testing Connection
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import vastorbit as vo

   try:
       vo.new_connection(conn_info)
       
       # Simple test query
       result = vo.sql("SELECT 'Connection successful!' AS status")
       print(result)
       
       # List available schemas
       schemas = vo.sql("SHOW SCHEMAS")
       print(f"Available schemas: {schemas}")
       
   except Exception as e:
       print(f"Connection failed: {e}")

Best Practices
--------------

1. **Use Environment Variables**: Never hard-code credentials
2. **Enable HTTPS**: Always use encrypted connections in production
3. **Set Timeouts**: Configure appropriate timeouts for your workload
4. **Optimize Sessions**: Tune memory and concurrency for your queries
5. **Close Connections**: Always close when done
6. **Test in Dev**: Validate connections before production deployment
7. **Monitor Performance**: Use Trino UI to monitor query execution

Production Example
------------------

Complete production-ready connection setup:

.. code-block:: python

   import vastorbit as vo
   from trino.auth import BasicAuthentication
   import os

   # Load from environment
   conn_config = {
       'host': os.getenv('TRINO_HOST'),
       'port': int(os.getenv('TRINO_PORT', 8080)),
       'catalog': os.getenv('TRINO_CATALOG', 'vast_catalog'),
       'schema': os.getenv('TRINO_SCHEMA', 'default'),
       'user': os.getenv('TRINO_USER'),
       'http_scheme': 'https',
       'auth': BasicAuthentication(
           os.getenv('TRINO_USER'),
           os.getenv('TRINO_PASSWORD')
       ),
       'session_properties': {
           'query_max_memory': '100GB',
           'query_max_execution_time': '2h',
           'join_distribution_type': 'AUTOMATIC',
           'task_concurrency': 16
       },
       'request_timeout': 60,
       'source': 'vastorbit_production'
   }

   # Connect
   try:
       vo.new_connection(conn_config)
       print(f"Connected to: {vo.current_connection()}")
   except Exception as e:
       print(f"✗ Connection failed: {e}")
       raise

Conclusion
----------

With a connection in place, VAST Orbit can query VAST DataBase tables, read data-lake
files directly, join across multiple sources in a single query, and let you do all of
it with familiar Python. That is the whole point of connecting through Trino: one
session, every source, no data movement. From here you are ready to explore the full
power of VAST Orbit for federated analytics and AI development.

.. seealso::

   - :ref:`getting_started` - Quick start guide
   - :ref:`user_guide` - VastFrame operations and federated queries
   - `Trino Documentation <https://trino.io/docs/current/>`__ - Trino reference
   - `VAST Data Platform <https://www.vastdata.com/platform/database>`__ - VAST overview