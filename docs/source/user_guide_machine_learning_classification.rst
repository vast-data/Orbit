.. _user_guide.machine_learning.classification:

==============
Classification
==============

Build and evaluate models to predict categorical outcomes.

____

Overview
--------

Classification algorithms predict categorical response variables. They are used for:

- **Binary classification** – Two classes (e.g., fraud/not fraud, churn/no churn)
- **Multiclass classification** – Multiple classes (e.g., flower species, product categories)

**Common use cases:**

- Customer churn prediction
- Fraud detection
- Image classification
- Sentiment analysis
- Disease diagnosis

____

Build a Classification Model
-----------------------------

We'll predict flower species using the Iris dataset with a Random Forest Classifier.

**Import the model:**

.. ipython:: python

    from vastorbit.machine_learning.vast import RandomForestClassifier

**Load the dataset:**

.. ipython:: python

    from vastorbit.datasets import load_iris
    
    iris = load_iris()
    iris.head(5)

**Initialize the model:**

.. ipython:: python

    model = RandomForestClassifier(
        n_estimators = 5,
        max_depth = 3,
    )

**Train the model:**

.. ipython:: python
    :okwarning:

    model.fit(
        iris,
        X=["PetalLengthCm", "SepalLengthCm"],
        y="Species",
    )

.. tip::

   All computation happens in-database. No data is moved to Python memory.

____

Evaluate Model Performance
---------------------------

**Generate classification report:**

.. code-block:: python

    model.report()

.. ipython:: python
    :suppress:
    :okwarning:

    res = model.report()
    html_file = open("SPHINX_DIRECTORY/figures/ug_ml_table_classification_1.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_ml_table_classification_1.html

**Key metrics:**

- **Accuracy** – Overall correctness (correct predictions / total predictions)
- **Precision** – Of predicted positives, how many are actually positive
- **Recall** – Of actual positives, how many were correctly identified
- **F1-Score** – Harmonic mean of precision and recall
- **AUC** – Area under ROC curve (discrimination ability)

____

Make Predictions
----------------

**Predict class labels:**

.. code-block:: python

    model.predict(iris, name="prediction")

.. ipython:: python
    :suppress:
    :okwarning:

    res = model.predict(iris, name="prediction")
    html_file = open("SPHINX_DIRECTORY/figures/ug_ml_table_classification_2.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_ml_table_classification_2.html

**Predict class probabilities:**

.. code-block:: python

    model.predict_proba(iris, name="prob")

.. ipython:: python
    :suppress:
    :okwarning:

    res = model.predict_proba(iris, name="prob")
    html_file = open("SPHINX_DIRECTORY/figures/ug_ml_table_classification_3.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_ml_table_classification_3.html

____

Visualize Results
-----------------

**ROC Curve:**

.. code-block:: python

    model.roc_curve()

**Confusion Matrix:**

.. code-block:: python

    model.confusion_matrix()

**Feature Importance:**

.. code-block:: python

    model.features_importance()

____

Understanding Metrics
---------------------

**The Accuracy Trap**

Accuracy alone can be misleading, especially with imbalanced datasets.

**Example: Fraud Detection**

Suppose fraudulent transactions represent only 1% of data:

.. code-block:: python

    # Naive model: predict "no fraud" for everything
    # Accuracy: 99% ✓
    # Usefulness: 0% ✗ (misses all fraud!)

**Better metrics for imbalanced data:**

- **ROC AUC** – Measures discrimination ability across all thresholds
- **PRC AUC** – Precision-Recall curve (better for rare events)
- **F1-Score** – Balances precision and recall
- **Class-specific metrics** – Precision/recall per class

**When to use which metric:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Metric
     - Best For
   * - **Accuracy**
     - Balanced datasets with equal class importance
   * - **Precision**
     - When false positives are costly (e.g., spam detection)
   * - **Recall**
     - When false negatives are costly (e.g., disease screening)
   * - **F1-Score**
     - Balance between precision and recall
   * - **ROC AUC**
     - Overall model discrimination ability
   * - **PRC AUC**
     - Imbalanced datasets with rare positive class

____

Train/Test Split
----------------

The example above used the entire dataset for training. For real-world applications, always split data:

.. code-block:: python

    from vastorbit.machine_learning.model_selection import train_test_split

    # Split data: 80% train, 20% test
    train, test = iris.train_test_split(test_size=0.2)

    # Train on training set
    model.fit(
        train,
        X=["PetalLengthCm", "SepalLengthCm"],
        y="Species",
    )

    # Evaluate on test set
    predictions = model.predict(test, name="prediction")
    model.report()

.. warning::

   Training and testing on the same data leads to overfitting and unrealistic performance metrics.

____

Advanced Techniques
-------------------

**Cross-validation:**

.. code-block:: python

    from vastorbit.machine_learning.model_selection import cross_validate

    # 5-fold cross-validation
    scores = cross_validate(
        model,
        iris,
        X=["PetalLengthCm", "SepalLengthCm"],
        y="Species",
        cv=5,
    )

**Hyperparameter tuning:**

.. code-block:: python

    # Grid search for best parameters
    best_model = RandomForestClassifier(
        n_estimators = 5,
        max_depth = 3,
    )

**Feature engineering:**

.. code-block:: python

    # Create interaction features
    iris["petal_sepal_ratio"] = iris["PetalLengthCm"] / iris["SepalLengthCm"]
    
    # Train with new feature
    model.fit(
        iris,
        X=["PetalLengthCm", "SepalLengthCm", "petal_sepal_ratio"],
        y="Species",
    )

____

Available Classifiers
---------------------

VAST Orbit supports multiple classification algorithms:

- :py:class:`~vastorbit.machine_learning.vast.RandomForestClassifier` – Ensemble of decision trees
- :py:class:`~vastorbit.machine_learning.vast.LogisticRegression` – Linear classification
- :py:class:`~vastorbit.machine_learning.vast.NaiveBayes` – Probabilistic classifier
- :py:class:`~vastorbit.machine_learning.vast.LinearSVC` – Support Vector Classifier
- :py:class:`~vastorbit.machine_learning.vast.KNeighborsClassifier` – K-nearest neighbors

Each algorithm has strengths for different data types and problem characteristics.

____

Next Steps
----------

Now that you understand classification, explore:

- :ref:`user_guide.machine_learning.regression` – Predict continuous values
- :ref:`user_guide.machine_learning.time_series` – Analyze temporal patterns
- :ref:`user_guide.machine_learning.clustering` – Discover data groups

.. seealso::

   - :ref:`api.machine_learning` – Complete ML API reference
   - :ref:`examples.learn.titanic` – Binary classification example
   - :ref:`examples.learn.iris` – Multiclass classification example

.. ipython:: python
   :suppress:

   from vastorbit._utils._sql._sys import purge_memory
   purge_memory()