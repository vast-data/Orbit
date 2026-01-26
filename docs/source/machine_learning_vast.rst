.. _api.machine_learning.vast:

===========
VAST Models
===========

.. include:: logo_include.rst

Hybrid ML workflow: train with sklearn/Spark, deploy for in-database inference at scale.

____

.. grid:: 1 2 2 3
    :gutter: 3

    .. grid-item::
    
        .. card:: 🎯 Classification
          :link: api.machine_learning.vast.classification
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
          Logistic Regression, Random Forest, XGBoost, Naive Bayes
          
          +++
          View API →

    .. grid-item::
    
        .. card:: 📈 Regression
          :link: api.machine_learning.vast.regression
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
          Linear, Ridge, Lasso, Random Forest, XGBoost
          
          +++
          View API →

    .. grid-item::
    
        .. card:: ⏱️ Time Series
          :link: api.machine_learning.vast.time_series
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
          ARIMA, VAR, Moving Average, Seasonal Decomposition
          
          +++
          View API →

    .. grid-item::
    
        .. card:: 🔍 Clustering & Anomalies
          :link: api.machine_learning.vast.clustering
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
          K-Means, DBSCAN, Isolation Forest, Local Outlier Factor
          
          +++
          View API →

    .. grid-item::
    
        .. card:: 🔧 Preprocessing
          :link: api.machine_learning.vast.decomposition
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
          PCA, Normalization, One-Hot Encoding, Feature Scaling
          
          +++
          View API →

    .. grid-item::
    
        .. card:: 📝 Text Analytics
          :link: api.machine_learning.vast.text
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
          TF-IDF, Word Embeddings, Sentiment Analysis
          
          +++
          View API →

    .. grid-item::
    
        .. card:: 🔄 Pipeline (Beta)
          :link: api.machine_learning.vast.pipeline
          :link-type: ref
          :text-align: center
          :class-card: custom-card-4
          
          +++
          
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