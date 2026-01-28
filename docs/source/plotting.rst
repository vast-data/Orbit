.. _api.plotting:

========
Plotting
========

Plotting base classes and configuration for VastOrbit visualizations.

For detailed plotting guides and examples, see :ref:`chart_gallery.guide`.

____

Base
----

.. currentmodule:: vastorbit.plotting.base

.. autosummary:: 
   :toctree: api/
   
   PlottingBase

**Methods:**

.. currentmodule:: vastorbit.plotting.base

.. autosummary:: 
   :toctree: api/
   
   PlottingBase.get_cmap
   PlottingBase.get_colors

____

SQL
---

.. currentmodule:: vastorbit.plotting.sql

.. autosummary:: 
   :toctree: api/
   
   PlottingBaseSQL

____

Switching Libraries
-------------------

**Plotly:**

.. code-block:: python

   vastorbit.set_option("plotting_lib", "plotly")

**Matplotlib:**

.. code-block:: python

   vastorbit.set_option("plotting_lib", "matplotlib")

**Highcharts:**

.. code-block:: python

   vastorbit.set_option("plotting_lib", "highcharts")