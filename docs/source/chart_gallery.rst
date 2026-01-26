.. _chart_gallery:

==============
Chart Gallery
==============

.. include:: logo_include.rst

VastOrbit offers an extensive selection of interactive visualizations that play a pivotal role in extracting valuable business insights. These versatile visualization tools empower you to effectively analyze and communicate data trends, enabling informed decision-making and enhancing data-driven strategies.

**Visualization Backends:**

- **Plotly**: Interactive web-based visualizations with hover effects and zoom capabilities
- **Matplotlib**: Publication-quality static plots with extensive customization
- **Highcharts**: Professional interactive charts optimized for business dashboards
- **Graphviz**: Specialized tree and graph visualizations for ML models

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
          :img-top: _static/gif_area.gif
          :link: chart_gallery.area
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Single` :bdg-primary:`Stacked` :bdg-primary:`Fully Stacked`

    .. grid-item::

        .. card:: Bar Chart
          :img-top: _static/gif_bar.gif
          :link: chart_gallery.bar
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`1D` :bdg-primary:`2D` :bdg-primary:`Stacked` :bdg-primary:`Fully Stacked` :bdg-primary:`Negative`

    .. grid-item::

        .. card:: Box Plot
          :img-top: _static/gif_boxplot.gif
          :link: chart_gallery.boxplot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Single` :bdg-primary:`Multi`

    .. grid-item::

        .. card:: Candlestick Chart
          :img-top: _static/gif_candlestick.gif
          :link: chart_gallery.candlestick
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Candlestick`

    .. grid-item::

        .. card:: Contour Plot
          :img-top: _static/gif_contour_plot.gif
          :link: chart_gallery.contour
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Contour`

    .. grid-item::

        .. card:: Correlation Matrix
          :img-top: _static/gif_corr.gif
          :link: chart_gallery.corr
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Matrix` :bdg-primary:`Vector`

    .. grid-item::

        .. card:: Density Plot
          :img-top: _static/gif_density.gif
          :link: chart_gallery.density
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Single` :bdg-primary:`Multi`

    .. grid-item::

        .. card:: Histogram
          :img-top: _static/gif_hist.gif
          :link: chart_gallery.hist
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Single` :bdg-primary:`Multi`

    .. grid-item::

        .. card:: Line Chart
          :img-top: _static/gif_line.gif
          :link: chart_gallery.line
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Single` :bdg-primary:`Multi`

    .. grid-item::

        .. card:: Pie Chart
          :img-top: _static/gif_pie.gif
          :link: chart_gallery.pie
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Regular` :bdg-primary:`Donut` :bdg-primary:`Rose` :bdg-primary:`3D` :bdg-primary:`Nested`

    .. grid-item::

        .. card:: Pivot Table
          :img-top: _static/gif_pivot.gif
          :link: chart_gallery.pivot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Pivot`

    .. grid-item::

        .. card:: Range Plot
          :img-top: _static/gif_range.gif
          :link: chart_gallery.range
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python`

          :bdg-primary:`Single` :bdg-primary:`Multi`

    .. grid-item::

        .. card:: Scatter Plot
          :img-top: _static/gif_scatter.gif
          :link: chart_gallery.scatter
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`1D` :bdg-primary:`2D` :bdg-primary:`3D` :bdg-primary:`Bubble`

    .. grid-item::

        .. card:: Spider Chart
          :img-top: _static/gif_spider.gif
          :link: chart_gallery.spider
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Single` :bdg-primary:`Multi`

____

Machine Learning & Analytics
-----------------------------

Advanced visualizations for model evaluation, time-series analysis, and statistical insights.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: ACF / PACF
          :img-top: _static/gif_acf.gif
          :link: chart_gallery.acf
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7

          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python`
          
          :bdg-primary:`Bar` :bdg-primary:`Heatmap`

    .. grid-item::

        .. card:: Champion Challenger
          :img-top: _static/pic_champion_challenger.png
          :link: chart_gallery.champion_challenger
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python`

          :bdg-primary:`Model Comparison`

    .. grid-item::

        .. card:: Classification Curves
          :img-top: _static/gif_classification_curve.gif
          :link: chart_gallery.classification_curve
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`ROC` :bdg-primary:`PRC` :bdg-primary:`Lift Chart`

    .. grid-item::

        .. card:: Classification Plot
          :img-top: _static/gif_classification_plot.gif
          :link: chart_gallery.classification_plot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python`

          :bdg-primary:`1D` :bdg-primary:`2D` :bdg-primary:`3D` :bdg-primary:`Logit`

    .. grid-item::

        .. card:: Correlation Analysis
          :img-top: _static/gif_corr.gif
          :link: chart_gallery.corr
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` :bdg-warning:`SQL`

          :bdg-primary:`Matrix` :bdg-primary:`Vector`

    .. grid-item::

        .. card:: Learning Curves
          :img-top: _static/gif_learning.gif
          :link: chart_gallery.learning
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Efficiency` :bdg-primary:`Scalability` :bdg-primary:`Performance`

    .. grid-item::

        .. card:: Elbow Curve
          :img-top: _static/pic_elbow.png
          :link: chart_gallery.elbow
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`K-Means` :bdg-primary:`Clustering`

    .. grid-item::

        .. card:: LOF (Local Outlier Factor)
          :img-top: _static/gif_lof.gif
          :link: chart_gallery.lof
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`1D` :bdg-primary:`2D` :bdg-primary:`3D`

    .. grid-item::

        .. card:: Outlier Detection
          :img-top: _static/gif_outliers.gif
          :link: chart_gallery.outliers
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`1D` :bdg-primary:`2D`

    .. grid-item::

        .. card:: Regression Plot
          :img-top: _static/gif_regression_plot.gif
          :link: chart_gallery.regression_plot
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Linear Regression` :bdg-primary:`Random Forest` :bdg-primary:`Residual Plot`

    .. grid-item::

        .. card:: Seasonal Decomposition
          :img-top: _static/pic_seasonal.png
          :link: chart_gallery.seasonal
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Trend` :bdg-primary:`Seasonal` :bdg-primary:`Residual`

    .. grid-item::

        .. card:: Stepwise Selection
          :img-top: _static/gif_stepwise.gif
          :link: chart_gallery.stepwise
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Forward` :bdg-primary:`Backward`

    .. grid-item::

        .. card:: Decision Tree
          :img-top: _static/pic_tree.png
          :link: chart_gallery.tree
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Graphviz`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Tree Visualization` :bdg-primary:`Rules`

    .. grid-item::

        .. card:: Time-Series Forecasting
          :img-top: _static/gif_time_series.gif
          :link: chart_gallery.tsa
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-success-line:`Plotly` :bdg-primary-line:`Matplotlib` :bdg-danger-line:`Highcharts`
          
          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Prediction Plot` :bdg-primary:`Confidence Intervals`

____

Geospatial Visualization
------------------------

Map-based visualizations for location data and geographic analysis.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: Geographic Maps
          :img-top: _static/gif_geo.gif
          :link: chart_gallery.geo
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-primary-line:`Matplotlib`

          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Choropleth` :bdg-primary:`Scatter` :bdg-primary:`Bubble` :bdg-primary:`Heat Map`

____

Animated Visualizations
-----------------------

Dynamic, time-based visualizations for presentations and storytelling.

.. grid:: 2 2 3 3
    :gutter: 3

    .. grid-item::

        .. card:: Animated Charts
          :img-top: _static/gif_animated.gif
          :link: chart_gallery.animated
          :link-type: ref
          :text-align: center
          :class-card: custom-card-6
          :class-img-top: custom-class-img-top-7
          
          Available in: :bdg-primary-line:`Matplotlib`

          Using: :bdg-secondary:`Python` 

          :bdg-primary:`Bar` :bdg-primary:`Pie` :bdg-primary:`Bubble` :bdg-primary:`Time-Series`

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