.. _api.sql.geospatial:

==========
Geospatial
==========

Geospatial functions for spatial analysis and geographic data manipulation.

____

Geospatial Functions
--------------------

.. currentmodule:: vastorbit.sql.geo

.. autosummary:: 
   :toctree: api/
   
   coordinate_converter
   intersect
   split_polygon_n

____

Index Functions
---------------

.. currentmodule:: vastorbit.sql.geo

.. autosummary:: 
   :toctree: api/
   
   create_index
   describe_index
   rename_index

____

Import/Export
-------------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/
   
   read_shp

**VastFrame Methods:**

.. currentmodule:: vastorbit.VastFrame

.. autosummary::
   :toctree: api/
   
   to_geopandas

____

Plotting & Graphics
-------------------

**VastColumn Methods:**

.. currentmodule:: vastorbit.VastColumn

.. autosummary::
   :toctree: api/
   
   geo_plot

____

Generic Functions
-----------------

**VastColumn Methods:**

.. currentmodule:: vastorbit.VastColumn

.. autosummary::
   :toctree: api/
   
   apply