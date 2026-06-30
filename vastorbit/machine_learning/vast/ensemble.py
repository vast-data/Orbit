"""
SPDX-License-Identifier: Apache-2.0
"""

import secrets
from typing import Literal, Optional, Union
import numpy as np
import sklearn

from vastorbit.connection.errors import MissingRelation, QueryError

from vastorbit._typing import (
    NoneType,
    PlottingObject,
    PythonNumber,
    SQLColumns,
    SQLRelation,
)
from vastorbit.errors import ModelError
from vastorbit._utils._gen import gen_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import clean_query, format_type, quote_ident
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.core.vastframe.base import VastFrame

import vastorbit.machine_learning.memmodel as mm
from vastorbit.machine_learning.vast.base import (
    MulticlassClassifier,
    Regressor,
    Tree,
)
from vastorbit.machine_learning.vast.cluster import Clustering

"""
General Classes.
"""


class RandomForest(Tree):
    """
    :py:class:`~vastorbit.machine_learning.vast.base.Tree`
    implementation of Random Forest.

    .. note::

        Refer to
        :py:class:`~vastorbit.machine_learning.vast.ensemble.RandomForestRegressor`
        for more information on Regression models. And refer to
        :py:class:`~vastorbit.machine_learning.vast.ensemble.RandomForestClassifier`
        for more information on Classification models.
    """


class GradientBoosting(Tree):
    """
    :py:class:`~vastorbit.machine_learning.vast.base.Tree`
    implementation of GradientBoosting.


    .. note::

        Refer to
        :py:class:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingRegressor`
        for more information on Regression models. And refer to
        :py:class:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingClassifier`
        for more information on Classification models.
    """

    # Attributes Methods.

    def _compute_prior(self) -> Union[float, list[float]]:
        """
        Returns the ``GradientBoosting`` priors.

        Returns
        -------
        float / list
            GradientBoosting priors.
        """
        condition = [f"{x} IS NOT NULL" for x in self.X] + [f"{self.y} IS NOT NULL"]
        query = f"""
            SELECT 
                /*+LABEL('learn.ensemble.GradientBoosting._compute_prior')*/ 
                {{}}
            FROM {self.input_relation} 
            WHERE {' AND '.join(condition)}{{}}"""
        if self._model_type == "GradientBoostingRegressor" or (
            len(self.classes_) == 2 and self.classes_[1] == 1 and self.classes_[0] == 0
        ):
            prior_ = _executeSQL(
                query=query.format(f"AVG({self.y})", ""),
                method="fetchfirstelem",
                print_time_sql=False,
            )
        else:
            prior_ = np.array([0.0 for p in self.classes_])
        return prior_

    # I/O Methods.

    def _to_json_tree_dict(self, tree_id: int, c: str = None) -> dict:
        """
        Method used to convert the model to JSON.
        """
        tree = self.get_tree(tree_id)
        attributes = self._compute_trees_arrays(tree, self.X)
        n_nodes = len(attributes[0])
        split_conditions = []
        parents = [0 for i in range(n_nodes)]
        parents[0] = min(secrets.randbelow(1000000000) + n_nodes + 1, 999999999)
        for i in range(n_nodes):
            left_child = attributes[0][i]
            right_child = attributes[1][i]
            if left_child != right_child:
                parents[left_child] = i
                parents[right_child] = i
            if attributes[5][i]:
                split_conditions += [attributes[3][i]]
            elif isinstance(attributes[5][i], NoneType):
                lr = self.parameters["learning_rate"]
                if self._model_type == "GradientBoostingRegressor":
                    split_conditions += [float(attributes[4][i]) * lr]
                else:
                    # GB classifier leaves carry a log-odds contribution stored
                    # as a "class:value,..." string. Parse it and pick the class
                    # for this tree; gradient-boosting regression trees hold a
                    # single contribution value (and the stored key is not always
                    # the target class), so fall back to that value when the
                    # exact class key is absent.
                    raw = attributes[6][i]
                    log_odds_map = {}
                    if raw:
                        for pair in str(raw).split(","):
                            key_part, _, val_part = pair.partition(":")
                            log_odds_map[key_part] = float(val_part)
                    if (
                        len(self.classes_) == 2
                        and self.classes_[1] == 1
                        and self.classes_[0] == 0
                    ):
                        wanted = "1"
                    else:
                        wanted = str(c)
                    value = log_odds_map.get(wanted)
                    if value is None:
                        value = next(iter(log_odds_map.values()), 0.0)
                    split_conditions += [lr * value]
            else:
                split_conditions += [float(attributes[3][i])]
        return {
            "base_weights": [0.0 for i in range(n_nodes)],
            "categories": [],
            "categories_nodes": [],
            "categories_segments": [],
            "categories_sizes": [],
            "default_left": [True for i in range(n_nodes)],
            "id": tree_id,
            "left_children": [-1 if x is None else x for x in attributes[0]],
            "loss_changes": [0.0 for i in range(n_nodes)],
            "parents": parents,
            "right_children": [-1 if x is None else x for x in attributes[1]],
            "split_conditions": split_conditions,
            "split_indices": [0 if x is None else x for x in attributes[2]],
            "split_type": [int(x) if isinstance(x, bool) else 0 for x in attributes[5]],
            "sum_hessian": [0.0 for i in range(n_nodes)],
            "tree_param": {
                "num_deleted": "0",
                "num_feature": str(len(self.X)),
                "num_nodes": str(n_nodes),
                "size_leaf_vector": "0",
            },
        }

    def _to_json_tree_dict_list(self) -> dict:
        """
        Method used to convert the model to JSON.
        """
        if self._model_type == "GradientBoostingClassifier" and (
            len(self.classes_) > 2 or self.classes_[1] != 1 or self.classes_[0] != 0
        ):
            trees = []
            for i in range(self.n_estimators_):
                for c in self.classes_:
                    trees += [self._to_json_tree_dict(i, str(c))]
            tree_info = [i for i in range(len(self.classes_))] * self.n_estimators_
            for idx, tree in enumerate(trees):
                tree["id"] = idx
        else:
            trees = [self._to_json_tree_dict(i) for i in range(self.n_estimators_)]
            tree_info = [0 for i in range(self.n_estimators_)]
        return {
            "model": {
                "trees": trees,
                "tree_info": tree_info,
                "gbtree_model_param": {
                    "num_trees": str(len(trees)),
                    "size_leaf_vector": "0",
                },
            },
            "name": "gbtree",
        }

    def _to_json_learner(self) -> dict:
        """
        Method used to convert the model to JSON.
        """
        if self._model_type == "GradientBoostingRegressor" or (
            len(self.classes_) == 2 and self.classes_[1] == 1 and self.classes_[0] == 0
        ):
            bs, num_class, param, param_val = (
                self.mean_,
                "0",
                "reg_loss_param",
                {"scale_pos_weight": "1"},
            )
            if self._model_type == "GradientBoostingRegressor":
                objective = "reg:squarederror"
                attributes_dict = {
                    "scikit_learn": '{"n_estimators": '
                    + str(self.n_estimators_)
                    + ', "objective": "reg:squarederror", "max_depth": '
                    + str(self.parameters["max_depth"])
                    + ', "learning_rate": '
                    + str(self.parameters["learning_rate"])
                    + ', "verbosity": null, "booster": null, "tree_method": null,'
                    + ' "gamma": null, "min_child_weight": null, "max_delta_step":'
                    + ' null, "subsample": null, "colsample_bytree": '
                    + str(self.parameters["col_sample_by_tree"])
                    + ', "colsample_bylevel": null, "colsample_bynode": '
                    + str(self.parameters["col_sample_by_node"])
                    + ', "reg_alpha": null, "reg_lambda": null, "scale_pos_weight":'
                    + ' null, "base_score": null, "missing": NaN, "num_parallel_tree"'
                    + ': null, "kwargs": {}, "random_state": null, "n_jobs": null, '
                    + '"monotone_constraints": null, "interaction_constraints": null,'
                    + ' "importance_type": "gain", "gpu_id": null, "validate_parameters"'
                    + ': null, "_estimator_type": "regressor"}'
                }
            else:
                objective = "binary:logistic"
                attributes_dict = {
                    "scikit_learn": '{"use_label_encoder": true, "n_estimators": '
                    + str(self.n_estimators_)
                    + ', "objective": "binary:logistic", "max_depth": '
                    + str(self.parameters["max_depth"])
                    + ', "learning_rate": '
                    + str(self.parameters["learning_rate"])
                    + ', "verbosity": null, "booster": null, "tree_method": null,'
                    + ' "gamma": null, "min_child_weight": null, "max_delta_step":'
                    + ' null, "subsample": null, "colsample_bytree": '
                    + str(self.parameters["col_sample_by_tree"])
                    + ', "colsample_bylevel": null, "colsample_bynode": '
                    + str(self.parameters["col_sample_by_node"])
                    + ', "reg_alpha": null, "reg_lambda": null, "scale_pos_weight":'
                    + ' null, "base_score": null, "missing": NaN, "num_parallel_tree"'
                    + ': null, "kwargs": {}, "random_state": null, "n_jobs": null,'
                    + ' "monotone_constraints": null, "interaction_constraints": null,'
                    + ' "importance_type": "gain", "gpu_id": null, "validate_parameters"'
                    + ': null, "classes_": [0, 1], "n_classes_": 2, "_le": {"classes_": '
                    + '[0, 1]}, "_estimator_type": "classifier"}'
                }
        else:
            objective, bs, num_class, param, param_val = (
                "multi:softprob",
                0.5,
                str(len(self.classes_)),
                "softmax_multiclass_param",
                {"num_class": str(len(self.classes_))},
            )
            attributes_dict = {
                "scikit_learn": '{"use_label_encoder": true, "n_estimators": '
                + str(self.n_estimators_)
                + ', "objective": "multi:softprob", "max_depth": '
                + str(self.parameters["max_depth"])
                + ', "learning_rate": '
                + str(self.parameters["learning_rate"])
                + ', "verbosity": null, "booster": null, "tree_method": null, '
                + '"gamma": null, "min_child_weight": null, "max_delta_step": '
                + 'null, "subsample": null, "colsample_bytree": '
                + str(self.parameters["col_sample_by_tree"])
                + ', "colsample_bylevel": null, "colsample_bynode": '
                + str(self.parameters["col_sample_by_node"])
                + ', "reg_alpha": null, "reg_lambda": null, "scale_pos_weight":'
                + ' null, "base_score": null, "missing": NaN, "num_parallel_tree":'
                + ' null, "kwargs": {}, "random_state": null, "n_jobs": null, '
                + '"monotone_constraints": null, "interaction_constraints": null, '
                + '"importance_type": "gain", "gpu_id": null, "validate_parameters":'
                + ' null, "classes_": '
                + str(list(self.classes_))
                + ', "n_classes_": '
                + str(len(self.classes_))
                + ', "_le": {"classes_": '
                + str(list(self.classes_))
                + '}, "_estimator_type": "classifier"}'
            }
        attributes_dict["scikit_learn"] = attributes_dict["scikit_learn"].replace(
            '"', "++++"
        )
        gradient_booster = self._to_json_tree_dict_list()
        return {
            "attributes": attributes_dict,
            "feature_names": [],
            "feature_types": [],
            "gradient_booster": gradient_booster,
            "learner_model_param": {
                "base_score": np.format_float_scientific(bs, precision=7).upper(),
                "num_class": num_class,
                "num_feature": str(len(self.X)),
            },
            "objective": {"name": objective, param: param_val},
        }

    def to_json(self, path: Optional[str] = None) -> Optional[str]:
        """
        Creates a Python ``GradientBoosting`` JSON file
        that can be imported into the Python
        ``GradientBoosting`` API.

        .. warning::

            For multiclass classifiers, the
            probabilities returned by the
            vastorbit and exported models
            might differ slightly because
            of normalization; while VAST
            uses multinomial ``LogisticRegression``,
            ``GradientBoosting`` Python uses Softmax.
            This difference does not affect
            the model's final predictions.
            Categorical predictors must be
            encoded.

        Parameters
        ----------
        path: str, optional
            The path and name of the
            output file. If a file with
            the same name already exists,
            the function returns an error.

        Returns
        -------
        None | str
            The content of the JSON file if
            variable ``path`` is empty.
            Otherwise, nothing is returned.

        Examples
        --------
        Let's use the wine quality dataset:

        .. ipython:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        Let's import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import GradientBoostingRegressor

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = GradientBoostingRegressor(
                n_estimators = 3,
                max_depth = 3,
                nbins = 6,
                split_proposal_method = 'global',
                tol = 0.001,
                learning_rate = 0.1,
                min_split_loss = 0,
                weight_reg = 0,
                sample = 0.7,
                col_sample_by_tree = 1,
                col_sample_by_node = 1,
            )

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(
                train,
                [
                    "fixed_acidity",
                    "volatile_acidity",
                    "citric_acid",
                    "residual_sugar",
                    "chlorides",
                    "density",
                ],
                "quality",
                test,
            )

        And export it to the JSON format.

        .. ipython:: python

            model.to_json()

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingRegressor`
            or :py:class:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingClassifier`
            for more information about the
            different methods and usages.
        """
        res = {"learner": self._to_json_learner(), "version": [1, 6, 2]}
        res = (
            str(res)
            .replace("'", '"')
            .replace("True", "true")
            .replace("False", "false")
            .replace("++++", '\\"')
        )
        if path:
            with open(path, "w+", encoding="utf-8") as f:
                f.write(res)

        else:
            return res


"""
Algorithms used for regression.
"""


class RandomForestRegressor(Regressor, RandomForest):
    """
    Creates an ``RandomForestRegressor``
    object using SKLEARN for training
    and the scalability of VASTDB for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    ``**kwargs``: SKLEARN model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``trees_``: list of BinaryTreeRegressor
        Tree models are instances of `
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeRegressor`,
        each possessing various attributes.
        For more detailed information, refer
        to the documentation for
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeRegressor`.
    ``feature_importances_``: numpy.array
        The importance of features. It is calculated
        using the MDI (Mean Decreased Impurity). To
        determine the final score, vastorbit sums the
        scores of each tree, normalizes them and applies
        an activation function to scale them.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``feature_importances_trees_``: dict of numpy.array
        Each element of the array represents the feature
        importance of tree i.
        The importance of features is calculated
        using the MDI (Mean Decreased Impurity).
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``n_estimators_``: int
        The number of model estimators.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    .. important::

        Many tree-based models inherit from the ``RandomForest``
        base class, and it's recommended to use it directly for
        access to a wider range of options.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    We import :py:mod:`vastorbit`:

    .. code-block:: python

        import vastorbit as vo

    .. hint::

        By assigning an alias to :py:mod:`vastorbit`,
        we mitigate the risk of code collisions with
        other libraries. This precaution is necessary
        because vastorbit uses commonly known function
        names like "average" and "median", which can
        potentially lead to naming conflicts. The use
        of an alias ensures that the functions from
        :py:mod:`vastorbit` are used as intended without
        interfering with functions from other libraries.

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

    .. note::

        vastorbit offers a wide range of sample
        datasets that are ideal for training
        and testing purposes. You can explore
        the full list of available datasets in
        the :ref:`api.datasets`, which provides
        detailed information on each dataset and
        how to use them effectively. These datasets
        are invaluable resources for honing your
        data analysis and machine learning skills
        within the vastorbit environment.

    You can easily divide your dataset
    into training and testing subsets
    using the
    ``VastFrame.``:py:meth:`~vastorbit.VastFrame.train_test_split`
    method. This is a crucial step when
    preparing your data for machine learning,
    as it allows you to evaluate the
    performance of your models accurately.

    .. code-block:: python

        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    .. warning::

        In this case, vastorbit utilizes seeded
        randomization to guarantee the reproducibility
        of your data split. However, please be aware
        that this approach may lead to reduced
        performance. For a more efficient data split,
        you can use the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db`
        method to save your results into ``tables``
        or ``temporary tables``. This will help
        enhance the overall performance of the
        process.

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        import vastorbit.datasets as vod
        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``RandomForestRegressor`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import RandomForestRegressor

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = RandomForestRegressor(
            n_estimators = 5,
            max_depth = 3,
        )

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(
            train,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "quality",
            test,
        )

    .. important::

        To train a model, you can directly use the
        :py:class:`~VastFrame` or the name of the
        relation stored in the database. The test
        set is optional and is only used to compute
        the test metrics. In :py:mod:`vastorbit`, we
        don't work using ``X`` matrices and ``y``
        vectors. Instead, we work directly with lists
        of predictors and the response name.

    Features Importance
    ^^^^^^^^^^^^^^^^^^^^

    We can conveniently get
    the features importance:

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_rfreg_feature.html")

    .. code-block:: python

        result = model.features_importance()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rfreg_feature.html

    .. note::

        In models such as ``RandomForest``, feature importance is calculated
        using the MDI (Mean Decreased Impurity). To determine the final score,
        vastorbit sums the scores of each tree, normalizes them and applies an
        activation function to scale them.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_rfreg_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rfreg_report.html

    .. important::

        Most metrics are computed using a single SQL query, but some of them might
        require multiple SQL queries. Selecting only the necessary metrics in the
        report can help optimize performance.
        E.g. ``model.report(metrics = ["mse", "r2"])``.

    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.ensemble.RandomForestRegressor.score`
    function to calculate various regression metrics, with the R-squared being the default.

    .. ipython:: python

        model.score()

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. ipython:: python
        :suppress:

        result = model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_rfreg_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rfreg_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.ensemble.RandomForestRegressor.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    Plots
    ^^^^^^

    Tree models can be visualized by drawing their tree plots.
    For more examples, check out :ref:`chart_gallery.tree`.

    .. code-block:: python

        model.plot_tree()

    .. ipython:: python
        :suppress:

        res = model.plot_tree()
        res.render(filename='figures/machine_learning_VAST_rfreg', format='png')


    .. image:: /../figures/machine_learning_VAST_rfreg.png

    .. note::

        The above example may not render
        properly in the doc because of the
        huge size of the tree. But it should
        render nicely in jupyter environment.

    In order to plot graph using
    `graphviz <https://graphviz.org/>`__
    separately, you can extract the
    graphviz DOT file code as follows:

    .. ipython:: python

        model.to_graphviz()

    This string can then be copied into a
    DOT file which can beparsed by graphviz.

    **Contour plot** is another useful plot
    that can be produced for models with two
    predictors.

    .. code-block:: python

        model.contour()

    .. important::

        Machine learning models with two
        predictors can usually benefit
        from their own contour plot.
        This visual representation aids
        in exploring predictions and
        gaining a deeper understanding
        of how these models perform in
        different scenarios.
        Please refer to
        :ref:`chart_gallery.contour`
        for more examples.Model Exporting

    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The following methods for exporting the model
    use ``MemModel``, and it is recommended to use
    ``MemModel`` directly.

    **To SQL**

    You can get the SQL code by:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[4.2, 0.17, 0.36, 1.8, 0.029, 0.9899]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.tree.RandomForestRegressor.to_python`
        method is used to retrieve predictions,
        probabilities, or cluster distances. For
        specific details on how to use this method
        for different model types, refer to the
        relevant documentation for each model.
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["REGRESSOR"]:
        return "REGRESSOR"

    @property
    def _model_type(self) -> Literal["RandomForestRegressor"]:
        return "RandomForestRegressor"

    @property
    def _attributes(self) -> list[str]:
        return [
            "n_estimators_",
            "trees_",
            "feature_importances_",
            "feature_importances_trees_",
            "max_depth_",
            "min_samples_split_",
            "min_samples_leaf_",
        ]

    @property
    def _sklearn_model(self) -> Literal[sklearn.ensemble.RandomForestRegressor]:
        return sklearn.ensemble.RandomForestRegressor

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from sklearn RandomForestRegressor.
        """
        # Basic attributes
        self.n_estimators_ = self._model.n_estimators
        self.n_features_ = self._model.n_features_in_

        # Feature importances
        self.feature_importances_trees_ = []
        for tree in self._model.estimators_:
            self.feature_importances_trees_.append(tree.feature_importances_)
        self.feature_importances_ = self._model.feature_importances_

        # Extract individual trees
        trees = []
        for estimator in self._model.estimators_:
            # Each estimator is a Decision Tree Regressor
            tree = estimator.tree_

            tree_d = {
                "children_left": tree.children_left.copy(),
                "children_right": tree.children_right.copy(),
                "feature": tree.feature.copy(),
                "threshold": tree.threshold.copy(),
                "value": tree.value[
                    :, 0, 0
                ].copy(),  # Shape: (n_nodes, 1, 1) -> (n_nodes,)
            }

            # Convert to float where needed
            tree_d["threshold"] = tree_d["threshold"].astype(float)
            tree_d["value"] = tree_d["value"].astype(float)

            # Create BinaryTreeRegressor model
            model = mm.BinaryTreeRegressor(**tree_d)
            trees.append(model)

        self.trees_ = trees

        # Additional useful attributes
        self.max_depth_ = self._model.max_depth
        self.min_samples_split_ = self._model.min_samples_split
        self.min_samples_leaf_ = self._model.min_samples_leaf

    # I/O Methods.

    def to_memmodel(self) -> Union[mm.RandomForestRegressor, mm.BinaryTreeRegressor]:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.ensemble.RandomForestRegressor`
            and
            :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeRegressor`
            for more information.
        """
        if self.n_estimators_ == 1:
            return self.trees_[0]
        else:
            return mm.RandomForestRegressor(self.trees_)


class GradientBoostingRegressor(Regressor, GradientBoosting):
    """
    Creates an ``GradientBoostingRegressor`` object
    using SKLEARN for training and
    the scalability of VASTDB for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    ``**kwargs``: SKLEARN model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``trees_``: list of BinaryTreeRegressor
        Tree models are instances of `
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeRegressor`,
        each possessing various attributes.
        For more detailed information, refer
        to the documentation for
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeRegressor`.
    ``feature_importances_``: numpy.array
        The importance of features. It is calculated
        using the average gain of each tree. To determine
        the final score, vastorbit sums the scores of each
        tree, normalizes them and applies an activation
        function to scale them.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``feature_importances_trees_``: dict of numpy.array
        Each element of the array represents the feature
        importance of tree i.
        The importance of features is calculated
        using the average gain of each tree.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``mean_``: float
        The mean of the response column.
    ``eta_``: float
        The learning rate, is a crucial hyperparameter in
        machine learning algorithms. It determines the step
        size at each iteration during the model training
        process. A well-chosen learning rate is essential
        for achieving optimal convergence and preventing
        overshooting or slow convergence in the training
        phase. Adjusting the learning rate is often necessary
        to strike a balance between model accuracy and
        computational efficiency.
    ``n_estimators_``: int
        The number of model estimators.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    .. important::

        Many tree-based models inherit from the ``GradientBoosting``
        base class, and it's recommended to use it directly for
        access to a wider range of options.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    We import :py:mod:`vastorbit`:

    .. code-block:: python

        import vastorbit as vo

    .. hint::

        By assigning an alias to :py:mod:`vastorbit`,
        we mitigate the risk of code collisions with
        other libraries. This precaution is necessary
        because vastorbit uses commonly known function
        names like "average" and "median", which can
        potentially lead to naming conflicts. The use
        of an alias ensures that the functions from
        :py:mod:`vastorbit` are used as intended without
        interfering with functions from other libraries.

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

    .. note::

        vastorbit offers a wide range of sample
        datasets that are ideal for training
        and testing purposes. You can explore
        the full list of available datasets in
        the :ref:`api.datasets`, which provides
        detailed information on each dataset and
        how to use them effectively. These datasets
        are invaluable resources for honing your
        data analysis and machine learning skills
        within the vastorbit environment.

    You can easily divide your dataset
    into training and testing subsets
    using the
    ``VastFrame.``:py:meth:`~vastorbit.VastFrame.train_test_split`
    method. This is a crucial step when
    preparing your data for machine learning,
    as it allows you to evaluate the
    performance of your models accurately.

    .. code-block:: python

        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    .. warning::

        In this case, vastorbit utilizes seeded
        randomization to guarantee the reproducibility
        of your data split. However, please be aware
        that this approach may lead to reduced
        performance. For a more efficient data split,
        you can use the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db`
        method to save your results into ``tables``
        or ``temporary tables``. This will help
        enhance the overall performance of the
        process.

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        import vastorbit.datasets as vod
        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``GradientBoostingRegressor`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import GradientBoostingRegressor

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = GradientBoostingRegressor(
            n_estimators = 3,
        )

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(
            train,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "quality",
            test,
        )

    .. important::

        To train a model, you can directly use the
        :py:class:`~VastFrame` or the name of the
        relation stored in the database. The test
        set is optional and is only used to compute
        the test metrics. In :py:mod:`vastorbit`, we
        don't work using ``X`` matrices and ``y``
        vectors. Instead, we work directly with lists
        of predictors and the response name.

    Features Importance
    ^^^^^^^^^^^^^^^^^^^^

    We can conveniently get
    the features importance:

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_gbreg_feature.html")

    .. code-block:: python

        result = model.features_importance()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gbreg_feature.html

    .. note::

        In models such as ``GradientBoosting``, feature importance is calculated
        using the average gain of each tree. To determine the final score,
        vastorbit sums the scores of each tree, normalizes them and applies an
        activation function to scale them.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_gbreg_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gbreg_report.html

    .. important::

        Most metrics are computed using a single SQL query, but some of them might
        require multiple SQL queries. Selecting only the necessary metrics in the
        report can help optimize performance.
        E.g. ``model.report(metrics = ["mse", "r2"])``.

    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingRegressor.score`
    function to calculate various regression metrics, with the R-squared being the default.

    .. ipython:: python

        model.score()

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. ipython:: python
        :suppress:

        result = model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_gbreg_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gbreg_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingRegressor.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    Plots
    ^^^^^^

    Tree models can be visualized by drawing their tree plots.
    For more examples, check out :ref:`chart_gallery.tree`.

    .. code-block:: python

        model.plot_tree()

    .. ipython:: python
        :suppress:

        res = model.plot_tree()
        res.render(filename='figures/machine_learning_VAST_gbreg', format='png')


    .. image:: /../figures/machine_learning_VAST_gbreg.png

    .. note::

        The above example may not render
        properly in the doc because of the
        huge size of the tree. But it should
        render nicely in jupyter environment.

    In order to plot graph using
    `graphviz <https://graphviz.org/>`__
    separately, you can extract the
    graphviz DOT file code as follows:

    .. ipython:: python

        model.to_graphviz()

    This string can then be copied into a
    DOT file which can beparsed by graphviz.

    **Contour plot** is another useful plot
    that can be produced for models with two
    predictors.

    .. code-block:: python

        model.contour()

    .. important::

        Machine learning models with two
        predictors can usually benefit
        from their own contour plot.
        This visual representation aids
        in exploring predictions and
        gaining a deeper understanding
        of how these models perform in
        different scenarios.
        Please refer to
        :ref:`chart_gallery.contour`
        for more examples.Model Exporting

    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the
    model use ``MemModel``, and it is
    recommended to use ``MemModel`` directly.

    **To SQL**

    You can get the SQL query equivalent of the ``GradientBoosting`` model by:

    .. ipython:: python

        model.to_sql()

    .. note::

        This SQL query can be
        directly used in any
        database.

    **Deploy SQL**

    To get the SQL query which uses
    VAST functions use below:

    .. ipython:: python

        model.deploySQL()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[4.2, 0.17, 0.36, 1.8, 0.029, 0.9899]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.tree.GradientBoostingRegressor.to_python`
        method is used to retrieve predictions,
        probabilities, or cluster distances. For
        specific details on how to use this method
        for different model types, refer to the
        relevant documentation for each model.
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["REGRESSOR"]:
        return "REGRESSOR"

    @property
    def _model_type(self) -> Literal["GradientBoostingRegressor"]:
        return "GradientBoostingRegressor"

    @property
    def _attributes(self) -> list[str]:
        return [
            "n_estimators_",
            "eta_",
            "mean_",
            "trees_",
            "feature_importances_",
            "feature_importances_trees_",
        ]

    # Attributes Methods.

    @property
    def _sklearn_model(self) -> Literal[sklearn.ensemble.GradientBoostingRegressor]:
        return sklearn.ensemble.GradientBoostingRegressor

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from the
        fitted scikit-learn gradient boosting model.
        """
        self.eta_ = self._model.learning_rate
        self.n_estimators_ = self._model.n_estimators_
        self.n_features_ = self._model.n_features_in_

        # Initial prediction the boosting starts from (the response mean).
        init = self._model.init_
        try:
            self.mean_ = float(np.ravel(init.constant_)[0])
        except AttributeError:
            self.mean_ = float(
                np.ravel(init.predict(np.zeros((1, self.n_features_))))[0]
            )

        # One regression tree per boosting iteration. GradientBoosting stores
        # estimators_ as a 2-D array (n_estimators, 1) for regression, so it is
        # flattened before iterating (RandomForest's estimators_ is already 1-D).
        estimators = np.ravel(self._model.estimators_)
        self.feature_importances_trees_ = [
            est.feature_importances_ for est in estimators
        ]
        self.feature_importances_ = self._model.feature_importances_

        trees = []
        for est in estimators:
            tree = est.tree_
            tree_d = {
                "children_left": tree.children_left.copy(),
                "children_right": tree.children_right.copy(),
                "feature": tree.feature.copy(),
                "threshold": tree.threshold.astype(float),
                # Raw leaf output; the learning rate (eta_) is applied by the
                # memmodel at prediction time, as the JSON export already does.
                "value": tree.value[:, 0, 0].astype(float),
            }
            trees.append(mm.BinaryTreeRegressor(**tree_d))
        self.trees_ = trees
        self.max_depth_ = self._model.max_depth

    # I/O Methods.

    def to_memmodel(self) -> mm.GradientBoostingRegressor:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.ensemble.GradientBoostingRegressor`
            for more information.
        """
        return mm.GradientBoostingRegressor(self.trees_, self.mean_, self.eta_)


"""
Algorithms used for classification.
"""


class RandomForestClassifier(MulticlassClassifier, RandomForest):
    """
    Creates an ``RandomForestClassifier``
    object using SKLEARN for training
    and the scalability of VASTDB for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    ``**kwargs``: SKLEARN model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``trees_``: list of BinaryTreeClassifier
        Tree models are instances of `
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeClassifier`,
        each possessing various attributes.
        For more detailed information, refer
        to the documentation for
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeClassifier`.
    ``feature_importances_``: numpy.array
        The importance of features. It is calculated
        using the MDI (Mean Decreased Impurity). To
        determine the final score, vastorbit sums the
        scores of each tree, normalizes them and applies
        an activation function to scale them.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``feature_importances_trees_``: dict of numpy.array
        Each element of the array represents the feature
        importance of tree i.
        The importance of features is calculated
        using the MDI (Mean Decreased Impurity).
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``n_estimators_``: int
        The number of model estimators.
    ``classes_``: numpy.array
        The classes labels.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    .. important::

        Many tree-based models inherit from the ``RandomForest``
        base class, and it's recommended to use it directly for
        access to a wider range of options.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    We import :py:mod:`vastorbit`:

    .. code-block:: python

        import vastorbit as vo

    .. hint::

        By assigning an alias to :py:mod:`vastorbit`,
        we mitigate the risk of code collisions with
        other libraries. This precaution is necessary
        because vastorbit uses commonly known function
        names like "average" and "median", which can
        potentially lead to naming conflicts. The use
        of an alias ensures that the functions from
        :py:mod:`vastorbit` are used as intended
        without interfering with functions from other
        libraries.

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

    .. note::

        vastorbit offers a wide range of sample
        datasets that are ideal for training
        and testing purposes. You can explore
        the full list of available datasets in
        the :ref:`api.datasets`, which provides
        detailed information on each dataset and
        how to use them effectively. These datasets
        are invaluable resources for honing your
        data analysis and machine learning skills
        within the vastorbit environment.

    You can easily divide your dataset
    into training and testing subsets
    using the
    ``VastFrame.``:py:meth:`~vastorbit.VastFrame.train_test_split`
    method. This is a crucial step when
    preparing your data for machine learning,
    as it allows you to evaluate the
    performance of your models accurately.

    .. code-block:: python

        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    .. warning::

        In this case, vastorbit utilizes seeded
        randomization to guarantee the reproducibility
        of your data split. However, please be aware
        that this approach may lead to reduced
        performance. For a more efficient data split,
        you can use the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db`
        method to save your results into ``tables``
        or ``temporary tables``. This will help
        enhance the overall performance of the
        process.

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        import vastorbit.datasets as vod
        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    Balancing the Dataset
    ^^^^^^^^^^^^^^^^^^^^^^

    In vastorbit, balancing a dataset to
    address class imbalances is made
    straightforward through the
    :py:meth:`~vastorbit.machine_learning.vast.preprocessing.balance`
    function within the ``preprocessing``
    module. This function enables users
    to rectify skewed class distributions
    efficiently. By specifying the target
    variable and setting parameters like
    the method for balancing, users can
    effortlessly achieve a more equitable
    representation of classes in their dataset.
    Whether opting for over-sampling,
    under-sampling, or a combination
    of both, vastorbit's
    :py:meth:`~vastorbit.machine_learning.vast.preprocessing.balance`
    function streamlines the process,
    empowering users to enhance the
    performance and fairness of their
    machine learning models trained
    on imbalanced data.

    To balance the dataset, use the following syntax.

    .. code-block:: python

        from vastorbit.machine_learning.vast.preprocessing import balance

        balanced_train = balance(
            name = "my_schema.train_balanced",
            input_relation = train,
            y = "good",
            method = "hybrid",
        )

    .. note::

        With this code, a table named `train_balanced`
        is created in the `my_schema` schema.
        It can then be used to train the model.
        In the rest of the example, we will work
        with the full dataset.

    .. hint::

        Balancing the dataset is a crucial
        step in improving the accuracy of
        machine learning models, particularly
        when faced with imbalanced class
        distributions. By addressing disparities
        in the number of instances across different
        classes, the model becomes more adept at
        learning patterns from all classes rather
        than being biased towards the majority
        class. This, in turn, enhances the model's
        ability to make accurate predictions for
        under-represented classes. The balanced
        dataset ensures that the model is not
        dominated by the majority class and, as a
        result, leads to more robust and unbiased
        model performance. Therefore, by employing
        techniques such as over-sampling, under-sampling,
        or a combination of both during dataset
        preparation, practitioners can significantly
        contribute to achieving higher accuracy and
        better generalization of their machine learning
        models.

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``RandomForestClassifier`` model:

    .. code-block::

        from vastorbit.machine_learning.vast import RandomForestClassifier

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast import RandomForestClassifier

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = RandomForestClassifier(
            n_estimators = 5,
            max_depth = 3,
        )

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(
            train,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "good",
            test,
        )

    .. important::

        To train a model, you can directly use the
        :py:class:`~VastFrame` or the name of the
        relation stored in the database. The test
        set is optional and is only used to compute
        the test metrics. In :py:mod:`vastorbit`, we
        don't work using ``X`` matrices and ``y``
        vectors. Instead, we work directly with lists
        of predictors and the response name.

    Features Importance
    ^^^^^^^^^^^^^^^^^^^^

    We can conveniently get
    the features importance:

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_feature.html")

    .. code-block:: python

        result = model.features_importance()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_feature.html

    .. note::

        In models such as ``RandomForest``, feature importance is calculated
        using the MDI (Mean Decreased Impurity). To determine the final score,
        vastorbit sums the scores of each tree, normalizes them and applies an
        activation function to scale them.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_report.html

    .. important::

        Most metrics are computed using a
        single SQL query, but some of them
        might require multiple SQL queries.
        Selecting only the necessary metrics
        in the report can help optimize performance.
        E.g. ``model.report(metrics = ["auc", "accuracy"])``.

    For classification models, we can easily modify the ``cutoff`` to observe
    the effect on different metrics:

    .. ipython:: python
        :suppress:

        result = model.report(cutoff = 0.2)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_report_cutoff.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report(cutoff = 0.2)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_report_cutoff.html

    You can also use the
    :py:meth:`~vastorbit.machine_learning.vast.ensemble.RandomForestClassifier.score`
    function to compute any classification metric. The default metric is the accuracy:

    .. ipython:: python

        model.score()

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. ipython:: python
        :suppress:

        result = model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.ensemble.RandomForestClassifier.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    Probabilities
    ^^^^^^^^^^^^^^

    It is also easy to get the model's probabilities:

    .. ipython:: python
        :suppress:

        result = model.predict_proba(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_proba.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict_proba(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_proba.html

    .. note::

        Probabilities are added to the :py:class:`~VastFrame`,
        and vastorbit uses the corresponding probability
        function in SQL behind the scenes. You can use
        the ``pos_label`` parameter to add only the
        probability of the selected category.

    Confusion Matrix
    ^^^^^^^^^^^^^^^^^

    You can obtain the confusion matrix of your choice by specifying
    the desired cutoff.

    .. ipython:: python

        model.confusion_matrix(cutoff = 0.5)

    .. note::

        In classification, the ``cutoff`` is a
        threshold value used to determine class
        assignment based on predicted probabilities
        or scores from a classification model. In
        binary classification, if the predicted
        probability for a specific class is greater
        than or equal to the cutoff, the instance is
        assigned to the positive class; otherwise, it
        is assigned to the negative class. Adjusting
        the cutoff allows for trade-offs between true
        positives and false positives, enabling the
        model to be optimized for specific objectives
        or to consider the relative costs of different
        classification errors. The choice of cutoff is
        critical for tailoring the model's performance
        to meet specific needs.

    Main Plots (Classification Curves)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Classification models allow for the
    creation of various plots that are
    very helpful in understanding the
    model, such as the ROC Curve,
    PRC Curve, Cutoff Curve, Gain
    Curve, and more.

    Most of the classification curves
    can be found in the
    :ref:`chart_gallery.classification_curve`.

    For example, let's draw the
    model's ROC curve.

    .. code-block:: python

        model.roc_curve()

    .. ipython:: python
        :suppress:

        fig = model.roc_curve()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_roc.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_rf_classifier_roc.html

    .. important::

        Most of the curves have a parameter called
        ``nbins``, which is essential for estimating
        metrics. The larger the ``nbins``, the more
        precise the estimation, but it can significantly
        impact performance. Exercise caution when
        increasing this parameter excessively.

    .. hint::

        In binary classification, various curves can
        be easily plotted. However, in multi-class
        classification, it's important to select the
        ``pos_label``, representing the class to be
        treated as positive when drawing the curve.

    Other Plots
    ^^^^^^^^^^^^

    Tree models can be visualized by drawing their tree plots.
    For more examples, check out :ref:`chart_gallery.tree`.

    .. code-block:: python

        model.plot_tree()

    .. ipython:: python
        :suppress:

        res = model.plot_tree()
        res.render(filename='figures/machine_learning_VAST_tree_rf_classifier_', format='png')


    .. image:: /../figures/machine_learning_VAST_tree_rf_classifier_.png

    .. note::

        The above example may not render
        properly in the doc because of the
        huge size of the tree. But it should
        render nicely in jupyter environment.

    In order to plot graph using
    `graphviz <https://graphviz.org/>`__
    separately, you can extract the
    graphviz DOT file code as follows:

    .. ipython:: python

        model.to_graphviz()

    This string can then be copied into a
    DOT file which can beparsed by graphviz.

    **Contour plot** is another useful plot
    that can be produced for models with two
    predictors.

    .. code-block:: python

        model.contour()

    .. important::

        Machine learning models with two
        predictors can usually benefit
        from their own contour plot.
        This visual representation aids
        in exploring predictions and
        gaining a deeper understanding
        of how these models perform in
        different scenarios.
        Please refer to
        :ref:`chart_gallery.contour`
        for more examples.

    Parameter Modification
    ^^^^^^^^^^^^^^^^^^^^^^^

    In order to see the parameters:

    .. ipython:: python

        model.get_params()

    And to manually change some of the parameters:

    .. ipython:: python

        model.set_params({'max_depth': 5})

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The following methods for exporting the model
    use ``MemModel``, and it is recommended to use
    ``MemModel`` directly.

    **To SQL**

    You can get the SQL code by:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[4.2, 0.17, 0.36, 1.8, 0.029, 0.9899]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.tree.RandomForestClassifier.to_python`
        method is used to retrieve predictions,
        probabilities, or cluster distances. For
        specific details on how to use this method
        for different model types, refer to the
        relevant documentation for each model.
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["CLASSIFIER"]:
        return "CLASSIFIER"

    @property
    def _model_type(self) -> Literal["RandomForestClassifier"]:
        return "RandomForestClassifier"

    @property
    def _attributes(self) -> list[str]:
        return [
            "n_estimators_",
            "classes_",
            "trees_",
            "feature_importances_",
            "feature_importances_trees_",
            "max_depth_",
            "oob_score_",
        ]

    @property
    def _sklearn_model(self) -> Literal[sklearn.ensemble.RandomForestClassifier]:
        return sklearn.ensemble.RandomForestClassifier

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from sklearn RandomForestClassifier.
        """
        self.n_estimators_ = self._model.n_estimators
        self.n_features_ = self._model.n_features_in_
        self.n_classes_ = self._model.n_classes_
        self.classes_ = self._model.classes_.copy()

        # Feature importances
        self.feature_importances_trees_ = []
        for tree in self._model.estimators_:
            self.feature_importances_trees_.append(tree.feature_importances_)
        self.feature_importances_ = self._model.feature_importances_

        trees = []
        n_classes = len(self.classes_)

        for estimator in self._model.estimators_:
            tree = estimator.tree_

            tree_d = {
                "children_left": tree.children_left.astype(int),
                "children_right": tree.children_right.astype(int),
                "feature": tree.feature.astype(int),
                "threshold": tree.threshold.astype(float),
                "value": [],
                "classes": self.classes_,
            }

            # Process each node
            for node_idx in range(tree.node_count):
                # Get class counts at this node
                # Shape: tree.value[node_idx, 0, :] = (n_classes,)
                class_counts = tree.value[node_idx, 0, :]

                # Convert to probabilities
                total_samples = np.sum(class_counts)

                if total_samples > 0:
                    # Normalize to probability distribution
                    probabilities = class_counts / total_samples
                else:
                    # Uniform distribution if no samples (shouldn't happen)
                    probabilities = np.ones(n_classes) / n_classes

                tree_d["value"].append(probabilities.tolist())

            # Create tree model
            model = mm.BinaryTreeClassifier(**tree_d)
            trees.append(model)

        self.trees_ = trees
        self.max_depth_ = self._model.max_depth
        self.oob_score_ = getattr(self._model, "oob_score_", None)

    # I/O Methods.

    def to_memmodel(self) -> Union[mm.RandomForestClassifier, mm.BinaryTreeClassifier]:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.ensemble.RandomForestClassifier`
            and
            :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeClassifier`
            for more information.
        """
        if self.n_estimators_ == 1:
            return self.trees_[0]
        else:
            return mm.RandomForestClassifier(self.trees_, self.classes_)


class GradientBoostingClassifier(MulticlassClassifier, GradientBoosting):
    """
    Creates an ``GradientBoostingClassifier`` object
    using SKLEARN for training and
    the scalability of VASTDB for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    ``**kwargs``: SKLEARN model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``trees_``: list of BinaryTreeClassifier
        Tree models are instances of `
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeClassifier`,
        each possessing various attributes.
        For more detailed information, refer
        to the documentation for
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeClassifier`.
    ``feature_importances_``: numpy.array
        The importance of features. It is calculated
        using the average gain of each tree. To determine
        the final score, vastorbit sums the scores of each
        tree, normalizes them and applies an activation
        function to scale them.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``feature_importances_trees_``: dict of numpy.array
        Each element of the array represents the feature
        importance of tree i.
        The importance of features is calculated
        using the average gain of each tree.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``logodds_``: numpy.array
        The log-odds. It quantifies the logarithm of the
        odds ratio, providing a measure of the likelihood
        of an event occurring.
    ``eta_``: float
        The learning rate, is a crucial hyperparameter in
        machine learning algorithms. It determines the step
        size at each iteration during the model training
        process. A well-chosen learning rate is essential
        for achieving optimal convergence and preventing
        overshooting or slow convergence in the training
        phase. Adjusting the learning rate is often necessary
        to strike a balance between model accuracy and
        computational efficiency.
    ``n_estimators_``: int
        The number of model estimators.
    ``classes_``: numpy.array
        The classes labels.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    .. important::

        Many tree-based models inherit from the ``GradientBoosting``
        base class, and it's recommended to use it directly for
        access to a wider range of options.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    We import :py:mod:`vastorbit`:

    .. code-block:: python

        import vastorbit as vo

    .. hint::

        By assigning an alias to :py:mod:`vastorbit`,
        we mitigate the risk of code collisions with
        other libraries. This precaution is necessary
        because vastorbit uses commonly known function
        names like "average" and "median", which can
        potentially lead to naming conflicts. The use
        of an alias ensures that the functions from
        :py:mod:`vastorbit` are used as intended
        without interfering with functions from other
        libraries.

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

    .. note::

        vastorbit offers a wide range of sample
        datasets that are ideal for training
        and testing purposes. You can explore
        the full list of available datasets in
        the :ref:`api.datasets`, which provides
        detailed information on each dataset and
        how to use them effectively. These datasets
        are invaluable resources for honing your
        data analysis and machine learning skills
        within the vastorbit environment.

    You can easily divide your dataset
    into training and testing subsets
    using the
    ``VastFrame.``:py:meth:`~vastorbit.VastFrame.train_test_split`
    method. This is a crucial step when
    preparing your data for machine learning,
    as it allows you to evaluate the
    performance of your models accurately.

    .. code-block:: python

        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    .. warning::

        In this case, vastorbit utilizes seeded
        randomization to guarantee the reproducibility
        of your data split. However, please be aware
        that this approach may lead to reduced
        performance. For a more efficient data split,
        you can use the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_db`
        method to save your results into ``tables``
        or ``temporary tables``. This will help
        enhance the overall performance of the
        process.

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        import vastorbit.datasets as vod
        data = vod.load_winequality()
        train, test = data.train_test_split(test_size = 0.2)

    Balancing the Dataset
    ^^^^^^^^^^^^^^^^^^^^^^

    In vastorbit, balancing a dataset to
    address class imbalances is made
    straightforward through the
    :py:meth:`~vastorbit.machine_learning.vast.preprocessing.balance`
    function within the ``preprocessing``
    module. This function enables users
    to rectify skewed class distributions
    efficiently. By specifying the target
    variable and setting parameters like
    the method for balancing, users can
    effortlessly achieve a more equitable
    representation of classes in their dataset.
    Whether opting for over-sampling,
    under-sampling, or a combination
    of both, vastorbit's
    :py:meth:`~vastorbit.machine_learning.vast.preprocessing.balance`
    function streamlines the process,
    empowering users to enhance the
    performance and fairness of their
    machine learning models trained
    on imbalanced data.

    To balance the dataset, use the following syntax.

    .. code-block:: python

        from vastorbit.machine_learning.vast.preprocessing import balance

        balanced_train = balance(
            name = "my_schema.train_balanced",
            input_relation = train,
            y = "good",
            method = "hybrid",
        )

    .. note::

        With this code, a table named `train_balanced`
        is created in the `my_schema` schema.
        It can then be used to train the model.
        In the rest of the example, we will work
        with the full dataset.

    .. hint::

        Balancing the dataset is a crucial
        step in improving the accuracy of
        machine learning models, particularly
        when faced with imbalanced class
        distributions. By addressing disparities
        in the number of instances across different
        classes, the model becomes more adept at
        learning patterns from all classes rather
        than being biased towards the majority
        class. This, in turn, enhances the model's
        ability to make accurate predictions for
        under-represented classes. The balanced
        dataset ensures that the model is not
        dominated by the majority class and, as a
        result, leads to more robust and unbiased
        model performance. Therefore, by employing
        techniques such as over-sampling, under-sampling,
        or a combination of both during dataset
        preparation, practitioners can significantly
        contribute to achieving higher accuracy and
        better generalization of their machine learning
        models.

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``GradientBoostingClassifier`` model:

    .. code-block::

        from vastorbit.machine_learning.vast import GradientBoostingClassifier

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast import GradientBoostingClassifier

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = GradientBoostingClassifier(
            n_estimators = 3,
            max_depth = 3,
            nbins = 6,
            split_proposal_method = 'global',
            tol = 0.001,
            learning_rate = 0.1,
            min_split_loss = 0,
            weight_reg = 0,
            sample = 0.7,
            col_sample_by_tree = 1,
            col_sample_by_node = 1,
        )

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(
            train,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "good",
            test,
        )

    .. important::

        To train a model, you can directly use the
        :py:class:`~VastFrame` or the name of the
        relation stored in the database. The test
        set is optional and is only used to compute
        the test metrics. In :py:mod:`vastorbit`, we
        don't work using ``X`` matrices and ``y``
        vectors. Instead, we work directly with lists
        of predictors and the response name.

    Features Importance
    ^^^^^^^^^^^^^^^^^^^^

    We can conveniently get
    the features importance:

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_feature.html")

    .. code-block:: python

        result = model.features_importance()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_feature.html

    .. note::

        In models such as ``GradientBoosting``, feature importance is calculated
        using the average gain of each tree. To determine the final score,
        vastorbit sums the scores of each tree, normalizes them and applies an
        activation function to scale them.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_report.html

    .. important::

        Most metrics are computed using a
        single SQL query, but some of them
        might require multiple SQL queries.
        Selecting only the necessary metrics
        in the report can help optimize performance.
        E.g. ``model.report(metrics = ["auc", "accuracy"])``.

    For classification models, we can easily modify the ``cutoff`` to observe
    the effect on different metrics:

    .. ipython:: python
        :suppress:

        result = model.report(cutoff = 0.2)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_report_cutoff.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report(cutoff = 0.2)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_report_cutoff.html

    You can also use the
    :py:meth:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingClassifier.score`
    function to compute any classification metric. The default metric is the accuracy:

    .. ipython:: python

        model.score()

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. ipython:: python
        :suppress:

        result = model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.ensemble.GradientBoostingClassifier.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    Probabilities
    ^^^^^^^^^^^^^^

    It is also easy to get the model's probabilities:

    .. ipython:: python
        :suppress:

        result = model.predict_proba(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_proba.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict_proba(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_proba.html

    .. note::

        Probabilities are added to the :py:class:`~VastFrame`,
        and vastorbit uses the corresponding probability
        function in SQL behind the scenes. You can use
        the ``pos_label`` parameter to add only the
        probability of the selected category.

    Confusion Matrix
    ^^^^^^^^^^^^^^^^^

    You can obtain the confusion matrix of your choice by specifying
    the desired cutoff.

    .. ipython:: python

        model.confusion_matrix(cutoff = 0.5)

    .. note::

        In classification, the ``cutoff`` is a
        threshold value used to determine class
        assignment based on predicted probabilities
        or scores from a classification model. In
        binary classification, if the predicted
        probability for a specific class is greater
        than or equal to the cutoff, the instance is
        assigned to the positive class; otherwise, it
        is assigned to the negative class. Adjusting
        the cutoff allows for trade-offs between true
        positives and false positives, enabling the
        model to be optimized for specific objectives
        or to consider the relative costs of different
        classification errors. The choice of cutoff is
        critical for tailoring the model's performance
        to meet specific needs.

    Main Plots (Classification Curves)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Classification models allow for the
    creation of various plots that are
    very helpful in understanding the
    model, such as the ROC Curve,
    PRC Curve, Cutoff Curve, Gain
    Curve, and more.

    Most of the classification curves
    can be found in the
    :ref:`chart_gallery.classification_curve`.

    For example, let's draw the
    model's ROC curve.

    .. code-block:: python

        model.roc_curve()

    .. ipython:: python
        :suppress:

        fig = model.roc_curve()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_roc.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_gb_classifier_roc.html

    .. important::

        Most of the curves have a parameter called
        ``nbins``, which is essential for estimating
        metrics. The larger the ``nbins``, the more
        precise the estimation, but it can significantly
        impact performance. Exercise caution when
        increasing this parameter excessively.

    .. hint::

        In binary classification, various curves can
        be easily plotted. However, in multi-class
        classification, it's important to select the
        ``pos_label``, representing the class to be
        treated as positive when drawing the curve.

    Other Plots
    ^^^^^^^^^^^^

    Tree models can be visualized by drawing their tree plots.
    For more examples, check out :ref:`chart_gallery.tree`.

    .. code-block:: python

        model.plot_tree()

    .. ipython:: python
        :suppress:

        res = model.plot_tree()
        res.render(filename='figures/machine_learning_VAST_tree_gb_classifier_', format='png')


    .. image:: /../figures/machine_learning_VAST_tree_gb_classifier_.png

    .. note::

        The above example may not render
        properly in the doc because of the
        huge size of the tree. But it should
        render nicely in jupyter environment.

    In order to plot graph using
    `graphviz <https://graphviz.org/>`__
    separately, you can extract the
    graphviz DOT file code as follows:

    .. ipython:: python

        model.to_graphviz()

    This string can then be copied into a
    DOT file which can beparsed by graphviz.

    **Contour plot** is another useful plot
    that can be produced for models with two
    predictors.

    .. code-block:: python

        model.contour()

    .. important::

        Machine learning models with two
        predictors can usually benefit
        from their own contour plot.
        This visual representation aids
        in exploring predictions and
        gaining a deeper understanding
        of how these models perform in
        different scenarios.
        Please refer to
        :ref:`chart_gallery.contour`
        for more examples.

    Parameter Modification
    ^^^^^^^^^^^^^^^^^^^^^^^

    In order to see the parameters:

    .. ipython:: python

        model.get_params()

    And to manually change some of the parameters:

    .. ipython:: python

        model.set_params({'max_depth': 5})

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the
    model use ``MemModel``, and it is
    recommended to use ``MemModel`` directly.

    **To SQL**

    You can get the SQL query equivalent of the
    ``GradientBoosting`` model by:

    .. ipython:: python

        model.to_sql()

    .. note::

        This SQL query can be
        directly used in any
        database.

    **Deploy SQL**

    To get the SQL query which uses
    VAST functions use below:

    .. ipython:: python

        model.deploySQL()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[4.2, 0.17, 0.36, 1.8, 0.029, 0.9899]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.tree.GradientBoostingClassifier.to_python`
        method is used to retrieve predictions,
        probabilities, or cluster distances. For
        specific details on how to use this method
        for different model types, refer to the
        relevant documentation for each model.
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["CLASSIFIER"]:
        return "CLASSIFIER"

    @property
    def _model_type(self) -> Literal["GradientBoostingClassifier"]:
        return "GradientBoostingClassifier"

    @property
    def _attributes(self) -> list[str]:
        return [
            "n_estimators_",
            "classes_",
            "eta_",
            "logodds_",
            "trees_",
            "feature_importances_",
            "feature_importances_trees_",
        ]

    # Attributes Methods.

    @property
    def _sklearn_model(self) -> Literal[sklearn.ensemble.GradientBoostingClassifier]:
        return sklearn.ensemble.GradientBoostingClassifier

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from the
        fitted scikit-learn gradient boosting model.
        """
        self.eta_ = self._model.learning_rate
        self.n_estimators_ = self._model.n_estimators_
        self.n_features_ = self._model.n_features_in_
        self.n_classes_ = self._model.n_classes_
        self.classes_ = self._model.classes_.copy()

        # Initial raw prediction (log-odds) the boosting starts from.
        try:
            priors = np.asarray(self._model.init_.class_prior_, dtype=float)
        except AttributeError:
            priors = np.full(self.n_classes_, 1.0 / self.n_classes_)
        if self._is_binary_classifier():
            prior = float(priors[1]) if len(priors) > 1 else 0.5
            self.logodds_ = [
                np.log((1 - prior) / prior),
                np.log(prior / (1 - prior)),
            ]
        else:
            with np.errstate(divide="ignore"):
                self.logodds_ = np.log(priors)

        # Feature importances.
        estimators = np.ravel(self._model.estimators_)
        self.feature_importances_trees_ = [
            est.feature_importances_ for est in estimators
        ]
        self.feature_importances_ = self._model.feature_importances_

        # GradientBoosting stores estimators_ as a 2-D array (n_estimators, K)
        # with K == 1 for binary and K == n_classes for multiclass, so it is
        # flattened (C-order) before iterating; tree j therefore targets
        # class (j % K). RandomForest's estimators_ is 1-D with class-count
        # leaves, so it falls through the (shape == n_classes) branch below.
        n_classes = len(self.classes_)
        K = self._model.estimators_.shape[1]
        trees = []
        for t_idx, est in enumerate(estimators):
            target_class = t_idx % K
            tree = est.tree_
            tree_d = {
                "children_left": tree.children_left.astype(int),
                "children_right": tree.children_right.astype(int),
                "feature": tree.feature.astype(int),
                "threshold": tree.threshold.astype(float),
                "value": [],
                "classes": self.classes_,
            }
            for node_idx in range(tree.node_count):
                node_value = tree.value[node_idx, 0, :]
                if node_value.shape[0] == n_classes:
                    # Class-count trees (RandomForest-style): normalize to a
                    # probability distribution over the classes.
                    total = float(np.sum(node_value))
                    if total > 0:
                        node_out = (node_value / total).tolist()
                    else:
                        node_out = (np.ones(n_classes) / n_classes).tolist()
                else:
                    # Single-output regression trees (gradient boosting): the
                    # leaf carries a raw log-odds increment. Expand it into a
                    # per-class vector so the shared proba machinery (which
                    # expects one value per class) works. Binary boosting has a
                    # single decision function f: class 1 gets +f, class 0 gets
                    # -f, which makes the downstream logistic+normalisation
                    # collapse to sigmoid(f). Multiclass places the increment in
                    # the tree's target class slot and 0 elsewhere.
                    increment = float(node_value[0])
                    node_out = [0.0] * n_classes
                    if K == 1:
                        node_out[0] = -increment
                        node_out[1] = increment
                    else:
                        node_out[target_class] = increment
                tree_d["value"].append(node_out)
            trees.append(mm.BinaryTreeClassifier(**tree_d))
        self.trees_ = trees
        self.max_depth_ = self._model.max_depth

    # I/O Methods.

    def to_memmodel(self) -> mm.GradientBoostingClassifier:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.ensemble.GradientBoostingClassifier`
            for more information.
        """
        return mm.GradientBoostingClassifier(
            self.trees_, self.logodds_, self.classes_, self.eta_
        )


"""
Algorithms used for anomaly detection.
"""


class IsolationForest(Clustering, Tree):
    """
    Creates an ``IsolationForest`` object
    using SKLEARN for training and
    the scalability of VASTDB for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    ``**kwargs``: SKLEARN model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``trees_``: list of BinaryTreeAnomaly
        Tree models are instances of `
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeAnomaly`,
        each possessing various attributes.
        For more detailed information, refer
        to the documentation for
        :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeAnomaly`.
    ``psy_``: int
        Sampling size used to compute the final score.
    ``n_estimators_``: int
        The number of model estimators.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.Tree.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    We import :py:mod:`vastorbit`:

    .. ipython:: python

        import vastorbit as vo

    .. hint::

        By assigning an alias to :py:mod:`vastorbit`,
        we mitigate the risk of code collisions with
        other libraries. This precaution is necessary
        because vastorbit uses commonly known function
        names like "average" and "median", which can
        potentially lead to naming conflicts. The use
        of an alias ensures that the functions from
        :py:mod:`vastorbit` are used as intended
        without interfering with functions from other
        libraries.

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

    .. note::

        vastorbit offers a wide range of sample
        datasets that are ideal for training
        and testing purposes. You can explore
        the full list of available datasets in
        the :ref:`api.datasets`, which provides
        detailed information on each dataset and
        how to use them effectively. These datasets
        are invaluable resources for honing your
        data analysis and machine learning skills
        within the vastorbit environment.

    .. ipython:: python
        :suppress:

        import vastorbit.datasets as vod
        data = vod.load_winequality()

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``IsolationForest`` model:

    .. code-block::

        from vastorbit.machine_learning.vast import IsolationForest

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast import IsolationForest

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = IsolationForest(
            n_estimators = 5,
        )

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(data, X = ["density", "sulphates"])

    .. important::

        To train a model, you can directly use the
        :py:class:`~VastFrame` or the name of the
        relation stored in the database. The test
        set is optional and is only used to compute
        the test metrics. In :py:mod:`vastorbit`, we
        don't work using ``X`` matrices and ``y``
        vectors. Instead, we work directly with lists
        of predictors and the response name.

    .. hint::

        For clustering and anomaly detection, the
        use of predictors is optional. In such cases,
        all available predictors are considered, which
        can include solely numerical variables or a
        combination of numerical and categorical variables,
        depending on the model's capabilities.

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. ipython:: python
        :suppress:

        result = model.predict(data, ["density", "sulphates"])
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(data, ["density", "sulphates"])

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_prediction.html

    Plots - Anomaly Detection
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    Plots highlighting the outliers can be easily drawn using:

    .. code-block:: python

        model.plot()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_plot.html

    .. note::

        Most anomaly detection methods produce a score. In scenarios involving
        2 or 3 predictors, using a bubble plot to visualize the model's results
        is a straightforward approach. In such plots, the size of each bubble
        corresponds to the anomaly score.

    Plots - Tree
    ^^^^^^^^^^^^^

    Tree models can be visualized by drawing their tree plots.
    For more examples, check out :ref:`chart_gallery.tree`.

    .. code-block:: python

        model.plot_tree()

    .. ipython:: python
        :suppress:

        res = model.plot_tree()
        res.render(filename='figures/machine_learning_VAST_tree_isolation_for_', format='png')


    .. image:: /../figures/machine_learning_VAST_tree_isolation_for_.png

    .. note::

        The above example may not render
        properly in the doc because of the
        huge size of the tree. But it should
        render nicely in jupyter environment.

    In order to plot graph using
    `graphviz <https://graphviz.org/>`__
    separately, you can extract the
    graphviz DOT file code as follows:

    .. ipython:: python

        model.to_graphviz()

    This string can then be copied into a DOT file which can be
    parsed by graphviz.

    Plots - Contour
    ^^^^^^^^^^^^^^^^

    In order to understand the parameter space, we can also look
    at the contour plots:

    .. code-block:: python

        model.contour()

    .. ipython:: python
        :suppress:

        fig = model.contour()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_contour.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_contour.html

    .. note::

        Machine learning models with two predictors can usually benefit
        from their own contour plot. This visual representation aids in
        exploring predictions and gaining a deeper understanding of how
        these models perform in different scenarios. Please refer to
        :ref:`chart_gallery.contour` for more examples.

    Parameter Modification
    ^^^^^^^^^^^^^^^^^^^^^^^

    In order to see the parameters:

    .. ipython:: python

        model.get_params()

    And to manually change some of the parameters:

    .. ipython:: python

        model.set_params({'max_depth': 5})

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the
    model use ``MemModel``, and it is
    recommended to use ``MemModel`` directly.

    **To SQL**

    You can get the SQL query equivalent of the ``IsolationForest`` model by:

    .. ipython:: python

        model.to_sql()

    .. note::

        This SQL query can be
        directly used in any
        database.

    **Deploy SQL**

    To get the SQL query which uses
    VAST functions use below:

    .. ipython:: python

        model.deploySQL()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[0.9, 0.5]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.tree.IsolationForest.to_python`
        method is used to retrieve the anomaly score.
        For specific details on how to
        use this method for different model types, refer to the relevant
        documentation for each model.
    """

    # Properties.

    @property
    def _sklearn_model(self) -> Literal[sklearn.ensemble.IsolationForest]:
        return sklearn.ensemble.IsolationForest

    @property
    def _model_subcategory(self) -> Literal["ANOMALY_DETECTION"]:
        return "ANOMALY_DETECTION"

    @property
    def _model_type(self) -> Literal["IsolationForest"]:
        return "IsolationForest"

    @property
    def _attributes(self) -> list[str]:
        return ["n_estimators_", "psy_", "trees_"]

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from sklearn IsolationForest.
        """
        self.n_estimators_ = self._model.n_estimators
        self.n_features_ = self._model.n_features_in_
        self.psy_ = int(self._model.max_samples_)
        trees = []
        for estimator in self._model.estimators_:
            tree = estimator.tree_
            # Isolation-forest scoring needs, per node, [path-depth, n_samples]:
            # the memmodel computes (depth + c(n_samples)) / c(psy). scikit-learn
            # only exposes n_node_samples, so the depth is derived from the tree.
            cl, cr = tree.children_left, tree.children_right
            depths = np.zeros(tree.node_count, dtype=float)
            stack = [(0, 0.0)]
            while stack:
                nid, d = stack.pop()
                depths[nid] = d
                if cl[nid] != -1:
                    stack.append((int(cl[nid]), d + 1.0))
                    stack.append((int(cr[nid]), d + 1.0))
            node_samples = tree.n_node_samples.astype(float)
            value = [
                [float(depths[i]), float(node_samples[i])]
                for i in range(tree.node_count)
            ]
            tree_d = {
                "children_left": tree.children_left.copy(),
                "children_right": tree.children_right.copy(),
                "feature": tree.feature.copy(),
                "threshold": tree.threshold.astype(float).copy(),
                "value": value,
                "psy": self.psy_,
            }
            trees += [mm.BinaryTreeAnomaly(**tree_d)]
        self.trees_ = trees

    # I/O Methods.

    def deploySQL(
        self,
        X: Optional[SQLColumns] = None,
        cutoff: PythonNumber = 0.7,
        contamination: Optional[PythonNumber] = None,
        return_score: bool = False,
    ) -> str:
        """
        Returns the SQL code needed
        to deploy the model.

        Parameters
        ----------
        X: SQLColumns, optional
            ``list`` of the columns used
            to deploy the model. If empty,
            the model predictors are used.
        cutoff: PythonNumber, optional
            ``float`` in the range ``(0.0, 1.0)``,
            specifies the threshold that
            determines  if a data  point is
            an anomaly.  If the ``anomaly_score``
            for a data point is greater than or
            equal to the ``cutoff``, the data
            point is marked as an anomaly.
        contamination: PythonNumber, optional
            ``float`` in the range ``(0,1)``,
            the approximate ratio of data
            points in the training data that
            should be labeled  as anomalous.
            If this parameter is specified, the
            ``cutoff`` parameter is ignored.
        return_score: bool, optional
            If set to ``True``, the anomaly
            score is returned, and the parameters
            ``cutoff`` and ``contamination``
            are ignored.

        Returns
        -------
        str
            the SQL code needed
            to deploy the model.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()

        We import the ``IsolationForest`` model:

        .. code-block::

            from vastorbit.machine_learning.vast import IsolationForest

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import IsolationForest

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = IsolationForest(
                n_estimators = 5,
            )

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, X = ["density", "sulphates"])

        To get the SQL query which uses
        VAST functions use below:

        .. ipython:: python

            model.deploySQL()

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.ensemble.IsolationForest`
            for more information about the
            different methods and usages.
        """
        X = format_type(X, dtype=list, na_out=self.X)
        X = quote_ident(X)
        if contamination and not return_score:
            assert 0 < contamination < 1, ValueError(
                "Incorrect parameter 'contamination'.\nThe parameter "
                "'contamination' must be between 0.0 and 1.0, exclusive."
            )
        elif not return_score:
            assert 0 < cutoff < 1, ValueError(
                "Incorrect parameter 'cutoff'.\nThe parameter "
                "'cutoff' must be between 0.0 and 1.0, exclusive."
            )
        score_sql = self.to_memmodel().predict_sql(X)
        if isinstance(score_sql, (list, tuple)):
            score_sql = score_sql[0]
        if return_score:
            return clean_query(score_sql)
        if not isinstance(contamination, NoneType):
            raise NotImplementedError(
                "Contamination-based thresholding is not available in deploySQL; "
                "use 'cutoff' or 'return_score=True'."
            )
        return clean_query(f"(CASE WHEN {score_sql} >= {cutoff} THEN 1 ELSE 0 END)")

    def to_memmodel(self) -> Union[mm.IsolationForest, mm.BinaryTreeAnomaly]:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.ensemble.IsolationForest`
            and
            :py:class:`~vastorbit.machine_learning.memmodel.tree.BinaryTreeAnomaly`
            for more information.
        """
        if self.n_estimators_ == 1:
            return self.trees_[0]
        else:
            return mm.IsolationForest(self.trees_)

    # Prediction / Transformation Methods.

    def decision_function(
        self,
        vdf: SQLRelation,
        X: Optional[SQLColumns] = None,
        name: Optional[str] = None,
        inplace: bool = True,
    ) -> VastFrame:
        """
        Returns the anomaly score using the
        input relation.

        Parameters
        ----------
        vdf: SQLRelation
            Object to use for the prediction.
            You can specify  a customized
            relation if it is enclosed with
            an alias. For example,``(SELECT 1) x``
            is valid, whereas ``(SELECT 1)``
            and ``SELECT 1`` are invalid.
        X: SQLColumns, optional
            ``list`` of columns used to deploy
            the models. If empty, the model
            predictors are used.
        name: str, optional
            Name of the additional
            :py:class:`~VastColumn`.
            If empty, a name is generated.
        inplace: bool, optional
            If ``True``, the prediction is added
            to the :py:class:`~VastFrame`.

        Returns
        -------
        VastFrame
            the input object.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()

        We import the ``IsolationForest`` model:

        .. code-block::

            from vastorbit.machine_learning.vast import IsolationForest

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import IsolationForest

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = IsolationForest(
                n_estimators = 5,
            )

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, X = ["density", "sulphates"])

        To get the SQL query which uses
        VAST functions use below:

        .. ipython:: python

            model.decision_function(data)

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.ensemble.IsolationForest`
            for more information about the
            different methods and usages.
        """
        # Inititalization
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        if not name:
            name = gen_name([self._model_type, self.model_name])

        # In Place
        vdf_return = vdf if inplace else vdf.copy()

        # Result
        return vdf_return.eval(
            name,
            self.deploySQL(
                X=X,
                return_score=True,
            ),
        )

    def predict(
        self,
        vdf: SQLRelation,
        X: Optional[SQLColumns] = None,
        name: Optional[str] = None,
        cutoff: PythonNumber = 0.7,
        contamination: Optional[PythonNumber] = None,
        inplace: bool = True,
    ) -> VastFrame:
        """
        Predicts using the input relation.

        Parameters
        ----------
        vdf: SQLRelation
            Object to use for the prediction. You can
            specify  a customized  relation if it  is
            enclosed  with  an  alias.  For  example,
            ``(SELECT 1) x`` is valid, whereas
            ``(SELECT 1)`` and ``SELECT 1`` are
            invalid.
        X: list, optional
            ``list`` of columns used to deploy the
            models. If empty,  the model  predictors
            are used.
        name: str, optional
            Name  of the  additional  VastColumn.
            If empty, a name is generated.
        cutoff: PythonNumber, optional
            ``float`` in the range ``(0.0, 1.0)``,
            specifies the  threshold  that determines
            if a data point is an anomaly. If the
            ``anomaly_score`` for a data point is
            greater than or equal to the ``cutfoff``,
            the data point is marked as an anomaly.
        contamination: PythonNumber, optional
            ``float``  in the range ``(0, 1)``, the
            approximate ratio of data points in the
            training data that should be labeled as
            anomalous. If this parameter is specified,
            the ``cutoff`` parameter is ignored.
        inplace: bool, optional
            If ``True``, the prediction is added to
            the :py:class:`~VastFrame`.

        Returns
        -------
        VastFrame
            the input object.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()

        We import the ``IsolationForest`` model:

        .. code-block::

            from vastorbit.machine_learning.vast import IsolationForest

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import IsolationForest

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = IsolationForest(
                n_estimators = 5,
            )

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, X = ["density", "sulphates"])

        Prediction is straight-forward:

        .. ipython:: python
            :suppress:

            result = model.predict(data, ["density", "sulphates"])
            html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_prediction.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. code-block:: python

            model.predict(data, ["density", "sulphates"])

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_isolation_for_prediction.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.ensemble.IsolationForest`
            for more information about the
            different methods and usages.
        """
        # Initialization
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        if not name:
            name = gen_name([self._model_type, self.model_name])

        # In Place
        vdf_return = vdf if inplace else vdf.copy()

        # Result
        return vdf_return.eval(
            name, self.deploySQL(cutoff=cutoff, contamination=contamination, X=X)
        )

    # Plotting Methods.

    def _get_plot_args(self, method: Optional[str] = None) -> list:
        """
        Returns the args used by plotting methods.
        """
        if method == "contour":
            args = [self.X, self.deploySQL(X=self.X, return_score=True)]
        else:
            raise NotImplementedError
        return args

    def _get_plot_kwargs(
        self,
        nbins: int = 30,
        chart: Optional[PlottingObject] = None,
        method: Optional[str] = None,
    ) -> dict:
        """
        Returns the kwargs used by plotting methods.
        """
        res = {"nbins": nbins, "chart": chart}
        if method == "contour":
            res["func_name"] = "anomaly_score"
        else:
            raise NotImplementedError
        return res
