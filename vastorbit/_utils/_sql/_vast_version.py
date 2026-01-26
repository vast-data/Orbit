"""
SPDX-License-Identifier: Apache-2.0
"""

from functools import wraps
from typing import Any, Callable, Optional

from vastorbit._utils._sql._format import format_type
from vastorbit.connection.connect import current_cursor
from vastorbit.errors import VersionError

MINIMUM_VAST_VERSION = {
    "ARIMA": [23, 4, 0],
    "AR": [11, 0, 0],
    "ARMA": [12, 0, 4],
    "balance": [8, 1, 1],
    "BernoulliNB": [8, 0, 0],
    "BisectingKMeans": [9, 3, 1],
    "CategoricalNB": [8, 0, 0],
    "confusion_matrix": [8, 0, 0],
    "DecisionTreeClassifier": [8, 1, 1],
    "DecisionTreeRegressor": [9, 0, 1],
    "DummyTreeClassifier": [8, 1, 1],
    "DummyTreeRegressor": [9, 0, 1],
    "edit_distance": [10, 1, 0],
    "ElasticNet": [8, 0, 0],
    "GaussianNB": [8, 0, 0],
    "gen_dataset": [9, 3, 0],
    "get_tree": [9, 1, 1],
    "IsolationForest": [12, 0, 0],
    "jaro_distance": [12, 0, 2],
    "jaro_winkler_distance": [12, 0, 2],
    "Lasso": [8, 0, 0],
    "lift_chart": [8, 0, 0],
    "LinearRegression": [8, 0, 0],
    "LinearSVC": [8, 1, 0],
    "LinearSVR": [8, 1, 1],
    "LogisticRegression": [8, 0, 0],
    "KMeans": [8, 0, 0],
    "KPrototypes": [12, 0, 3],
    "MA": [11, 0, 0],
    "MCA": [9, 1, 0],
    "MinMaxScaler": [8, 1, 0],
    "MultinomialNB": [8, 0, 0],
    "NaiveBayes": [8, 0, 0],
    "OneHotEncoder": [9, 0, 0],
    "PCA": [9, 1, 0],
    "PLSRegression": [24, 2, 0],
    "PoissonRegressor": [12, 0, 0],
    "prc_curve": [9, 1, 0],
    "QueryProfiler": [11, 0, 0],
    "QueryProfilerComparison": [11, 0, 0],
    "QueryProfilerInterface": [11, 0, 0],
    "QueryProfilerStats": [11, 0, 0],
    "RandomForestClassifier": [8, 1, 1],
    "RandomForestRegressor": [9, 0, 1],
    "read_file": [11, 1, 1],
    "RegisteredModel": [12, 0, 4],
    "Ridge": [8, 0, 0],
    "RobustScaler": [8, 1, 0],
    "roc_curve": [8, 0, 0],
    "Scaler": [8, 1, 0],
    "soundex": [10, 1, 0],
    "soundex_matches": [10, 1, 0],
    "StandardScaler": [8, 1, 0],
    "SVD": [9, 1, 0],
    "VAR": [24, 2, 1],
    "XGBClassifier": [11, 1, 0],
    "XGBRegressor": [11, 1, 0],
}


def check_minimum_version(func: Callable) -> Callable:
    """
    check_minimum_version decorator. It
    simplifies the code by checking
    whether the feature is available
    in the user's version.

    You can utilize the decorator as
    follows.

    .. code-block:: python

        from vastorbit._utils._sql._vast_version import check_minimum_version

        @check_minimum_version
        def function(...):
            ...

    .. note::

        vastorbit will automatically check the version
        in the ``MINIMUM_VAST_VERSION`` dictionary.
        Ensure to update the dictionary to accommodate
        your specific function name. For classes,
        place it above the ``__init__`` function.
    """

    @wraps(func)
    def func_prec_check_minimum_version(*args, **kwargs) -> Any:
        fun_name, object_name = func.__name__, ""
        if len(args) > 0:
            object_name = type(args[0]).__name__
        name = object_name if fun_name == "__init__" else fun_name
        vast_version(MINIMUM_VAST_VERSION[name])

        return func(*args, **kwargs)

    return func_prec_check_minimum_version


def vast_version(condition: Optional[list] = None) -> tuple[int, int, int, int]:
    """
    Returns the VAST Version.

    Parameters
    ----------
    condition: list, optional
        List of the minimal version
        information. If the current
        version is not greater or
        equal to this version, the
        function raises an error.

    Returns
    -------
    tuple
        List containing the version
        information.
        ``(MAJOR, MINOR, PATCH, POST)``

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._vast_version import vast_version

        # Function Example.
        vast_version()

    .. note::

        Utilize the condition parameter if you want
        to raise an error when the condition is not
        met. The following code will raise an error
        if the VAST version is less than 23.3.

        .. code-block:: python

            vast_version(condition = (23, 3, 0))

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    condition = format_type(condition, dtype=list)
    if len(condition) > 0:
        condition = condition + [0 for elem in range(4 - len(condition))]
    current_version = int(
        current_cursor()
        .execute("SELECT /*+LABEL('_version')*/ version()")
        .fetchone()[0]
    )
    res = [current_version, 0, 0]
    if condition:
        if condition[0] < res[0]:
            test = True
        elif condition[0] == res[0]:
            if condition[1] < res[1]:
                test = True
            elif condition[1] == res[1]:
                if condition[2] <= res[2]:
                    test = True
                else:
                    test = False
            else:
                test = False
        else:
            test = False
        if not test:
            v0, v1, v2 = res[0], res[1], str(res[2]).split("-", maxsplit=1)[0]
            v = ".".join([str(c) for c in condition[:3]])
            raise VersionError(
                (
                    "This Function is not available for VAST version "
                    f"{v0}.{v1}.{v2}.\nPlease upgrade your VAST "
                    f"version to at least {v} to get this functionality."
                )
            )
    return tuple(res)
