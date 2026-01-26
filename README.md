.. raw:: html

   <p align="center">
   <img src='https://raw.githubusercontent.com/vastdata-dev/vastorbit/master/assets/img/logo.svg' width="180px">
   </p>

.. note::

   VastOrbit 0.1.x represents the first beta release series. The API and features are subject to change as we work toward a more robust 1.0.0 release.

=========
VastOrbit
=========

.. image:: https://badge.fury.io/py/vastorbit.svg
   :target: https://badge.fury.io/py/vastorbit
   :alt: PyPI version

.. image:: https://img.shields.io/conda/vn/conda-forge/vastorbit?color=yellowgreen
   :target: https://anaconda.org/conda-forge/vastorbit
   :alt: Conda Version

.. image:: https://img.shields.io/badge/License-Apache%202.0-orange.svg
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: License

.. image:: https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://codecov.io/gh/vastdata-dev/vastorbit/branch/master/graph/badge.svg?token=a6GiFYI9at
   :target: https://codecov.io/gh/vastdata-dev/vastorbit
   :alt: codecov

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
   :target: https://github.com/pylint-dev/pylint
   :alt: linting: pylint

.. raw:: html

   <p align="center">
   <!-- TODO: Add benefits image -->
   <img src='https://raw.githubusercontent.com/vastdata-dev/vastorbit/master/assets/img/benefits.png' width="92%">
   </p>

VastOrbit is a Python library with scikit-learn-like functionality for conducting data science projects on data stored in VAST Database. Train models using familiar scikit-learn syntax and deploy them directly in the database, leveraging VAST's high-performance analytics capabilities. VastOrbit offers robust support for the entire data science life cycle, uses a 'pipeline' mechanism to sequentialize data transformation operations, and provides beautiful graphical options.

.. contents:: **Table of Contents**
   :local:
   :depth: 2

============
Introduction
============

VAST Database combines enterprise-grade storage with powerful analytics capabilities. Today, VastOrbit leverages Trino as the SQL engine to deliver exceptional performance for data science workloads at scale. Soon, we will support the VAST SQL Engine (currently in development), which will provide even greater speed through VAST's columnar-optimized format. However, SQL alone isn't flexible enough to meet the evolving needs of modern data scientists.

Python has become the lingua franca of data science, offering unparalleled flexibility through its high-level abstraction and an extensive ecosystem of libraries. The accessibility of Python has led to the development of powerful APIs like pandas and scikit-learn, supported by a vibrant community of data scientists worldwide. Unfortunately, traditional Python tools operate in-memory as single-node processes, creating fundamental limitations when working with large-scale data. While distributed computing frameworks attempt to address these constraints, they still require moving data for processing—an approach that is prohibitively expensive and increasingly impractical in the modern data landscape. On top of these challenges, data scientists face additional complexity in deploying and operationalizing their models. The entire workflow is time-consuming and inefficient.

**VastOrbit solves these problems**. The concept is elegant: instead of moving data to compute, VastOrbit brings the compute logic to where the data lives—in VAST Database. Train your models using familiar scikit-learn syntax in Python, then deploy them directly in the database for high-performance predictions at scale.

Main Advantages
---------------

- **Easy Data Exploration**: Interactive exploration of massive datasets without memory constraints
- **Fast Data Preparation**: Leverage Trino's distributed processing for rapid data transformation
- **Familiar Scikit-learn API**: Train models using the scikit-learn interface you already know
- **In-Database Deployment**: Deploy trained models directly in VAST Database for production workloads
- **Easy Model Evaluation**: Comprehensive model evaluation tools with visual insights
- **Seamless SQL Integration**: Use Python or SQL interchangeably based on your preference and use case

.. raw:: html

   <p align="center">
   <!-- TODO: Add architecture diagram -->
   <img src='https://raw.githubusercontent.com/vastdata-dev/vastorbit/master/assets/img/architecture.png' width="92%">
   </p>

============
Installation
============

To install VastOrbit with pip:

.. code-block:: shell

   # Latest release version
   pip3 install vastorbit[all]

   # Latest commit on master branch
   pip3 install git+https://github.com/vastdata-dev/vastorbit.git@master

To install VastOrbit from source, run the following command from the root directory:

.. code-block:: shell

   python3 setup.py install

===========================
Connecting to the Database
===========================

VastOrbit currently connects to VAST Database through Trino. Ensure you have Trino set up and configured to access your VAST Database instance.

Connection example:

.. code-block:: python

   import vastorbit as vo

   vo.new_connection({
       "host": "your-trino-host", 
       "port": "8080", 
       "database": "your_database", 
       "user": "your_username"},
       name="VAST_Connection")

Use the connection:

.. code-block:: python

   vo.connect("VAST_Connection")

For more details on connection configuration, refer to the documentation.

=============
Documentation
=============

The easiest and most accurate way to find documentation for a particular function is to use the help function:

.. code-block:: python

   import vastorbit as vo

   help(vo.VastFrame)

Documentation can be generated locally. Refer to the documentation generation guide in the ``docs/`` directory.

Official documentation will be available soon at a dedicated documentation site.

====================
Highlighted Features
====================

Themes - Dark | Light
---------------------

VastOrbit offers users the flexibility to customize their coding experience with two visually appealing themes: **Dark** and **Light**.

Dark mode, ideal for extended coding sessions, features a sleek and stylish dark color scheme, providing a comfortable and eye-friendly environment.

.. raw:: html

   <p align="center">
   <!-- TODO: Add dark theme screenshot -->
   <img src="path/to/dark-theme-screenshot.png" width="70%">
   </p>

On the other hand, Light mode serves as the default theme, offering a clean and bright interface for users who prefer a traditional coding ambiance.

.. raw:: html

   <p align="center">
   <!-- TODO: Add light theme screenshot -->
   <img src="path/to/light-theme-screenshot.png" width="70%">
   </p>

Theme can be easily switched by:

.. code-block:: python

   import vastorbit as vo

   vo.set_option("theme", "dark")  # can be switched to 'light'

VastOrbit's theme-switching option ensures that users can tailor their experience to their preferences, making data exploration and analysis a more personalized and enjoyable journey.

SQL Magic
---------

You can use VastOrbit to execute SQL queries directly from a Jupyter notebook.

Example
~~~~~~~

Load the SQL extension:

.. code-block:: python

   %load_ext vastorbit.sql

Execute your SQL queries:

.. code-block:: sql

   %%sql
   SELECT version();

SQL Plots
---------

You can create interactive, professional plots directly from SQL.

To create plots, simply provide the type of plot along with the SQL command.

Example
~~~~~~~

.. code-block:: python

   %load_ext vastorbit.jupyter.extensions.chart_magic
   %chart -k pie -c "SELECT pclass, AVG(age) AS avg_age FROM titanic GROUP BY 1;"

.. raw:: html

   <p align="center">
   <!-- TODO: Add SQL plot screenshot -->
   <img src="path/to/sql-plot-screenshot.png" width="50%">
   </p>

Python and SQL Combo
--------------------

VastOrbit has a unique place in the market because it allows users to use Python and SQL in the same environment.

Example
~~~~~~~

.. code-block:: python

   import vastorbit as vo

   selected_titanic = vo.VastFrame(
       "(SELECT pclass, embarked, AVG(survived) FROM titanic GROUP BY 1, 2) x"
   )
   selected_titanic.groupby(columns=["pclass"], expr=["AVG(AVG)"])

Charts
------

VastOrbit comes integrated with three popular plotting libraries: matplotlib, highcharts, and plotly.

A gallery of VastOrbit-generated charts will be available in the documentation.

.. raw:: html

   <p align="center">
   <!-- TODO: Add charts gallery screenshot -->
   <img src="path/to/charts-gallery.png" width="70%">
   </p>

Complete Machine Learning Pipeline
-----------------------------------

Data Ingestion
~~~~~~~~~~~~~~

VastOrbit allows users to ingest data from a diverse range of file formats including CSV, JSON, and more formats coming in the future. VastOrbit automatically infers data types during ingestion, though the inferred types may not always be optimal for your specific use case.

CSV Example:

.. code-block:: python

   import vastorbit as vo

   vo.read_csv(
       "/path/to/your/data.csv",
       table_name="my_table",
   )

JSON Example:

.. code-block:: python

   import vastorbit as vo

   vo.read_json(
       "/path/to/your/data.json",
       table_name="my_table",
   )

.. note::
   VastOrbit performs automatic type inference during data ingestion. However, the automatically inferred data types may not always be optimal for your specific use case. You can explicitly specify data types if needed.

Data Exploration
~~~~~~~~~~~~~~~~

VastOrbit provides extensive options for descriptive and visual exploration.

Scatter Plot Example:

.. code-block:: python

   from vastorbit.datasets import load_iris

   iris_data = load_iris()
   iris_data.scatter(
       ["SepalWidthCm", "SepalLengthCm", "PetalLengthCm"], 
       by="Species", 
       max_nb_points=30
   )

.. raw:: html

   <p align="center">
   <!-- TODO: Add scatter plot screenshot -->
   <img src="path/to/scatter-plot.png" width="40%">
   </p>

The **Correlation Matrix** is fast and convenient to compute. Users can choose from a wide variety of correlations, including Cramer, Spearman, Pearson, etc.

.. code-block:: python

   from vastorbit.datasets import load_titanic

   titanic = load_titanic()
   titanic.corr(method="spearman")

.. raw:: html

   <p align="center">
   <!-- TODO: Add correlation matrix screenshot -->
   <img src="path/to/correlation-matrix.png" width="75%">
   </p>

By turning on the SQL print option, users can see and copy SQL queries:

.. code-block:: python

   from vastorbit import set_option

   set_option("sql_on", True)

VastOrbit allows users to calculate a focused correlation using the "focus" parameter:

.. code-block:: python

   titanic.corr(method="spearman", focus="survived")

.. raw:: html

   <p align="center">
   <!-- TODO: Add focused correlation screenshot -->
   <img src="path/to/focused-correlation.png" width="20%">
   </p>

Data Preparation
~~~~~~~~~~~~~~~~

VastOrbit provides comprehensive data preparation capabilities including joining tables, encoding categorical variables, and filling missing values. Refer to the documentation for detailed examples.

Outlier Detection Example:

.. code-block:: python

   import random
   import vastorbit as vo

   data = vo.VastFrame({"Heights": [random.randint(10, 60) for _ in range(40)] + [100]})
   data.outliers_plot(columns="Heights")

.. raw:: html

   <p align="center">
   <!-- TODO: Add outliers plot screenshot -->
   <img src="path/to/outliers-plot.png" width="50%">
   </p>

Machine Learning
~~~~~~~~~~~~~~~~

VastOrbit's machine learning capabilities allow you to train models using the familiar scikit-learn API and deploy them directly in the database for high-performance predictions. VastOrbit supports a wide array of algorithms including time series forecasting, clustering, and classification.

Key Feature: **Train with scikit-learn syntax, deploy in-database for production**

Example with Logistic Regression:

.. code-block:: python

   from vastorbit.machine_learning.model_selection.model_validation import cross_validate
   from vastorbit.machine_learning.linear_model import LogisticRegression

   # Create and evaluate model
   model = LogisticRegression()
   
   cross_validate(
       model,
       titanic_vd,
       X=["age", "fare", "parch", "pclass"],
       y="survived",
       cv=5,
   )

.. raw:: html

   <p align="center">
   <!-- TODO: Add model evaluation screenshot -->
   <img src="path/to/model-evaluation.png" width="50%">
   </p>

Loading Predefined Datasets
----------------------------

VastOrbit provides some predefined datasets that can be easily loaded for testing and learning. These datasets include the iris dataset, titanic dataset, and more.

There are two ways to access the provided datasets:

(1) Use the standard Python method:

.. code-block:: python

   from vastorbit.datasets import load_iris

   iris_data = load_iris()

(2) Use the standard name of the dataset from the schema:

.. code-block:: python

   import vastorbit as vo
   
   iris_data = vo.VastFrame(input_relation="public.iris")

==========
Quickstart
==========

Install the library with pip:

.. code-block:: shell

   pip3 install vastorbit[all]

Create a new VAST connection through Trino:

.. code-block:: python

   import vastorbit as vo

   vo.new_connection({
       "host": "your-trino-host", 
       "port": "8080", 
       "database": "your_database", 
       "user": "your_username"},
       name="VAST_Connection")

Use the newly created connection:

.. code-block:: python

   vo.connect("VAST_Connection")

Create a VastFrame from your data:

.. code-block:: python

   from vastorbit import VastFrame

   vdf = VastFrame("my_table")

Load a sample dataset:

.. code-block:: python

   from vastorbit.datasets import load_titanic

   vdf = load_titanic()

Examine your data:

.. code-block:: python

   vdf.describe()

.. raw:: html

   <p align="center">
   <!-- TODO: Add describe output screenshot -->
   <img src="path/to/describe-output.png" width="100%">
   </p>

Print the SQL query with ``set_option``:

.. code-block:: python

   from vastorbit import set_option
   
   set_option("sql_on", True)
   vdf.describe()

   # Output
   # SELECT 
   #   COUNT(*) AS count,
   #   AVG(pclass) AS avg_pclass,
   #   AVG(survived) AS avg_survived,
   #   AVG(age) AS avg_age,
   #   ...
   # FROM titanic

With VastOrbit, you can solve ML problems with few lines of code:

.. code-block:: python

   from vastorbit.machine_learning.linear_model import LogisticRegression
   from vastorbit.machine_learning.model_selection.model_validation import cross_validate

   # Data Preparation
   vdf["sex"].label_encode()["boat"].fillna(method="0ifnull")["name"].str_extract(
       " ([A-Za-z]+)\."
   ).eval("family_size", expr="parch + sibsp + 1").drop(
       columns=["cabin", "body", "ticket", "home.dest"]
   )[
       "fare"
   ].fill_outliers().fillna()

   # Model Training and Evaluation
   model = LogisticRegression()
   
   cross_validate(
       model,
       vdf,
       X=["age", "family_size", "sex", "pclass", "fare", "boat"],
       y="survived",
       cv=5,
   )

.. raw:: html

   <p align="center">
   <!-- TODO: Add cross-validation results screenshot -->
   <img src="path/to/cross-validation.png" width="100%">
   </p>

Train and deploy the model:

.. code-block:: python

   # Train the model
   model.fit(
       vdf, 
       X=["age", "family_size", "sex", "pclass", "fare", "boat"], 
       y="survived"
   )
   
   # Feature importance
   model.features_importance()

.. raw:: html

   <p align="center">
   <!-- TODO: Add feature importance screenshot -->
   <img src="path/to/feature-importance.png" width="80%">
   </p>

ROC Curve:

.. code-block:: python

   # ROC Curve
   model.roc_curve()

.. raw:: html

   <p align="center">
   <!-- TODO: Add ROC curve screenshot -->
   <img src="path/to/roc-curve.png" width="80%">
   </p>

The model is now deployed in the database and ready for high-performance predictions!

Enjoy!

=================
Help and Support
=================

For contribution guidelines and additional support documentation, please refer to the project documentation.

For questions and community support, join our Slack channel: **vastsupport.slack.com**