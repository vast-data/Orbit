"""
SPDX-License-Identifier: Apache-2.0
"""

import itertools
from typing import Literal, Optional
import numpy as np

from vastorbit.connection.errors import QueryError

from vastorbit._typing import (
    NoneType,
    PlottingObject,
    PythonNumber,
    PythonScalar,
    SQLColumns,
    SQLRelation,
)
from vastorbit._utils._gen import gen_name, gen_tmp_name
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import (
    clean_query,
    format_type,
    quote_ident,
    schema_relation,
)
from vastorbit._utils._sql._sys import _executeSQL


from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame

from vastorbit.plotting._utils import PlottingUtils

import vastorbit.machine_learning.metrics as mt
from vastorbit.machine_learning.vast.base import (
    MulticlassClassifier,
    Regressor,
    Tree,
    VASTModel,
)
from vastorbit.machine_learning.vast.tree import DecisionTreeRegressor

from vastorbit.sql.drop import drop

"""
Algorithms used for regression.
"""


class KNeighborsRegressor(Regressor):
    """
    [Beta Version]
    Creates a ``KNeighborsRegressor``
    object using the k-nearest neighbors
    algorithm. This object uses pure SQL
    to compute all the distances and final
    score.

    .. warning::

        This   algorithm   uses  a   CROSS  JOIN
        during   computation  and  is  therefore
        computationally  expensive at  O(n * n),
        where n is the total number of elements.
        Since  KNeighborsRegressor  uses  the p-
        distance,  it  is  highly  sensitive  to
        unnormalized data.

    .. important::

        This algorithm is not VAST
        Native and relies solely on SQL
        for attribute computation. While
        this model does not take advantage
        of the benefits provided by a model
        management system, including versioning
        and tracking, the SQL code it generates
        can still be used to create a pipeline.

    Parameters
    ----------
    n_neighbors: int, optional
        Number of neighbors to
        consider when computing
        the score.
    p: int, optional
        The ``p`` of the ``p``-distances
        (distance metric used during
        the model computation).

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``n_neighbors_``: int
        Number of neighbors.
    ``p_``: int
        The ``p`` of the ``p``-distances.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.VASTModel.get_attributes`
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

    First we import the ``KNeighborsRegressor`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import KNeighborsRegressor

    Then we can create the model:

    .. ipython:: python

        model = KNeighborsRegressor()

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


    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_linear_model_knnreg_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        result = model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_linear_model_knnreg_report.html

    .. important::

        Most metrics are computed using a single SQL query, but some
        of them might require multiple SQL queries. Selecting only the
        necessary metrics in the report can help optimize performance.
        E.g. ``model.report(metrics = ["mse", "r2"])``.

    For ``KNeighborsRegressor``, we can easily get the ANOVA table using:

    .. ipython:: python
        :suppress:

        result = model.report(metrics = "anova")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_linear_model_knnreg_report_anova.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        result = model.report(metrics = "anova")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_linear_model_knnreg_report_anova.html

    You can also use the ``KNeighborsRegressor.score`` function to compute the R-squared
    value:

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
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_linear_model_knnreg_prediction.html", "w")
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
                "density"
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_linear_model_knnreg_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.linear_model.LinearModel.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    Parameter Modification
    ^^^^^^^^^^^^^^^^^^^^^^^

    In order to see the parameters:

    .. ipython:: python

        model.get_params()

    And to manually change some of the parameters:

    .. ipython:: python

        model.set_params({'n_neighbors': 3})
    """

    # Properties.

    @property
    def _is_native(self) -> Literal[False]:
        return False

    @property
    def _fit_sql(self) -> Literal[""]:
        return ""

    @property
    def _predict_sql(self) -> Literal[""]:
        return ""

    @property
    def _model_subcategory(self) -> Literal["REGRESSOR"]:
        return "REGRESSOR"

    @property
    def _model_type(self) -> Literal["KNeighborsRegressor"]:
        return "KNeighborsRegressor"

    @property
    def _attributes(self) -> list[str]:
        return ["n_neighbors_", "p_"]

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        n_neighbors: int = 5,
        p: int = 2,
    ) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {"n_neighbors": n_neighbors, "p": p}

    def drop(self) -> bool:
        """
        ``KNeighborsRegressor`` models
        are not stored in the VAST DB.

        The method will always return
        ``False``.
        """
        return False

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        self.p_ = self.parameters["p"]
        self.n_neighbors_ = self.parameters["n_neighbors"]

    # I/O Methods.

    def deploySQL(
        self,
        X: Optional[SQLColumns] = None,
        test_relation: Optional[str] = None,
        key_columns: Optional[SQLColumns] = None,
    ) -> str:
        """
        Returns the SQL code
        needed to deploy the
        model.

        Parameters
        ----------
        X: SQLColumns
            ``list`` of the predictors.
        test_relation: str, optional
            Relation used to do the
            predictions.
        key_columns: SQLColumns, optional
            A ``list`` of columns to
            include in the results,
            but to exclude from
            computation of the
            prediction.

        Returns
        -------
        str
            the SQL code needed
            to deploy the model.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. code-block:: python

            import vastorbit as vo

        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        Let's divide the dataset into
        training and testing subsets.

        .. code-block:: python

            train, test = data.train_test_split(test_size = 0.2)

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            import vastorbit.datasets as vod
            data = vod.load_winequality()
            train, test = data.train_test_split(test_size = 0.2)

        First we import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import KNeighborsRegressor

        Then we can create the model:

        .. ipython:: python

            model = KNeighborsRegressor()

        We can now fit the model:

        .. ipython:: python

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

        And generate the VAST SQL:

        .. ipython:: python

            model.deploySQL()

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.neighbors.KNeighborsRegressor`
            for more information about the
            different methods and usages.
        """
        key_columns = format_type(key_columns, dtype=list)
        X = format_type(X, dtype=list, na_out=self.X)
        X = quote_ident(X)
        if not test_relation:
            test_relation = self.test_relation
            if not key_columns:
                key_columns = [self.y]
        p = self.parameters["p"]
        X_str = ", ".join([f"x.{x}" for x in X])
        if key_columns:
            key_columns_str = ", " + ", ".join(
                ["x." + quote_ident(x) for x in key_columns]
            )
        else:
            key_columns_str = ""
        sql = [f"POWER(ABS(x.{X[i]} - y.{self.X[i]}), {p})" for i in range(len(self.X))]
        sql = f"""
            SELECT 
                {X_str}{key_columns_str}, 
                ROW_NUMBER() OVER(PARTITION BY {X_str}, row_id 
                                  ORDER BY POWER({' + '.join(sql)}, 1 / {p})) 
                                  AS ordered_distance, 
                y.{self.y} AS predict_neighbors, 
                row_id 
            FROM
                (SELECT 
                    *, 
                    ROW_NUMBER() OVER() AS row_id 
                 FROM {test_relation} 
                 WHERE {" AND ".join([f"{x} IS NOT NULL" for x in X])}) x 
                 CROSS JOIN 
                 (SELECT 
                    * 
                 FROM {self.input_relation} 
                 WHERE {" AND ".join([f"{x} IS NOT NULL" for x in self.X])}) y"""
        if key_columns:
            key_columns_str = ", " + ", ".join(quote_ident(key_columns))
        n_neighbors = self.parameters["n_neighbors"]
        sql = f"""
            (SELECT 
                {", ".join(X)}{key_columns_str}, 
                AVG(predict_neighbors) AS predict_neighbors 
             FROM ({sql}) z 
             WHERE ordered_distance <= {n_neighbors} 
             GROUP BY {", ".join(X)}{key_columns_str}, row_id) knr_table"""
        return clean_query(sql)

    # Prediction / Transformation Methods.

    def _predict(
        self,
        vdf: SQLRelation,
        X: Optional[SQLColumns] = None,
        name: Optional[str] = None,
        inplace: bool = True,
        **kwargs,
    ) -> VastFrame:
        """
        Predicts using the input relation.
        """
        X = format_type(X, dtype=list)
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        X = quote_ident(X) if (X) else self.X
        key_columns = vdf.get_columns(exclude_columns=X)
        if "key_columns" in kwargs:
            key_columns_arg = None
        else:
            key_columns_arg = key_columns
        if not name:
            name = f"{self._model_type}_" + "".join(
                ch for ch in self.model_name if ch.isalnum()
            )
        if key_columns:
            key_columns_str = ", " + ", ".join(key_columns)
        else:
            key_columns_str = ""
        table = self.deploySQL(
            X=X, test_relation=vdf.current_relation(), key_columns=key_columns_arg
        )
        sql = f"""
            SELECT 
                {", ".join(X)}{key_columns_str}, 
                predict_neighbors AS {name} 
             FROM {table}"""
        if inplace:
            vdf.__init__(sql)
            return vdf
        else:
            return VastFrame(sql)

    # Plotting Methods.

    def _get_plot_args(self, method: Optional[str] = None) -> list:
        """
        Returns the args used by plotting methods.
        """
        if method == "contour":
            args = [
                self.X,
                self.deploySQL(X=self.X, test_relation="{1}").replace(
                    "predict_neighbors", "{0}"
                ),
            ]
        else:
            raise NotImplementedError
        return args


"""
Algorithms used for classification.
"""


class KNeighborsClassifier(MulticlassClassifier):
    """
    [Beta Version]
    Creates a KNeighborsClassifier object using the
    k-nearest neighbors algorithm. This object uses
    pure SQL to compute all the distances and final
    score.

    .. warning::

        This   algorithm   uses  a   CROSS  JOIN
        during   computation  and  is  therefore
        computationally  expensive at  O(n * n),
        where n is the total number of elements.
        Since  KNeighborsClassifier uses  the p-
        distance,  it  is  highly  sensitive  to
        unnormalized data.

    .. important::

        This algorithm is not VAST
        Native and relies solely on SQL
        for attribute computation. While
        this model does not take advantage
        of the benefits provided by a model
        management system, including versioning
        and tracking, the SQL code it generates
        can still be used to create a pipeline.

    Parameters
    ----------
    n_neighbors: int, optional
        Number of neighbors to consider
        when computing  the score.
    p: int, optional
        The ``p`` of the ``p``-distances
        (distance metric used during the
        model computation).

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``n_neighbors_``: int
        Number of neighbors.
    ``p_``: int
        The ``p`` of the ``p``-distances.
    ``classes_``: numpy.array
        The classes labels.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.VASTModel.get_attributes`
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

    There are multiple classes for the "quality" column. Let us
    filter the data for classes between 5 and 7:

    .. code-block:: python

        data = data[data["quality"]>=5]
        data = data[data["quality"]<=7]

    We can the balance the dataset to ensure equal representation:

    .. code-block:: python

        data = data.balance(column="quality", x = 1)

    You can easily divide your dataset
    into training and testing subsets
    using the
    ``VastFrame.``:py:meth:`~vastorbit.VastFrame.train_test_split`
    method. This is a crucial step when
    preparing your data for machine learning,
    as it allows you to evaluate the
    performance of your models accurately.

    .. code-block:: python

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
        data = data[data["quality"]>=5]
        data = data[data["quality"]<=7]
        data = data.balance(column="quality", x = 1)
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

    First we import the ``KNeighborsClassifier`` model:

    .. code-block::

        from vastorbit.machine_learning.vast import KNeighborsClassifier

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast import KNeighborsClassifier

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = KNeighborsClassifier(
           n_neighbors = 10,
           p = 2,
        )

    .. hint::

        In :py:mod:`vastorbit` 1.0.x and higher,
        you do not need to specify the model name,
        as the name is automatically assigned. If
        you need to re-use the model, you can fetch
        the model name from the model's attributes.

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
                "density",
                "pH",
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

    .. important::

        As this model is not native, it solely
        relies on SQL statements to compute
        various attributes, storing them within
        the object. No data is saved in the database.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. ipython:: python
        :suppress:

        result = model.report()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_report.html

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
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_report_cutoff.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.report(cutoff = 0.2)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_report_cutoff.html


    You can also use the ``KNeighborsClassifier.score`` function to compute any
    classification metric. The default metric is the accuracy:

    .. ipython:: python

        model.score(metric = "f1", average = "macro")

    .. note::

        For multi-class scoring, :py:mod:`vastorbit`
        allows the flexibility to use three averaging
        techniques: ``micro``, ``macro`` and ``weighted``.
        Please refer to
        `this link <https://towardsdatascience.com/micro-macro-weighted-averages-of-f1-score-clearly-explained-b603420b292f>`__
        for more details on how they are calculated.

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
                "density",
                "pH",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "density",
                "pH",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_prediction.html

    .. note::

        Predictions can be made automatically
        using the test set, in which case you
        don't need to specify the predictors.
        Alternatively, you can pass only the
        :py:class:`~VastFrame` to the
        :py:meth:`~vastorbit.machine_learning.vast.linear_model.LinearModel.predict`
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
                "density",
                "pH",
            ],
            "prediction",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_proba.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.predict_proba(
            test,
            [
                "fixed_acidity",
                "volatile_acidity",
                "density",
                "pH",
            ],
            "prediction",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_proba.html

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

            model.confusion_matrix(pos_label = "5", cutoff = 0.6)

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

        model.roc_curve(pos_label = "5")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.roc_curve(pos_label = "5")
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_roc.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_neighbors_knc_roc.html

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

        model.contour(pos_label = "5")

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

        model.set_params({'n_neighbors': 8})

    Model Register
    ^^^^^^^^^^^^^^

    As this model is not native, it does not
    support model management and versioning.
    However, it is possible to use the SQL
    code it generates for deployment.

    Model Exporting
    ^^^^^^^^^^^^^^^^

    It is not possible to export this type of
    model, but you can still examine the SQL
    code generated by using the
    :py:meth:`~vastorbit.machine_learning.vast.neighbors.KNeighborsClassifier.deploySQL`
    method.
    """

    # Properties.

    @property
    def _is_native(self) -> Literal[False]:
        return False

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
    def _model_type(self) -> Literal["KNeighborsClassifier"]:
        return "KNeighborsClassifier"

    @property
    def _attributes(self) -> list[str]:
        return ["classes_", "n_neighbors_", "p_"]

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        n_neighbors: int = 5,
        p: int = 2,
    ) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {"n_neighbors": n_neighbors, "p": p}

    def drop(self) -> bool:
        """
        ``KNeighborsClassifier`` models
        are not stored in the VAST DB.

        The method will always return
        ``False``.
        """
        return False

    def _check_cutoff(
        self, cutoff: Optional[PythonNumber] = None
    ) -> Optional[PythonNumber]:
        if isinstance(cutoff, NoneType):
            return 1.0 / len(self.classes_)
        elif not 0 <= cutoff <= 1:
            ValueError(
                "Incorrect parameter 'cutoff'.\nThe cutoff "
                "must be between 0 and 1, inclusive."
            )
        else:
            return cutoff

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the
        model's attributes.
        """
        self.classes_ = self._get_classes()
        self.p_ = self.parameters["p"]
        self.n_neighbors_ = self.parameters["n_neighbors"]

    # I/O Methods.

    def deploySQL(
        self,
        X: Optional[SQLColumns] = None,
        test_relation: Optional[str] = None,
        predict: bool = False,
        key_columns: Optional[SQLColumns] = None,
    ) -> str:
        """
        Returns the SQL code
        needed to deploy the
        model.

        Parameters
        ----------
        X: SQLColumns
            ``list`` of the predictors.
        test_relation: str, optional
            Relation used to do
            the predictions.
        predict: bool, optional
            If set to ``True``, returns
            the prediction instead
            of the probability.
        key_columns: SQLColumns, optional
            A ``list`` of columns to
            include in the results,
            but to exclude from
            computation of the
            prediction.

        Returns
        -------
        SQLExpression
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

        Let's divide the dataset into
        training and testing subsets.

        .. code-block:: python

            train, test = data.train_test_split(test_size = 0.2)

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data = data[data["quality"]>=5]
            data = data[data["quality"]<=7]
            data = data.balance(column="quality", x = 1)
            train, test = data.train_test_split(test_size = 0.2)

        We import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import KNeighborsClassifier

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import KNeighborsClassifier

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = KNeighborsClassifier(
               n_neighbors = 10,
               p = 2,
            )

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(
                train,
                [
                    "fixed_acidity",
                    "volatile_acidity",
                    "density",
                    "pH",
                ],
                "quality",
                test,
            )

        And generate the VAST SQL:

        .. ipython:: python

            model.deploySQL()

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.neighbors.KNeighborsClassifier`
            for more information about the
            different methods and usages.
        """
        key_columns = format_type(key_columns, dtype=list)
        X = format_type(X, dtype=list, na_out=self.X)
        X = quote_ident(X)
        if not test_relation:
            test_relation = self.test_relation
            if not key_columns:
                key_columns = [self.y]
        p = self.parameters["p"]
        n_neighbors = self.parameters["n_neighbors"]
        X_str = ", ".join([f"x.{x}" for x in X])
        if key_columns:
            key_columns_str = ", " + ", ".join(
                ["x." + quote_ident(x) for x in key_columns]
            )
        else:
            key_columns_str = ""
        sql = [f"POWER(ABS(x.{X[i]} - y.{self.X[i]}), {p})" for i in range(len(self.X))]
        sql = f"""
            SELECT 
                {X_str}{key_columns_str}, 
                ROW_NUMBER() OVER(PARTITION BY 
                                  {X_str}, row_id 
                                  ORDER BY POWER({' + '.join(sql)}, 1 / {p})) 
                                  AS ordered_distance, 
                y.{self.y} AS predict_neighbors, 
                row_id 
            FROM 
                (SELECT 
                    *, 
                    ROW_NUMBER() OVER() AS row_id 
                 FROM {test_relation} 
                 WHERE {" AND ".join([f"{x} IS NOT NULL" for x in X])}) x 
                 CROSS JOIN 
                (SELECT * FROM {self.input_relation} 
                 WHERE {" AND ".join([f"{x} IS NOT NULL" for x in self.X])}) y"""

        if key_columns:
            key_columns_str = ", " + ", ".join(quote_ident(key_columns))

        sql = f"""
            (SELECT 
                row_id, 
                {", ".join(X)}{key_columns_str}, 
                predict_neighbors, 
                COUNT(*) / {n_neighbors} AS proba_predict 
             FROM ({sql}) z 
             WHERE ordered_distance <= {n_neighbors} 
             GROUP BY {", ".join(X)}{key_columns_str}, 
                      row_id, 
                      predict_neighbors) kneighbors_table"""
        if predict:
            sql = f"""
                (SELECT 
                    {", ".join(X)}{key_columns_str}, 
                    predict_neighbors 
                 FROM 
                    (SELECT 
                        {", ".join(X)}{key_columns_str}, 
                        predict_neighbors, 
                        ROW_NUMBER() OVER (PARTITION BY {", ".join(X)} 
                                           ORDER BY proba_predict DESC) 
                                           AS order_prediction 
                     FROM {sql}) VASTORBIT_SUBTABLE 
                     WHERE order_prediction = 1) predict_neighbors_table"""
        return clean_query(sql)

    # Prediction / Transformation Methods.

    def _get_final_relation(
        self,
        pos_label: Optional[PythonScalar] = None,
    ) -> str:
        """
        Returns the final relation
        used to do the predictions.
        """
        filter_sql = ""
        if not (isinstance(pos_label, NoneType)):
            filter_sql = f"WHERE predict_neighbors = '{pos_label}'"
        return f"""
            (SELECT 
                * 
                FROM {self.deploySQL()}
            {filter_sql}) 
            final_centroids_relation"""

    def _get_y_proba(
        self,
        pos_label: Optional[PythonScalar] = None,
    ) -> str:
        """
        Returns the input which
        represents the model's
        probabilities.
        """
        return "proba_predict"

    def _get_y_score(
        self,
        pos_label: Optional[PythonScalar] = None,
        cutoff: Optional[PythonNumber] = None,
        allSQL: bool = False,
    ) -> str:
        """
        Returns the input that
        represents the model's
        scoring.
        """
        cutoff = self._check_cutoff(cutoff=cutoff)
        if isinstance(pos_label, NoneType) and not (self._is_binary_classifier()):
            return "predict_neighbors"
        elif self._is_binary_classifier():
            return f"""
                (CASE 
                    WHEN proba_predict > {cutoff} THEN '{self.classes_[1]}'
                    ELSE '{self.classes_[0]}'
                 END)"""
        elif allSQL:
            return f"""
                (CASE 
                    WHEN predict_neighbors = '{pos_label}' THEN proba_predict
                    ELSE NULL 
                 END)"""
        else:
            return f"""
                (CASE 
                    WHEN proba_predict < {cutoff} AND predict_neighbors = '{pos_label}' THEN NULL
                    ELSE predict_neighbors 
                 END)"""

    def _compute_accuracy(self) -> float:
        """
        Computes the
        model accuracy.
        """
        return mt.accuracy_score(
            self.y, "predict_neighbors", self.deploySQL(predict=True)
        )

    def _confusion_matrix(
        self,
        pos_label: Optional[PythonScalar] = None,
        cutoff: Optional[PythonNumber] = None,
    ) -> TableSample:
        """
        Computes the model
        confusion matrix.
        """
        if isinstance(pos_label, NoneType):
            input_relation = f"""
                (SELECT 
                    *, 
                    ROW_NUMBER() OVER(PARTITION BY {", ".join(self.X)}, row_id 
                                      ORDER BY proba_predict DESC) AS pos 
                 FROM {self.deploySQL()}) neighbors_table WHERE pos = 1"""
            return mt.confusion_matrix(
                self.y, "predict_neighbors", input_relation, labels=self.classes_
            )
        else:
            cutoff = self._check_cutoff(cutoff=cutoff)
            pos_label = self._check_pos_label(pos_label=pos_label)
            input_relation = (
                self.deploySQL() + f" WHERE predict_neighbors = '{pos_label}'"
            )
            y_score = f"(CASE WHEN proba_predict > {cutoff} THEN 1 ELSE 0 END)"
            y_true = f"CASE WHEN {self.y} = '{pos_label}' THEN 1 ELSE 0 END"
            return mt.confusion_matrix(y_true, y_score, input_relation)

    # Model Evaluation Methods.

    def _predict(
        self,
        vdf: SQLRelation,
        X: Optional[SQLColumns] = None,
        name: Optional[str] = None,
        cutoff: Optional[PythonNumber] = None,
        inplace: bool = True,
        **kwargs,
    ) -> VastFrame:
        """
        Predicts using the
        input relation.
        """
        X = format_type(X, dtype=list)
        cutoff = self._check_cutoff(cutoff=cutoff)
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        X = quote_ident(X) if (X) else self.X
        key_columns = vdf.get_columns(exclude_columns=X)
        if "key_columns" in kwargs:
            key_columns_arg = None
        else:
            key_columns_arg = key_columns
        if key_columns:
            key_columns_str = ", " + ", ".join(key_columns)
        else:
            key_columns_str = ""
        if not name:
            name = gen_name([self._model_type, self.model_name])

        if self._is_binary_classifier():
            table = self.deploySQL(
                X=X, test_relation=vdf.current_relation(), key_columns=key_columns_arg
            )
            sql = f"""
                (SELECT 
                    {", ".join(X)}{key_columns_str}, 
                    (CASE 
                        WHEN proba_predict > {cutoff} 
                            THEN '{self.classes_[1]}' 
                        ELSE '{self.classes_[0]}' 
                     END) AS {name} 
                 FROM {table} 
                 WHERE predict_neighbors = '{self.classes_[1]}') VASTORBIT_SUBTABLE"""
        else:
            table = self.deploySQL(
                X=X,
                test_relation=vdf.current_relation(),
                key_columns=key_columns_arg,
                predict=True,
            )
            sql = f"""
                SELECT 
                    {", ".join(X)}{key_columns_str}, 
                    predict_neighbors AS {name} 
                 FROM {table}"""
        if inplace:
            vdf.__init__(sql)
            return vdf
        else:
            return VastFrame(sql)

    def _predict_proba(
        self,
        vdf: SQLRelation,
        X: Optional[SQLColumns] = None,
        name: Optional[str] = None,
        pos_label: Optional[PythonScalar] = None,
        inplace: bool = True,
        **kwargs,
    ) -> VastFrame:
        """
        Returns the model's probabilities
        using the input relation.
        """
        # Inititalization
        X = format_type(X, dtype=list)
        assert pos_label is None or pos_label in self.classes_, ValueError(
            (
                "Incorrect parameter 'pos_label'.\nThe class label "
                f"must be in [{'|'.join([str(c) for c in self.classes_])}]. "
                f"Found '{pos_label}'."
            )
        )
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        X = quote_ident(X) if (X) else self.X
        key_columns = vdf.get_columns(exclude_columns=X)
        if not name:
            name = gen_name([self._model_type, self.model_name])
        if "key_columns" in kwargs:
            key_columns_arg = None
        else:
            key_columns_arg = key_columns

        # Generating the probabilities
        if isinstance(pos_label, NoneType):
            predict = [
                f"""COALESCE(AVG(CASE WHEN predict_neighbors = '{c}' THEN proba_predict END), 0) AS {gen_name([name, c])}"""
                for c in self.classes_
            ]
        else:
            predict = [f"""COALESCE(AVG(CASE WHEN predict_neighbors = '{pos_label}' THEN proba_predict END), 0) AS {name}"""]
        if key_columns:
            key_columns_str = ", " + ", ".join(key_columns)
        else:
            key_columns_str = ""
        table = self.deploySQL(
            X=X, test_relation=vdf.current_relation(), key_columns=key_columns_arg
        )
        sql = f"""
            SELECT 
                {", ".join(X)}{key_columns_str}, 
                {", ".join(predict)} 
             FROM {table} 
             GROUP BY {", ".join(X + key_columns)}"""

        # Result
        if inplace:
            vdf.__init__(sql)
            return vdf
        else:
            return VastFrame(sql)

    # Plotting Methods.

    def _get_plot_args(
        self, pos_label: Optional[PythonScalar] = None, method: Optional[str] = None
    ) -> list:
        """
        Returns the args used
        by plotting methods.
        """
        pos_label = self._check_pos_label(pos_label)
        if method == "contour":
            sql = (
                f"""
                SELECT
                    {', '.join(self.X)},
                    COALESCE(AVG(CASE WHEN predict_neighbors = '{pos_label}' THEN proba_predict ELSE NULL), 0) AS {{0}}
                FROM """
                + self.deploySQL(X=self.X, test_relation="{1}")
                + f" GROUP BY {', '.join(self.X)}"
            )
            args = [self.X, sql]
        else:
            input_relation = (
                self.deploySQL() + f" WHERE predict_neighbors = '{pos_label}'"
            )
            args = [self.y, "proba_predict", input_relation, pos_label]
        return args

    def _get_plot_kwargs(
        self,
        pos_label: Optional[PythonScalar] = None,
        nbins: int = 30,
        chart: Optional[PlottingObject] = None,
        method: Optional[str] = None,
    ) -> dict:
        """
        Returns the kwargs used
        by plotting methods.
        """
        pos_label = self._check_pos_label(pos_label)
        res = {"nbins": nbins, "chart": chart}
        if method == "contour":
            res["func_name"] = f"p({self.y} = '{pos_label}')"
        elif method == "cutoff":
            res["cutoff_curve"] = True
        return res


"""
Algorithms used for anomaly detection.
"""


class LocalOutlierFactor(VASTModel):
    """
    [Beta Version]
    Creates a ``LocalOutlierFactor`` object by using the Local Outlier
    Factor algorithm. Works without creating persistent tables -
    generates SQL on-demand.
    """

    # Properties.
    @property
    def _model_category(self) -> Literal["UNSUPERVISED"]:
        return "UNSUPERVISED"

    @property
    def _model_subcategory(self) -> Literal["ANOMALY_DETECTION"]:
        return "ANOMALY_DETECTION"

    @property
    def _model_type(self) -> Literal["LocalOutlierFactor"]:
        return "LocalOutlierFactor"

    @property
    def _attributes(self) -> list[str]:
        return ["n_neighbors_", "p_", "n_errors_", "cnt_"]

    # System & Special Methods.
    @save_vastorbit_logs
    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        n_neighbors: int = 20,
        p: int = 2,
    ) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {"n_neighbors": n_neighbors, "p": p}
        self._lof_sql = None  # Store the SQL query

    def drop(self) -> bool:
        """Drops the model (clears stored SQL)."""
        self._lof_sql = None
        return True

    # Attributes Methods.
    def _compute_attributes(self) -> None:
        """Computes the model's attributes."""
        self.p_ = self.parameters["p"]
        self.n_neighbors_ = self.parameters["n_neighbors"]

        # Compute count from the SQL
        if self._lof_sql:
            self.cnt_ = _executeSQL(
                query=f"SELECT COUNT(*) FROM ({self._lof_sql}) t",
                method="fetchfirstelem",
                print_time_sql=False,
            )
        else:
            self.cnt_ = 0

    def _generate_lof_sql(self) -> str:
        """
        Generates the complete LOF computation SQL.
        Returns a query that can be used as a subquery.
        """
        n_neighbors = self.parameters["n_neighbors"]
        p = self.parameters["p"]
        X = self.X
        key_columns = self.key_columns

        # Build distance formula
        sql = [f"POWER(ABS(x.{X[i]} - y.{X[i]}), {p})" for i in range(len(X))]
        distance = f"POWER({' + '.join(sql)}, 1 / {p})"

        # Complete LOF query
        query = f"""
            WITH 
            main_data AS (
                SELECT 
                    ROW_NUMBER() OVER() AS id,
                    {', '.join(X + key_columns)}
                FROM {self.input_relation}
                WHERE {' AND '.join([f"{x} IS NOT NULL" for x in X])}
            ),
            distance_table AS (
                SELECT 
                    x.id AS node_id,
                    y.id AS nn_id,
                    {distance} AS distance,
                    ROW_NUMBER() OVER(PARTITION BY x.id ORDER BY {distance}) AS knn
                FROM main_data AS x
                CROSS JOIN main_data AS y
            ),
            knn_distances AS (
                SELECT *
                FROM distance_table
                WHERE knn <= {n_neighbors + 1}
            ),
            kdistance_table AS (
                SELECT 
                    node_id,
                    nn_id,
                    distance
                FROM knn_distances
                WHERE knn = {n_neighbors + 1}
            ),
            lrd_table AS (
                SELECT 
                    knn.node_id,
                    {n_neighbors} / SUM(
                        CASE 
                            WHEN knn.distance > kdist.distance 
                            THEN knn.distance 
                            ELSE kdist.distance 
                        END
                    ) AS lrd
                FROM knn_distances AS knn
                LEFT JOIN kdistance_table AS kdist
                    ON knn.nn_id = kdist.node_id
                GROUP BY knn.node_id
            ),
            lof_scores AS (
                SELECT 
                    knn.node_id,
                    SUM(lrd_nn.lrd) / (MAX(lrd_node.lrd) * {n_neighbors}) AS lof
                FROM knn_distances AS knn
                LEFT JOIN lrd_table AS lrd_node
                    ON knn.node_id = lrd_node.node_id
                LEFT JOIN lrd_table AS lrd_nn
                    ON knn.nn_id = lrd_nn.node_id
                GROUP BY knn.node_id
            )
            SELECT 
                {', '.join(X + key_columns)},
                CASE 
                    WHEN lof.lof > 1e100 OR lof.lof != lof.lof THEN 0 
                    ELSE lof.lof 
                END AS lof_score
            FROM main_data AS m
            LEFT JOIN lof_scores AS lof
                ON m.id = lof.node_id
        """

        return query

    # Model Fitting Method.
    def fit(
        self,
        input_relation: SQLRelation,
        X: Optional[SQLColumns] = None,
        key_columns: Optional[SQLColumns] = None,
        index: Optional[str] = None,
        return_report: bool = False,
    ) -> None:
        """
        Trains the model by generating and storing the LOF SQL query.
        """
        X, key_columns = format_type(X, key_columns, dtype=list)
        X = quote_ident(X)
        self.key_columns = quote_ident(key_columns)

        if isinstance(input_relation, VastFrame):
            self.input_relation = input_relation.current_relation()
            if not X:
                X = input_relation.numcol()
        else:
            self.input_relation = input_relation
            if not X:
                X = VastFrame(input_relation).numcol()

        self.X = X

        # Generate and store the SQL
        self._lof_sql = self._generate_lof_sql()

        # Compute error count
        self.n_errors_ = _executeSQL(
            query=f"""
                SELECT COUNT(*) 
                FROM ({self._lof_sql}) t
                WHERE lof_score > 1e100 OR lof_score != lof_score
            """,
            method="fetchfirstelem",
            print_time_sql=False,
        )

        self._compute_attributes()

    # Prediction / Transformation Methods.
    def predict(self) -> VastFrame:
        """
        Returns a VastFrame with the LOF scores.
        """
        if self._lof_sql is None:
            raise ValueError("Model not fitted yet. Call fit() first.")

        # Return VastFrame directly from the SQL
        return VastFrame(self._lof_sql)

    # Plotting Methods.
    def plot(
        self,
        max_nb_points: int = 100,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """Draws the model."""
        if self._lof_sql is None:
            raise ValueError("Model not fitted yet. Call fit() first.")

        vo_plt, kwargs = self.get_plotting_lib(
            class_name="LOFPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.LOFPlot(
            vdf=VastFrame(self._lof_sql),
            columns=self.X + ["lof_score"],
            max_nb_points=max_nb_points,
        ).draw(**kwargs)
