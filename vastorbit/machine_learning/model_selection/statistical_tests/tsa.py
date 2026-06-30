"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional, Union

from scipy.stats import chi2, norm, f
import numpy as np

from vastorbit.connection.errors import QueryError

import vastorbit._config.config as conf
from vastorbit._typing import (
    NoneType,
    PythonNumber,
    SQLColumns,
    SQLRelation,
    TimeInterval,
)
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import (
    clean_query,
    format_type,
    quote_ident,
)
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit._utils._sql._vast_version import vast_version

from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame

from vastorbit.machine_learning.vast.linear_model import (
    LinearModel,
    LinearRegression,
)

"""
Time Series Tests: stationarity / trend.
"""


def _df_critical_value(alpha: float, N: int, with_trend: bool) -> float:
    """
    Dickey Fuller test Critical value.
    """
    if not with_trend:
        if N <= 25:
            if alpha == 0.01:
                return -3.75
            if alpha == 0.10:
                return -2.62
            if alpha == 0.025:
                return -3.33
            return -3.00
        elif N <= 50:
            if alpha == 0.01:
                return -3.58
            if alpha == 0.10:
                return -2.60
            if alpha == 0.025:
                return -3.22
            return -2.93
        elif N <= 100:
            if alpha == 0.01:
                return -3.51
            if alpha == 0.10:
                return -2.58
            if alpha == 0.025:
                return -3.17
            return -2.89
        elif N <= 250:
            if alpha == 0.01:
                return -3.46
            if alpha == 0.10:
                return -2.57
            if alpha == 0.025:
                return -3.14
            return -2.88
        elif N <= 500:
            if alpha == 0.01:
                return -3.44
            if alpha == 0.10:
                return -2.57
            if alpha == 0.025:
                return -3.13
            return -2.87
        else:
            if alpha == 0.01:
                return -3.43
            if alpha == 0.10:
                return -2.57
            if alpha == 0.025:
                return -3.12
            return -2.86
    else:
        if N <= 25:
            if alpha == 0.01:
                return -4.38
            if alpha == 0.10:
                return -3.24
            if alpha == 0.025:
                return -3.95
            return -3.60
        elif N <= 50:
            if alpha == 0.01:
                return -4.15
            if alpha == 0.10:
                return -3.18
            if alpha == 0.025:
                return -3.80
            return -3.50
        elif N <= 100:
            if alpha == 0.01:
                return -4.04
            if alpha == 0.10:
                return -3.15
            if alpha == 0.025:
                return -3.73
            return -5.45
        elif N <= 250:
            if alpha == 0.01:
                return -3.99
            if alpha == 0.10:
                return -3.13
            if alpha == 0.025:
                return -3.69
            return -3.43
        elif N <= 500:
            if alpha == 0.01:
                return 3.98
            if alpha == 0.10:
                return -3.13
            if alpha == 0.025:
                return -3.68
            return -3.42
        else:
            if alpha == 0.01:
                return -3.96
            if alpha == 0.10:
                return -3.12
            if alpha == 0.025:
                return -3.66
            return -3.41


@save_vastorbit_logs
def adfuller(
    input_relation: SQLRelation,
    column: str,
    ts: str,
    by: Optional[SQLColumns] = None,
    p: int = 1,
    with_trend: bool = False,
    regresults: bool = False,
) -> TableSample:
    """
    Augmented Dickey Fuller test (Time Series stationarity).

    Parameters
    ----------
    input_relation: SQLRelation
        Input relation.
    column: str
        Input VastColumn to test.
    ts: str
        VastColumn used as timeline to order the data.
        It can be a numerical or type date like
        (date, datetime, timestamp...) VastColumn.
    by: SQLColumns, optional
        VastColumns used in the partition.
    p: int, optional
        Number of lags to consider in the test.
    with_trend: bool, optional
        Adds a trend in the Regression.
    regresults: bool, optional
        If True, the full regression results are returned.

    Returns
    -------
    TableSample
        result of the test.

    Examples
    --------

    Initialization
    ^^^^^^^^^^^^^^^

    Let's try this test on a dummy dataset that has the
    following elements:

    - A value of interest
    - Time-stamp data

    Before we begin we can import the necessary libraries:

    .. ipython:: python

        import vastorbit as vo
        import numpy as np

    Example 1: Trend
    ^^^^^^^^^^^^^^^^^

    Now we can create the dummy dataset:

    .. ipython:: python

        # Initialization
        N = 100  # Number of Rows

        # VastFrame
        vdf = vo.VastFrame(
            {
                "year": list(range(N)),
                "X": [x + np.random.normal(0, 5) for x in range(N)],
            }
        )

    We can visually inspect the trend by drawing the
    appropriate graph:

    .. code-block:: python

        vdf["X"].plot(ts="year")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf["X"].plot(ts="year", width=550)
        fig.write_html("SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_adfuller.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_adfuller.html

    Though the increasing trend is obvious,
    we can test its ``adfuller`` score by first importing
    the function:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import adfuller

    And then simply applying it on the :py:class:`~VastFrame`:

    .. ipython:: python

        adfuller(vdf, column="X", ts="year")

    In the above context, the high p-value is
    evidence of lack of stationarity.

    .. note::

        A ``p_value`` in statistics represents the
        probability of obtaining results as extreme
        as, or more extreme than, the observed data,
        assuming the null hypothesis is true.
        A *smaller* p-value typically suggests
        stronger evidence against the null hypothesis
        i.e. the test data does not have
        a trend with respect to time in the current case.

        However, *small* is a relative term. And
        the choice for the threshold value which
        determines a "small" should be made before
        analyzing the data.

        Generally a ``p-value`` less than 0.05
        is considered the threshold to reject the
        null hypothesis. But it is not always
        the case -
        `read more <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10232224/#:~:text=If%20the%20p%2Dvalue%20is,necessarily%20have%20to%20be%200.05.>`__

    Example 2: Stationary
    ^^^^^^^^^^^^^^^^^^^^^^

    We can contrast the results with a dataset that
    has barely any trend:

    .. ipython:: python

        vdf = vo.VastFrame(
            {
                "year": list(range(N)),
                "X": [np.random.normal(0, 5) for x in range(N)],
            }
        )

    We can visually inspect the absence of trend
    by drawing the appropriate graph:

    .. code-block:: python

        vdf["X"].plot(ts="year")

    .. ipython:: python
        :suppress:

        fig = vdf["X"].plot(ts="year", width=550)
        fig.write_html("SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_adfuller_2.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_adfuller_2.html

    Now we can perform the test on this dataset:

    .. ipython:: python

        adfuller(vdf, column="X", ts="year")

    .. note::

        Notice the low p-value which proves
        that there is stationarity.

        For more information, see
        `Mann-Kendall Test <https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm>`__.
    """
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)

    by_cols = format_type(by, dtype=list)
    ts, column, by_cols = vdf.format_colnames(ts, column, by_cols)

    # Sort by time
    vdf = vdf.sort({ts: "asc"})

    # Create lag features using eval with window functions
    partition_by = f"PARTITION BY {', '.join(by_cols)} " if by_cols else ""
    order_by = f"ORDER BY {ts}"

    # lag1: Y(t-1)
    vdf.eval("lag1", expr=f"LAG({column}, 1) OVER ({partition_by}{order_by})")

    # delta: Y(t) - Y(t-1)
    vdf.eval("delta", expr=f"{column} - lag1")

    # delta1 to deltap: differences of lagged values
    for i in range(1, p + 1):
        vdf.eval(
            f"delta{i}",
            expr=f"LAG({column}, {i}) OVER ({partition_by}{order_by}) - LAG({column}, {i + 1}) OVER ({partition_by}{order_by})",
        )

    # Add time trend if needed
    if with_trend:
        if vdf[ts].isdate():
            min_ts = vdf[ts].min()
            vdf.eval(
                "ts_numeric",
                expr=f"DATE_DIFF('second', CAST('{min_ts}' AS TIMESTAMP), {ts})",
            )
        else:
            vdf.eval("ts_numeric", expr=ts)

    # Filter out NULL values created by LAG operations
    filter_conditions = ["lag1 IS NOT NULL", "delta IS NOT NULL"]
    for i in range(1, p + 1):
        filter_conditions.append(f"delta{i} IS NOT NULL")
    vdf = vdf.search(" AND ".join(filter_conditions))

    # Build predictor list
    predictors = ["lag1"] + [f"delta{i}" for i in range(1, p + 1)]
    if with_trend:
        predictors.append("ts_numeric")

    # Fit linear regression
    from scipy import stats

    model = LinearRegression(tol=1e-6)
    model.fit(vdf, X=predictors, y="delta")

    # Get data from model
    X = model._X
    y = model._y
    sklearn_model = model._model

    # Calculate statistics
    n = len(y)
    k = X.shape[1]
    dof = n - k - 1

    # Residuals and MSE
    y_pred = sklearn_model.predict(X)
    residuals = y - y_pred
    mse = np.sum(residuals**2) / dof

    # Standard errors
    X_T_X_inv = np.linalg.inv(X.T @ X)
    std_errors = np.sqrt(mse * X_T_X_inv.diagonal())

    # T-statistics and p-values
    t_stats = sklearn_model.coef_ / std_errors
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), dof))

    # Return full results if requested
    if regresults:
        return TableSample(
            {
                "predictor": predictors,
                "coefficient": sklearn_model.coef_,
                "std_err": std_errors,
                "t_stat": t_stats,
                "p_value": p_values,
            }
        )

    # Get lag1 statistics
    lag1_idx = predictors.index("lag1")
    DF = t_stats[lag1_idx]
    p_value = p_values[lag1_idx]

    # Determine stationarity
    critical_1pct = _df_critical_value(0.01, n, with_trend)
    res = DF < critical_1pct and p_value < 0.01

    # Return ADF test results
    return TableSample(
        {
            "index": [
                "ADF Test Statistic",
                "p_value",
                "# Lags used",
                "# Observations Used",
                "Critical Value (1%)",
                "Critical Value (2.5%)",
                "Critical Value (5%)",
                "Critical Value (10%)",
                "Stationarity (alpha = 1%)",
            ],
            "value": [
                DF,
                p_value,
                p,
                n,
                _df_critical_value(0.01, n, with_trend),
                _df_critical_value(0.025, n, with_trend),
                _df_critical_value(0.05, n, with_trend),
                _df_critical_value(0.10, n, with_trend),
                res,
            ],
        }
    )


@save_vastorbit_logs
def mkt(
    input_relation: SQLRelation, column: str, ts: str, alpha: PythonNumber = 0.05
) -> TableSample:
    """
    Mann Kendall test (Time Series trend).

    .. warning::

        This Test is  computationally  expensive
        because it uses a CROSS  JOIN  during the
        computation.  The complexity is O(n * k),
        n being the total count of the VastFrame
        and k the number of rows to use to do the
        test.

    Parameters
    ----------
    input_relation: SQLRelation
        Input relation.
    column: str
        Input VastColumn to test.
    ts: str
        VastColumn used as timeline used to order
        the data. It can be a numerical or type date like
        (date, datetime, timestamp...) VastColumn.
    alpha: PythonNumber, optional
        Significance Level. Probability to accept H0.

    Returns
    -------
    TableSample
        result of the test.

    Examples
    --------

    Initialization
    ^^^^^^^^^^^^^^^

    Let's try this test on a dummy dataset that has the
    following elements:

    - A value of interest
    - Time-stamp data

    Before we begin we can import the necessary libraries:

    .. ipython:: python

        import vastorbit as vo

    Example 1: Trend
    ^^^^^^^^^^^^^^^^^

    Now we can create the dummy dataset:

    .. ipython:: python

        vdf = vo.VastFrame(
            {
                "X": [0, 1, 2, 3, 4, 5, 6],
                "year": [1990, 1991, 1992, 1993, 1994, 1995, 1996],
            }
        )

    We can visually inspect the trend by drawing the
    appropriate graph:

    .. code-block::

        vdf["X"].plot(ts="year")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf["X"].plot(ts="year")
        fig.write_html("SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_mkt.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_mkt.html

    Though the increasing trend is obvious,
    we can test its ``mkt`` score by first importing
    the function:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt

    And then simply applying it on the :py:class:`~VastFrame`:

    .. ipython:: python

        mkt(vdf, column = "X", ts= "year")

    In the above context, the low p-value is
    evidence of the presence of trend. The function
    also gives us information about the nature of
    trend. In this case, we can see that it is a
    monotonically increasing trend which conforms
    with our plot that we observed above.

    .. note::

        A ``p_value`` in statistics represents the
        probability of obtaining results as extreme
        as, or more extreme than, the observed data,
        assuming the null hypothesis is true.
        A *smaller* p-value typically suggests
        stronger evidence against the null hypothesis
        i.e. the test data does not have
        a trend with respect to time in the current case.

        However, *small* is a relative term. And
        the choice for the threshold value which
        determines a "small" should be made before
        analyzing the data.

        Generally a ``p-value`` less than 0.05
        is considered the threshold to reject the
        null hypothesis. But it is not always
        the case -
        `read more <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10232224/#:~:text=If%20the%20p%2Dvalue%20is,necessarily%20have%20to%20be%200.05.>`__

    Example 1: No Trend
    ^^^^^^^^^^^^^^^^^^^^

    We can contrast the results with a dataset that
    has barely any trend:

    .. ipython:: python

        vdf = vo.VastFrame(
            {
                "X":[1, 1, 1, 1, 1, 1, 1],
                "year": [1990, 1991, 1992, 1993, 1994, 1995, 1996],
            }
        )

    We can visually inspect the absence of trend
    by drawing the appropriate graph:

    .. code-block::

        vdf["X"].plot(ts="year")

    .. ipython:: python
        :suppress:

        fig = vdf["X"].plot(ts="year")
        fig.write_html("SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_mkt_2.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_tsa_mkt_2.html

    Now we can perform the test on this dataset:

    .. ipython:: python

        mkt(vdf, column = "X", ts = "year")

    .. note::

        Notice the extreme p-value which is
        significant to disprove the null hypothesis.

        For more information check out
        `this link <https://vsp.pnnl.gov/help/vsample/design_trend_mann_kendall.htm>`__.
    """
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)
    column, ts = vdf.format_colnames(column, ts)
    table = f"(SELECT {column}, {ts} FROM {vdf})"
    query = f"""
        SELECT 
            /*+LABEL('statistical_tests.mkt')*/ 
            SUM(SIGN(y.{column} - x.{column})) 
        FROM {table} x 
        CROSS JOIN {table} y 
        WHERE y.{ts} > x.{ts}"""
    S = _executeSQL(
        query=query, title="Computing the Mann Kendall S.", method="fetchfirstelem"
    )
    try:
        S = float(S)
    except TypeError:
        S = None
    n = vdf[column].count()
    query = f"""
        SELECT 
            /*+LABEL('statistical_tests.mkt')*/ 
            SQRT(({n} * ({n} - 1) * (2 * {n} + 5) 
            - SUM(row * (row - 1) * (2 * row + 5))) / 18) 
        FROM 
            (SELECT 
                MAX(row) AS row 
             FROM 
                (SELECT 
                    ROW_NUMBER() OVER (PARTITION BY {column}) AS row 
                 FROM {vdf}) VASTORBIT_SUBTABLE 
             GROUP BY row) VASTORBIT_SUBTABLE"""
    STDS = _executeSQL(
        query=query,
        title="Computing the Mann Kendall S standard deviation.",
        method="fetchfirstelem",
    )
    try:
        STDS = float(STDS)
    except TypeError:
        STDS = None
    if STDS in (None, 0) or isinstance(S, NoneType):
        return None
    if S > 0:
        ZMK = (S - 1) / STDS
        trend = "increasing"
    elif S < 0:
        ZMK = (S + 1) / STDS
        trend = "decreasing"
    else:
        ZMK = 0
        trend = "no trend"
    pvalue = 2 * norm.sf(abs(ZMK))
    if (ZMK <= 0 and pvalue < alpha) or (ZMK >= 0 and pvalue < alpha):
        result = True
    else:
        result = False
        trend = "no trend"
    return TableSample(
        {
            "index": [
                "Mann Kendall Test Statistic",
                "S",
                "STDS",
                "p_value",
                "Monotonic Trend",
                "Trend",
            ],
            "value": [ZMK, S, STDS, pvalue, result, trend],
        }
    )


"""
Time Series Tests: Residual Autocorrelation.
"""


@save_vastorbit_logs
def cochrane_orcutt(
    model: LinearModel,
    input_relation: SQLRelation,
    ts: str,
    prais_winsten: bool = False,
    drop_tmp_model: bool = True,
) -> LinearModel:
    """
    Performs a Cochrane-Orcutt estimation.

    Parameters
    ----------
    model: LinearModel
        Linear regression object.
    input_relation: SQLRelation
        Input relation.
    ts: str
        VastColumn of numeric  or date-like type (date,
        datetime, timestamp, etc.) used as the timeline
        and to order the data.
    prais_winsten: bool, optional
        If True,  retains  the  first  observation of the
        time series, increasing precision and efficiency.
        This  configuration is  called the  Prais–Winsten
        estimation.
    drop_tmp_model: bool, optional
        If true, drops the temporary model.

    Returns
    -------
    model_tmp
        A Linear Model with the different information
        stored as attributes:

        - ``intercept_``:
            Model's intercept.

        - ``coef_``:
            Model's coefficients.

        - ``pho_``:
            Cochrane-Orcutt pho.

        - ``anova_table_``:
            ANOVA table.

        - ``r2_``:
            R2 score.

    Examples
    --------

    Initialization
    ^^^^^^^^^^^^^^^

    Let's try this test on a dummy dataset that has the
    following elements:

    - A value of interest that has noise related to time
    - Time-stamp data

    Before we begin we can import the necessary libraries:

    .. ipython:: python

        import vastorbit as vo
        import numpy as np

    Example 1: Trend
    ^^^^^^^^^^^^^^^^^

    Now we can create the dummy dataset:

    .. ipython:: python

        # Initialization
        N = 30 # Number of Rows.
        days = list(range(N))
        y_val = [2 * x + np.random.normal(scale = 4 * x) for x in days]

        # VastFrame
        vdf = vo.VastFrame(
            {
                "day": days,
                "y1": y_val,
            }
        )

    We can visually inspect the trend by drawing the
    appropriate graph:

    .. code-block::

        vdf.scatter(["day", "y1"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf.scatter(["day", "y1"], width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_statistical_tests_cochrane_orcutt.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_machine_learning_model_selection_statistical_tests_cochrane_orcutt.html

    Model Fitting
    ^^^^^^^^^^^^^^

    Next, we can fit a Linear Model. To do that
    we need to first import the model and intialize:

    .. ipython:: python

        from vastorbit.machine_learning.vast.linear_model import LinearRegression

        model = LinearRegression()

    Next we can fit the model:

    .. ipython:: python

        model.fit(vdf, X = "day", y = "y1")

    Now we can apply the Cochrane-Orcutt estimation
    to get the new modified model:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import cochrane_orcutt

        new_model = cochrane_orcutt(model = model, input_relation = vdf, ts = "day")

    Now we can compare the coefficients of both the models to see the difference.

    .. ipython:: python

        model.coef_

    .. ipython:: python

        new_model.coef_

    We can see that the new model has slightly different
    coefficients to cater for the autocorrelated noise.
    """
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)
    ts = vdf.format_colnames(ts)
    param = model.get_params()
    model_tmp = type(model)()
    model_tmp.set_params(param)
    X, y = model.X, model.y
    print_info = conf.get_option("print_info")
    conf.set_option("print_info", False)
    if prais_winsten:
        vdf = vdf[X + [y, ts]].dropna()
    conf.set_option("print_info", print_info)
    prediction_name = gen_tmp_name(name="prediction")[1:-1]
    eps_name = gen_tmp_name(name="eps")[1:-1]
    model.predict(vdf, X=X, name=prediction_name)
    vdf[eps_name] = vdf[y] - vdf[prediction_name]
    query = f"""
        SELECT 
            /*+LABEL('statistical_tests.cochrane_orcutt')*/ 
            SUM(num) / SUM(den) 
        FROM 
            (SELECT 
                {eps_name} * LAG({eps_name}) OVER (ORDER BY {ts}) AS num,  
                POWER({eps_name}, 2) AS den 
             FROM {vdf}) x"""
    pho = _executeSQL(
        query=query, title="Computing the Cochrane Orcutt pho.", method="fetchfirstelem"
    )
    for predictor in X + [y]:
        new_val = f"{predictor} - {pho} * LAG({predictor}) OVER (ORDER BY {ts})"
        if prais_winsten:
            new_val = f"COALESCE({new_val}, {predictor} * {(1 - pho ** 2) ** (0.5)})"
        vdf[predictor] = new_val
    # The Cochrane-Orcutt transform uses LAG(), which produces a NULL first row;
    # drop it before fitting (Prais-Winsten already COALESCEs that row away, so
    # this is a no-op there) to avoid sklearn's "Input contains NaN".
    vdf = vdf[X + [y]].dropna()
    model_tmp.drop()
    model_tmp.fit(
        vdf,
        X,
        y,
        return_report=True,
    )
    model_tmp.pho_ = pho
    model_tmp.anova_table_ = model.regression_report(metrics="anova")
    model_tmp.r2_ = model.score(metric="r2")
    if drop_tmp_model:
        model_tmp.drop()
    return model_tmp


@save_vastorbit_logs
def durbin_watson(
    input_relation: SQLRelation, eps: str, ts: str, by: Optional[SQLColumns] = None
) -> float:
    """
    Durbin Watson test (residuals autocorrelation).

    Parameters
    ----------
    input_relation: SQLRelation
        Input relation.
    eps: str
        Input residual VastColumn.
    ts: str
        VastColumn used as timeline to order the data.
        It can be a numerical or date-like type
        (date,   datetime,   timestamp...) VastColumn.
    by: SQLColumns, optional
        VastColumns used in the partition.

    Returns
    -------
    float
        Durbin Watson statistic.

    Examples
    --------

    Initialization
    ^^^^^^^^^^^^^^^

    Let's try this test on a dummy dataset that has the
    following elements:

    - A value of interest that has noise related to time
    - Time-stamp data

    Before we begin we can import the necessary libraries:

    .. ipython:: python

        import vastorbit as vo
        import numpy as np

    Data
    ^^^^^

    Now we can create the dummy dataset:

    .. ipython:: python

        # Initialization
        N = 50 # Number of Rows
        days = list(range(N))
        y_val = [2 * x + np.random.normal(scale = 4 * x * x) for x in days]

        # VastFrame
        vdf = vo.VastFrame(
            {
                "day": days,
                "y1": y_val,
            }
        )

    Model Fitting
    ^^^^^^^^^^^^^^^^

    Next, we can fit a Linear Model. To do that
    we need to first import the model and intialize:

    .. ipython:: python

        from vastorbit.machine_learning.vast.linear_model import LinearRegression

        model = LinearRegression()

    Next we can fit the model:

    .. ipython:: python

        model.fit(vdf, X = "day", y = "y1")

    We can create a column in the :py:class:`~VastFrame` that
    has the predictions:

    .. code-block:: python

        model.predict(vdf, X = "day", name = "y_pred")

    .. ipython:: python
        :suppress:

        result = model.predict(vdf, X = "day", name = "y_pred")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_durbin_watson_1.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_durbin_watson_1.html

    Then we can calculate the residuals i.e. ``eps``:

    .. ipython:: python

        vdf["eps"] = vdf["y1"] - vdf["y_pred"]

    We can plot the residuals to see the trend:

    .. code-block:: python

        vdf.scatter(["day", "eps"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf.scatter(["day", "eps"], width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_durbin_watson_2.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_durbin_watson_2.html

    Test
    ^^^^^

    Now we can apply the Durbin Watson Test:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import durbin_watson

        durbin_watson(input_relation = vdf, ts = "day", eps = "eps")

    We can see that the Durbin-Watson statistic
    is not equal to 2. This shows the presence
    of autocorrelation.

    .. note::

        The Durbin-Watson statistic values can be
        interpretted as such:

        **Approximately 2**: No significant
        autocorrelation.

        **Less than 2**: Positive autocorrelation
        (residuals are correlated positively with their
        lagged values).

        **Greater than 2**: Negative autocorrelation
        (residuals are correlated negatively with
        their lagged values).
    """
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)
    by = format_type(by, dtype=list)
    eps, ts, by = vdf.format_colnames(eps, ts, by)
    by_str = f"PARTITION BY {', '.join(by)} " if by else ""
    by_select = (", " + ", ".join(by)) if by else ""
    query = f"""
        SELECT 
            /*+LABEL('statistical_tests.durbin_watson')*/ 
            SUM(POWER(et - lag_et, 2)) / SUM(POWER(et, 2)) 
        FROM
            (SELECT 
                et, 
                LAG(et) OVER({by_str}ORDER BY {ts}) AS lag_et 
             FROM (SELECT 
                    {eps} AS et, 
                    {ts}{by_select} 
                   FROM {vdf}) VASTORBIT_SUBTABLE) 
                   VASTORBIT_SUBTABLE"""
    return _executeSQL(
        query=query,
        title="Computing the Durbin Watson d.",
        method="fetchfirstelem",
    )


@save_vastorbit_logs
def ljungbox(
    input_relation: SQLRelation,
    column: str,
    ts: str,
    by: Optional[SQLColumns] = None,
    p: int = 1,
    alpha: PythonNumber = 0.05,
    box_pierce: bool = False,
) -> TableSample:
    """
    Ljung–Box test (whether any of a group of autocorrelations
    of a time series are different from zero).

    Parameters
    ----------
    input_relation: SQLRelation
        Input relation.
    column: str
        Input VastColumn to test.
    ts: str
        VastColumn used as timeline to order the data.
        It can be a numerical or date-like type
        (date, datetime, timestamp...) VastColumn.
    by: SQLColumns, optional
        VastColumns used in the partition.
    p: int, optional
        Number of lags to consider in the test.
    alpha: PythonNumber, optional
        Significance Level. Probability to accept H0.
    box_pierce: bool
        If set to True, the Box-Pierce statistic is used.

    Returns
    -------
    TableSample
        result of the test.

    Examples
    --------

    Initialization
    ^^^^^^^^^^^^^^^

    Let's try this test on a dummy dataset that has the
    following elements:

    - Time-stamp data
    - Some columns related to time
    - Some columns independent of time

    Before we begin we can import the necessary libraries:

    .. ipython:: python

        import vastorbit as vo
        import numpy as np

    Data
    ^^^^^

    Now we can create the dummy dataset:

    .. ipython:: python

        # Initialization
        N = 50 # Number of Rows.
        day = list(range(N))
        x_val_1 = [2 * x + np.random.normal(scale = 4) for x in day]
        x_val_2 = np.random.normal(0, 4, N)

        # VastFrame
        vdf = vo.VastFrame(
            {
                "day": day,
                "x1": x_val_1,
                "x2": x_val_2,
            }
        )

    Note that in the above dataset we have create
    two columns ``x1`` and ``x2``.

    - ``x1``:
        It is related to ``day``

    - ``x2``:
        It is independent of ``day``

    Data Visualization
    ^^^^^^^^^^^^^^^^^^^

    We can visualize ther relationship with the
    help of a scatter plot:

    .. code-block:: python

        vdf.scatter(["day", "x1"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf.scatter(["day", "x1"], width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_ljungbox_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_ljungbox_1.html

    We can see that the variable ``x1``
    seems to be correalted with time.
    Now let us check the other variable
    ``x2``.

    .. code-block:: python

        vdf.scatter(["day", "x2"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf.scatter(["day", "x2"], width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_ljungbox_2.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_ljungbox_2.html

    Above we observe that there is no
    apparent correlation with time.

    Test
    ^^^^^

    Now we can apply the Ljung-Box test Test:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import ljungbox
        ljungbox(vdf, "x1", ts = "day")


    The test confirms that there is indeed a
    relationship.

    Now, we can test the other independent column as well:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import ljungbox
        ljungbox(vdf, "x2", ts = "day")

    We can confirm that ``x2`` is indeed independent
    of time. The results are consistent with
    our earlier visual observation.

    """
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)
    by = format_type(by, dtype=list)
    column, ts, by = vdf.format_colnames(column, ts, by)
    acf = vdf.acf(column=column, ts=ts, by=by, p=p, show=False)
    if p >= 2:
        acf = acf.values["value"][1:]
    else:
        acf = [acf]
    n = vdf[column].count()
    if not box_pierce:
        name = "Ljung–Box Test Statistic"
    else:
        name = "Box-Pierce Test Statistic"
    res = TableSample({"index": [], name: [], "p_value": [], "Serial Correlation": []})
    Q = 0
    for k in range(p):
        div = n - k - 1 if not box_pierce else 1
        mult = n * (n + 2) if not box_pierce else n
        Q += mult * acf[k] ** 2 / div
        pvalue = chi2.sf(Q, k + 1)
        res.values["index"] += [k + 1]
        res.values[name] += [Q]
        res.values["p_value"] += [pvalue]
        res.values["Serial Correlation"] += [True if pvalue < alpha else False]
    return res


"""
Time Series Tests: ARCH.
"""


@save_vastorbit_logs
def het_arch(
    input_relation: SQLRelation,
    eps: str,
    ts: str,
    by: Optional[SQLColumns] = None,
    p: int = 1,
) -> tuple[float, float, float, float]:
    """
    Engle’s Test for Autoregressive Conditional Heteroscedasticity
    (ARCH).

    Parameters
    ----------
    input_relation: SQLRelation
        Input relation.
    eps: str
        Input residual VastColumn.
    ts: str
        VastColumn used as timeline to to order the data.
        It can be a numerical or date-like type
        (date, datetime, timestamp...) VastColumn.
    by: SQLColumns, optional
        VastColumns used in the partition.
    p: int, optional
        Number of lags to consider in the test.

    Returns
    -------
    tuple
        Lagrange Multiplier statistic, LM pvalue,
        F statistic, F pvalue

    Examples
    --------

    Initialization
    ^^^^^^^^^^^^^^^

    Let's try this test on a dummy dataset that has the
    following elements:

    - A value of interest that has noise
    - Time-stamp data

    Before we begin we can import the necessary libraries:

    .. ipython:: python

        import vastorbit as vo
        import numpy as np

    Example 1: Random
    ^^^^^^^^^^^^^^^^^^

    Now we can create the dummy dataset:

    .. ipython:: python

        # Initialization
        N = 50 # Number of Rows.
        days = list(range(N))
        vals = [np.random.normal(5) for x in days]

        # VastFrame
        vdf = vo.VastFrame(
            {
                "day": days,
                "eps": vals,
            }
        )

    Let us plot the distribution of noise
    with respect to time:

    .. code-block:: python

        vdf.scatter(["day", "eps"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf.scatter(["day", "eps"], width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_het_arch_2.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_het_arch_2.html

    Test
    ^^^^^

    Now we can apply the Durbin Watson Test:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import het_arch

        het_arch(input_relation = vdf, ts = "day", eps = "eps", p = 5)

    We can see that there is no relationship
    with any lag except that which is by chance.

    Now let us contrast it with another example where
    the lags are related:

    Example 1: Correlated
    ^^^^^^^^^^^^^^^^^^^^^^

    We can create an alternate dataset that exhibits
    some correlation with a specific lag. Below, we
    intertwine two separate values, one after the other,
    thereby creating a new value. This new value has the
    characteristic that every other value is related
    to the one that is two steps before it, but not to
    the one immediately before it

    .. ipython:: python

        # Initialization
        N = 50 # Number of Rows
        days = list(range(N))
        x1 = [2 * -x for x in list(range(40, 40 + 5 * N, 5))]
        x2 = [-2 * -x * x * x / 2 for x in list(range(4, 4 + 2 * N, 2))]
        vals = []
        for elem_1, elem_2 in zip(x1, x2):
            vals.extend([elem_1, elem_2])

        # VastFrame
        vdf = vo.VastFrame(
            {
                "day": days,
                "eps": vals,
            }
        )

    Let us plot the distribution of noise
    with respect to time to observe the trend:

    .. code-block:: python

        vdf.scatter(["day", "eps"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = vdf.scatter(["day", "eps"], width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_het_arch_2.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_het_arch_2.html

    Notice that it is a bit hard to see the
    relationship of certain lags. That is why
    we need the Engle's Test for Autoregressive
    Conditional Heteroscedasticity.

    Test
    ^^^^^

    Now we can apply the Durbin Watson Test:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import het_arch

        het_arch(input_relation = vdf, ts = "day", eps = "eps", p = 5)

    We can see that the lags of multiple of 2
    have a very low value of ``p``.
    This confirms the presence of correaltion with
    certain lags.

    """
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)
    by = format_type(by, dtype=list)
    eps, ts, by = vdf.format_colnames(eps, ts, by)
    by_str = f"PARTITION BY {', '.join(by)}" if by else ""
    X = []
    X_names = []
    for i in range(0, p + 1):
        X += [f"""LAG(POWER({eps}, 2), {i}) OVER({by_str}ORDER BY {ts}) 
                AS lag_{i}"""]
        X_names += [f"lag_{i}"]
    query = f"SELECT {', '.join(X)} FROM {vdf}"
    vdf_lags = VastFrame(query)
    model = LinearRegression()
    try:
        model.fit(
            vdf_lags,
            X_names[1:],
            X_names[0],
            return_report=True,
        )
        R2 = model.score(metric="r2")
    except QueryError:
        model.set_params({"solver": "lbfgs"})
        model.fit(
            vdf_lags,
            X_names[1:],
            X_names[0],
            return_report=True,
        )
        R2 = model.score(metric="r2")
    finally:
        model.drop()
    n = vdf.shape()[0]
    LM = (n - p) * R2
    lm_pvalue = chi2.sf(LM, p)
    F = (n - 2 * p - 1) * R2 / (1 - R2) / p
    f_pvalue = f.sf(F, p, n - 2 * p - 1)
    return LM, lm_pvalue, F, f_pvalue


"""
Time Series Seasonal Decomposition.
"""


@save_vastorbit_logs
def seasonal_decompose(
    input_relation: SQLRelation,
    columns: SQLColumns,
    ts: str,
    by: Optional[SQLColumns] = None,
    period: Union[int, tuple, list] = -1,
    polynomial_order: Union[int, tuple, list] = 1,
    estimate_seasonality: bool = True,
    rule: Optional[TimeInterval] = None,
    mult: bool = False,
    two_sided: bool = False,
    use_row: bool = True,
    genSQL: bool = False,
) -> VastFrame:
    """
    Performs a seasonal time series
    decomposition. Seasonal decomposition
    plots are graphical representations
    of the decomposition of time series
    data into its various components:
    trend, seasonality, and residual
    (error). Seasonal decomposition is
    a technique used to break down a
    time series into these underlying
    components to better understand its
    patterns and behavior.

    Seasonal decomposition plots are
    useful for several purposes:

     - Trend Analysis:
        Understanding the long-term
        direction or behavior of the
        time series.
     - Seasonal Patterns:
        Identifying repeating patterns
        or cycles within the data.
     - Anomaly Detection:
        Spotting unusual behavior or
        outliers in the residuals.
     - Modeling:
        Informing the choice of
        appropriate models for
        forecasting or analysis.

    Parameters
    ----------
    input_relation: SQLRelation
        Input relation.
    columns: SQLColumns
        Input :py:class:`VastColumn`
        to decompose.
    ts: str
        Time series :py:class:`VastColumn`
        used to order the data.
        It can be of type date or a
        numerical VastColumn.
    by: SQLColumns, optional
        :py:class:`VastColumn` used
        in the partition.
    period: int | tuple | list, optional
        Time series period. It is used
        to retrieve the seasonality
        component. If ``period <= 0``,
        the seasonal component is
        estimated using ACF.
        In this case, ``polynomial_order``
        must be greater than 0.

        It can be an int or a list |
        tuple of int, each one representing
        the ``period`` of the i-th column.
    polynomial_order: int | tuple | list, optional
        If greater than 0, the trend is
        estimated using a polynomial of
        degree ``'polynomial_order'``
        and the parameter ``two_sided``
        is ignored. If equal to 0, the
        trend is estimated using Moving
        Averages.

        It can be an int or a list |
        tuple of int, each one representing
        the ``polynomial_order`` of the
        i-th column.
    estimate_seasonality: bool, optional
        If set to ``True``, the seasonality
        is estimated using cosine and sine
        functions.
    rule: TimeInterval, optional
        Interval  used to slice the
        time. For example, ``'5 minutes'``
        creates records separated by
        ``'5 minutes'`` time interval.
    mult: bool, optional
        If set to ``True``, the
        decomposition type is
        'multiplicative'. Otherwise,
        'additive'.
    two_sided: bool, optional
        If set to ``True``, a centered
        moving average is used for the
        trend isolation. Otherwise, only
        past values are used.
    use_row: bool, optional
        If set to ``True``, the ``ROW``
        datatype is used to merge all
        the different columns time
        series components together.
    genSQL: bool, optional
        If set to ``True``, the SQL code
        for creating the final relation
        is generated but not executed.

    Returns
    -------
    VastFrame
        object containing the different
        time series components.

    Examples
    --------

    Let us use a dataset that has seasonality.
    The Airline passengers dataset is a good example.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_airline_passengers()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html

    .. note::
        vastorbit offers a wide range of sample datasets that are
        ideal for training and testing purposes. You can explore
        the full list of available datasets in the :ref:`api.datasets`,
        which provides detailed information on each dataset
        and how to use them effectively. These datasets are invaluable
        resources for honing your data analysis and machine learning
        skills within the vastorbit environment.

    .. ipython:: python
        :suppress:

        import vastorbit.datasets as vod
        data = vod.load_airline_passengers()

    Data Visualization
    ^^^^^^^^^^^^^^^^^^^

    Let us first have a look how the data
    looks like:

    .. code-block::

        data["passengers"].plot(ts = "date")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = data["passengers"].plot(ts = "date", width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_1.html

    We can visually observe:

    - Overall increasing trend
    - A seasonal component
    - Some noise

    Now we can use the ``seasonal_decompose`` to
    separate these three.

    Decomposition
    ^^^^^^^^^^^^^^

    We can directly the function on the dataset:

    .. ipython:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import seasonal_decompose

        decomposition = seasonal_decompose(
            data,
            "passengers",
            "date",
            polynomial_order = 2,
            mult = True,
            use_row = False,
        )

    .. ipython:: python
        :suppress:

        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_decomposition.html", "w")
        html_file.write(decomposition._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_decomposition.html

    We can see that there are now three new
    columns capturing the three elements
    of data.

    Let's visualize them.

    **Seasonality**


    .. code-block::

        decomposition["passengers_seasonal"].plot(ts = "date")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = decomposition["passengers_seasonal"].plot(ts = "date", width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_seasonal.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_seasonal.html


    **Trend**

    .. code-block::

        decomposition["passengers_trend"].plot(ts = "date")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = decomposition["passengers_trend"].plot(ts = "date", width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_trend.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_trend.html

    **Noise**

    .. code-block::

        decomposition["passengers_epsilon"].plot(ts = "date")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = decomposition["passengers_epsilon"].plot(ts = "date", width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_eps.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_model_selection_statistical_tests_seasonal_decompose_plot_eps.html

    .. note::

        Thanks to seasonal decomposition, we can effortlessly extract
        the residual, predict its values, and obtain crucial information
        necessary for computing the time series. Subsequently, by
        leveraging all the individual components, we are able to
        effectively recompose the time series.
    """

    # Initialization
    if use_row:
        vast_version(condition=[12, 0, 0])
    assert period > 0 or polynomial_order > 0, ValueError(
        "Parameters 'polynomial_order' and 'period' can not be both null."
    )
    columns = format_type(columns, dtype=list)
    by = format_type(by, dtype=list)
    if isinstance(input_relation, VastFrame):
        vdf = input_relation.copy()
    else:
        vdf = VastFrame(input_relation)
    ts, columns, by = vdf.format_colnames(ts, columns, by)
    by_str = "" if not by else f"PARTITION BY {', '.join(by)} "
    if rule:
        vdf = vdf.interpolate(
            ts=ts, rule=rule, method={column: "linear" for column in columns}, by=by
        )
    else:
        vdf = vdf[[ts] + columns]
    n = len(columns)

    # Periods
    if isinstance(period, int):
        periods = [period for i in range(n)]
    elif not (isinstance(period, (tuple, list))):
        raise TypeError(
            "Wrong type for parameter 'period'. Expecting "
            f"int | tuple | list.\nFound {type(period)}."
        )
    elif len(period) != n:
        raise ValueError(f"Parameter 'period' size should be {n}.")
    else:
        periods = []
        for pr in period:
            if not (isinstance(pr, int)):
                raise TypeError(
                    "Each element inside 'period' should "
                    f"be an int.\nFound {type(pr)}."
                )
            periods += [period]

    # Polynomial Orders
    if isinstance(polynomial_order, int):
        polynomial_orders = [polynomial_order for i in range(n)]
    elif not (isinstance(polynomial_order, (tuple, list))):
        raise TypeError(
            "Wrong type for parameter 'polynomial_order'. Expecting "
            f"int | tuple | list.\nFound {type(polynomial_order)}."
        )
    elif len(polynomial_order) != n:
        raise ValueError(f"Parameter 'polynomial_order' size should be {n}.")
    else:
        polynomial_orders = []
        for pr in polynomial_order:
            if not (isinstance(pr, int)):
                raise TypeError(
                    "Each element inside 'polynomial_order' should "
                    f"be an int.\nFound {type(pr)}."
                )
            polynomial_orders += [polynomial_order]

    # Main
    rows, flat = [], []
    for idx, column in enumerate(columns):
        trend_name = f"{column[1:-1]}_trend"
        seasonal_name = f"{column[1:-1]}_seasonal"
        epsilon_name = f"{column[1:-1]}_epsilon"
        row_number_name = f"{column[1:-1]}_row_id"

        # INIT
        if two_sided:
            if periods[idx] == 1:
                window = (-1, 1)
            else:
                if periods[idx] % 2 == 0:
                    window = (-periods[idx] / 2 + 1, periods[idx] / 2)
                else:
                    window = (int(-periods[idx] / 2), int(periods[idx] / 2))
        else:
            if periods[idx] == 1:
                window = (-2, 0)
            else:
                window = (-periods[idx] + 1, 0)

        # TREND
        if polynomial_orders[idx] <= 0:
            vdf.rolling("avg", window, column, by, ts, trend_name)
        else:
            vdf_poly = vdf.copy()
            X = []
            for i in range(1, polynomial_orders[idx] + 1):
                vdf_poly[f"t_{i}"] = (
                    f"POWER(ROW_NUMBER() OVER ({by_str}ORDER BY {ts}), {i})"
                )
                X += [f"t_{i}"]
            model = LinearRegression(tol=1e-6)
            model.fit(
                vdf_poly,
                X,
                column,
                return_report=True,
            )
            coefficients = [str(model.intercept_)] + [
                (
                    f"{model.coef_[i-1]} * POWER(ROW_NUMBER() OVER({by_str}ORDER BY {ts}), {i})"
                    if i != 1
                    else f"{model.coef_[0]} * ROW_NUMBER() OVER({by_str}ORDER BY {ts})"
                )
                for i in range(1, polynomial_orders[idx] + 1)
            ]
            vdf[trend_name] = " + ".join(coefficients)
            model.drop()

        # SEASONALITY
        if mult:
            vdf[seasonal_name] = f'{column} / NULLIF("{trend_name}", 0)'
        else:
            vdf[seasonal_name] = vdf[column] - vdf[trend_name]
        if periods[idx] <= 0:
            acf = vdf.acf(column=seasonal_name, ts=ts, p=23, kind="heatmap", show=False)
            periods[idx] = int(acf["index"][1].split("_")[1])
            if periods[idx] == 1:
                periods[idx] = int(acf["index"][2].split("_")[1])
        vdf[row_number_name] = (
            f"MOD(ROW_NUMBER() OVER ({by_str} ORDER BY {ts}), {periods[idx]})"
        )
        if mult:
            vdf[seasonal_name] = f"""
                AVG(1.000000000 * {seasonal_name}) OVER (PARTITION BY {row_number_name}) 
              / NULLIF(AVG(1.000000000 * {seasonal_name}) OVER (), 0)"""
        else:
            vdf[seasonal_name] = f"""
                AVG(1.000000000 * {seasonal_name}) OVER (PARTITION BY {row_number_name}) 
              - AVG(1.000000000 * {seasonal_name}) OVER ()"""
        if estimate_seasonality:
            vdf_seasonality = vdf.copy()
            vdf_seasonality["t_cos"] = (
                f"COS(2.00000000 * PI() * ROW_NUMBER() OVER ({by_str}ORDER BY {ts}) / {periods[idx]})"
            )
            vdf_seasonality["t_sin"] = (
                f"SIN(2.00000000 * PI() * ROW_NUMBER() OVER ({by_str}ORDER BY {ts}) / {periods[idx]})"
            )
            X = ["t_cos", "t_sin"]
            model = LinearRegression(tol=1e-6)
            model.fit(
                vdf_seasonality,
                X,
                seasonal_name,
                return_report=True,
            )
            vdf[
                seasonal_name
            ] = f"""
                {model.intercept_} + {model.coef_[0]} * 
                COS(2.00000000 * PI() * ROW_NUMBER() OVER ({by_str}ORDER BY {ts}) / {periods[idx]}) 
              + {model.coef_[1]} 
              * SIN(2.00000000 * PI() * ROW_NUMBER() OVER ({by_str}ORDER BY {ts}) / {periods[idx]})"""
            model.drop()

        # EPSILON
        if mult:
            vdf[epsilon_name] = (
                f'{column} / NULLIF("{trend_name}", 0) / NULLIF("{seasonal_name}", 0)'
            )
        else:
            vdf[epsilon_name] = vdf[column] - vdf[trend_name] - vdf[seasonal_name]

        rows += [f"""
            ROW({column} AS "value", 
                {trend_name} AS "trend", 
                {seasonal_name} AS "seasonal", 
                {epsilon_name} AS eps) AS {quote_ident(column)}"""]
        flat += [
            quote_ident(column),
            quote_ident(trend_name),
            quote_ident(seasonal_name),
            quote_ident(epsilon_name),
        ]

    # OUTPUT
    if use_row:
        by_str = ""
        if by:
            by_str = ", ".join(by) + ", "
        sql = f"""SELECT {ts}, {by_str} {', '.join(rows)} FROM {vdf}"""

    else:
        sql = f"""SELECT {ts}, {by_str} {', '.join(flat)} FROM {vdf}"""

    sql = clean_query(sql)

    if genSQL:
        return sql

    return VastFrame(sql)
