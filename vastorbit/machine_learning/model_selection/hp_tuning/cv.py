"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional, Union
from collections.abc import Iterable

import numpy as np

from tqdm.auto import tqdm

import vastorbit._config.config as conf
from vastorbit._typing import PythonNumber, PythonScalar, SQLColumns, SQLRelation
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._format import format_type
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._sys import _executeSQL


from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame

from vastorbit.datasets.generators import gen_meshgrid, gen_dataset

from vastorbit.machine_learning.model_selection.hp_tuning.param_gen import (
    gen_params_grid,
    parameter_grid,
)
from vastorbit.machine_learning.model_selection.model_validation import cross_validate
import vastorbit.machine_learning.vast as vml
from vastorbit.machine_learning.vast.base import VASTModel

from vastorbit.sql.drop import drop

"""
RANDOM
"""


@save_vastorbit_logs
def randomized_search_cv(
    estimator: VASTModel,
    input_relation: SQLRelation,
    X: SQLColumns,
    y: str,
    metric: str = "auto",
    cv: int = 3,
    average: Literal["binary", "micro", "macro", "weighted"] = "weighted",
    pos_label: Optional[PythonScalar] = None,
    cutoff: float = -1,
    nbins: int = 1000,
    lmax: int = 4,
    optimized_grid: int = 1,
    print_info: bool = True,
) -> TableSample:
    """
    Computes the K-Fold randomized
    search of an estimator.

    Parameters
    ----------
    estimator: VASTModel
        VAST estimator with
        a fit method.
    input_relation: SQLRelation
        Relation used to
        train the model.
    X: SQLColumns
        ``list`` of the
        predictor columns.
    y: str
        Response Column.
    metric: str, optional
        Metric used for the
        model evaluation.

        - auto:
            logloss for classification
            & RMSE for regression.

        **For Classification**

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

        **For Regression**

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
        The method used to
        compute the final
        score for multiclass
        -classification.

        - binary:
            considers one of the
            classes as positive
            and use the binary
            confusion matrix to
            compute the score.

        - micro:
            positive and negative
            values globally.

        - macro:
            average of the score
            of each class.

        - weighted:
            weighted average of
            the score of each
            class.

    pos_label: PythonScalar, optional
        The main class to be
        considered as positive
        (classification only).
    cutoff: float, optional
        The model cutoff
        (classification only).
    nbins: int, optional
        Number of bins used to
        compute the different
        parameters categories.
    lmax: int, optional
        Maximum length of each
        parameter ``list``.
    optimized_grid: int, optional
        If set to ``0``, the
        randomness is based
        on the input parameters.
        If set to ``1``, the
        randomness is limited
        to some  parameters
        while others  are
        picked based on a
        default grid.
        If set to ``2``,
        there is no randomness
        and a default grid
        is returned.
    print_info: bool, optional
        If set to ``True``, prints
        the model information at
        each step.

    Returns
    -------
    TableSample
        result of the randomized
        search.

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
    :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.randomized_search_cv`
    function to find the K-Fold
    randomized search of an
    estimator.

    .. code-block:: python

        from vastorbit.machine_learning.model_selection import randomized_search_cv

        result = randomized_search_cv(
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
            lmax = 5,
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        import vastorbit as vo
        from vastorbit.machine_learning.model_selection import randomized_search_cv

        result = randomized_search_cv(
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
            lmax = 5,
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_model_selection_hp_tuning_cv_randomized_search_cv_table.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_hp_tuning_cv_randomized_search_cv_table.html

    .. note::

        :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.randomized_search_cv`
        works almost the same as
        :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.grid_search_cv`.
        The only difference is that
        the function will generate
        a random grid of parameters
        at the beginning.

    .. seealso::

        | :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.grid_search_cv` :
            Computes the k-fold grid
            search of an estimator.
    """
    X = format_type(X, dtype=list)
    param_grid = gen_params_grid(estimator, nbins, len(X), lmax, optimized_grid)
    return grid_search_cv(
        estimator,
        param_grid,
        input_relation,
        X,
        y,
        metric=metric,
        cv=cv,
        average=average,
        pos_label=pos_label,
        cutoff=cutoff,
        training_score=True,
        skip_error="no_print",
        print_info=print_info,
    )


"""
GRID SEARCH
"""


@save_vastorbit_logs
def grid_search_cv(
    estimator: VASTModel,
    param_grid: Union[dict, list],
    input_relation: SQLRelation,
    X: SQLColumns,
    y: str,
    metric: str = "auto",
    cv: int = 3,
    average: Literal["binary", "micro", "macro", "weighted"] = "weighted",
    pos_label: Optional[PythonScalar] = None,
    cutoff: PythonNumber = -1,
    training_score: bool = True,
    skip_error: Union[bool, Literal["no_print"]] = True,
    print_info: bool = True,
    **kwargs,
) -> TableSample:
    """
    Computes the k-fold grid
    search of an estimator.

    Parameters
    ----------
    estimator: VASTModel
        VAST estimator
        with a fit method.
    param_grid: dict | list
        Dictionary of the parameters
        to test. It can also be a
        ``list`` of the different
        combinations.
    input_relation: SQLRelation
        Relation used to
        train the model.
    X: SQLColumns
        ``list`` of the
        predictor columns.
    y: str
        Response Column.
    metric: str, optional
        Metric used for the
        model evaluation.

        - auto:
            logloss for classification
            & RMSE for regression.

        **For Classification**

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

        **For Regression**

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
    training_score: bool, optional
        If set to ``True``,
        the training score
        is computed with the
        validation score.
    skip_error: bool, optional
        If set to ``True`` and
        an error occurs, the error
        is displayed but not raised.
    print_info: bool, optional
        If set to ``True``, prints
        the model information at
        each step.

    Returns
    -------
    TableSample
        Result of the grid search.

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
    :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.grid_search_cv`
    to search for the estimator using
    k-fold grid search.

    .. code-block:: python

        from vastorbit.machine_learning.model_selection import grid_search_cv

        result = grid_search_cv(
            model,
            {
                "tol": [1e-2, 1e-4, 1e-6],
                "max_iter": [3, 10, 100],
                "solver": ["newton-cg", "lbfgs"]
            },
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
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        import vastorbit as vo
        from vastorbit.machine_learning.model_selection import grid_search_cv

        result = grid_search_cv(
            model,
            {
                "tol": [1e-2, 1e-4, 1e-6],
                "max_iter": [3, 10, 100],
                "solver": ["newton-cg", "lbfgs"]
            },
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
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_model_selection_hp_tuning_cv_grid_search_cv_table.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_hp_tuning_cv_grid_search_cv_table.html

    .. note::

        Grid Search in vastorbit involves
        systematically evaluating different
        combinations of hyperparameters
        specified in a predefined grid. It
        iterates through all possible parameter
        combinations, training and evaluating
        models for each set. This exhaustive
        search helps identify the optimal
        hyperparameters that result in the best
        model performance. Grid Search is a
        powerful tool for fine-tuning machine
        learning models in vastorbit to achieve
        better accuracy and generalization
        across various datasets.

    .. seealso::

        | :py:func:`~vastorbit.machine_learning.model_selection.hp_tuning.cv.randomized_search_cv` :
            Computes the K-Fold randomized
            search of an estimator.
    """
    X = format_type(X, dtype=list)
    if estimator._model_subcategory == "REGRESSOR" and metric == "auto":
        metric = "rmse"
    elif metric == "auto":
        metric = "logloss"
    if isinstance(param_grid, dict):
        for param in param_grid:
            assert isinstance(param_grid[param], Iterable) and not (
                isinstance(param_grid[param], str)
            ), ValueError(
                "When of type dictionary, the parameter 'param_grid'"
                " must be a dictionary where each value is a list of "
                f"parameters, found {type(param_grid[param])} for "
                f"parameter '{param}'."
            )
        all_configuration = parameter_grid(param_grid)
    else:
        for idx, param in enumerate(param_grid):
            assert isinstance(param, dict), ValueError(
                "When of type List, the parameter 'param_grid' must "
                f"be a list of dictionaries, found {type(param)} for elem '{idx}'."
            )
        all_configuration = param_grid
    # testing all the config
    for config in all_configuration:
        estimator.set_params(config)
    # applying all the config
    data = []
    if all_configuration == []:
        all_configuration = [{}]
    if (
        conf.get_option("tqdm")
        and ("tqdm" not in kwargs or ("tqdm" in kwargs and kwargs["tqdm"]))
        and print_info
    ):
        loop = tqdm(all_configuration)
    else:
        loop = all_configuration
    for config in loop:
        try:
            estimator.set_params(config)
            current_cv = cross_validate(
                estimator,
                input_relation,
                X,
                y,
                metrics=metric,
                cv=cv,
                average=average,
                pos_label=pos_label,
                cutoff=cutoff,
                show_time=True,
                training_score=training_score,
                tqdm=False,
            )
            if training_score:
                keys = list(current_cv[0].values)
                data += [
                    (
                        estimator.get_params(),
                        current_cv[0][keys[1]][cv],
                        current_cv[1][keys[1]][cv],
                        current_cv[0][keys[2]][cv],
                        current_cv[0][keys[1]][cv + 1],
                        current_cv[1][keys[1]][cv + 1],
                    )
                ]
                if print_info:
                    print_message(
                        f"Model: {str(estimator.__class__).split('.')[-1][:-2]}; "
                        f"Parameters: {config}; \033[91mTest_score: "
                        f"{current_cv[0][keys[1]][cv]}\033[0m; \033[92mTrain_score:"
                        f" {current_cv[1][keys[1]][cv]}\033[0m; \033[94mTime:"
                        f" {current_cv[0][keys[2]][cv]}\033[0m;"
                    )
            else:
                keys = list(current_cv.values)
                data += [
                    (
                        config,
                        current_cv[keys[1]][cv],
                        current_cv[keys[2]][cv],
                        current_cv[keys[1]][cv + 1],
                    )
                ]
                if print_info:
                    print_message(
                        f"Model: {str(estimator.__class__).split('.')[-1][:-2]}; "
                        f"Parameters: {config}; \033[91mTest_score: "
                        f"{current_cv[keys[1]][cv]}\033[0m; \033[94mTime:"
                        f"{current_cv[keys[2]][cv]}\033[0m;"
                    )
        except Exception as e:
            if skip_error and skip_error != "no_print":
                print_message(e)
            elif not skip_error:
                raise e
    if not data:
        if training_score:
            return TableSample(
                {
                    "parameters": [],
                    "avg_score": [],
                    "avg_train_score": [],
                    "avg_time": [],
                    "score_std": [],
                    "score_train_std": [],
                }
            )
        else:
            return TableSample(
                {
                    "parameters": [],
                    "avg_score": [],
                    "avg_time": [],
                    "score_std": [],
                }
            )
    reverse = True
    if metric in [
        "logloss",
        "max",
        "mae",
        "median",
        "mse",
        "msle",
        "rmse",
        "aic",
        "bic",
        "auto",
    ]:
        reverse = False
    data.sort(key=lambda tup: tup[1], reverse=reverse)
    if training_score:
        result = TableSample(
            {
                "parameters": [d[0] for d in data],
                "avg_score": [d[1] for d in data],
                "avg_train_score": [d[2] for d in data],
                "avg_time": [d[3] for d in data],
                "score_std": [d[4] for d in data],
                "score_train_std": [d[5] for d in data],
            }
        )
        if print_info and (
            "final_print" not in kwargs or kwargs["final_print"] != "no_print"
        ):
            print_message("\033[1mGrid Search Selected Model\033[0m")
            print_message(
                f"{str(estimator.__class__).split('.')[-1][:-2]}; "
                f"Parameters: {result['parameters'][0]}; \033"
                f"[91mTest_score: {result['avg_score'][0]}\033[0m;"
                f" \033[92mTrain_score: {result['avg_train_score'][0]}"
                f"\033[0m; \033[94mTime: {result['avg_time'][0]}\033[0m;"
            )
    else:
        result = TableSample(
            {
                "parameters": [d[0] for d in data],
                "avg_score": [d[1] for d in data],
                "avg_time": [d[2] for d in data],
                "score_std": [d[3] for d in data],
            }
        )
        if print_info and (
            "final_print" not in kwargs or kwargs["final_print"] != "no_print"
        ):
            print_message("\033[1mGrid Search Selected Model\033[0m")
            print_message(
                f"{str(estimator.__class__).split('.')[-1][:-2]}; "
                f"Parameters: {result['parameters'][0]}; \033[91mTest_score:"
                f" {result['avg_score'][0]}\033[0m; \033[94mTime:"
                f" {result['avg_time'][0]}\033[0m;"
            )
    return result
