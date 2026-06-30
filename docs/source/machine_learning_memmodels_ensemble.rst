.. _api.machine_learning.memmodels.ensemble:

=============
Ensemble
=============



Base Class
--------------

.. currentmodule:: vastorbit.machine_learning.memmodel
   
.. autosummary::
   :toctree: api/

   ensemble.Ensemble

.. currentmodule:: vastorbit.machine_learning.memmodel.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   Ensemble.get_attributes
   Ensemble.plot_tree
   Ensemble.set_attributes

**Attributes:**

.. autosummary::
   :toctree: api/

   Ensemble.object_type

____

Random Forest Regressor
------------------------

.. currentmodule:: vastorbit.machine_learning.memmodel
   
.. autosummary::
   :toctree: api/

   ensemble.RandomForestRegressor

.. currentmodule:: vastorbit.machine_learning.memmodel.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   RandomForestRegressor.get_attributes
   RandomForestRegressor.plot_tree
   RandomForestRegressor.predict
   RandomForestRegressor.predict_sql
   RandomForestRegressor.set_attributes


**Attributes:**

.. autosummary::
   :toctree: api/

   RandomForestRegressor.object_type


____

Random Forest Classifier
------------------------

.. currentmodule:: vastorbit.machine_learning.memmodel
   
.. autosummary::
   :toctree: api/

   ensemble.RandomForestClassifier

.. currentmodule:: vastorbit.machine_learning.memmodel.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   RandomForestClassifier.get_attributes
   RandomForestClassifier.plot_tree
   RandomForestClassifier.predict
   RandomForestClassifier.predict_proba
   RandomForestClassifier.predict_proba_sql
   RandomForestClassifier.predict_sql
   RandomForestClassifier.set_attributes


**Attributes:**

.. autosummary::
   :toctree: api/

   RandomForestClassifier.object_type


____

GradientBoosting Regressor
--------------------------

.. currentmodule:: vastorbit.machine_learning.memmodel
   
.. autosummary::
   :toctree: api/

   ensemble.GradientBoostingRegressor

.. currentmodule:: vastorbit.machine_learning.memmodel.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   GradientBoostingRegressor.get_attributes
   GradientBoostingRegressor.plot_tree
   GradientBoostingRegressor.predict
   GradientBoostingRegressor.predict_sql
   GradientBoostingRegressor.set_attributes


**Attributes:**

.. autosummary::
   :toctree: api/

   GradientBoostingRegressor.object_type



_____

GradientBoosting Classifier
---------------------------

.. currentmodule:: vastorbit.machine_learning.memmodel
   
.. autosummary::
   :toctree: api/

   ensemble.GradientBoostingClassifier

.. currentmodule:: vastorbit.machine_learning.memmodel.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   GradientBoostingClassifier.get_attributes
   GradientBoostingClassifier.plot_tree
   GradientBoostingClassifier.predict
   GradientBoostingClassifier.predict_proba
   GradientBoostingClassifier.predict_proba_sql
   GradientBoostingClassifier.predict_sql
   GradientBoostingClassifier.set_attributes

**Attributes:**

.. autosummary::
   :toctree: api/

   GradientBoostingClassifier.object_type


_____


Isolation Forest
-----------------

.. currentmodule:: vastorbit.machine_learning.memmodel
   
.. autosummary::
   :toctree: api/

   ensemble.IsolationForest

.. currentmodule:: vastorbit.machine_learning.memmodel.ensemble

**Methods:**

.. autosummary::
   :toctree: api/

   IsolationForest.get_attributes
   IsolationForest.plot_tree
   IsolationForest.predict
   IsolationForest.predict_sql
   IsolationForest.set_attributes


**Attributes:**

.. autosummary::
   :toctree: api/

   IsolationForest.object_type