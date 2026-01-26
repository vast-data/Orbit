.. _api.sql.geospatial:

==============
Geospatial
==============

______

Geospatial Functions
--------------------------

.. currentmodule:: vastorbit.sql.geo

.. autosummary:: 
   :toctree: api/

   coordinate_converter
   intersect
   split_polygon_n


_____

Index Functions
--------------------------

.. currentmodule:: vastorbit.sql.geo

.. autosummary:: 
   :toctree: api/

   create_index
   describe_index
   rename_index



______

Import/Export
--------------

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

Plotting & Graohics
------------------------


.. tab:: VastColumn

   ``VastFrame[].func(...)``

   .. currentmodule:: vastorbit.VastColumn

   .. autosummary::
      :toctree: 

      geo_plot

______

Generic Functions
------------------------


.. tab:: VastColumn

   ``VastFrame[].func(...)``

   .. currentmodule:: vastorbit.VastColumn

   .. autosummary::
      :toctree: 

      apply