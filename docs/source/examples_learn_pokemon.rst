.. _examples.learn.pokemon:

Pokemon
========

This example uses the ``pokemons`` and ``combats`` datasets to predict the winner of a 1-on-1 Pokemon battle. You can download the two datasets:

`pokemons <https://github.com/vast-data/Orbit/tree/master/examples/learn/pokemon/pokemons.csv>`__

- **Name:** The name of the Pokemon.
- **Generation:** Pokemon's generation.
- **Legendary:** True if the Pokemon is legendary.
- **HP:** Number of hit points.
- **Attack:** Attack stat.
- **Sp_Atk:** Special attack stat.
- **Defense:** Defense stat.
- **Sp_Def:** Special defense stat.
- **Speed:** Speed stat.
- **Type_1:** Pokemon's first type.
- **Type_2:** Pokemon's second type.

`fights <https://github.com/vast-data/Orbit/tree/master/examples/learn/pokemon/fights.csv>`__

- **First_pokemon:** Pokemon of trainer 1.
- **Second_pokemon:** Pokemon of trainer 2.
- **Winner:** Winner of the battle.

We will follow the data science cycle (Data Exploration - Data Preparation - Data Modeling - Model Evaluation - Model Deployment) to solve this problem.

Initialization
---------------

This example uses the following version of vastorbit:

.. ipython:: python
    
    import vastorbit as vo
    
    vo.__version__

Connect to VAST. This example uses an existing connection called ``VASTDSN`` . 
For details on how to create a connection, see the :ref:`connection` tutorial.
You can skip the below cell if you already have an established connection.

.. code-block:: python
    
    vo.connect("VASTDSN")

Let's ingest the datasets.

.. code-block:: python
    
    combats = vo.read_csv("fights.csv")
    combats

.. ipython:: python
    :suppress:

    try:
        combats = vo.read_csv("SPHINX_DIRECTORY/source/_static/website/examples/data/pokemon/fights.csv")
    except:
        combats = vo.VastFrame("fights")
    res = combats
    html_file = open("SPHINX_DIRECTORY/figures/examples_combats_table.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_combats_table.html

.. code-block:: python

    pokemons = vo.read_csv("pokemons.csv")
    pokemons

.. ipython:: python
    :suppress:

    try:
        pokemons = vo.read_csv("SPHINX_DIRECTORY/source/_static/website/examples/data/pokemon/pokemons.csv")
    except:
        pokemons = vo.VastFrame("pokemons")
    res = pokemons
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_table_2.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_table_2.html

Data Exploration and Preparation
---------------------------------

The table ``combats`` will be joined to the table ``pokemons`` to predict the winner.

The ``pokemons`` table contains the information on each Pokemon. Let's describe this table.

.. code-block:: python

    pokemons.describe(method = "categorical", unique = True)

.. ipython:: python
    :suppress:

    res = pokemons.describe(method = "categorical", unique = True)
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_table_describe.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_table_describe.html

The pokemons's ``Name``, ``Generation``, and whether or not it's ``Legendary`` will never influence the outcome of the battle, so we can drop these columns.

.. code-block:: python

    pokemons.drop(
        [
            "Generation", 
            "Legendary", 
            "Name",
        ]
    )

.. ipython:: python
    :suppress:

    res = pokemons.drop(
        [
            "Generation", 
            "Legendary", 
            "Name",
        ]
    )
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_table_drop.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_table_drop.html

The ``ID`` will be the key to join the data. By joining the data, we will be able to create more relevant features.

.. ipython:: python

    fights = pokemons.join(
        combats, 
        on = {"ID": "First_Pokemon"}, 
        how = "inner",
        expr1 = [
            "Sp_Atk AS Sp_Atk_1", 
            "Speed AS Speed_1", 
            "Sp_Def AS Sp_Def_1", 
            "Defense AS Defense_1", 
            "Type_1 AS Type_1_1", 
            "Type_2 AS Type_2_1", 
            "HP AS HP_1",  
            "Attack AS Attack_1",
        ],
        expr2 = [
            "First_Pokemon", 
            "Second_Pokemon", 
            "Winner",
        ]).join(pokemons, 
        on = {"Second_Pokemon": "ID"}, 
        how = "inner",
        expr2 = [
            "Sp_Atk AS Sp_Atk_2", 
            "Speed AS Speed_2", 
            "Sp_Def AS Sp_Def_2", 
            "Defense AS Defense_2", 
            "Type_1 AS Type_1_2", 
            "Type_2 AS Type_2_2", 
            "HP AS HP_2", 
            "Attack AS Attack_2",
        ],
        expr1 = 
            [
                "Sp_Atk_1", 
                "Speed_1", 
                "Sp_Def_1", 
                "Defense_1", 
                "Type_1_1", 
                "Type_2_1", 
                "HP_1", 
                "Attack_1", 
                "Winner", 
                "Second_pokemon",
            ]
    )

Features engineering is the key. Here, we can create features that describe the stat differences between the first and second Pokemon. We can also change ``winner`` to a binary value: 1 if the first pokemons won and 0 otherwise.

.. ipython:: python
    
    import vastorbit.sql.functions as fun
    
    fights["Sp_Atk_diff"] = fights["Sp_Atk_1"] - fights["Sp_Atk_2"]
    fights["Speed_diff"] = fights["Speed_1"] - fights["Speed_2"]
    fights["Sp_Def_diff"] = fights["Sp_Def_1"] - fights["Sp_Def_2"]
    fights["Defense_diff"] = fights["Defense_1"] - fights["Defense_2"]
    fights["HP_diff"] = fights["HP_1"] - fights["HP_2"]
    fights["Attack_diff"] = fights["Attack_1"] - fights["Attack_2"]
    fights["Winner"] = fun.case_when(fights["Winner"] == fights["Second_pokemon"], 0, 1)
    fights = fights[
        [
            "Sp_Atk_diff",
            "Speed_diff",
            "Sp_Def_diff", 
            "Defense_diff",
            "HP_diff",
            "Attack_diff", 
            "Type_1_1",
            "Type_1_2",
            "Type_2_1",
            "Type_2_2", 
            "Winner",
        ]
    ]

Missing values can not be handled by most machine learning models. Let's see which features we should impute.

.. code-block:: python

    fights.count()

.. ipython:: python
    :suppress:

    res = fights.count()
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_table_clean_1.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_table_clean_1.html

In terms of missing values, our only concern is the Pokemon's second type (``Type_2_1`` and ``Type_2_2``). Since some Pokemon only have one type, these features are MNAR (missing values not at random). We can impute the missing values by creating another category.

.. code-block:: python

    fights["Type_2_1"].fillna("No")
    fights["Type_2_2"].fillna("No")

.. ipython:: python
    :suppress:

    fights["Type_2_1"].fillna("No")
    res = fights["Type_2_2"].fillna("No")
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_table_clean_2.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_table_clean_2.html

Let's use a one hot encoder to get numerical dummies out of the different types.

.. code-block:: python

    fights["Type_1_1"].one_hot_encode()
    fights["Type_1_2"].one_hot_encode()
    fights["Type_2_1"].one_hot_encode()
    fights["Type_2_2"].one_hot_encode()

.. ipython:: python
    :suppress:

    fights["Type_1_1"].one_hot_encode()
    fights["Type_1_2"].one_hot_encode()
    fights["Type_2_1"].one_hot_encode()
    res = fights["Type_2_2"].one_hot_encode()
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_table_clean_2.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_table_clean_2.html

Let's use the current_relation method to see how our data preparation so far on the :py:mod:`~vastorbit.VastFrame` generates SQL code.

.. ipython:: python

    print(fights.current_relation())

vastorbit will remember your modifications and always generate an up-to-date SQL query.

Let's look at the correlations between all the variables.

.. code-block:: python

    fights.corr(method = "spearman")

.. ipython:: python
    :suppress:

    import vastorbit
    vastorbit.set_option("plotting_lib", "plotly")
    fig = fights.corr(method = "spearman")
    fig.write_html("SPHINX_DIRECTORY/figures/examples_pokemons_corr.html")

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_corr.html

Many variables are correlated to the response column. We have enough information to create our predictive model.

Machine Learning
-----------------

Let's create a ``LogisticRegression`` to see the importance of the features in the final result.

.. code-block:: python

    from vastorbit.machine_learning.vast import LogisticRegression
    from vastorbit.machine_learning.model_selection import cross_validate

    predictors = fights.get_columns(exclude_columns = ["Winner", "Type_1_1", "Type_1_2", "Type_2_1", "Type_2_2"])
    model = LogisticRegression(max_iter=1000)
    cross_validate(model, fights, predictors, "Winner")

.. ipython:: python
    :suppress:
    :okwarning:

    from vastorbit.machine_learning.vast import RandomForestClassifier
    from vastorbit.machine_learning.model_selection import cross_validate

    predictors = fights.get_columns(exclude_columns = ["Winner", "Type_1_1", "Type_1_2", "Type_2_1", "Type_2_2"])
    model = LogisticRegression(max_iter=1000)
    res = cross_validate(model, fights, predictors, "Winner")
    html_file = open("SPHINX_DIRECTORY/figures/examples_pokemons_cv.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_cv.html

We have an excellent model with an average ``AUC`` of more than ``99%``. Let's create a model with the entire dataset and look at the importance of each feature.

.. code-block:: python

    model.fit(
        fights,
        predictors, 
        "Winner",
    )
    model.features_importance()

.. ipython:: python
    :suppress:
    :okwarning:

    model.fit(
        fights,
        predictors, 
        "Winner",
    )
    fig = model.features_importance()
    fig.write_html("SPHINX_DIRECTORY/figures/examples_pokemons_feature_importances_ml.html")

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/examples_pokemons_feature_importances_ml.html

Based on our model, it seems that a Pokemon's speed and attack stats are the strongest predictors for the winner of a battle.

Conclusion
-----------

We've solved our problem in a pandas-like way, all without ever loading data into memory!

.. ipython:: python
   :suppress:

   from vastorbit._utils._sql._sys import purge_memory
   purge_memory()