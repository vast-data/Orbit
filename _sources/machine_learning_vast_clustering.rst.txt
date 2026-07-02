.. _api.machine_learning.vast.clustering:

===============================
Clustering & Anomaly Detection
===============================


Clustering
----------

K-Means
~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   cluster.KMeans

.. currentmodule:: vastorbit.machine_learning.vast.cluster

**Methods:**

.. autosummary::
   :toctree: api/

   KMeans.contour
   KMeans.deploySQL
   KMeans.drop
   KMeans.export_models
   KMeans.fit
   KMeans.get_attributes
   KMeans.get_match_index
   KMeans.get_params
   KMeans.get_plotting_lib
   KMeans.import_models
   KMeans.plot
   KMeans.plot_voronoi
   KMeans.predict
   KMeans.set_params
   KMeans.summarize
   KMeans.to_binary
   KMeans.to_memmodel
   KMeans.to_python
   KMeans.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   KMeans.object_type

Bisecting K-Means
~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   cluster.BisectingKMeans

.. currentmodule:: vastorbit.machine_learning.vast.cluster

**Methods:**

.. autosummary::
   :toctree: api/

   BisectingKMeans.contour
   BisectingKMeans.deploySQL
   BisectingKMeans.drop
   BisectingKMeans.export_models
   BisectingKMeans.features_importance
   BisectingKMeans.fit
   BisectingKMeans.get_attributes
   BisectingKMeans.get_match_index
   BisectingKMeans.get_params
   BisectingKMeans.get_plotting_lib
   BisectingKMeans.get_tree
   BisectingKMeans.import_models
   BisectingKMeans.plot
   BisectingKMeans.plot_tree
   BisectingKMeans.plot_voronoi
   BisectingKMeans.predict
   BisectingKMeans.set_params
   BisectingKMeans.summarize
   BisectingKMeans.to_binary
   BisectingKMeans.to_graphviz
   BisectingKMeans.to_memmodel
   BisectingKMeans.to_python
   BisectingKMeans.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   BisectingKMeans.object_type

DBSCAN (Beta)
~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   cluster.DBSCAN

.. currentmodule:: vastorbit.machine_learning.vast.cluster

**Methods:**

.. autosummary::
   :toctree: api/

   DBSCAN.contour
   DBSCAN.deploySQL
   DBSCAN.drop
   DBSCAN.export_models
   DBSCAN.fit
   DBSCAN.get_attributes
   DBSCAN.get_match_index
   DBSCAN.get_params
   DBSCAN.get_plotting_lib
   DBSCAN.import_models
   DBSCAN.plot
   DBSCAN.predict
   DBSCAN.set_params
   DBSCAN.summarize
   DBSCAN.to_binary
   DBSCAN.to_python
   DBSCAN.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   DBSCAN.object_type

_____________

Anomaly Detection
-------------------

Isolation Forest
~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   ensemble.IsolationForest

.. currentmodule:: vastorbit.machine_learning.vast.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   IsolationForest.contour
   IsolationForest.decision_function
   IsolationForest.deploySQL
   IsolationForest.drop
   IsolationForest.export_models
   IsolationForest.features_importance
   IsolationForest.fit
   IsolationForest.get_attributes
   IsolationForest.get_match_index
   IsolationForest.get_params
   IsolationForest.get_plotting_lib
   IsolationForest.get_tree
   IsolationForest.import_models
   IsolationForest.plot
   IsolationForest.plot_tree
   IsolationForest.predict
   IsolationForest.set_params
   IsolationForest.summarize
   IsolationForest.to_binary
   IsolationForest.to_graphviz
   IsolationForest.to_memmodel
   IsolationForest.to_python
   IsolationForest.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   IsolationForest.object_type

Local Outlier Factor (Beta)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   neighbors.LocalOutlierFactor

.. currentmodule:: vastorbit.machine_learning.vast.neighbors

**Methods:**

.. autosummary::
   :toctree: api/

   LocalOutlierFactor.contour
   LocalOutlierFactor.deploySQL
   LocalOutlierFactor.drop
   LocalOutlierFactor.export_models
   LocalOutlierFactor.fit
   LocalOutlierFactor.get_attributes
   LocalOutlierFactor.get_match_index
   LocalOutlierFactor.get_params
   LocalOutlierFactor.get_plotting_lib
   LocalOutlierFactor.import_models
   LocalOutlierFactor.predict
   LocalOutlierFactor.set_params
   LocalOutlierFactor.summarize
   LocalOutlierFactor.to_binary
   LocalOutlierFactor.to_python
   LocalOutlierFactor.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   LocalOutlierFactor.object_type