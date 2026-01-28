.. _api.sql.utils:

=========
Utilities
=========

Utility functions for creating, managing, and querying database objects.

____

Create New Relations
--------------------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/
   
   create_schema
   create_table

____

Ingest Data
-----------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/
   
   insert_into

See other parsers at :ref:`api.parsers`.

____

Drop Data
---------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/
   
   drop

____

Database Information
--------------------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/
   
   current_session
   username
   does_table_exist
   has_privileges

____

Table Information
-----------------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/
   
   get_data_types
   vast_python_dtype