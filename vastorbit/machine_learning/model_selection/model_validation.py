"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import warnings
import secrets
import time
from typing import Literal, Optional, Union

import numpy as np

from tqdm.auto import tqdm

import vastorbit._config.config as conf
from vastorbit._typing import (
    NoneType,
    PlottingObject,
    PythonNumber,
    PythonScalar,
    SQLColumns,
    SQLRelation,
)
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type

from vastorbit.sql.drop import drop

from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame

from vastorbit.machine_learning.vast.base import VASTModel

from vastorbit.plotting._utils import PlottingUtils


def _materialize(vdf: VastFrame, label: str) -> str:
    """
    Persists ``vdf`` to a temporary base table and returns the table name.

    The source frame is **not** mutated (``inplace=False``): if the underlying
    ``CREATE TABLE`` fails, the caller's frame must keep pointing at its original
    relation. The previous ``inplace=True`` version repointed the frame *before*
    the create was confirmed, so a failed/partial create left every later query
    referencing a table that never existed (``TABLE_NOT_FOUND``). Callers repoint
    explicitly via ``VastFrame(name)`` only after this returns successfully, and
    clean up with :py:func:`_drop_relation`.
    """
    name = gen_tmp_name(schema=conf.get_option("temp_schema"), name=f"cv_{label}")
    vdf.to_db(name, relation_type="table", inplace=False)
    return name


def _drop_relation(name: Optional[str]) -> None:
    """Best-effort drop of a temporary table created by :py:func:`_materialize`."""
    if not name:
        return
    try:
        drop(name, method="table")
    except Exception:
        pass


@save_vastorbit_logs
def cross_validate(
    estimator: VASTModel,
    input_relation: SQLRelation,
    X: SQLColumns,
    y: str,
    metrics: Union[None, str, list[str]] = None,
    cv: int = 3,
    average: Literal["binary", "micro", "macro", "weighted"] = "weighted",
    pos_label: Optional[PythonScalar] = None,
    cutoff: PythonNumber = -1,
    show_time: bool = True,
    training_score: bool = False,
    **kwargs,
) -> TableSample:
    """
    Computes the K-Fold cross
    validation of an estimator.

    Parameters
    ----------
    estimator: object
        VAST estimator
        with a fit method.
    input_relation: SQLRelation
        Relation used to
        train the model.
    X: SQLColumns
        ``list`` of the predictor
        columns.
    y: str
        Response Column.
    metrics: str | list, optional
        Metrics used to do the model
        evaluation. It can also be a
        ``list`` of metrics. If empty,
        most of the estimator metrics
        are computed.

        For Classification:

        - accuracy:
            Accuracy.

            .. math::

                Accuracy = \\frac{TP + TN}{TP + TN + FP + FN}

        - auc:
            Area Under the Curve (ROC).

            .. math::

                AUC = \\int_{0}^{1} TPR(FPR) \\, dFPR

        - ba:
            Balanced Accuracy.

            .. math::

                BA = \\frac{TPR + TNR}{2}

        - bm:
            Informedness

            .. math::

                BM = TPR + TNR - 1

        - csi:
            Critical Success Index

            .. math::

                index = \\frac{TP}{TP + FN + FP}

        - f1:
            F1 Score
            .. math::

                F_1 Score = 2 \\times \frac{Precision \\times Recall}{Precision + Recall}

        - fdr:
            False Discovery Rate

            .. math::

                FDR = 1 - PPV

        - fm:
            Fowlkes-Mallows index

            .. math::

                FM = \\sqrt{PPV * TPR}

        - fnr:
            False Negative Rate

            .. math::

                FNR = \\frac{FN}{FN + TP}

        - for:
            False Omission Rate

            .. math::

                FOR = 1 - NPV

        - fpr:
            False Positive Rate

            .. math::

                FPR = \\frac{FP}{FP + TN}

        - logloss:
            Log Loss

            .. math::

                Loss = -\\frac{1}{N} \\sum_{i=1}^{N} \\left( y_i \\log(p_i) + (1 - y_i) \\log(1 - p_i) \\right)

        - lr+:
            Positive Likelihood Ratio.

            .. math::

                LR+ = \\frac{TPR}{FPR}

        - lr-:
            Negative Likelihood Ratio.

            .. math::

                LR- = \\frac{FNR}{TNR}

        - dor:
            Diagnostic Odds Ratio.

            .. math::

                DOR = \\frac{TP \\times TN}{FP \\times FN}

        - mcc:
            Matthews Correlation Coefficient

        - mk:
            Markedness

            .. math::

                MK = PPV + NPV - 1

        - npv:
            Negative Predictive Value

            .. math::

                NPV = \\frac{TN}{TN + FN}

        - prc_auc:
            Area Under the Curve (PRC)

            .. math::

                AUC = \\int_{0}^{1} Precision(Recall) \\, dRecall

        - precision:
            Precision

            .. math::

                TP / (TP + FP)

        - pt:
            Prevalence Threshold.

            .. math::

                \\frac{\\sqrt{FPR}}{\\sqrt{TPR} + \\sqrt{FPR}}

        - recall:
            Recall.

            .. math::
                TP / (TP + FN)

        - specificity:
            Specificity.

            .. math::

                TN / (TN + FP)

        For Regression:

        - max:
            Max Error.

            .. math::

                ME = \\max_{i=1}^{n} \\left| y_i - \\hat{y}_i \\right|

        - mae:
            Mean Absolute Error.

            .. math::

                MAE = \\frac{1}{n} \\sum_{i=1}^{n} \\left| y_i - \\hat{y}_i \\right|

        - median:
            Median Absolute Error.

            .. math::

                MedAE = \\text{median}_{i=1}^{n} \\left| y_i - \\hat{y}_i \\right|

        - mse:
            Mean Squared Error.

            .. math::

                MSE = \\frac{1}{n} \\sum_{i=1}^{n} \\left( y_i - \\hat{y}_i \\right)^2

        - msle:
            Mean Squared Log Error.

            .. math::

                MSLE = \\frac{1}{n} \\sum_{i=1}^{n} (\\log(1 + y_i) - \\log(1 + \\hat{y}_i))^2

        - r2:
            R squared coefficient.

            .. math::

                R^2 = 1 - \\frac{\\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}{\\sum_{i=1}^{n} (y_i - \\bar{y})^2}

        - r2a:
            R2 adjusted

            .. math::

                \\text{Adjusted } R^2 = 1 - \\frac{(1 - R^2)(n - 1)}{n - k - 1}

        - var:
            Explained Variance.

            .. math::

                VAR = 1 - \\frac{Var(y - \\hat{y})}{Var(y)}

        - rmse:
            Root-mean-squared error

            .. math::

                RMSE = \\sqrt{\\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}

    cv: int, optional
        Number of folds.
    average: str, optional
        The method used to compute
        the final score for
        multiclass-classification.

        - binary:
            considers one of the classes
            as positive and use the binary
            confusion matrix to compute the
            score.

        - micro:
            positive and negative values
            globally.

        - macro:
            average of the score of each
            class.

        - weighted:
            weighted average of the
            score of each class.

    pos_label: PythonScalar, optional
        The main class to be
        considered as positive
        (classification only).
    cutoff: PythonNumber, optional
        The model cutoff
        (classification only).
    show_time: bool, optional
        If set to ``True``,
        the time and the
        average time are
        added to the report.
    training_score: bool, optional
        If set to ``True``,
        the training score
        is computed with the
        validation score.

    Returns
    -------
    TableSample
        result of the
        cross validation.

    Examples
    --------
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

    For this example, we will use
    the Wine Quality dataset.

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

    Next, we can initialize a
    :py:class:`~vastorbit.machine_learning.vast.linear_model.LogisticRegression`
    model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import LogisticRegression

        model = LogisticRegression()

    Now we can conveniently use the
    :py:func:`~vastorbit.machine_learning.model_selection.model_validation.cross_validate`
    function to evaluate our model.

    .. code-block:: python

        from vastorbit.machine_learning.model_selection import cross_validate

        cross_validate(
            model,
            input_relation = data,
            X = [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            y = "good",
            cv = 3,
            metric = "auc",
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        import vastorbit as vo
        from vastorbit.machine_learning.model_selection import cross_validate

        result = cross_validate(
            model,
            input_relation = data,
            X = [
                "fixed_acidity",
                "volatile_acidity",
                "citric_acid",
                "residual_sugar",
                "chlorides",
                "density",
            ],
            y = "good",
            cv = 3,
            metric = "auc",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_model_selection_cross_validate_table.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_cross_validate_table.html

    .. note::

        vastorbit Cross-Validation involves splitting
        the dataset into multiple folds, training the
        model on subsets of the data, and evaluating
        its performance on the remaining data. This
        process is repeated for each fold, and the
        overall model performance is averaged across
        all folds. Cross-Validation helps assess how
        well a model generalizes to new, unseen data
        and provides more robust performance metrics.
        In vastorbit, cross-validation is a valuable
        technique for model evaluation and parameter
        tuning, contributing to the reliability and
        effectiveness of machine learning models.

        For example,
        :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.grid_search_cv`,
        :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.randomized_search_cv`
        and some other model validation functions
        are using Cross-Validation techniques.

    .. seealso::

        | :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.grid_search_cv` :
            Computes the k-fold grid
            search of an estimator.
        | :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.randomized_search_cv` :
            Computes the K-Fold randomized
            search of an estimator.
    """
    X = format_type(X, dtype=list)
    if isinstance(input_relation, str):
        input_relation = VastFrame(input_relation)
    # Materialize the (possibly deeply nested) input relation to a flat base
    # table ONCE up front. train_test_split runs an APPROX_PERCENTILE over
    # ``input_relation`` on every fold; if the relation is deeply nested that
    # query alone exceeds Trino's stage limit before any per-fold flattening
    # can help. Flattening here keeps every fold's split query small.
    _cv_base_name = None
    try:
        _cv_base_name = _materialize(input_relation, "cv_base")
        input_relation = VastFrame(_cv_base_name)
    except Exception as e:
        # Falling back to the un-flattened relation means train_test_split runs
        # its APPROX_PERCENTILE over a deeply nested query and may exceed Trino's
        # stage limit. Surface why the flatten failed instead of swallowing it.
        warnings.warn(f"cross_validate: could not materialize cv_base ({e!r}); "
                      "falling back to the nested relation.")
        _drop_relation(_cv_base_name)
        _cv_base_name = None
    if cv < 2:
        raise ValueError("Cross Validation is only possible with at least 2 folds")
    if estimator._model_subcategory == "REGRESSOR":
        all_metrics = [
            "explained_variance",
            "max_error",
            "median_absolute_error",
            "mean_absolute_error",
            "mean_squared_error",
            "root_mean_squared_error",
            "r2",
            "r2_adj",
            "aic",
            "bic",
        ]
    elif estimator._model_subcategory == "CLASSIFIER":
        all_metrics = [
            "auc",
            "prc_auc",
            "accuracy",
            "log_loss",
            "precision",
            "recall",
            "f1_score",
            "mcc",
            "informedness",
            "markedness",
            "csi",
        ]
    else:
        raise Exception(
            "Cross Validation is only possible for Regressors and Classifiers"
        )
    if isinstance(metrics, NoneType):
        final_metrics = all_metrics
    elif isinstance(metrics, str):
        final_metrics = [metrics]
    else:
        final_metrics = copy.deepcopy(metrics)
    result = {"index": final_metrics}
    if training_score:
        result_train = {"index": final_metrics}
    total_time = []
    if conf.get_option("tqdm") and (
        "tqdm" not in kwargs or ("tqdm" in kwargs and kwargs["tqdm"])
    ):
        loop = tqdm(range(cv))
    else:
        loop = range(cv)
    for i in loop:
        estimator.drop()
        random_state = conf.get_option("random_state")
        random_state = (
            secrets.randbelow(2000001) - 1000000
            if not random_state
            else random_state + i
        )
        train, test = input_relation.train_test_split(
            test_size=float(1 / cv), order_by=[X[0]], random_state=random_state
        )
        # Flatten the (possibly deeply nested) split/sample relations into base
        # tables so the per-fold metric query stays under Trino's stage limit.
        train_name = test_name = None
        try:
            train_name = _materialize(train, "train")
            train = VastFrame(train_name)
            test_name = _materialize(test, "test")
            test = VastFrame(test_name)
            start_time = time.time()
            estimator.fit(
                train,
                X,
                y,
                test,
                return_report=True,
            )
            total_time += [time.time() - start_time]
            fun = estimator.report
            kwargs = {"metrics": final_metrics}
            key = "value"
            if estimator._model_subcategory == "CLASSIFIER" and not (
                estimator._is_binary_classifier()
            ):
                key = f"avg_{average}"
            result[f"{i + 1}-fold"] = fun(**kwargs)[key]
            if training_score:
                estimator.test_relation = estimator.input_relation
                result_train[f"{i + 1}-fold"] = fun(**kwargs)[key]
        finally:
            estimator.drop()
            _drop_relation(train_name)
            _drop_relation(test_name)
    n = len(final_metrics)
    total = [[] for item in range(n)]
    total_time = np.array(total_time).astype(float)
    for i in range(cv):
        for k in range(n):
            total[k] += [result[f"{i + 1}-fold"][k]]
    if training_score:
        total_train = [[] for item in range(n)]
        for i in range(cv):
            for k in range(n):
                total_train[k] += [result_train[f"{i + 1}-fold"][k]]
    result["avg"], result["std"] = [], []
    if training_score:
        result_train["avg"], result_train["std"] = [], []
    for item in total:
        result["avg"] += [np.nanmean(np.array(item).astype(float))]
        result["std"] += [np.nanstd(np.array(item).astype(float))]
    if training_score:
        for item in total_train:
            result_train["avg"] += [np.nanmean(np.array(item).astype(float))]
            result_train["std"] += [np.nanstd(np.array(item).astype(float))]

    total_time = list(total_time) + [np.nanmean(total_time), np.nanstd(total_time)]
    result = TableSample(values=result).transpose()
    if show_time:
        result.values["time"] = total_time
    if training_score:
        result_train = TableSample(values=result_train).transpose()
        if show_time:
            result_train.values["time"] = total_time
    _drop_relation(_cv_base_name)
    if training_score:
        return result, result_train
    else:
        return result


@save_vastorbit_logs
def learning_curve(
    estimator: VASTModel,
    input_relation: SQLRelation,
    X: SQLColumns,
    y: str,
    sizes: Optional[list] = None,
    method: Literal["efficiency", "performance", "scalability"] = "efficiency",
    metric: str = "auto",
    cv: int = 3,
    average: Literal["binary", "micro", "macro", "weighted"] = "weighted",
    pos_label: Optional[PythonScalar] = None,
    cutoff: PythonNumber = -1,
    std_coeff: PythonNumber = 1,
    chart: Optional[PlottingObject] = None,
    return_chart: Optional[bool] = False,
    **style_kwargs,
) -> TableSample:
    """
    Draws the learning curve.

    Parameters
    ----------
    estimator: object
        VAST estimator
        with a fit method.
    input_relation: SQLRelation
        Relation used to
        train the model.
    X: SQLColumns
        ``list`` of the predictor
        columns.
    y: str
        Response Column.
    sizes: list, optional
        Different sizes of the
        dataset used to train
        the model. Multiple
        models are trained
        using the different
        sizes.
    method: str, optional
        Method used to plot the curve.

         - efficiency:
            Draws train/test score
            vs sample size.

         - performance:
            draws score vs time.

         - scalability:
            draws time vs
            sample size.
    metric: str, optional
        Metric used to do
        the model evaluation.

         - auto:
            logloss for classification
            & RMSE for regression.

        For Classification:

        - accuracy:
            Accuracy.

            .. math::

                Accuracy = \\frac{TP + TN}{TP + TN + FP + FN}

        - auc:
            Area Under the Curve (ROC).

            .. math::

                AUC = \\int_{0}^{1} TPR(FPR) \\, dFPR

        - ba:
            Balanced Accuracy.

            .. math::

                BA = \\frac{TPR + TNR}{2}

        - bm:
            Informedness

            .. math::

                BM = TPR + TNR - 1

        - csi:
            Critical Success Index

            .. math::

                index = \\frac{TP}{TP + FN + FP}

        - f1:
            F1 Score
            .. math::

                F_1 Score = 2 \\times \frac{Precision \\times Recall}{Precision + Recall}

        - fdr:
            False Discovery Rate

            .. math::

                FDR = 1 - PPV

        - fm:
            Fowlkes-Mallows index

            .. math::

                FM = \\sqrt{PPV * TPR}

        - fnr:
            False Negative Rate

            .. math::

                FNR = \\frac{FN}{FN + TP}

        - for:
            False Omission Rate

            .. math::

                FOR = 1 - NPV

        - fpr:
            False Positive Rate

            .. math::

                FPR = \\frac{FP}{FP + TN}

        - logloss:
            Log Loss

            .. math::

                Loss = -\\frac{1}{N} \\sum_{i=1}^{N} \\left( y_i \\log(p_i) + (1 - y_i) \\log(1 - p_i) \\right)

        - lr+:
            Positive Likelihood Ratio.

            .. math::

                LR+ = \\frac{TPR}{FPR}

        - lr-:
            Negative Likelihood Ratio.

            .. math::

                LR- = \\frac{FNR}{TNR}

        - dor:
            Diagnostic Odds Ratio.

            .. math::

                DOR = \\frac{TP \\times TN}{FP \\times FN}

        - mcc:
            Matthews Correlation Coefficient

        - mk:
            Markedness

            .. math::

                MK = PPV + NPV - 1

        - npv:
            Negative Predictive Value

            .. math::

                NPV = \\frac{TN}{TN + FN}

        - prc_auc:
            Area Under the Curve (PRC)

            .. math::

                AUC = \\int_{0}^{1} Precision(Recall) \\, dRecall

        - precision:
            Precision

            .. math::

                TP / (TP + FP)

        - pt:
            Prevalence Threshold.

            .. math::

                \\frac{\\sqrt{FPR}}{\\sqrt{TPR} + \\sqrt{FPR}}

        - recall:
            Recall.

            .. math::
                TP / (TP + FN)

        - specificity:
            Specificity.

            .. math::

                TN / (TN + FP)

        For Regression:

        - max:
            Max Error.

            .. math::

                ME = \\max_{i=1}^{n} \\left| y_i - \\hat{y}_i \\right|

        - mae:
            Mean Absolute Error.

            .. math::

                MAE = \\frac{1}{n} \\sum_{i=1}^{n} \\left| y_i - \\hat{y}_i \\right|

        - median:
            Median Absolute Error.

            .. math::

                MedAE = \\text{median}_{i=1}^{n} \\left| y_i - \\hat{y}_i \\right|

        - mse:
            Mean Squared Error.

            .. math::

                MSE = \\frac{1}{n} \\sum_{i=1}^{n} \\left( y_i - \\hat{y}_i \\right)^2

        - msle:
            Mean Squared Log Error.

            .. math::

                MSLE = \\frac{1}{n} \\sum_{i=1}^{n} (\\log(1 + y_i) - \\log(1 + \\hat{y}_i))^2

        - r2:
            R squared coefficient.

            .. math::

                R^2 = 1 - \\frac{\\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}{\\sum_{i=1}^{n} (y_i - \\bar{y})^2}

        - r2a:
            R2 adjusted

            .. math::

                \\text{Adjusted } R^2 = 1 - \\frac{(1 - R^2)(n - 1)}{n - k - 1}

        - var:
            Explained Variance.

            .. math::

                VAR = 1 - \\frac{Var(y - \\hat{y})}{Var(y)}

        - rmse:
            Root-mean-squared error

            .. math::

                RMSE = \\sqrt{\\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}

    cv: int, optional
        Number of folds.
    average: str, optional
        The method used to compute
        the final score for
        multiclass-classification.

        - binary:
            considers one of the classes
            as positive and use the binary
            confusion matrix to compute the
            score.

        - micro:
            positive and negative
            values globally.

        - macro:
            average of the score
            of each class.

        - weighted:
            weighted average of the
            score of each class.

    pos_label: PythonScalar, optional
        The main class to  be
        considered as positive
        (classification only).
    cutoff: float, optional
        The model cutoff
        (classification only).
    std_coeff: PythonNumber, optional
        Value of the standard
        deviation coefficient
        used to compute the
        area plot around each
        score.
    chart: PlottingObject, optional
        The chart object to
        plot on.
    return_chart: bool, optional
        Select whether you want
        to get the chart as the
        output only.
    ``**style_kwargs``
        Any optional parameter
        to pass to the Plotting
        functions.

    Returns
    -------
    TableSample
        result of the
        learning curve.

    Examples
    --------

    .. note::

        The below example is a very basic one. For
        other more detailed examples and customization
        options, please see :ref:`chart_gallery.learning`

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

    Let's generate a dataset
    using the following data.

    .. ipython:: python

        import random

        N = 200 # Number of Records
        k = 10 # step

        # Normal Distributions
        x = np.random.normal(5, 1, round(N / 2))
        y = np.random.normal(3, 1, round(N / 2))
        z = np.random.normal(3, 1, round(N / 2))

        # Creating a VastFrame with two clusters
        data = vo.VastFrame({
            "x": np.concatenate([x, x + k]),
            "y": np.concatenate([y, y + k]),
            "z": np.concatenate([z, z + k]),
            "c": [random.randint(0, 1) for _ in range(N)]
        })

    Let's proceed by creating a
    :py:class:`~vastorbit.machine_learning.vast.ensemble.RandomForestClassifier`
    model using the complete dataset.

    .. ipython:: python

        # Importing the VAST ML module
        import vastorbit.machine_learning.vast as vml

        # Importing the model selection module
        import vastorbit.machine_learning.model_selection as vms

        # Defining the Model
        model = vml.RandomForestClassifier(n_estimators = 5)

    Let's draw the learning curve.

    .. code-block:: python

        vms.learning_curve(
            model,
            data,
            X = ["x", "y", "z"],
            y = "c",
            method = "efficiency",
            cv = 3,
            metric = "auc",
            return_chart = True,
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = vms.learning_curve(
            model,
            data,
            X = ["x", "y", "z"],
            y = "c",
            method = "efficiency",
            cv = 3,
            metric = "auc",
            return_chart = True,
        )
        fig.write_html("figures/plotting_machine_learning_validation_learning_efficiency.html")

    .. raw:: html
          :file: SPHINX_DIRECTORY/figures/plotting_machine_learning_validation_learning_efficiency.html

    .. note::

        vastorbit's Learning Curve tool is
        an essential asset for evaluating
        machine learning models. It enables
        users to visualize a model's performance
        by plotting key metrics against varying
        training dataset sizes. By analyzing
        these curves, data analysts can identify
        issues such as overfitting or underfitting,
        make informed decisions about dataset size,
        and optimize model performance. This feature
        plays a crucial role in enhancing model
        robustness and facilitating data-driven
        decision-making.

    .. seealso::

        | :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.plotting.validation_curve` :
            Draws the validation curve.
    """
    sizes = format_type(sizes, dtype=list, na_out=[0.1, 0.33, 0.55, 0.78, 1.0])
    for s in sizes:
        assert 0 < s <= 1, ValueError("Each size must be in ]0,1].")
    if estimator._model_subcategory == "REGRESSOR" and metric == "auto":
        metric = "rmse"
    elif metric == "auto":
        metric = "logloss"
    if isinstance(input_relation, str):
        input_relation = VastFrame(input_relation)
    # Flatten the input relation up front: ``.sample()`` runs a quantile
    # aggregation over ``input_relation`` for every size, which exceeds Trino's
    # stage limit when the relation is deeply nested. Materializing once keeps
    # each size's sample query small.
    _lc_base_name = None
    try:
        _lc_base_name = _materialize(input_relation, "lc_base")
        input_relation = VastFrame(_lc_base_name)
    except Exception as e:
        warnings.warn(f"learning_curve: could not materialize lc_base ({e!r}); "
                      "falling back to the nested relation.")
        _drop_relation(_lc_base_name)
        _lc_base_name = None
    lc_result_final = []
    sizes = sorted(set(sizes))
    if conf.get_option("tqdm"):
        loop = tqdm(sizes)
    else:
        loop = sizes
    for s in loop:
        relation = input_relation.sample(x=s)
        # Persist the sample once per size: makes it deterministic across the cv
        # folds (the same rows are reused) and removes one more nested sub-query
        # from each fold's metric query.
        relation_name = None
        try:
            relation_name = _materialize(relation, "lc_sample")
            relation = VastFrame(relation_name)
            lc_result = cross_validate(
                estimator,
                relation,
                X,
                y,
                metrics=metric,
                cv=cv,
                average=average,
                pos_label=pos_label,
                cutoff=cutoff,
                show_time=True,
                training_score=True,
                tqdm=False,
            )
            lc_result_final += [
                (
                    relation.shape()[0],
                    lc_result[0][metric][cv],
                    lc_result[0][metric][cv + 1],
                    lc_result[1][metric][cv],
                    lc_result[1][metric][cv + 1],
                    lc_result[0]["time"][cv],
                    lc_result[0]["time"][cv + 1],
                )
            ]
        finally:
            _drop_relation(relation_name)
    if method in ("efficiency", "scalability"):
        lc_result_final.sort(key=lambda tup: tup[0])
    else:
        lc_result_final.sort(key=lambda tup: tup[5])
    result = TableSample(
        {
            "n": [elem[0] for elem in lc_result_final],
            metric: [elem[1] for elem in lc_result_final],
            metric + "_std": [elem[2] for elem in lc_result_final],
            metric + "_train": [elem[3] for elem in lc_result_final],
            metric + "_train_std": [elem[4] for elem in lc_result_final],
            "time": [elem[5] for elem in lc_result_final],
            "time_std": [elem[6] for elem in lc_result_final],
        }
    )
    if method == "efficiency":
        x = np.array(result["n"])
        Y = np.column_stack(
            (
                [
                    result[metric][i] - std_coeff * result[metric + "_std"][i]
                    for i in range(len(sizes))
                ],
                result[metric],
                [
                    result[metric][i] + std_coeff * result[metric + "_std"][i]
                    for i in range(len(sizes))
                ],
                [
                    result[metric + "_train"][i]
                    - std_coeff * result[metric + "_train_std"][i]
                    for i in range(len(sizes))
                ],
                result[metric + "_train"],
                [
                    result[metric + "_train"][i]
                    + std_coeff * result[metric + "_train_std"][i]
                    for i in range(len(sizes))
                ],
            ),
        )
        order_by = "n"
        y_label = metric
        columns = [
            "test",
            "train",
        ]
    elif method == "performance":
        x = np.array(result["time"])
        Y = np.column_stack(
            (
                [
                    result[metric][i] - std_coeff * result[metric + "_std"][i]
                    for i in range(len(sizes))
                ],
                result[metric],
                [
                    result[metric][i] + std_coeff * result[metric + "_std"][i]
                    for i in range(len(sizes))
                ],
            )
        )
        order_by = "time"
        y_label = None
        columns = [metric]
    else:
        x = np.array(result["n"])
        Y = np.column_stack(
            (
                [
                    result["time"][i] - std_coeff * result["time_std"][i]
                    for i in range(len(sizes))
                ],
                result["time"],
                [
                    result["time"][i] + std_coeff * result["time_std"][i]
                    for i in range(len(sizes))
                ],
            )
        )
        order_by = "n"
        y_label = None
        columns = ["time"]
    vo_plt, kwargs = PlottingUtils().get_plotting_lib(
        class_name="RangeCurve",
        chart=chart,
        style_kwargs=style_kwargs,
    )
    data = {"x": x, "Y": Y}
    layout = {"columns": columns, "order_by": order_by, "y_label": y_label}
    vo_plt.RangeCurve(data=data, layout=layout).draw(**kwargs)
    _drop_relation(_lc_base_name)
    if return_chart:
        return vo_plt.RangeCurve(data=data, layout=layout).draw(**kwargs)
    return result