.. _api.machine_learning.vast:

===========
VAST Models
===========

.. include:: logo_include.rst

Hybrid ML workflow: train with sklearn / Spark, deploy for in-database
inference at scale. Every estimator below runs natively against your VAST
relation — no extraction, no copies, no leaving the database.

____

.. grid:: 1 2 2 3
    :gutter: 3

    .. grid-item-card:: |i-classify| Classification
      :link: api.machine_learning.vast.classification
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_classification_plot.svg

      Logistic Regression, Random Forest, GradientBoosting, Naive Bayes

      +++
      View API →

    .. grid-item-card:: |i-stats| Regression
      :link: api.machine_learning.vast.regression
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_regression_plot.svg

      Linear, Ridge, Lasso, Random Forest, GradientBoosting

      +++
      View API →

    .. grid-item-card:: |i-time| Time Series
      :link: api.machine_learning.vast.time_series
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_time_series.svg

      ARIMA, VAR, Moving Average, Seasonal Decomposition

      +++
      View API →

    .. grid-item-card:: |i-cluster| Clustering & Anomalies
      :link: api.machine_learning.vast.clustering
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_voronoi.svg

      K-Means, DBSCAN, Isolation Forest, Local Outlier Factor

      +++
      View API →

    .. grid-item-card:: |i-prep| Preprocessing
      :link: api.machine_learning.vast.decomposition
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_pivot.svg

      PCA, Normalization, One-Hot Encoding, Feature Scaling

      +++
      View API →

    .. grid-item-card:: |i-text| Text Analytics
      :link: api.machine_learning.vast.text
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_spider.svg

      TF-IDF, Word Embeddings, Sentiment Analysis

      +++
      View API →

    .. grid-item-card:: |i-pipeline| Pipeline (Beta)
      :link: api.machine_learning.vast.pipeline
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_stepwise.svg

      Chain preprocessing, training, and inference steps

      +++
      View API →

____

.. toctree::
  :maxdepth: 1
  :hidden:

  machine_learning_vast_classification
  machine_learning_vast_regression
  machine_learning_vast_time_series
  machine_learning_vast_clustering
  machine_learning_vast_decomposition
  machine_learning_vast_text
  machine_learning_vast_pipeline