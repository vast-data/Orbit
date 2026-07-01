.. _user_guide.full_stack.train_test_split:

=================
Train Test Split
=================

Before you test a supervised model, you'll need separate, non-overlapping sets for training and testing.

In vastorbit, the :py:func:`~vastorbit.VastFrame.train_test_split` method uses a random number generator to assign each row to either the training or the testing set, ensuring that the two sets never overlap.

.. ipython:: python

    from vastorbit.datasets import load_titanic

    titanic = load_titanic()
    # LinearRegression is ``scikit-learn`` backed and rejects NaN, so we drop rows
    # with missing values in the columns we model on before splitting.
    titanic = titanic.dropna(columns = ["age", "fare", "survived"])
    train, test = titanic.train_test_split()

.. ipython:: python

    titanic.shape()

.. ipython:: python

    train.shape()

.. ipython:: python

    test.shape()

Because the split is driven by a random assignment, it depends on the order in which the rows are processed. If your data isn't sorted by a unique (or near-unique) feature, the same row could end up in a different set from one run to the next. To make the split consistent and reproducible, pass the ``order_by`` parameter so the rows are processed in a deterministic order.

.. ipython:: python

    train, test = titanic.train_test_split(order_by = {"fare": "asc"})

Even if ``fare`` has duplicates, ordering the data this way drastically decreases the likelihood of a collision.

Let's create a model and evaluate it.

.. ipython:: python

    from vastorbit.machine_learning.vast import LinearRegression

    model = LinearRegression()

When fitting the model with the :py:func:`~vastorbit.machine_learning.vast.LinearRegression.fit` method, you can use the parameter ``test_relation`` to score your data on a specific relation.

.. ipython:: python

    model.fit(
        train,
        ["age", "fare"],
        "survived",
        test,
    )

.. code-block:: ipython

    model.report()

.. ipython:: python
    :suppress:
    :okwarning:

    res = model.report()
    html_file = open("SPHINX_DIRECTORY/figures/ug_fs_table_tts_4.html", "w")
    html_file.write(res._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/ug_fs_table_tts_4.html

All model evaluation abstractions will now use the test relation for the scoring. After that, you can evaluate the efficiency of your model.

.. ipython:: python
   :suppress:

   from vastorbit._utils._sql._sys import purge_memory
   purge_memory()