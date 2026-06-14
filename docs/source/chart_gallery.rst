.. _chart_gallery:

==============
Chart Gallery
==============

.. include:: logo_include.rst

VastOrbit offers an extensive selection of interactive visualizations that play a pivotal role in extracting valuable business insights. These versatile visualization tools empower you to effectively analyze and communicate data trends, enabling informed decision-making and enhancing data-driven strategies.

**Visualization Backends:**

- **Plotly**: Interactive web-based visualizations with hover effects and zoom capabilities
- **Matplotlib**: Publication-quality static plots with extensive customization
- **Graphviz**: Specialized tree and graph visualizations for ML models

.. tip::

   Every chart below is available in **Plotly and Matplotlib**, driven by
   **Python or SQL**, unless a card notes otherwise.

**Key Features:**

✓ **In-Database Execution**: Charts render from VAST DataBase without moving data to Python  
✓ **Smart Sampling**: Automatically samples large datasets for responsive visualizations  
✓ **Federated Queries**: Visualize data from multiple sources (VAST, S3, PostgreSQL) in one chart  
✓ **Export Options**: Save as PNG, SVG, HTML, or interactive web dashboards  

.. note:: 

   For detailed documentation on chart customization, parameters, and advanced examples, 
   see the :ref:`chart_gallery.guide`.

____

Basic Charts
------------

Fundamental visualizations for exploratory data analysis and presentation.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: Area Chart
          :img-top: _static/thumbs/thumb_area.svg
          :link: chart_gallery.area
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Stacked` :bdg-secondary-line:`Fully Stacked`

    .. grid-item::

        .. card:: Bar Chart
          :img-top: _static/thumbs/thumb_bar.svg
          :link: chart_gallery.bar
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`1D` :bdg-secondary-line:`2D` :bdg-secondary-line:`Stacked` :bdg-secondary-line:`Fully Stacked` :bdg-secondary-line:`Negative`

    .. grid-item::

        .. card:: Box Plot
          :img-top: _static/thumbs/thumb_boxplot.svg
          :link: chart_gallery.boxplot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Multi`

    .. grid-item::

        .. card:: Candlestick Chart
          :img-top: _static/thumbs/thumb_candlestick.svg
          :link: chart_gallery.candlestick
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Candlestick`

    .. grid-item::

        .. card:: Contour Plot
          :img-top: _static/thumbs/thumb_contour_plot.svg
          :link: chart_gallery.contour
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Contour`

    .. grid-item::

        .. card:: Correlation Matrix
          :img-top: _static/thumbs/thumb_corr.svg
          :link: chart_gallery.corr
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Matrix` :bdg-secondary-line:`Vector`

    .. grid-item::

        .. card:: Density Plot
          :img-top: _static/thumbs/thumb_density.svg
          :link: chart_gallery.density
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Multi`

    .. grid-item::

        .. card:: Histogram
          :img-top: _static/thumbs/thumb_hist.svg
          :link: chart_gallery.hist
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Multi`

    .. grid-item::

        .. card:: Line Chart
          :img-top: _static/thumbs/thumb_line.svg
          :link: chart_gallery.line
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Multi`

    .. grid-item::

        .. card:: Pie Chart
          :img-top: _static/thumbs/thumb_pie.svg
          :link: chart_gallery.pie
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Regular` :bdg-secondary-line:`Donut` :bdg-secondary-line:`Rose` :bdg-secondary-line:`3D` :bdg-secondary-line:`Nested`

    .. grid-item::

        .. card:: Pivot Table
          :img-top: _static/thumbs/thumb_pivot.svg
          :link: chart_gallery.pivot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Pivot`

    .. grid-item::

        .. card:: Range Plot
          :img-top: _static/thumbs/thumb_range.svg
          :link: chart_gallery.range
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Multi`

    .. grid-item::

        .. card:: Scatter Plot
          :img-top: _static/thumbs/thumb_scatter.svg
          :link: chart_gallery.scatter
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`1D` :bdg-secondary-line:`2D` :bdg-secondary-line:`3D` :bdg-secondary-line:`Bubble`

    .. grid-item::

        .. card:: Spider Chart
          :img-top: _static/thumbs/thumb_spider.svg
          :link: chart_gallery.spider
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Single` :bdg-secondary-line:`Multi`

____

Machine Learning & Analytics
-----------------------------

Advanced visualizations for model evaluation, time-series analysis, and statistical insights.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: ACF / PACF
          :img-top: _static/thumbs/thumb_acf.svg
          :link: chart_gallery.acf
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7

          :bdg-secondary-line:`Bar` :bdg-secondary-line:`Heatmap`

    .. grid-item::

        .. card:: Champion Challenger
          :img-top: _static/thumbs/thumb_champion_challenger.svg
          :link: chart_gallery.champion_challenger
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Model Comparison`

    .. grid-item::

        .. card:: Classification Curves
          :img-top: _static/thumbs/thumb_classification_curve.svg
          :link: chart_gallery.classification_curve
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`ROC` :bdg-secondary-line:`PRC` :bdg-secondary-line:`Lift Chart`

    .. grid-item::

        .. card:: Classification Plot
          :img-top: _static/thumbs/thumb_classification_plot.svg
          :link: chart_gallery.classification_plot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`1D` :bdg-secondary-line:`2D` :bdg-secondary-line:`3D` :bdg-secondary-line:`Logit`

    .. grid-item::

        .. card:: Correlation Analysis
          :img-top: _static/thumbs/thumb_corr.svg
          :link: chart_gallery.corr
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Matrix` :bdg-secondary-line:`Vector`

    .. grid-item::

        .. card:: Learning Curves
          :img-top: _static/thumbs/thumb_learning.svg
          :link: chart_gallery.learning
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Efficiency` :bdg-secondary-line:`Scalability` :bdg-secondary-line:`Performance`

    .. grid-item::

        .. card:: Validation Curves
          :img-top: _static/thumbs/thumb_validation.svg
          :link: chart_gallery.learning
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Efficiency` :bdg-secondary-line:`Scalability` :bdg-secondary-line:`Performance`

    .. grid-item::

        .. card:: Elbow Curve
          :img-top: _static/thumbs/thumb_elbow.svg
          :link: chart_gallery.elbow
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`K-Means` :bdg-secondary-line:`Clustering`

    .. grid-item::

        .. card:: Voronoi Plot
          :img-top: _static/thumbs/thumb_voronoi.svg
          :link: chart_gallery.voronoi_plot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-light:`Matplotlib only`

          :bdg-secondary-line:`K-Means` :bdg-secondary-line:`Clustering`

    .. grid-item::

        .. card:: LOF (Local Outlier Factor)
          :img-top: _static/thumbs/thumb_lof.svg
          :link: chart_gallery.lof
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`1D` :bdg-secondary-line:`2D` :bdg-secondary-line:`3D`

    .. grid-item::

        .. card:: Outlier Detection
          :img-top: _static/thumbs/thumb_outliers.svg
          :link: chart_gallery.outliers
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`1D` :bdg-secondary-line:`2D`

    .. grid-item::

        .. card:: Regression Plot
          :img-top: _static/thumbs/thumb_regression_plot.svg
          :link: chart_gallery.regression_plot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Linear Regression` :bdg-secondary-line:`Random Forest` :bdg-secondary-line:`Residual Plot`

    .. grid-item::

        .. card:: Seasonal Decomposition
          :img-top: _static/thumbs/thumb_seasonal.svg
          :link: chart_gallery.seasonal
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Trend` :bdg-secondary-line:`Seasonal` :bdg-secondary-line:`Residual`

    .. grid-item::

        .. card:: Stepwise Selection
          :img-top: _static/thumbs/thumb_stepwise.svg
          :link: chart_gallery.stepwise
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Forward` :bdg-secondary-line:`Backward`

    .. grid-item::

        .. card:: Decision Tree
          :img-top: _static/thumbs/thumb_tree.svg
          :link: chart_gallery.tree
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-light:`Graphviz`

          :bdg-secondary-line:`Tree Visualization` :bdg-secondary-line:`Rules`

    .. grid-item::

        .. card:: Time-Series Forecasting
          :img-top: _static/thumbs/thumb_time_series.svg
          :link: chart_gallery.tsa
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-secondary-line:`Prediction Plot` :bdg-secondary-line:`Confidence Intervals`

____

Geospatial Visualization
------------------------

Map-based visualizations for location data and geographic analysis.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: Geographic Maps
          :img-top: _static/thumbs/thumb_geo.svg
          :link: chart_gallery.geo
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-light:`Plotly · Matplotlib`

          :bdg-secondary-line:`Choropleth` :bdg-secondary-line:`Scatter` :bdg-secondary-line:`Bubble` :bdg-secondary-line:`Heat Map`

____

Animated Visualizations
-----------------------

Dynamic, time-based visualizations for presentations and storytelling.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: Animated Charts
          :img-top: _static/thumbs/thumb_animated.svg
          :link: chart_gallery.animated
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6 gallery-card
          :class-img-top: custom-class-img-top-7
          
          :bdg-light:`Matplotlib only`

          :bdg-secondary-line:`Bar` :bdg-secondary-line:`Pie` :bdg-secondary-line:`Bubble` :bdg-secondary-line:`Time-Series`

____

Quick Start Examples
--------------------

**Basic Visualization:**

.. code-block:: python

    import vastorbit as vo
    
    # Connect to VAST
    vo.new_connection({
        'host': 'vast-cluster.com',
        'catalog': 'vast_catalog'
    })
    
    # Load data
    vdf = vo.VastFrame('sales_data')
    
    # Create interactive scatter plot
    vdf.scatter(
        columns=['revenue', 'profit'],
        by='region',
        max_nb_points=10000
    )

**Machine Learning Visualization:**

.. code-block:: python

    from vastorbit.machine_learning import LogisticRegression
    
    # Train model
    model = LogisticRegression()
    model.fit(vdf, 'churn', ['age', 'tenure', 'spend'])
    
    # Plot ROC curve
    model.roc_curve()
    
    # Plot classification boundaries
    model.plot_classification()

**Federated Query Visualization:**

.. code-block:: python

    # Query VAST table + S3 file in one visualization
    customers = vo.VastFrame('vast_catalog.customers')
    transactions = vo.VastFrame('hive.s3_bucket.transactions')
    
    # Join and visualize
    result = customers.join(transactions, on='customer_id')
    result.bar(columns=['region', 'total_revenue'])

.. tip::

   All visualizations support:
   
   - **Automatic sampling** for large datasets (configurable via ``max_nb_points``)
   - **Export to HTML** for embedding in reports and dashboards
   - **Interactive legends** for filtering data on-the-fly
   - **Customizable color schemes** to match your brand

For complete API documentation and advanced customization options, visit the :ref:`api` reference.