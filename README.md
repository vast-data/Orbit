<p align="center">
<img src='https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/vo_logo.png' width="480px">
</p>

> **Beta:** VAST Orbit `0.1.x` is the first beta release series. The API and features will change as we work toward a stable `1.0.0`. See [Project Status & Roadmap](#project-status--roadmap).

# VAST Orbit

[![PyPI version](https://badge.fury.io/py/vastorbit.svg)](https://badge.fury.io/py/vastorbit)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/vastorbit?color=yellowgreen)](https://anaconda.org/conda-forge/vastorbit)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)](https://www.python.org/downloads/)
[![codecov](https://codecov.io/gh/vastdata-dev/vastorbit/branch/main/graph/badge.svg?token=a6GiFYI9at)](https://codecov.io/gh/vastdata-dev/vastorbit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

## Trailer Video

<p align="center">
  <a href="https://github.com/vastdata-dev/VastOrbit/blob/main/docs/source/_static/website/video/vastorbit_trailer_med.mp4">
    <img src="docs/source/_static/website/video/vastorbit_intro_poster.png"
         width="100%" alt="VAST Orbit — Trailer (click to watch)">
  </a>
</p>

VAST Orbit is a Python library with scikit-learn-like functionality for conducting data science projects on data stored in VAST Database. Train models using familiar scikit-learn syntax and deploy them directly in the database, leveraging VAST's high-performance analytics capabilities. VAST Orbit offers robust support for the entire data science life cycle, uses a 'pipeline' mechanism to sequentialize data transformation operations, and provides beautiful graphical options.

## Table of Contents
- [Introduction](#introduction)
- [Project Status & Roadmap](#project-status--roadmap)
- [Installation](#installation)
- [Connecting to the Database](#connecting-to-the-database)
- [Documentation](#documentation)
- [Highlighted Features](#highlighted-features)
  - [Themes - Dark | Light](#themes---dark--light)
  - [SQL Magic](#sql-magic)
  - [SQL Plots](#sql-plots)
  - [Python and SQL Combo](#python-and-sql-combo)
  - [Charts](#charts)
  - [Complete Machine Learning Pipeline](#complete-machine-learning-pipeline)
- [Quickstart](#quickstart)
- [Help and Support](#help-and-support)

## Introduction

VAST Database combines enterprise-grade storage with powerful analytics capabilities. Today, VAST Orbit leverages Trino as the SQL engine to deliver exceptional performance for data science workloads at scale. Soon, we will support the VAST SQL Engine (currently in development), which will provide even greater speed through VAST's columnar-optimized format. However, SQL alone isn't flexible enough to meet the evolving needs of modern data scientists.

Python has become the lingua franca of data science, offering unparalleled flexibility through its high-level abstraction and an extensive ecosystem of libraries. The accessibility of Python has led to the development of powerful APIs like pandas and scikit-learn, supported by a vibrant community of data scientists worldwide. Unfortunately, traditional Python tools operate in-memory as single-node processes, creating fundamental limitations when working with large-scale data. While distributed computing frameworks attempt to address these constraints, they still require moving data for processing—an approach that is prohibitively expensive and increasingly impractical in the modern data landscape. On top of these challenges, data scientists face additional complexity in deploying and operationalizing their models. The entire workflow is time-consuming and inefficient.

**VAST Orbit solves these problems**. The concept is elegant: instead of moving data to compute, VAST Orbit brings the compute logic to where the data lives—in VAST Database. Train your models using familiar scikit-learn syntax in Python, then deploy them directly in the database for high-performance predictions at scale.

### Main Advantages

- **Easy Data Exploration**: Interactive exploration of massive datasets without memory constraints
- **Fast Data Preparation**: Leverage Trino's distributed processing for rapid data transformation
- **Familiar Scikit-learn API**: Train models using the scikit-learn interface you already know
- **In-Database Deployment**: Deploy trained models directly in VAST Database for production workloads _(with some current limitations — see [Project Status & Roadmap](#project-status--roadmap))_
- **Easy Model Evaluation**: Comprehensive model evaluation tools with visual insights
- **Seamless SQL Integration**: Use Python or SQL interchangeably based on your preference and use case

<p align="center">
<!-- TODO: Add architecture diagram -->
<img src='https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/architecture.png' width="92%">
</p>

## Project Status & Roadmap

VAST Orbit is **beta** software (the `0.1.x` series). It is evolving quickly, and we expect **multiple iterations before a stable `1.0.0`** — including occasional breaking changes to the API, defaults, and behavior as the library matures.

A few things to keep in mind at this stage:

- **Training back-end.** As of now, **most machine-learning models are trained with scikit-learn** (in-memory). Trained models can then be **deployed in-database** for prediction — though in-database deployment currently has **some limitations for certain algorithms**. Native in-database training is on the roadmap.
- **In-database ML maturity.** Some of the **in-database ML capabilities are still beta** and under active validation; their coverage and behavior will keep improving across releases.
- **Indicative roadmap.** Priorities and timelines are **indicative and may change based on user feedback and incoming requests**.
- **Toward 1.0.0.** Expect the API surface, defaults, and feature set to keep maturing until the `1.0.0` milestone.

Your feedback directly shapes what we build next — see [Help and Support](#help-and-support).

## Installation

To install VAST Orbit with pip:

```shell
# Latest release version
pip3 install vastorbit[all]

# Latest commit on main branch
pip3 install git+https://github.com/vastdata-dev/vastorbit.git@main
```

To install VAST Orbit from source, run the following command from the root directory:

```shell
python3 setup.py install
```

## Connecting to the Database

VAST Orbit currently connects to VAST Database through Trino. Ensure you have Trino set up and configured to access your VAST Database instance.

Connection example:

```python
import vastorbit as vo

vo.new_connection({
    "host": "your-trino-host", 
    "port": "8080", 
    "database": "your_database", 
    "user": "your_username"},
    name="VAST_Connection")
```

Use the connection:

```python
vo.connect("VAST_Connection")
```

For more details on connection configuration, refer to the documentation.

## Documentation

The easiest and most accurate way to find documentation for a particular function is to use the help function:

```python
import vastorbit as vo

help(vo.VastFrame)
```

Documentation can be generated locally. Refer to the documentation generation guide in the `docs/` directory.

Official documentation will be available soon at a dedicated documentation site.

## Highlighted Features

### Themes - Dark | Light

VAST Orbit offers users the flexibility to customize their coding experience with two visually appealing themes: **Dark** and **Light**.

Dark mode, ideal for extended coding sessions, features a sleek and stylish dark color scheme, providing a comfortable and eye-friendly environment.

<p align="center">
<!-- TODO: Add dark theme screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/dark-theme-screenshot.png" width="100%">
</p>

On the other hand, Light mode serves as the default theme, offering a clean and bright interface for users who prefer a traditional coding ambiance.

<p align="center">
<!-- TODO: Add light theme screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/light-theme-screenshot.png" width="100%">
</p>

Theme can be easily switched by:

```python
import vastorbit as vo

vo.set_option("theme", "dark")  # can be switched to 'light'
```

VAST Orbit's theme-switching option ensures that users can tailor their experience to their preferences, making data exploration and analysis a more personalized and enjoyable journey.

### SQL Magic

You can use VAST Orbit to execute SQL queries directly from a Jupyter notebook.

#### Example

Load the SQL extension:

```python
%load_ext vastorbit.sql
```

Execute your SQL queries:

```sql
%%sql
SELECT version();
```

<p align="center">
<!-- TODO: Add light theme screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/sql_version.png" width="15%">
</p>

### SQL Plots

You can create interactive, professional plots directly from SQL.

To create plots, simply provide the type of plot along with the SQL command.

#### Example

```python
%load_ext vastorbit.jupyter.extensions.chart_magic
%chart -k pie -c "SELECT pclass, AVG(age) AS avg_age FROM titanic GROUP BY 1;"
```

<p align="center">
<!-- TODO: Add SQL plot screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/sql-plot-screenshot.png" width="90%">
</p>

### Python and SQL Combo

VAST Orbit has a unique place in the market because it allows users to use Python and SQL in the same environment.

#### Example

```python
import vastorbit as vo

selected_titanic = vo.VastFrame(
    "SELECT pclass, embarked, survived FROM titanic"
)
selected_titanic.groupby(columns=["pclass"], expr=["AVG(survived) AS avg_survived"])
```

<p align="center">
<!-- TODO: Add SQL plot screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/select_gb.png" width="30%">
</p>

### Charts

VAST Orbit comes integrated with two popular plotting libraries: matplotlib and plotly.

A gallery of VAST Orbit-generated charts will be available in the documentation.

<p align="center">
<!-- TODO: Add charts gallery screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/charts-gallery.png" width="100%">
</p>

### Complete Machine Learning Pipeline

#### Data Ingestion

VAST Orbit allows users to ingest data from a diverse range of file formats including CSV, JSON, and more formats coming in the future. VAST Orbit automatically infers data types during ingestion, though the inferred types may not always be optimal for your specific use case.

CSV Example:

```python
import vastorbit as vo

vo.read_csv(
    "/path/to/your/data.csv",
    table_name="my_table",
)
```

JSON Example:

```python
import vastorbit as vo

vo.read_json(
    "/path/to/your/data.json",
    table_name="my_table",
)
```

> **Note:** VAST Orbit performs automatic type inference during data ingestion. However, the automatically inferred data types may not always be optimal for your specific use case. You can explicitly specify data types if needed.

#### Data Exploration

VAST Orbit provides extensive options for descriptive and visual exploration.

Scatter Plot Example:

```python
from vastorbit.datasets import load_iris

iris_data = load_iris()
iris_data.scatter(
    ["SepalWidthCm", "SepalLengthCm", "PetalLengthCm"], 
    by="Species", 
    max_nb_points=30
)
```

<p align="center">
<!-- TODO: Add scatter plot screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/scatter-plot.png" width="70%">
</p>

The **Correlation Matrix** is fast and convenient to compute. Users can choose from a wide variety of correlations, including Cramer, Spearman, Pearson, etc.

```python
from vastorbit.datasets import load_titanic

titanic = load_titanic()
titanic.corr(method="spearman")
```

<p align="center">
<!-- TODO: Add correlation matrix screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/correlation-matrix.png" width="70%">
</p>

By turning on the SQL print option, users can see and copy SQL queries:

```python
from vastorbit import set_option

set_option("sql_on", True)
```

VAST Orbit allows users to calculate a focused correlation using the "focus" parameter:

```python
titanic.corr(method="spearman", focus="survived")
```

<p align="center">
<!-- TODO: Add focused correlation screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/focused-correlation.png" width="50%">
</p>

#### Data Preparation

VAST Orbit provides comprehensive data preparation capabilities including joining tables, encoding categorical variables, and filling missing values. Refer to the documentation for detailed examples.

Outlier Detection Example:

```python
import random
import vastorbit as vo

data = vo.VastFrame({"Heights": [random.randint(10, 60) for _ in range(40)] + [100]})
data.outliers_plot(columns="Heights")
```

<p align="center">
<!-- TODO: Add outliers plot screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/outliers-plot.png" width="70%">
</p>

#### Machine Learning

VAST Orbit's machine learning capabilities let you build models using the familiar scikit-learn API and evaluate them with rich, visual tooling. VAST Orbit supports a wide array of algorithms including time series forecasting, clustering, regression, and classification.

**Key idea: build with scikit-learn syntax, then deploy in-database for predictions.**

> **Note (beta):** As of now, **most models are trained using scikit-learn** (in-memory) and can then be **deployed in-database** for prediction. In-database deployment is available for many algorithms but carries **some limitations depending on the model**, and a number of **in-database ML features are still beta**. Native in-database training is planned. See [Project Status & Roadmap](#project-status--roadmap).

Example with Logistic Regression:

```python
from vastorbit.machine_learning.model_selection.model_validation import cross_validate
from vastorbit.machine_learning.vast import LogisticRegression

# Imputing missing values
titanic_vd.fillna()

# Create and evaluate model
model = LogisticRegression()

cross_validate(
    model,
    titanic_vd,
    X=["age", "fare", "parch", "pclass"],
    y="survived",
    cv=5,
)
```

<p align="center">
<!-- TODO: Add model evaluation screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/model-evaluation.png" width="100%">
</p>

### Loading Predefined Datasets

VAST Orbit provides some predefined datasets that can be easily loaded for testing and learning. These datasets include the iris dataset, titanic dataset, and more.

There are two ways to access the provided datasets:

(1) Use the standard Python method:

```python
from vastorbit.datasets import load_iris

iris_data = load_iris()
```

<p align="center">
<!-- TODO: Add model evaluation screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/iris-dataset.png" width="70%">
</p>

(2) Use the standard name of the dataset from the schema:

```python
import vastorbit as vo

iris_data = vo.VastFrame(input_relation="public.iris")
```

<p align="center">
<!-- TODO: Add model evaluation screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/iris-dataset.png" width="70%">
</p>

## Quickstart

Install the library with pip:

```shell
pip3 install vastorbit[all]
```

Create a new VAST connection through Trino:

```python
import vastorbit as vo

vo.new_connection({
    "host": "your-trino-host", 
    "port": "8080", 
    "database": "your_database", 
    "user": "your_username"},
    name="VAST_Connection")
```

Use the newly created connection:

```python
vo.connect("VAST_Connection")
```

Create a VastFrame from your data:

```python
from vastorbit import VastFrame

vdf = VastFrame("database.schema.my_table")
```

Load a sample dataset:

```python
from vastorbit.datasets import load_titanic

vdf = load_titanic()
```

<p align="center">
<!-- TODO: Add model evaluation screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/light-theme-screenshot.png" width="100%">
</p>

Examine your data:

```python
vdf.describe()
```

<p align="center">
<!-- TODO: Add describe output screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/describe-output.png" width="100%">
</p>

Print the SQL query with `set_option`:

```python
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
```

With VAST Orbit, you can solve ML problems with few lines of code:

```python
from vastorbit.machine_learning.vast import LogisticRegression
from vastorbit.machine_learning.model_selection.model_validation import cross_validate

# Data Preparation
vdf["sex"].label_encode()["boat"].fillna(method="0ifnull")["name"].str_extract(
    r" ([A-Za-z]+)\."
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
```

<p align="center">
<!-- TODO: Add cross-validation results screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/cross-validation.png" width="100%">
</p>

Train and deploy the model:

```python
# Train the model
model.fit(
    vdf, 
    X=["age", "family_size", "sex", "pclass", "fare", "boat"], 
    y="survived"
)

# Feature importance
model.features_importance()
```

<p align="center">
<!-- TODO: Add feature importance screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/feature-importance.png" width="100%">
</p>

ROC Curve:

```python
# ROC Curve
model.roc_curve()
```

<p align="center">
<!-- TODO: Add ROC curve screenshot -->
<img src="https://github.com/vastdata-dev/VastOrbit/blob/main/assets/img/roc-curve.png" width="70%">
</p>

Once trained, the model can be deployed in the database for high-performance predictions _(in-database deployment availability and limitations vary by algorithm — see [Project Status & Roadmap](#project-status--roadmap))_.

Enjoy!

## Help and Support

For contribution guidelines and additional support documentation, please refer to the project documentation.

For questions and community support, join our Slack channel: [![Slack](https://img.shields.io/badge/Slack-VAST%20Support-4A154B?logo=slack&logoColor=white)](https://vastsupport.slack.com)