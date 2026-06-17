"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal
import numpy as np

from vastorbit._typing import PythonNumber
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import quote_ident
from vastorbit.errors import MissingRelation

from vastorbit.core.vastframe.base import VastFrame

import vastorbit.machine_learning.memmodel as mm

from vastorbit.machine_learning.vast.base import MulticlassClassifier

"""
Algorithms used for classification.
"""


class NaiveBayes(MulticlassClassifier):
    """
    Creates an ``NaiveBayes`` object
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
    **kwargs: SKLEARN model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    prior_: numpy.array
        The model's classes probabilities.
    attributes_: list of dict
        ``list`` of the model's attributes.
        Each feature is represented by a
        ``dictionary``, which differs based
        on the distribution.
    classes_: numpy.array
        The classes labels.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.MulticlassClassifier.get_attributes`
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

    For this example, we will use the iris dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_iris()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_iris.html

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

        data = vod.load_iris()
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
        data = vod.load_iris()
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

    First we import the ``NaiveBayes`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import NaiveBayes

    Then we can create the model:

    .. ipython:: python

        model = NaiveBayes()

    .. hint::

        In :py:mod:`vastorbit` 1.0.x and higher,
        you do not need to specify the model name,
        as the name is automatically assigned. If
        you need to re-use the model, you can fetch
        the model name from the model's attributes.

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python

        model.fit(
            train,
            [
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
            ],
            "Species",
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

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_report.html

    .. important::

        Most metrics are computed using a
        single SQL query, but some of them
        might require multiple SQL queries.
        Selecting only the necessary metrics
        in the report can help optimize performance.
        E.g. ``model.report(metrics = ["auc", "accuracy"])``.

    For classification models, we can
    easily modify the ``cutoff`` to
    observe the effect on different
    metrics:

    .. ipython:: python
        :suppress:

        result = model.report(cutoff = 0.2)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_report_cutoff.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report(cutoff = 0.2)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_report_cutoff.html


    You can also use the ``NaiveBayes.score``
    function to compute any classification
    metric. The default metric is the accuracy:

    .. ipython:: python

        model.score(metric = "f1", average = "macro")

    .. note::

        For multi-class scoring, :py:mod:`vastorbit`
        allows the flexibility to use three averaging
        techniques: ``micro``, ``macro`` and ``weighted``.
        Please refer to
        `this link <https://towardsdatascience.com/micro-macro-weighted-averages-of-f1-score-clearly-explained-b603420b292f>`_
        for more details on how they are calculated.

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. ipython:: python
        :suppress:

        result = model.predict(
            test,
            [
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(
            test,
            [
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.naive_bayes.NaiveBayes.predict`
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
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_proba.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict_proba(
            test,
            [
                "SepalLengthCm",
                "SepalWidthCm",
                "PetalLengthCm",
                "PetalWidthCm",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_proba.html

    .. note::

        Probabilities are added to the :py:class:`~VastFrame`,
        and vastorbit uses the corresponding probability
        function in SQL behind the scenes. You can use
        the ``pos_label`` parameter to add only the
        probability of the selected category.

    Confusion Matrix
    ^^^^^^^^^^^^^^^^^

    You can obtain the confusion matrix.

    .. ipython:: python

        model.confusion_matrix()

    .. hint::

        In the context of multi-class classification,
        you typically work with an overall confusion
        matrix that summarizes the classification
        efficiency across all classes. However, you
        have the flexibility to specify a ``pos_label``
        and adjust the cutoff threshold. In this case,
        a binary confusion matrix is computed, where
        the chosen class is treated as the positive
        class, allowing you to evaluate its efficiency
        as if it were a binary classification problem.

        .. ipython:: python

            model.confusion_matrix(pos_label = "Iris-setosa", cutoff = 0.6)

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

        model.roc_curve(pos_label = "Iris-setosa")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.roc_curve(pos_label = "Iris-setosa")
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_roc.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_NB_naivebayes_roc.html

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

    **Contour plot** is another useful plot that can be produced
    for models with two predictors.

    .. code-block:: python

        model.contour(pos_label = "Iris-setosa")

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

        model.set_params({'alpha': 0.9})

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

        X = [[5, 2, 3, 1]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.naive_bayes.NaiveBayes.to_python`
        method is used to retrieve predictions,
        probabilities, or cluster distances. For
        specific details on how to use this method
        for different model types, refer to the
        relevant documentation for each model.
    """

    # Properties.

    @property
    def _fit_sql(self) -> Literal[""]:
        return ""

    @property
    def _predict_sql(self) -> Literal[""]:
        return ""

    @property
    def _model_subcategory(self) -> Literal["CLASSIFIER"]:
        return "CLASSIFIER"

    @property
    def _model_type(self) -> Literal["NaiveBayes"]:
        return "NaiveBayes"

    @property
    def _attributes(self) -> list[str]:
        return ["attributes_", "prior_", "classes_"]

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        alpha: PythonNumber = 1.0,
        nbtype: Literal[
            "auto", "bernoulli", "categorical", "multinomial", "gaussian"
        ] = "auto",
    ) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {"alpha": alpha, "nbtype": str(nbtype).lower()}

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from the
        fitted scikit-learn naive bayes model.
        """
        self.classes_ = self._array_to_int(np.asarray(self._model.classes_))
        # Bernoulli/Multinomial/Categorical/Complement expose log priors;
        # GaussianNB exposes the priors directly.
        if hasattr(self._model, "class_log_prior_"):
            self.prior_ = np.exp(self._model.class_log_prior_)
        else:
            self.prior_ = np.asarray(self._model.class_prior_, dtype=float)
        self.attributes_ = self._get_nb_attributes()

    def _get_nb_attributes(self) -> list[dict]:
        """
        Builds, for each input feature, a dictionary describing its
        per-class naive bayes parameters in the format expected by the
        memmodel. Parameters are read directly from the fitted
        scikit-learn estimator (``self._model``).

        Unlike the database engine, scikit-learn uses a single
        distribution for every feature, determined by the estimator
        class, so the distribution type is taken from the model rather
        than detected column by column.
        """
        model = self._model
        model_name = type(model).__name__
        n_features = len(self.X)
        attributes = []

        if model_name == "GaussianNB":
            # var_ replaced sigma_ in scikit-learn 1.0.
            variances = getattr(model, "var_", None)
            if variances is None:
                variances = model.sigma_
            for j in range(n_features):
                var_info = {"type": "gaussian"}
                for ci, c in enumerate(self.classes_):
                    var_info[c] = {
                        "mu": float(model.theta_[ci, j]),
                        "sigma_sq": float(variances[ci, j]),
                    }
                attributes.append(var_info)

        elif model_name in ("BernoulliNB", "MultinomialNB", "ComplementNB"):
            nb_type = "bernoulli" if model_name == "BernoulliNB" else "multinomial"
            # feature_log_prob_ shape: (n_classes, n_features).
            proba = np.exp(model.feature_log_prob_)
            for j in range(n_features):
                var_info = {"type": nb_type}
                for ci, c in enumerate(self.classes_):
                    var_info[c] = float(proba[ci, j])
                attributes.append(var_info)

        elif model_name == "CategoricalNB":
            # feature_log_prob_ is a list (one entry per feature), each of
            # shape (n_classes, n_categories_feature). categories_ holds the
            # category labels when available, otherwise integer indices.
            categories = getattr(model, "categories_", None)
            for j in range(n_features):
                var_info = {"type": "categorical"}
                log_prob_j = model.feature_log_prob_[j]
                n_categories = log_prob_j.shape[1]
                cats_j = (
                    list(categories[j])
                    if categories is not None
                    else list(range(n_categories))
                )
                for ci, c in enumerate(self.classes_):
                    var_info[c] = {
                        cats_j[k]: float(np.exp(log_prob_j[ci, k]))
                        for k in range(n_categories)
                    }
                attributes.append(var_info)

        else:
            raise TypeError(f"Unsupported naive bayes model type: '{model_name}'.")

        return attributes

    # I/O Methods.

    def to_memmodel(self) -> mm.NaiveBayes:
        """
        Converts  the model to an InMemory object  that
        can be used for different types of predictions.
        """
        return mm.NaiveBayes(
            self.attributes_,
            self.prior_,
            self.classes_,
        )


class BernoulliNB(NaiveBayes):
    """
    :py:class:`~vastorbit.machine_learning.vast.naive_bayes.NaiveBayes`
    with parameter ``nbtype = 'bernoulli'``.
    """

    def __init__(
        self, name: str = None, overwrite_model: bool = False, alpha: float = 1.0
    ) -> None:
        super().__init__(name, overwrite_model, alpha, nbtype="bernoulli")


class CategoricalNB(NaiveBayes):
    """
    :py:class:`~vastorbit.machine_learning.vast.naive_bayes.NaiveBayes`
    with parameter ``nbtype = 'categorical'``.
    """

    def __init__(
        self, name: str = None, overwrite_model: bool = False, alpha: float = 1.0
    ) -> None:
        super().__init__(name, overwrite_model, alpha, nbtype="categorical")


class GaussianNB(NaiveBayes):
    """
    :py:class:`~vastorbit.machine_learning.vast.naive_bayes.NaiveBayes`
    with parameter ``nbtype = 'gaussian'``.
    """

    def __init__(self, name: str = None, overwrite_model: bool = False) -> None:
        super().__init__(name, overwrite_model, nbtype="gaussian")


class MultinomialNB(NaiveBayes):
    """
    :py:class:`~vastorbit.machine_learning.vast.naive_bayes.NaiveBayes`
    with parameter ``nbtype = 'multinomial'``.
    """

    def __init__(
        self, name: str = None, overwrite_model: bool = False, alpha: float = 1.0
    ) -> None:
        super().__init__(name, overwrite_model, alpha, nbtype="multinomial")