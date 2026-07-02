.. _api.machine_learning.memmodels:

=============
Memory Models
=============

.. include:: logo_include.rst

In-memory estimators for fast, local experimentation. Train on a sampled or
materialized VastFrame, iterate quickly, then promote the winning model to
in-database inference with the VAST Models API.

____

.. grid:: 1 2 2 3
    :gutter: 3

    .. grid-item-card:: |i-cluster| Cluster
      :link: api.machine_learning.memmodels.clusters
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_voronoi.svg

      Clustering algorithms that group data points and reveal the inherent
      patterns within your datasets.

      +++
      View API →

    .. grid-item-card:: |i-decomp| Decomposition
      :link: api.machine_learning.memmodels.decomposition
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_pivot.svg

      Decomposition techniques that break down complex data structures,
      enhancing understanding and simplifying analysis.

      +++
      View API →

    .. grid-item-card:: |i-ensemble| Ensemble
      :link: api.machine_learning.memmodels.ensemble
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_champion_challenger.svg

      Ensemble methods that combine multiple models to achieve superior
      predictive accuracy.

      +++
      View API →

    .. grid-item-card:: |i-stats| Linear Model
      :link: api.machine_learning.memmodels.linear_model
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_regression_plot.svg

      Linear models for straightforward representations, ideal for scenarios
      where simplicity is key.

      +++
      View API →

    .. grid-item-card:: |i-classify| Naive Bayes
      :link: api.machine_learning.memmodels.naive_bayes
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_classification_plot.svg

      Naive Bayes algorithms for efficient, rapid classification — especially
      useful on large datasets.

      +++
      View API →

    .. grid-item-card:: |i-prep| Preprocessing
      :link: api.machine_learning.memmodels.preprocessing
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_hist.svg

      Streamline data preparation to ensure optimal input for your machine
      learning models.

      +++
      View API →

    .. grid-item-card:: |i-tree| Trees
      :link: api.machine_learning.memmodels.trees
      :link-type: ref
      :text-align: center
      :class-card: custom-card-4
      :img-top: /_static/thumbs/thumb_tree.svg

      Decision trees for robust, interpretable models.

      +++
      View API →

____

.. toctree::
  :maxdepth: 1
  :hidden:

  machine_learning_memmodels_cluster
  machine_learning_memmodels_decomposition
  machine_learning_memmodels_ensemble
  machine_learning_memmodels_linear_model
  machine_learning_memmodels_naive_bayes
  machine_learning_memmodels_preprocessing
  machine_learning_memmodels_trees