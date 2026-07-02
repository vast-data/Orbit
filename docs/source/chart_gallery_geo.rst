:orphan:

.. _chart_gallery.geo:

================
Geospatial Plots
================

.. Necessary Code Elements

.. ipython:: python
    :suppress:

    import vastorbit as vo
    import vastorbit.datasets as vod

    world = vod.load_world()

    # We filter to select only the African continent
    africa = world[world["continent"] == "Africa"]

    # This dataset provides multiple scores of students in Africa.
    africa_education = vod.load_africa_education()


General
-------

Let's begin by importing the dataset module of ``vastorbit``. It provides a range of datasets for both training and exploring vastorbit's capabilities.

.. ipython:: python

    import vastorbit.datasets as vod

Let's utilize the World dataset to demonstrate geospatial capabilities.

.. code-block:: python
    
    import vastorbit.datasets as vod

    world = vod.load_world()

    # We filter to select only the African continent
    africa = world[world["continent"] == "Africa"]

Let's use Africa Education dataset from the vastorbit datasets. 
Data is also available `here <https://github.com/vast-data/Orbit/blob/main/assets/data/understand/africa_education/students.csv>`__.

.. code-block:: python
    
    import vastorbit as vo

    # This dataset provides multiple scores of students in Africa.
    africa_education = vod.load_africa_education()

vastorbit provides the option to create various types of geospatial plots, including scatter plots and heat maps. To leverage these capabilities, it's important to have geospatial data stored within VAST, specifically in either GEOMETRY or GEOGRAPHY data types. This data forms the foundation for generating insightful geospatial visualizations using vastorbit.

.. note::
    
    Currently, vastorbit provides geospatial capabilities using Matplotlib and Geopandas. We plan to expand these functionalities in the future by incorporating Plotly.

.. ipython:: python
    :suppress:

    import vastorbit as vo
            
.. tab:: Matplotlib

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "matplotlib")

    We can switch to using the ``matplotlib`` module.

    .. code-block:: python
        
        vo.set_option("plotting_lib", "matplotlib")

    vastorbit offers a range of geospatial plots, including scatter plots for visualizing individual data points on a map, heat maps for displaying data density, and choropleth maps that shade regions based on variable values. These plots enable data analysts to gain actionable insights from geospatial data, whether it's for understanding point distributions, identifying hotspots, or visualizing regional trends, making vastorbit a valuable tool for location-based analysis and data-driven decision-making.

    .. tab:: Regular

      .. ipython:: python
          :okwarning:

          @savefig plotting_matplotlib_geo_regular.png
          africa["geometry"].geo_plot(edgecolor = "black", color = "white")

    .. tab:: CMAP

      .. ipython:: python
          :okwarning:

          @savefig plotting_matplotlib_geo_cmap.png
          africa["geometry"].geo_plot(edgecolor = "black", column = "pop_est")

    .. tab:: Scatter

      .. ipython:: python
          :okwarning:

          ax = africa["geometry"].geo_plot(color = "white", edgecolor = "black")
          @savefig plotting_matplotlib_geo_scatter.png
          africa_education.scatter(
            columns = ["lon", "lat"], 
            by = "country_long",
            ax = ax,
          )

    .. tab:: Bubble

      .. ipython:: python
          :okwarning:

          ax = africa["geometry"].geo_plot(color = "white", edgecolor = "black")
          @savefig plotting_matplotlib_geo_bubble.png
          africa_education.scatter(
            columns = ["lon", "lat"],
            size = "zmalocp",
            by = "country_long",
            ax = ax,
          )

___________________


Chart Customization
-------------------

vastorbit empowers users with a high degree of flexibility when it comes to tailoring the visual aspects of their plots. 
This customization extends to essential elements such as **color schemes**, **text labels**, and **plot sizes**, as well as a wide range of other attributes that can be fine-tuned to align with specific design preferences and analytical requirements. Whether you want to make your visualizations more visually appealing or need to convey specific insights with precision, vastorbit's customization options enable you to craft graphics that suit your exact needs.

.. note:: As geospatial plots encompass various chart types such as heatmaps and scatter plots, customization options vary between graphics. To tailor your visualization, please refer to the corresponding :ref:`chart_gallery` for specific guidance on customization.

.. ipython:: python
   :suppress:

   from vastorbit._utils._sql._sys import purge_memory
   purge_memory()