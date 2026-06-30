.. _api.machine_learning.vast.classification:

===============
Classification
===============



Linear Models
-------------

Linear SVC
~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast

.. autosummary::
   :toctree: api/

   svm.LinearSVC

.. currentmodule:: vastorbit.machine_learning.vast.svm

**Methods:**

.. autosummary::
   :toctree: api/

   LinearSVC.classification_report
   LinearSVC.confusion_matrix
   LinearSVC.contour
   LinearSVC.cutoff_curve
   LinearSVC.deploySQL
   LinearSVC.drop
   LinearSVC.export_models
   LinearSVC.features_importance
   LinearSVC.fit
   LinearSVC.get_attributes
   LinearSVC.get_match_index
   LinearSVC.get_params
   LinearSVC.get_plotting_lib
   LinearSVC.import_models
   LinearSVC.lift_chart
   LinearSVC.plot
   LinearSVC.prc_curve
   LinearSVC.predict
   LinearSVC.predict_proba
   LinearSVC.report
   LinearSVC.roc_curve
   LinearSVC.score
   LinearSVC.set_params
   LinearSVC.summarize
   LinearSVC.to_binary
   LinearSVC.to_memmodel
   LinearSVC.to_python
   LinearSVC.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   LinearSVC.object_type
   LinearSVC.classes_

Logistic Regression
~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast

.. autosummary::
   :toctree: api/

   linear_model.LogisticRegression

.. currentmodule:: vastorbit.machine_learning.vast.linear_model

**Methods:**

.. autosummary::
   :toctree: api/

   LogisticRegression.classification_report
   LogisticRegression.confusion_matrix
   LogisticRegression.contour
   LogisticRegression.cutoff_curve
   LogisticRegression.deploySQL
   LogisticRegression.drop
   LogisticRegression.export_models
   LogisticRegression.features_importance
   LogisticRegression.fit
   LogisticRegression.get_attributes
   LogisticRegression.get_match_index
   LogisticRegression.get_params
   LogisticRegression.get_plotting_lib
   LogisticRegression.import_models
   LogisticRegression.lift_chart
   LogisticRegression.plot
   LogisticRegression.prc_curve
   LogisticRegression.predict
   LogisticRegression.predict_proba
   LogisticRegression.report
   LogisticRegression.roc_curve
   LogisticRegression.score
   LogisticRegression.set_params
   LogisticRegression.summarize
   LogisticRegression.to_binary
   LogisticRegression.to_memmodel
   LogisticRegression.to_python
   LogisticRegression.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   LogisticRegression.object_type
   LogisticRegression.classes_

_____

Tree-based algorithms
---------------------

Random Forest Classifier
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   ensemble.RandomForestClassifier

.. currentmodule:: vastorbit.machine_learning.vast.ensemble

**Methods:**

.. autosummary::
   :toctree: api/


   RandomForestClassifier.classification_report
   RandomForestClassifier.confusion_matrix
   RandomForestClassifier.contour
   RandomForestClassifier.cutoff_curve
   RandomForestClassifier.deploySQL
   RandomForestClassifier.drop
   RandomForestClassifier.export_models
   RandomForestClassifier.features_importance
   RandomForestClassifier.fit
   RandomForestClassifier.get_attributes
   RandomForestClassifier.get_match_index
   RandomForestClassifier.get_params
   RandomForestClassifier.get_plotting_lib
   RandomForestClassifier.get_tree
   RandomForestClassifier.import_models
   RandomForestClassifier.lift_chart
   RandomForestClassifier.plot
   RandomForestClassifier.plot_tree
   RandomForestClassifier.prc_curve
   RandomForestClassifier.predict
   RandomForestClassifier.predict_proba
   RandomForestClassifier.report
   RandomForestClassifier.roc_curve
   RandomForestClassifier.score
   RandomForestClassifier.set_params
   RandomForestClassifier.summarize
   RandomForestClassifier.to_binary
   RandomForestClassifier.to_graphviz
   RandomForestClassifier.to_memmodel
   RandomForestClassifier.to_python
   RandomForestClassifier.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   RandomForestClassifier.object_type

GradientBoosting Classifier
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   ensemble.GradientBoostingClassifier

.. currentmodule:: vastorbit.machine_learning.vast.ensemble

**Methods:**

.. autosummary::
   :toctree: api/


   GradientBoostingClassifier.classification_report
   GradientBoostingClassifier.confusion_matrix
   GradientBoostingClassifier.contour
   GradientBoostingClassifier.cutoff_curve
   GradientBoostingClassifier.deploySQL
   GradientBoostingClassifier.drop
   GradientBoostingClassifier.export_models
   GradientBoostingClassifier.features_importance
   GradientBoostingClassifier.fit
   GradientBoostingClassifier.get_attributes
   GradientBoostingClassifier.get_match_index
   GradientBoostingClassifier.get_params
   GradientBoostingClassifier.get_plotting_lib
   GradientBoostingClassifier.get_tree
   GradientBoostingClassifier.import_models
   GradientBoostingClassifier.lift_chart
   GradientBoostingClassifier.plot
   GradientBoostingClassifier.plot_tree
   GradientBoostingClassifier.prc_curve
   GradientBoostingClassifier.predict
   GradientBoostingClassifier.predict_proba
   GradientBoostingClassifier.report
   GradientBoostingClassifier.roc_curve
   GradientBoostingClassifier.score
   GradientBoostingClassifier.set_params
   GradientBoostingClassifier.summarize
   GradientBoostingClassifier.to_binary
   GradientBoostingClassifier.to_graphviz
   GradientBoostingClassifier.to_json
   GradientBoostingClassifier.to_memmodel
   GradientBoostingClassifier.to_python
   GradientBoostingClassifier.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   GradientBoostingClassifier.object_type

________

Naive Bayes
--------------

Naive Bayes
~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   naive_bayes.NaiveBayes

.. currentmodule:: vastorbit.machine_learning.vast.naive_bayes

**Methods:**

.. autosummary::
   :toctree: api/


   NaiveBayes.classification_report
   NaiveBayes.confusion_matrix
   NaiveBayes.contour
   NaiveBayes.cutoff_curve
   NaiveBayes.deploySQL
   NaiveBayes.drop
   NaiveBayes.export_models
   NaiveBayes.fit
   NaiveBayes.get_attributes
   NaiveBayes.get_match_index
   NaiveBayes.get_params
   NaiveBayes.get_plotting_lib
   NaiveBayes.import_models
   NaiveBayes.lift_chart
   NaiveBayes.prc_curve
   NaiveBayes.predict
   NaiveBayes.predict_proba
   NaiveBayes.report
   NaiveBayes.roc_curve
   NaiveBayes.score
   NaiveBayes.set_params
   NaiveBayes.summarize
   NaiveBayes.to_binary
   NaiveBayes.to_memmodel
   NaiveBayes.to_python
   NaiveBayes.to_sql

**Attributes:**

.. autosummary::
   :toctree: api/

   NaiveBayes.object_type

_______

Neighbors
-----------

K-Nearest Neighbors Classifier (Beta)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   neighbors.KNeighborsClassifier

.. currentmodule:: vastorbit.machine_learning.vast.neighbors

**Methods:**

.. autosummary::
   :toctree: api/


   KNeighborsClassifier.classification_report
   KNeighborsClassifier.confusion_matrix
   KNeighborsClassifier.contour
   KNeighborsClassifier.cutoff_curve
   KNeighborsClassifier.deploySQL
   KNeighborsClassifier.drop
   KNeighborsClassifier.export_models
   KNeighborsClassifier.fit
   KNeighborsClassifier.get_attributes
   KNeighborsClassifier.get_match_index
   KNeighborsClassifier.get_params
   KNeighborsClassifier.get_plotting_lib
   KNeighborsClassifier.import_models
   KNeighborsClassifier.lift_chart
   KNeighborsClassifier.prc_curve
   KNeighborsClassifier.predict
   KNeighborsClassifier.predict_proba
   KNeighborsClassifier.report
   KNeighborsClassifier.roc_curve
   KNeighborsClassifier.score
   KNeighborsClassifier.set_params
   KNeighborsClassifier.summarize
   KNeighborsClassifier.to_binary
   KNeighborsClassifier.to_python
   KNeighborsClassifier.to_sql


**Attributes:**

.. autosummary::
   :toctree: api/

   KNeighborsClassifier.object_type


Nearest Centroid (Beta)
~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: vastorbit.machine_learning.vast
   
.. autosummary::
   :toctree: api/

   cluster.NearestCentroid

.. currentmodule:: vastorbit.machine_learning.vast.cluster

**Methods:**

.. autosummary::
   :toctree: api/


   NearestCentroid.classification_report
   NearestCentroid.confusion_matrix
   NearestCentroid.contour
   NearestCentroid.cutoff_curve
   NearestCentroid.deploySQL
   NearestCentroid.drop
   NearestCentroid.export_models
   NearestCentroid.fit
   NearestCentroid.get_attributes
   NearestCentroid.get_match_index
   NearestCentroid.get_params
   NearestCentroid.get_plotting_lib
   NearestCentroid.import_models
   NearestCentroid.lift_chart
   NearestCentroid.prc_curve
   NearestCentroid.predict
   NearestCentroid.predict_proba
   NearestCentroid.report
   NearestCentroid.roc_curve
   NearestCentroid.score
   NearestCentroid.set_params
   NearestCentroid.summarize
   NearestCentroid.to_binary
   NearestCentroid.to_memmodel
   NearestCentroid.to_python
   NearestCentroid.to_sql


**Attributes:**

.. autosummary::
   :toctree: api/

   NearestCentroid.object_type



