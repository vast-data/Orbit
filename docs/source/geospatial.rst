.. _api.geospatial:

==============
Geospatial
==============

______

Geospatial Functions
--------------------

.. currentmodule:: vastorbit.sql.geo

.. autosummary:: 
   :toctree: api/

   coordinate_converter
   create_index
   describe_index
   intersect
   rename_index
   split_polygon_n

______

Mathematical Functions
----------------------

.. currentmodule:: vastorbit

.. autosummary:: 
   :toctree: api/

   read_shp

.. tab:: VastFrame

   ``VastFrame.func(...)``

   .. currentmodule:: vastorbit.VastFrame

   .. autosummary::
      :toctree: api/

      to_geopandas

______

Plotting & Graphics
-------------------

.. tab:: VastColumn

   ``VastFrame[].func(...)``

   .. currentmodule:: vastorbit.VastColumn

   .. autosummary::
      :toctree: api/

      geo_plot

______

Generic Functions
-----------------

.. tab:: VastColumn

   ``VastFrame[].func(...)``

   .. currentmodule:: vastorbit.VastColumn

   .. autosummary::
      :toctree: api/

      apply