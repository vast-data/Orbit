"""
SPDX-License-Identifier: Apache-2.0

Complete base.py for TimeSeriesModelBase with SQL-based AR/VAR training.
This replaces the fit() method and adds helper methods for pure SQL inference.
"""

from abc import abstractmethod
import copy
import datetime
from dateutil.relativedelta import relativedelta
from typing import Literal, Optional, Union

import numpy as np

from vastorbit._typing import (
    PlottingObject,
    NoneType,
    SQLColumns,
    SQLRelation,
)
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._format import (
    clean_query,
    format_type,
    quote_ident,
    schema_relation,
)
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.core.vastframe.base import TableSample, VastFrame

import vastorbit.machine_learning.metrics as mt
from vastorbit.machine_learning.vast.base import VASTModel

from vastorbit.sql.drop import drop

"""
General Classes.
"""


class TimeSeriesModelBase(VASTModel):
    """
    Base Class for VAST Time Series Models.

    This implementation uses pure SQL for AR and VAR model training.
    MA, ARMA, and ARIMA models with MA components are not supported.
    """

    # Properties.

    @property
    def _model_category(self) -> Literal["TIMESERIES"]:
        return "TIMESERIES"

    @property
    def _attributes(self) -> list[str]:
        common_params = [
            "mse_",
            "n_",
        ]
        if self._model_type in ("ARMA", "ARIMA"):
            # When the MA term is absent (and no differencing for ARIMA) the
            # model is fitted as AR(p) and exposes the AR attribute set.
            if self._is_ar_like:
                return [
                    "phi_",
                    "intercept_",
                    "feature_importances_",
                ] + common_params
            return [
                "phi_",
                "theta_",
                "mean_",
                "feature_importances_",
            ] + common_params
        elif self._model_type == "AR":
            return [
                "phi_",
                "intercept_",
                "feature_importances_",
            ] + common_params
        else:
            return [
                "theta_",
                "mu_",
                "mean_",
            ] + common_params

    def _ismultivar(self) -> bool:
        """
        Returns ``True`` if the model is multivariate.
        """
        return isinstance(self.y, list) and len(self.y) > 1

    @property
    def _is_ar_like(self) -> bool:
        """
        ``True`` when the model can be fitted with the pure-SQL AR machinery:
        AR, VAR, or an ARMA / ARIMA whose Moving-Average term is absent
        (``q == 0``) and, for ARIMA, with no differencing (``d == 0``). In those
        cases the model is mathematically an autoregression of order
        ``order[0]`` and is routed through the AR code path.
        """
        if self._model_type in ("AR", "VAR"):
            return True
        order = self.parameters.get("order", [0, 0, 0])
        if self._model_type == "ARMA":
            return len(order) >= 2 and order[1] == 0
        if self._model_type == "ARIMA":
            return len(order) >= 3 and order[1] == 0 and order[2] == 0
        return False

    # Model Fitting Method.

    def fit(
        self,
        input_relation: SQLRelation,
        ts: str,
        y: SQLColumns,
        test_relation: SQLRelation = "",
        return_report: bool = False,
    ) -> Optional[str]:
        """
        Trains the model using pure SQL.

        Parameters
        ----------
        input_relation: SQLRelation
            Training relation.
        ts: str
            TS (Time Series) VastColumn used to order the data.
            The VastColumn type must be date (date, datetime,
            timestamp...) or numerical.
        y: SQLColumns
            Response column.

            In the case of multivariate analysis, it represents
            a list of all the predictors.
        test_relation: SQLRelation, optional
            Relation used to test the model.
        return_report: bool, optional
            When set to True, the model summary will be returned.
            Otherwise, it will be printed.

        Returns
        -------
        str
            model's summary.

        Raises
        ------
        NotImplementedError
            If the model contains MA (Moving Average) components.
            Only AR and VAR models are supported for SQL-based training.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will use the airline passengers dataset.

        .. code-block:: python

            import vastorbit.datasets as vod
            data = vod.load_airline_passengers()

        First we import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast.tsa import AR

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = AR(p=2)

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, "date", "passengers")
        """
        # Check if model has MA component - only AR/VAR models supported
        if self._model_type == "MA":
            raise NotImplementedError(
                "Pure SQL training not available for MA models. "
                "MA models require iterative error term calculations "
                "that cannot be efficiently implemented in SQL."
            )
        elif self._model_type == "ARMA":
            if self.parameters.get("order", [0, 0])[1] > 0:
                raise NotImplementedError(
                    "Pure SQL training not available for ARMA models "
                    "with Moving Average component (q > 0). Only AR models "
                    "can be trained using pure SQL."
                )
        elif self._model_type == "ARIMA":
            if self.parameters.get("order", [0, 0, 0])[2] > 0:
                raise NotImplementedError(
                    "Pure SQL training not available for ARIMA models "
                    "with Moving Average component (q > 0). Only models "
                    "without MA terms can be trained using pure SQL."
                )

        # Initialization
        self.ts = quote_ident(ts)
        y = format_type(y, dtype=list)

        if len(y) > 1:
            self.y = quote_ident(y)
        else:
            self.y = quote_ident(y[0])

        if isinstance(input_relation, VastFrame):
            self.input_relation = input_relation.current_relation()
        else:
            self.input_relation = input_relation

        if isinstance(test_relation, VastFrame):
            self.test_relation = test_relation.current_relation()
        elif test_relation:
            self.test_relation = test_relation
        else:
            self.test_relation = self.input_relation

        # ARMA/ARIMA with no Moving-Average term (and, for ARIMA, no
        # differencing) are exactly AR(order[0]); expose ``p`` so the shared AR
        # machinery can fit, deploy and predict them.
        if self._model_type in ("ARMA", "ARIMA") and self._is_ar_like:
            self.parameters["p"] = self.parameters.get("order", [1])[0]

        # Fit using SQL
        if self._is_ar_like:
            self._fit_ar_sql()
        else:
            raise NotImplementedError(
                f"SQL training not implemented for {self._model_type} models "
                f"with the requested order. Only AR/VAR, and ARMA/ARIMA without "
                f"a Moving-Average term (q=0) and without differencing (d=0), "
                f"can be trained using pure SQL."
            )

        # Compute attributes
        self._compute_attributes()

        report = self.summarize() if hasattr(self, "summarize") else None
        if return_report and report:
            return report
        elif report:
            print_message(report)

        return None

    def _fit_ar_sql(self) -> None:
        """
        Fits AR/VAR model using pure SQL OLS (no tables created).

        Supports:
        - AR: Univariate autoregression
        - VAR: Vector autoregression (multivariate)

        Uses Ordinary Least Squares for coefficient estimation:
        - AR(1), AR(2): Closed-form solutions
        - AR(p>2): Yule-Walker equations via autocorrelations
        - VAR(1): Simplified OLS per equation
        """
        p = self.parameters.get("p", 1)
        is_multivar = self._ismultivar()

        if is_multivar:
            self._compute_var_coefficients(p)
        else:
            self._compute_ar_coefficients(p)

        print_message(f"{self._model_type}({p}) model fitted using pure SQL.")

    def _compute_ar_coefficients(self, p: int) -> None:
        """
        Compute AR coefficients using SQL OLS.

        Parameters
        ----------
        p: int
            Number of lags
        """
        # Build lag columns
        lags = [
            f"LAG({self.y}, {i}) OVER (ORDER BY {self.ts}) AS lag{i}"
            for i in range(1, p + 1)
        ]

        if p == 1:
            # AR(1): Simple linear regression
            # beta = Cov(X,Y) / Var(X)
            query = f"""
                WITH lagged_data AS (
                    SELECT {self.y} AS y, {lags[0]}
                    FROM {self.input_relation}
                ),
                stats AS (
                    SELECT AVG(y) AS y_mean, AVG(lag1) AS x_mean, COUNT(*) AS n
                    FROM lagged_data WHERE lag1 IS NOT NULL
                ),
                coef AS (
                    SELECT
                        SUM((y - s.y_mean) * (lag1 - s.x_mean)) / 
                            NULLIF(SUM(POWER(lag1 - s.x_mean, 2)), 0) AS phi_1,
                        s.y_mean, s.x_mean, s.n
                    FROM lagged_data CROSS JOIN stats s
                    WHERE lag1 IS NOT NULL
                    GROUP BY s.y_mean, s.x_mean, s.n
                )
                SELECT phi_1, y_mean - phi_1 * x_mean AS intercept, n
                FROM coef
            """

        elif p == 2:
            # AR(2): Normal equations (X'X)^-1 X'Y with 2x2 matrix inversion
            query = f"""
                WITH lagged_data AS (
                    SELECT {self.y} AS y, {', '.join(lags)}
                    FROM {self.input_relation}
                ),
                stats AS (
                    SELECT 
                        AVG(y) AS y_mean, 
                        AVG(lag1) AS x1_mean, 
                        AVG(lag2) AS x2_mean, 
                        COUNT(*) AS n
                    FROM lagged_data 
                    WHERE lag1 IS NOT NULL AND lag2 IS NOT NULL
                ),
                moments AS (
                    SELECT
                        SUM((y - s.y_mean) * (lag1 - s.x1_mean)) AS s_y1,
                        SUM((y - s.y_mean) * (lag2 - s.x2_mean)) AS s_y2,
                        SUM(POWER(lag1 - s.x1_mean, 2)) AS s_11,
                        SUM(POWER(lag2 - s.x2_mean, 2)) AS s_22,
                        SUM((lag1 - s.x1_mean) * (lag2 - s.x2_mean)) AS s_12,
                        s.y_mean, s.x1_mean, s.x2_mean, s.n
                    FROM lagged_data CROSS JOIN stats s
                    WHERE lag1 IS NOT NULL AND lag2 IS NOT NULL
                    GROUP BY s.y_mean, s.x1_mean, s.x2_mean, s.n
                )
                SELECT
                    (s_y1 * s_22 - s_y2 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0) AS phi_1,
                    (s_y2 * s_11 - s_y1 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0) AS phi_2,
                    y_mean - 
                        ((s_y1 * s_22 - s_y2 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0)) * x1_mean -
                        ((s_y2 * s_11 - s_y1 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0)) * x2_mean 
                    AS intercept, n
                FROM moments
            """

        else:
            # AR(p) for p > 2: Use Yule-Walker equations via autocorrelations
            print_message(
                f"AR({p}): Using Yule-Walker estimation via autocorrelations. "
                f"Note: For p > 5, consider using specialized libraries for better performance."
            )

            # Compute autocorrelations up to lag p
            # rho_k = Corr(y_t, y_{t-k})
            autocorr_lags = []
            for k in range(1, p + 1):
                autocorr_lags.append(f"""SUM((y - y_mean) * (lag{k} - y_mean)) / 
                        NULLIF(SUM(POWER(y - y_mean, 2)), 0) AS rho_{k}""")

            query = f"""
                WITH lagged_data AS (
                    SELECT {self.y} AS y, {', '.join(lags)}
                    FROM {self.input_relation}
                ),
                stats AS (
                    SELECT AVG(y) AS y_mean, COUNT(*) AS n
                    FROM lagged_data
                    WHERE {' AND '.join([f"lag{i} IS NOT NULL" for i in range(1, p + 1)])}
                ),
                autocorrs AS (
                    SELECT
                        s.y_mean,
                        {', '.join(autocorr_lags)},
                        s.n
                    FROM lagged_data
                    CROSS JOIN stats s
                    WHERE {' AND '.join([f"lag{i} IS NOT NULL" for i in range(1, p + 1)])}
                    GROUP BY s.y_mean, s.n
                )
                SELECT * FROM autocorrs
            """

        result = _executeSQL(
            query, title=f"Computing AR({p}) coefficients", method="fetchrow"
        )

        if result:
            if p <= 2:
                self._phi_values = [result[i] for i in range(p)]
                self._intercept_value = result[p]
                self._n_obs = int(result[p + 1])
            else:
                # For p > 2: Solve Yule-Walker using autocorrelations
                y_mean = result[0]
                autocorrs = [result[i] for i in range(1, p + 1)]  # rho_1, ..., rho_p
                n_obs = int(result[p + 1])

                # Solve Yule-Walker: Toeplitz(R) * phi = r
                phi_coeffs = self._solve_yule_walker(autocorrs, p)

                self._phi_values = phi_coeffs
                self._intercept_value = y_mean * (1 - sum(phi_coeffs))
                self._n_obs = n_obs
        else:
            raise ValueError("Failed to compute AR coefficients")

    def _compute_var_coefficients(self, p: int) -> None:
        """
        Compute VAR coefficients using SQL OLS with proper matrix inversion.

        For VAR(p), each equation has n_vars*p predictors.
        We compute the covariance matrices in SQL, then solve in Python.
        """
        n_vars = len(self.y)
        total_predictors = n_vars * p

        # Build lag columns for all variables
        lags = []
        lag_names = []
        for i in range(1, p + 1):
            for col in self.y:
                col_name = col[1:-1]
                lags.append(
                    f"LAG({col}, {i}) OVER (ORDER BY {self.ts}) AS {col_name}_lag{i}"
                )
                lag_names.append(f"{col_name}_lag{i}")

        if p <= 3 and n_vars <= 3 and (n_vars * p) <= 6:
            # Use SQL-based computation for small systems
            self._compute_var_small(p, n_vars, lags, lag_names)
        else:
            # Use Python-based computation for larger systems
            self._compute_var_python(p, n_vars, lags, lag_names)

    def _compute_var_small(
        self, p: int, n_vars: int, lags: list, lag_names: list
    ) -> None:
        """Compute VAR using SQL for small systems."""
        phi_matrices = []
        intercepts = []

        for idx, y_col in enumerate(self.y):
            y_col_name = y_col[1:-1]

            if n_vars == 1:
                # Univariate case - just AR
                self._compute_ar_coefficients(p)
                return
            elif n_vars == 2 and p == 1:
                # Bivariate VAR(1) - use 2x2 matrix inversion
                other_col = self.y[1 - idx][1:-1]

                query = f"""
                    WITH lagged_data AS (
                        SELECT {y_col} AS y, {', '.join(lags)}
                        FROM {self.input_relation}
                    ),
                    stats AS (
                        SELECT 
                            AVG(y) AS y_mean,
                            AVG({y_col_name}_lag1) AS x1_mean,
                            AVG({other_col}_lag1) AS x2_mean,
                            COUNT(*) AS n
                        FROM lagged_data 
                        WHERE {y_col_name}_lag1 IS NOT NULL AND {other_col}_lag1 IS NOT NULL
                    ),
                    moments AS (
                        SELECT
                            SUM((y - s.y_mean) * ({y_col_name}_lag1 - s.x1_mean)) AS s_y1,
                            SUM((y - s.y_mean) * ({other_col}_lag1 - s.x2_mean)) AS s_y2,
                            SUM(POWER({y_col_name}_lag1 - s.x1_mean, 2)) AS s_11,
                            SUM(POWER({other_col}_lag1 - s.x2_mean, 2)) AS s_22,
                            SUM(({y_col_name}_lag1 - s.x1_mean) * ({other_col}_lag1 - s.x2_mean)) AS s_12,
                            s.y_mean, s.x1_mean, s.x2_mean, s.n
                        FROM lagged_data CROSS JOIN stats s
                        WHERE {y_col_name}_lag1 IS NOT NULL AND {other_col}_lag1 IS NOT NULL
                        GROUP BY s.y_mean, s.x1_mean, s.x2_mean, s.n
                    )
                    SELECT
                        (s_y1 * s_22 - s_y2 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0) AS phi_1,
                        (s_y2 * s_11 - s_y1 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0) AS phi_2,
                        y_mean - 
                            ((s_y1 * s_22 - s_y2 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0)) * x1_mean -
                            ((s_y2 * s_11 - s_y1 * s_12) / NULLIF(s_11 * s_22 - s_12 * s_12, 0)) * x2_mean 
                        AS intercept, n
                    FROM moments
                """

                result = _executeSQL(
                    query,
                    title=f"Computing VAR coef for {y_col_name}",
                    method="fetchrow",
                )

                if result:
                    phi_matrices.append(
                        [
                            result[0] if result[0] else 0.0,
                            result[1] if result[1] else 0.0,
                        ]
                    )
                    intercepts.append(result[2] if result[2] else 0.0)
                    if idx == 0:
                        self._n_obs = int(result[3])
            else:
                # Fall back to Python method
                print_message(
                    f"VAR({p}) with {n_vars} variables: using Python-based OLS."
                )
                return self._compute_var_python(p, n_vars, lags, lag_names)

        self._phi_values = np.array(phi_matrices)
        self._intercept_value = np.array(intercepts)
        if not hasattr(self, "_n_obs"):
            self._n_obs = 0

    def _compute_var_python(
        self, p: int, n_vars: int, lags: list, lag_names: list
    ) -> None:
        """
        Compute VAR coefficients using Python matrix operations.

        This fetches the data from SQL, then computes OLS in Python using NumPy.
        More efficient for larger systems.
        """
        from numpy.linalg import lstsq

        print_message(
            f"Computing VAR({p}) with {n_vars} variables using Python OLS. "
            f"System size: {n_vars} equations × {n_vars*p} predictors."
        )

        # Fetch data from SQL
        y_cols = ", ".join(self.y)
        lag_select = ", ".join(lags)

        # Build WHERE clause to ensure NO NULLs in any lag
        where_conditions = " AND ".join(
            [f"{lag_name} IS NOT NULL" for lag_name in lag_names]
        )

        query = f"""
            WITH lagged_data AS (
                SELECT
                    {y_cols},
                    {lag_select},
                    ROW_NUMBER() OVER (ORDER BY {self.ts}) AS idx
                FROM {self.input_relation}
            )
            SELECT {y_cols}, {', '.join(lag_names)}
            FROM lagged_data
            WHERE {where_conditions}
            ORDER BY idx
        """

        result = _executeSQL(
            query, title="Fetching data for VAR estimation", method="fetchall"
        )

        if not result or len(result) < n_vars * p + 10:
            raise ValueError(
                f"Insufficient data for VAR({p}). Got {len(result) if result else 0} observations, "
                f"need at least {n_vars*p + 10}."
            )

        # Convert to numpy arrays
        try:
            data = np.array(result, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Data contains non-numeric values: {e}")

        # Final check for NaN or Inf (shouldn't happen with proper WHERE clause)
        if np.any(np.isnan(data)):
            # Try to identify which columns have NaN
            nan_mask = np.isnan(data)
            nan_cols = np.where(nan_mask.any(axis=0))[0]
            print_message(
                f"Warning: NaN detected in columns: {nan_cols}. Removing affected rows."
            )
            # Remove rows with any NaN
            data = data[~nan_mask.any(axis=1)]

        if np.any(np.isinf(data)):
            raise ValueError(
                "Data contains Inf values. Check for division by zero or extreme values."
            )

        if len(data) < n_vars * p + 10:
            raise ValueError(
                f"After cleaning, only {len(data)} observations remain. Need at least {n_vars*p + 10}."
            )

        Y = data[:, :n_vars]  # Response variables
        X = data[:, n_vars:]  # Lagged predictors

        # Add intercept column
        X = np.column_stack([np.ones(X.shape[0]), X])

        # Check for perfect multicollinearity
        rank = np.linalg.matrix_rank(X)
        if rank < X.shape[1]:
            print_message(
                f"Warning: Predictor matrix has rank {rank} but {X.shape[1]} columns. "
                "Perfect collinearity detected. Using Ridge regression with small penalty."
            )
            # Use Ridge regression instead
            return self._compute_var_ridge(Y, X, n_vars)

        # Solve for each equation: Y_i = X @ beta_i
        phi_matrices = []
        intercepts = []

        for i in range(n_vars):
            y_i = Y[:, i]

            try:
                # Solve using least squares: beta = (X'X)^-1 X'y
                beta, residuals, rank, s = lstsq(X, y_i, rcond=None)

                intercepts.append(beta[0])
                phi_matrices.append(beta[1:])  # All coefficients except intercept

            except np.linalg.LinAlgError as e:
                print_message(
                    f"Warning: SVD failed for variable {i}. Using Ridge regression fallback."
                )
                # Fallback to Ridge regression
                return self._compute_var_ridge(Y, X, n_vars)

        self._phi_values = np.array(phi_matrices)
        self._intercept_value = np.array(intercepts)
        self._n_obs = len(data)

    def _compute_var_ridge(self, Y: np.ndarray, X: np.ndarray, n_vars: int) -> None:
        """
        Fallback VAR estimation using Ridge regression.

        Used when OLS fails due to collinearity or numerical issues.
        """
        print_message("Using Ridge regression with lambda=0.01 to handle collinearity.")

        # Ridge regression: beta = (X'X + lambda*I)^-1 X'y
        lambda_ridge = 0.01
        XtX = X.T @ X
        I = np.eye(X.shape[1])
        I[0, 0] = 0  # Don't penalize intercept

        phi_matrices = []
        intercepts = []

        for i in range(n_vars):
            y_i = Y[:, i]
            Xty = X.T @ y_i

            try:
                # Solve (X'X + lambda*I) beta = X'y
                beta = np.linalg.solve(XtX + lambda_ridge * I, Xty)

                intercepts.append(beta[0])
                phi_matrices.append(beta[1:])

            except np.linalg.LinAlgError:
                # Last resort: use pseudo-inverse
                print_message(f"Warning: Using pseudo-inverse for variable {i}.")
                beta = np.linalg.pinv(X) @ y_i
                intercepts.append(beta[0])
                phi_matrices.append(beta[1:])

        self._phi_values = np.array(phi_matrices)
        self._intercept_value = np.array(intercepts)
        self._n_obs = Y.shape[0]

    def _solve_yule_walker(self, autocorrs: list, p: int) -> list:
        """
        Solve Yule-Walker equations for AR(p) coefficients.

        The Yule-Walker equations are:
        Γ φ = γ

        Where:
        - Γ is the Toeplitz autocorrelation matrix [p×p]
        - γ is the autocorrelation vector [p×1]
        - φ is the coefficient vector we solve for

        For AR(3) example:
        [[1,      rho_1,  rho_2],     [phi_1]     [rho_1]
         [rho_1,  1,      rho_1],  *  [phi_2]  =  [rho_2]
         [rho_2,  rho_1,  1    ]]     [phi_3]     [rho_3]

        Parameters
        ----------
        autocorrs: list
            Autocorrelations [rho_1, rho_2, ..., rho_p]
        p: int
            AR order

        Returns
        -------
        list
            AR coefficients [phi_1, phi_2, ..., phi_p]
        """
        from numpy.linalg import solve

        # Construct Toeplitz matrix Γ
        # Γ[i,j] = rho_{|i-j|}
        gamma_matrix = np.zeros((p, p))
        for i in range(p):
            for j in range(p):
                if i == j:
                    gamma_matrix[i, j] = 1.0
                else:
                    lag_idx = abs(i - j) - 1
                    if lag_idx < len(autocorrs):
                        gamma_matrix[i, j] = autocorrs[lag_idx]

        # γ vector is [rho_1, rho_2, ..., rho_p]
        gamma_vector = np.array(autocorrs)

        # Solve Γ φ = γ
        try:
            phi = solve(gamma_matrix, gamma_vector)
            return phi.tolist()
        except np.linalg.LinAlgError:
            # Singular matrix - use regularized solution
            print_message(
                f"Warning: Singular autocorrelation matrix for AR({p}). "
                "Using regularized solution with ridge penalty."
            )
            # Add small ridge to diagonal
            gamma_matrix += np.eye(p) * 1e-6
            phi = solve(gamma_matrix, gamma_vector)
            return phi.tolist()

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from fitted coefficients.

        For AR/VAR models, this stores the computed ``phi_``, ``intercept_``,
        ``n_``, and ``mse_`` attributes.
        """
        if self._is_ar_like:
            # Store coefficients as numpy arrays
            if hasattr(self, "_phi_values"):
                self.phi_ = (
                    np.array(self._phi_values)
                    if not isinstance(self._phi_values, np.ndarray)
                    else self._phi_values
                )
            else:
                p = self.parameters.get("p", 1)
                self.phi_ = np.zeros(p)

            if hasattr(self, "_intercept_value"):
                self.intercept_ = self._intercept_value
            else:
                self.intercept_ = 0.0

            if hasattr(self, "_n_obs"):
                self.n_ = self._n_obs
            else:
                self.n_ = 0

            # MSE would require residuals calculation - set to None for now
            self.mse_ = None

        else:
            raise NotImplementedError(
                f"Attribute computation not implemented for {self._model_type}"
            )

    # Features Importance

    def features_importance(
        self, show: bool = True, chart: Optional[PlottingObject] = None, **style_kwargs
    ) -> Union[PlottingObject, TableSample]:
        """
        Computes the model's features importance.

        For AR/VAR models, feature importance is based on the
        magnitude of the autoregressive coefficients (phi).

        Parameters
        ----------
        show: bool
            If set to ``True``, draw the feature's importance.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to pass to the Plotting functions.

        Returns
        -------
        obj
            Features importance.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. code-block:: python

            import vastorbit as vo

        For this example, we will use the airline passengers dataset.

        .. code-block:: python

            import vastorbit.datasets as vod
            data = vod.load_airline_passengers()

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            import vastorbit.datasets as vod
            data = vod.load_airline_passengers()

        First we import the model:

        .. code-block::

            from vastorbit.machine_learning.vast.tsa import AR

        Then we can create the model:

        .. code-block::

            model = AR(p=5)

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast.tsa import AR
            model = AR(p=5)

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, "date", "passengers")

        We can conveniently get the features importance:

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.features_importance()
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_feature.html")

        .. code-block:: python

            result = model.features_importance()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_feature.html

        .. important::

            For this example, a specific model is utilized, and it may
            not correspond exactly to the model you are working with.
            To see a comprehensive example specific to your class of
            interest, please refer to that particular class.
        """
        fi = self._get_features_importance()

        if show:
            if self._ismultivar():
                # For VAR models: each variable has its own feature importance
                # Create separate chart for each variable
                n_vars = len(self.y)
                p = self.parameters.get("p", 1)

                # Prepare data for first variable (or could show all)
                # For simplicity, showing importance for first variable
                data = {
                    "importance": fi[0] if isinstance(fi, list) else fi,
                }
                # Feature names: all lags of all variables
                feature_names = []
                for lag in range(1, p + 1):
                    for var_idx, var in enumerate(self.y):
                        var_name = var[1:-1]  # Remove quotes
                        feature_names.append(f"{var_name}_lag{lag}")

                layout = {"columns": feature_names}
            else:
                # For AR models: importance of each lag
                p = self.parameters.get("p", 1)
                data = {
                    "importance": fi,
                }
                layout = {"columns": [f"lag{i+1}" for i in range(p)]}

            vo_plt, kwargs = self.get_plotting_lib(
                class_name="ImportanceBarChart",
                chart=chart,
                style_kwargs=style_kwargs,
            )
            return vo_plt.ImportanceBarChart(data=data, layout=layout).draw(**kwargs)

        # Return as TableSample
        if self._ismultivar():
            # For VAR: return importance for each variable
            n_vars = len(self.y)
            p = self.parameters.get("p", 1)

            importances = {"index": []}
            for var_idx, var in enumerate(self.y):
                var_name = var[1:-1]
                importances[var_name] = []

            # Build feature names
            for lag in range(1, p + 1):
                for var_idx, var in enumerate(self.y):
                    var_name = var[1:-1]
                    importances["index"].append(f"{var_name}_lag{lag}")

                    # Add importance values for each variable's equation
                    for eq_idx, eq_var in enumerate(self.y):
                        eq_var_name = eq_var[1:-1]
                        if isinstance(fi, list) and len(fi) > eq_idx:
                            # Calculate index in flattened coefficient array
                            coef_idx = (lag - 1) * n_vars + var_idx
                            if coef_idx < len(fi[eq_idx]):
                                importances[eq_var_name].append(
                                    abs(fi[eq_idx][coef_idx])
                                )
                            else:
                                importances[eq_var_name].append(0.0)
                        else:
                            importances[eq_var_name].append(0.0)

            return TableSample(values=importances)
        else:
            # For AR: simple lag importance
            p = self.parameters.get("p", 1)
            importances = {
                "index": [f"lag{i+1}" for i in range(p)],
                "importance": list(abs(fi)),
                "sign": list(np.sign(self.phi_)),
            }
            return TableSample(values=importances).sort(column="importance", desc=True)

    # I/O Methods.

    def deploySQL(
        self,
        ts: Optional[str] = None,
        y: Optional[SQLColumns] = None,
        start: Optional[int] = None,
        npredictions: int = 10,
        output_standard_errors: bool = False,
        output_index: bool = False,
        use_index_as_suffix: bool = False,
    ) -> str:
        """
        Returns the SQL code needed to deploy the model.

        For AR/VAR models trained with pure SQL, this generates
        SQL to compute predictions using the learned coefficients.

        Parameters
        ----------
        ts: str, optional
            TS (Time Series) VastColumn used to order the data.
        y: SQLColumns, optional
            Response column(s).
        start: int, optional
            Starting position for prediction.
        npredictions: int, optional
            Number of predicted timesteps.
        output_standard_errors: bool, optional
            Whether to return standard error estimates (not supported).
        output_index: bool, optional
            Whether to return the index of each position.
        use_index_as_suffix: bool, optional
            For multivariate models, use indexes as suffix instead of names.

        Returns
        -------
        str
            SQL code for prediction.

        Raises
        ------
        NotImplementedError
            For MA/ARMA/ARIMA models, as they require iterative calculations.
        """
        if not self._is_ar_like:
            raise NotImplementedError(
                f"deploySQL not implemented for {self._model_type} models. "
                f"Only AR and VAR models support SQL-based deployment."
            )

        if output_standard_errors:
            print_message(
                "Warning: Standard errors not supported for SQL-trained models."
            )

        # For SQL-trained AR/VAR models, generate manual prediction SQL
        return self._generate_ar_prediction_sql(
            ts=ts,
            y=y,
            start=start,
            npredictions=npredictions,
            output_index=output_index,
            use_index_as_suffix=use_index_as_suffix,
        )

    def _generate_ar_prediction_sql(
        self,
        ts: Optional[str] = None,
        y: Optional[SQLColumns] = None,
        start: Optional[int] = None,
        npredictions: int = 10,
        output_index: bool = False,
        use_index_as_suffix: bool = False,
    ) -> str:
        """
        Generate SQL for AR/VAR prediction using learned coefficients.

        This creates SQL that computes predictions using the AR/VAR formula
        with the fitted coefficients.
        """
        p = self.parameters.get("p", 1)
        is_multivar = self._ismultivar()

        if ts is None:
            ts = self.ts
        else:
            ts = quote_ident(ts)

        if y is None:
            y = self.y
        else:
            y = format_type(y, dtype=list)
            y = quote_ident(y) if isinstance(y, list) else quote_ident(y)

        if is_multivar:
            # VAR prediction SQL
            return self._generate_var_prediction_sql(ts, y, npredictions, output_index)

        # AR prediction SQL
        # Build lag references
        lag_cols = [
            f"LAG({y}, {i}) OVER (ORDER BY {ts}) AS lag{i}" for i in range(1, p + 1)
        ]

        # Build prediction formula using fitted coefficients
        terms = []
        for i in range(p):
            coef = float(self.phi_[i])
            coef_str = f"({coef})" if coef < 0 else str(coef)
            terms.append(f"{coef_str} * lag{i+1}")

        intercept = float(self.intercept_)
        intercept_str = f"({intercept})" if intercept < 0 else str(intercept)
        prediction_formula = f"{intercept_str} + {' + '.join(terms)}"

        sql = f"""
            WITH lagged_data AS (
                SELECT
                    {ts},
                    {y} AS actual,
                    {', '.join(lag_cols)},
                    ROW_NUMBER() OVER (ORDER BY {ts}) AS idx
                FROM {{input_relation}}
            )
            SELECT 
                {ts},
                {"idx," if output_index else ""}
                {prediction_formula} AS prediction
            FROM lagged_data
            WHERE {' AND '.join([f"lag{i} IS NOT NULL" for i in range(1, p + 1)])}
            ORDER BY {ts}
        """

        return clean_query(sql)

    def _generate_var_prediction_sql(
        self,
        ts: str,
        y: list,
        npredictions: int,
        output_index: bool,
    ) -> str:
        """
        Generate SQL for VAR prediction using fitted coefficients.

        For VAR models, each variable's prediction uses ALL variables' lags.
        """
        p = self.parameters.get("p", 1)
        n_vars = len(y)

        # Build lag columns for all variables
        lag_cols = []
        for i in range(1, p + 1):
            for col in y:
                col_name = col[1:-1]
                lag_cols.append(
                    f"LAG({col}, {i}) OVER (ORDER BY {ts}) AS {col_name}_lag{i}"
                )

        # Build prediction formulas for each variable
        prediction_formulas = []
        for var_idx in range(n_vars):
            y_col_name = y[var_idx][1:-1]

            # Get coefficients for this equation
            phi_coefs = self._phi_values[var_idx]
            intercept = (
                float(self._intercept_value[var_idx])
                if isinstance(self._intercept_value, np.ndarray)
                else float(self._intercept_value)
            )
            intercept_str = f"({intercept})" if intercept < 0 else str(intercept)

            # Build terms: use ALL variables' lags
            terms = []
            coef_idx = 0
            for lag in range(1, p + 1):
                for col_idx, col in enumerate(y):
                    col_name = col[1:-1]
                    if coef_idx < len(phi_coefs):
                        coef = float(phi_coefs[coef_idx])
                        coef_str = f"({coef})" if coef < 0 else str(coef)
                        terms.append(f"{coef_str} * {col_name}_lag{lag}")
                        coef_idx += 1

            prediction_formula = f"{intercept_str} + {' + '.join(terms)}"
            prediction_formulas.append(
                f"{prediction_formula} AS prediction_{y_col_name}"
            )

        # Generate SQL
        sql = f"""
            WITH lagged_data AS (
                SELECT
                    {ts},
                    {', '.join(y)},
                    {', '.join(lag_cols)},
                    ROW_NUMBER() OVER (ORDER BY {ts}) AS idx
                FROM {{input_relation}}
            )
            SELECT 
                {ts},
                {"idx," if output_index else ""}
                {', '.join(prediction_formulas)}
            FROM lagged_data
            WHERE {' AND '.join([f"{y[0][1:-1]}_lag{i} IS NOT NULL" for i in range(1, p + 1)])}
            ORDER BY {ts}
        """

        return clean_query(sql)

    # Prediction / Transformation Methods.

    def predict(
        self,
        vdf: Optional[SQLRelation] = None,
        ts: Optional[str] = None,
        y: Optional[SQLColumns] = None,
        start: Optional[int] = None,
        npredictions: int = 10,
        output_standard_errors: bool = False,
        output_index: bool = False,
        output_estimated_ts: bool = False,
        freq: Literal[None, "m", "months", "y", "year", "infer"] = "infer",
        filter_step: Optional[int] = None,
        method: Literal["auto", "forecast"] = "auto",
        use_index_as_suffix: bool = False,
    ) -> VastFrame:
        """
        Predicts using the input relation.

        For SQL-trained AR/VAR models, this generates predictions using
        the learned coefficients directly in SQL.

        Parameters
        ----------
        vdf: SQLRelation, optional
            Object used to run the prediction.
        ts: str, optional
            TS column used to order the data.
        y: SQLColumns, optional
            Response column(s).
        start: int, optional
            Starting position for prediction.
        npredictions: int, optional
            Number of predicted timesteps.
        output_standard_errors: bool, optional
            Whether to return standard errors (not supported for SQL models).
        output_index: bool, optional
            Whether to return the index.
        output_estimated_ts: bool, optional
            Whether to estimate timestamps.
        freq: str, optional
            Frequency for timestamp estimation.
        filter_step: int, optional
            Filter frequency for predictions.
        method: str, optional
            Forecasting method ('auto' or 'forecast').
        use_index_as_suffix: bool, optional
            For multivariate models.

        Returns
        -------
        VastFrame
            Predictions.

        Raises
        ------
        NotImplementedError
            For MA/ARMA/ARIMA models.
        """
        if not self._is_ar_like:
            raise NotImplementedError(
                f"Predict not implemented for {self._model_type} models. "
                f"Only AR and VAR models support SQL-based prediction."
            )

        # Use manual AR prediction for SQL-trained models
        return self._predict_ar_manual(
            vdf=vdf,
            ts=ts,
            y=y,
            start=start,
            npredictions=npredictions,
            output_index=output_index,
            method=method,
        )

    def _predict_ar_manual(
        self,
        vdf: Optional[SQLRelation] = None,
        ts: Optional[str] = None,
        y: Optional[SQLColumns] = None,
        start: Optional[int] = None,
        npredictions: int = 10,
        output_index: bool = False,
        method: Literal["auto", "forecast"] = "auto",
    ) -> VastFrame:
        """
        Generate AR/VAR predictions using SQL queries.

        method="auto": One-step ahead (uses actual values as lags)
        method="forecast": Multi-step ahead (uses predicted values as lags)
        """
        p = self.parameters.get("p", 1)
        is_multivar = self._ismultivar()

        if ts is None:
            ts = self.ts
        else:
            ts = quote_ident(ts)

        if y is None:
            y = self.y

        if vdf is None:
            vdf = self.input_relation
        elif isinstance(vdf, VastFrame):
            vdf = vdf.current_relation()

        if is_multivar:
            return self._predict_var_manual(
                vdf, ts, y, start, npredictions, output_index, method
            )

        # AR model prediction

        if method == "forecast":
            # Multi-step ahead: use recursive forecasting (predicted values as inputs)
            return self._forecast_ar_recursive(
                vdf, ts, y, start, npredictions, output_index
            )
        else:
            # One-step ahead: use actual values as lags
            return self._forecast_ar_onestep(
                vdf, ts, y, start, npredictions, output_index
            )

    def _forecast_ar_onestep(
        self,
        vdf: SQLRelation,
        ts: str,
        y: str,
        start: Optional[int],
        npredictions: int,
        output_index: bool,
    ) -> VastFrame:
        """
        One-step ahead AR forecasting (uses actual values as lags).
        """
        p = self.parameters.get("p", 1)

        lag_cols = [
            f"LAG({y}, {i}) OVER (ORDER BY {ts}) AS lag{i}" for i in range(1, p + 1)
        ]

        # Build prediction formula
        terms = []
        for i in range(p):
            coef = float(self.phi_[i])
            coef_str = f"({coef})" if coef < 0 else str(coef)
            terms.append(f"{coef_str} * lag{i+1}")

        intercept = float(self.intercept_)
        intercept_str = f"({intercept})" if intercept < 0 else str(intercept)
        prediction_formula = f"{intercept_str} + {' + '.join(terms)}"

        where_start = f"AND idx >= {start}" if start else ""

        sql = f"""
            WITH lagged_data AS (
                SELECT
                    {ts},
                    {y} AS actual,
                    {', '.join(lag_cols)},
                    ROW_NUMBER() OVER (ORDER BY {ts}) - 1 AS idx
                FROM {vdf}
            ),
            predictions AS (
                SELECT
                    idx,
                    {ts},
                    actual,
                    {prediction_formula} AS prediction
                FROM lagged_data
                WHERE {' AND '.join([f"lag{i} IS NOT NULL" for i in range(1, p + 1)])}
                    {where_start}
            )
            SELECT 
                {"idx," if output_index else ""}
                prediction
            FROM predictions
            ORDER BY idx
            LIMIT {npredictions}
        """

        return VastFrame(clean_query(sql))

    def _forecast_ar_recursive(
        self,
        vdf: SQLRelation,
        ts: str,
        y: str,
        start: Optional[int],
        npredictions: int,
        output_index: bool,
    ) -> VastFrame:
        """
        Multi-step ahead AR forecasting using Python (recursive).

        This fetches initial values from SQL, then computes predictions
        recursively in Python where each prediction uses previous predictions.
        """
        p = self.parameters.get("p", 1)

        # Determine starting point
        if start is None:
            start_idx = self.n_ - p
        else:
            start_idx = start

        # Fetch last p actual values to use as initial lags
        query = f"""
            WITH numbered_data AS (
                SELECT 
                    {y} AS value,
                    ROW_NUMBER() OVER (ORDER BY {ts}) - 1 AS idx
                FROM {vdf}
            )
            SELECT value
            FROM numbered_data
            WHERE idx >= {start_idx - p} AND idx < {start_idx}
            ORDER BY idx DESC
            LIMIT {p}
        """

        result = _executeSQL(
            query,
            title="Fetching initial values for recursive forecast",
            method="fetchall",
        )

        if not result or len(result) < p:
            raise ValueError(
                f"Insufficient data for forecasting. Need at least {p} values before start position."
            )

        # Initialize with last p actual values (in reverse order: most recent first)
        lags = [float(row[0]) for row in result]

        # Generate predictions recursively
        predictions = []
        phi = self.phi_
        intercept = float(self.intercept_)

        for step in range(npredictions):
            # Compute prediction: y_t = intercept + phi_1*y_{t-1} + phi_2*y_{t-2} + ...
            pred = intercept
            for i in range(p):
                pred += phi[i] * lags[i]

            predictions.append(pred)

            # Update lags: shift and add new prediction
            lags = [pred] + lags[:-1]

        # Create VastFrame with predictions
        # Build SQL with literal values
        predictions_values = ", ".join(
            [f"({start_idx + i}, {pred})" for i, pred in enumerate(predictions)]
        )

        sql = f"""
            SELECT 
                {"idx," if output_index else ""}
                prediction
            FROM (VALUES {predictions_values}) AS t(idx, prediction)
            ORDER BY idx
        """

        return VastFrame(clean_query(sql))

    def _predict_var_manual(
        self,
        vdf: SQLRelation,
        ts: str,
        y: list,
        start: Optional[int],
        npredictions: int,
        output_index: bool,
        method: Literal["auto", "forecast"],
    ) -> VastFrame:
        """
        Generate VAR predictions using SQL.

        For VAR models, each equation uses ALL variables' lags.
        """
        p = self.parameters.get("p", 1)
        n_vars = len(y)

        # Build lag columns for all variables
        lag_cols = []
        for i in range(1, p + 1):
            for col in y:
                col_name = col.strip('"')
                lag_cols.append(
                    f"LAG({col}, {i}) OVER (ORDER BY {ts}) AS {col_name}_lag{i}"
                )

        # Build prediction formulas for each variable
        prediction_formulas = []
        for var_idx in range(n_vars):
            y_col_name = y[var_idx].strip('"')

            # Get coefficients for this equation
            phi_coefs = self._phi_values[var_idx]
            intercept = (
                float(self._intercept_value[var_idx])
                if isinstance(self._intercept_value, np.ndarray)
                else float(self._intercept_value)
            )
            intercept_str = f"({intercept})" if intercept < 0 else str(intercept)

            # Build terms: use ALL variables' lags
            terms = []
            coef_idx = 0
            for lag in range(1, p + 1):
                for col_idx, col in enumerate(y):
                    col_name = col.strip('"')
                    if coef_idx < len(phi_coefs):
                        coef = float(phi_coefs[coef_idx])
                        coef_str = f"({coef})" if coef < 0 else str(coef)
                        terms.append(f"{coef_str} * {col_name}_lag{lag}")
                        coef_idx += 1

            prediction_formula = f"{intercept_str} + {' + '.join(terms)}"
            prediction_formulas.append(f"{prediction_formula} AS prediction{var_idx}")

        # Generate SQL
        sql = f"""
            WITH lagged_data AS (
                SELECT
                    {ts},
                    {', '.join(y)},
                    {', '.join(lag_cols)},
                    ROW_NUMBER() OVER (ORDER BY {ts}) AS idx
                FROM {vdf}
            ),
            predictions AS (
                SELECT
                    idx,
                    {ts},
                    {', '.join(prediction_formulas)}
                FROM lagged_data
                WHERE {' AND '.join([f"{y[0].strip('"')}_lag{i} IS NOT NULL" for i in range(1, p + 1)])}
            )
            SELECT 
                {"idx," if output_index else ""}
                {', '.join([f"prediction{i}" for i in range(n_vars)])}
            FROM predictions
            ORDER BY idx DESC
            LIMIT {npredictions}
        """

        return VastFrame(clean_query(sql))

    # Features Importance Methods.

    def _compute_features_importance(self) -> None:
        """
        Computes the features importance for AR/VAR models.

        For AR models, feature importance is based on the magnitude
        of the phi coefficients.
        """
        if self._model_type == "MA" or (
            self._model_type in ("ARMA", "ARIMA")
            and self.get_params().get("order", [0])[0] == 0
        ):
            raise AttributeError(
                "Features Importance cannot be computed for Moving Averages."
            )
        elif self._ismultivar():
            # VAR model
            res = []
            n = len(self.y)
            p = self.parameters["p"]

            if self.phi_.ndim == 2:
                # phi_ shape is (n_vars, p)
                for i in range(n):
                    phi_row = self.phi_[i, :]
                    importance = 100.0 * np.abs(phi_row) / np.sum(np.abs(phi_row))
                    res.append(importance)
                self.feature_importances_ = res
            else:
                # Fallback
                self.feature_importances_ = [100.0 / p] * n
        else:
            # AR model
            self.feature_importances_ = (
                100.0 * np.abs(self.phi_) / np.sum(np.abs(self.phi_))
            )

    def _get_features_importance(self) -> np.ndarray:
        """
        Returns the features' importance.
        """
        if not hasattr(self, "feature_importances_"):
            self._compute_features_importance()
        return copy.deepcopy(self.feature_importances_)

    # Features importance plotting method remains unchanged...
    # (Keep the existing features_importance() method from original file)

    # Model Evaluation Methods.

    def _evaluation_relation(
        self,
        start: Optional[int] = None,
        npredictions: Optional[int] = None,
        method: Literal["auto", "forecast"] = "auto",
    ) -> str:
        """
        Returns the relation needed to evaluate the model.

        For SQL-trained AR/VAR models, this uses the manual prediction method.
        """
        if hasattr(self, "test_relation"):
            test_relation = self.test_relation
        elif hasattr(self, "input_relation"):
            test_relation = self.input_relation
        else:
            raise AttributeError(
                "No attributes found. The model is probably not yet fitted."
            )

        # Ensure npredictions is positive
        if isinstance(npredictions, NoneType) or npredictions <= 0:
            npredictions = 10  # Default to 10 predictions if calculation gives negative

        if isinstance(start, NoneType):
            start = self.n_ // 4
        if isinstance(npredictions, NoneType):
            npredictions = self.n_ - start

        prediction = self._predict_ar_manual(
            vdf=test_relation,
            ts=self.ts,
            y=self.y,
            start=start,
            npredictions=npredictions,
            output_index=True,
            method=method,
        )

        if self._ismultivar():
            y_str = ", ".join([f"{col} AS y_true{i}" for i, col in enumerate(self.y)])
            prediction_str = ", ".join(
                [
                    f"prediction_relation.prediction{i} AS y_pred{i}"
                    for i in range(len(self.y))
                ]
            )
            y_true_str = ", ".join(
                [f"true_values.y_true{i}" for i in range(len(self.y))]
            )
        else:
            y_str = f"{self.y} AS y_true"
            prediction_str = "prediction_relation.prediction AS y_pred"
            y_true_str = "true_values.y_true"

        sql = f"""
            (SELECT
                {y_true_str},
                {prediction_str}
            FROM 
                (SELECT
                    ROW_NUMBER() OVER (ORDER BY {self.ts}) - 1 AS idx,
                    {y_str}
                FROM {test_relation}
                ) AS true_values
                INNER JOIN
                (SELECT * FROM {prediction}) AS prediction_relation
                ON true_values.idx = prediction_relation.idx
            ) VASTORBIT_SUBTABLE
        """

        return clean_query(sql)

    # Model Evaluation

    def regression_report(
        self,
        metrics: Union[
            str,
            Literal[None, "anova", "details"],
            list[Literal[tuple(mt.FUNCTIONS_REGRESSION_DICTIONNARY)]],
        ] = None,
        start: Optional[int] = None,
        npredictions: Optional[int] = None,
        method: Literal["auto", "forecast"] = "auto",
    ) -> Union[float, TableSample]:
        """
        Computes a regression report
        using multiple metrics to
        evaluate the model (``r2``,
        ``mse``, ``max error``...).

        Parameters
        ----------
        metrics: str | list, optional
            The metrics used to compute
            the regression report.

             - None:
                Computes the model different metrics.
             - anova:
                Computes the model ANOVA table.
             - details:
                Computes the model details.

            It can also be a ``list`` of the
            metrics used to compute the final
            report.

            - aic:
                Akaike's Information Criterion

                .. math::

                    AIC = 2k - 2\\ln(\\hat{L})

            - bic:
                Bayesian Information Criterion

                .. math::

                    BIC = -2\\ln(\\hat{L}) + k \\ln(n)

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

                    MsE = \\frac{1}{n} \\sum_{i=1}^{n} \\left( y_i - \\hat{y}_i \\right)^2

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

            - qe:
                quantile error, the quantile must be
                included in the name. Example:
                qe50.1% will  return the quantile
                error using q=0.501.

            - rmse:
                Root-mean-squared error

                .. math::

                    RMSE = \\sqrt{\\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}

            - var:
                Explained Variance

                .. math::

                    \\text{Explained Variance}   = 1 - \\frac{Var(y - \\hat{y})}{Var(y)}
        start: int, optional
            The behavior of the start parameter and its
            range of accepted values depends on whether
            you provide a timeseries-column (``ts``):

            - No provided timeseries-column:
                ``start`` must be an integer
                greater or equal to 0, where
                zero indicates to start
                prediction at the end of the
                in-sample data. If ``start``
                is a positive value, the function
                predicts the values between the
                end of the in-sample data and
                the start index, and then uses
                the predicted values as time
                series inputs for the subsequent
                ``npredictions``.
            - timeseries-column provided:
                ``start`` must be an ``integer``
                greater or equal to ``1`` and
                identifies the index (row) of
                the timeseries-column at which
                to begin prediction. If the
                ``start`` index is greater than
                the number of rows, ``N``, in the
                input data, the function predicts
                the values between ``N`` and
                ``start`` and uses the predicted
                values as time series inputs for
                the subsequent npredictions.

            Default:

            - No provided timeseries-column:
                prediction begins from the
                end of the in-sample data.
            - timeseries-column provided:
                prediction begins from the
                end of the provided input
                data.

        npredictions: int, optional
            ``integer`` greater or equal to ``1``,
            the number of predicted timesteps.
        method: str, optional
            Forecasting method. One of the following:

            - auto:
                the model initially utilizes the true
                values at each step for forecasting.
                However, when it reaches a point where
                it can no longer rely on true values,
                it transitions to using its own
                predictions for further forecasting.
                This method is often referred to as
                "one step ahead" forecasting.

             - forecast:
                the model initiates forecasting from
                an initial value and entirely disregards
                any subsequent true values. This approach
                involves forecasting based solely on the
                model's own predictions and does not
                consider actual observations after the
                start point.

        Returns
        -------
        TableSample
            report.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will use
        the airline passengers dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_airline_passengers()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_airline_passengers()

        First we import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast.tsa import ARIMA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = ARIMA(order = (12, 0, 0))

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, "date", "passengers")

        We can get the entire report using:

        .. code-block:: python

            model.report()

        .. ipython:: python
            :suppress:
            :okwarning:

            result = model.report()
            html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_report.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_report.html

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.

            Examples:
            :py:class:`~vastorbit.machine_learning.vast.tsa.ARIMA`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.ARMA`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.AR`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.MA`;
        """
        if self._ismultivar():
            for i in range(len(self.y)):
                tmp_res = mt.regression_report(
                    f"y_true{i}",
                    f"y_pred{i}",
                    self._evaluation_relation(
                        start=start, npredictions=npredictions, method=method
                    ),
                    metrics=metrics,
                    k=1,
                )
                if i == 0:
                    res = {"index": tmp_res["index"]}
                res[self.y[i]] = tmp_res["value"]
            return TableSample(res)
        else:
            return mt.regression_report(
                "y_true",
                "y_pred",
                self._evaluation_relation(
                    start=start, npredictions=npredictions, method=method
                ),
                metrics=metrics,
                k=1,
            )

    report = regression_report

    def score(
        self,
        metric: Literal[
            tuple(mt.FUNCTIONS_REGRESSION_DICTIONNARY)
            + ("r2a", "r2_adj", "rsquared_adj", "r2adj", "r2adjusted", "rmse")
        ] = "r2",
        start: Optional[int] = None,
        npredictions: Optional[int] = None,
        method: Literal["auto", "forecast"] = "auto",
    ) -> Union[float, TableSample]:
        """
        Computes the model score.

        Parameters
        ----------
        metric: str, optional
            The metric used to compute the score.

            - aic:
                Akaike's Information Criterion

                .. math::

                    AIC = 2k - 2\\ln(\\hat{L})

            - bic:
                Bayesian Information Criterion

                .. math::

                    BIC = -2\\ln(\\hat{L}) + k \\ln(n)

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

                    MsE = \\frac{1}{n} \\sum_{i=1}^{n} \\left( y_i - \\hat{y}_i \\right)^2

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

            - qe:
                quantile error, the quantile must be
                included in the name. Example:
                qe50.1% will  return the quantile
                error using q=0.501.

            - rmse:
                Root-mean-squared error

                .. math::

                    RMSE = \\sqrt{\\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}

            - var:
                Explained Variance

                .. math::

                    \\text{Explained Variance}   = 1 - \\frac{Var(y - \\hat{y})}{Var(y)}
        start: int, optional
            The behavior of the start parameter and its
            range of accepted values depends on whether
            you provide a timeseries-column (``ts``):

            - No provided timeseries-column:
                ``start`` must be an integer
                greater or equal to 0, where
                zero indicates to start
                prediction at the end of the
                in-sample data. If ``start``
                is a positive value, the function
                predicts the values between the
                end of the in-sample data and
                the start index, and then uses
                the predicted values as time
                series inputs for the subsequent
                ``npredictions``.
            - timeseries-column provided:
                ``start`` must be an ``integer``
                greater or equal to ``1`` and
                identifies the index (row) of
                the timeseries-column at which
                to begin prediction. If the
                ``start`` index is greater than
                the number of rows, ``N``, in the
                input data, the function predicts
                the values between ``N`` and
                ``start`` and uses the predicted
                values as time series inputs for
                the subsequent npredictions.

            Default:

            - No provided timeseries-column:
                prediction begins from the
                end of the in-sample data.
            - timeseries-column provided:
                prediction begins from the
                end of the provided input
                data.

        npredictions: int, optional
            ``integer`` greater or equal to ``1``,
            the number of predicted timesteps.
        method: str, optional
            Forecasting method. One of the following:

            - auto:
                the model initially utilizes the true
                values at each step for forecasting.
                However, when it reaches a point where
                it can no longer rely on true values,
                it transitions to using its own
                predictions for further forecasting.
                This method is often referred to as
                "one step ahead" forecasting.
            - forecast:
                the model initiates forecasting from
                an initial value and entirely disregards
                any subsequent true values. This approach
                involves forecasting based solely on the
                model's own predictions and does not
                consider actual observations after the
                start point.

        Returns
        -------
        float
            score.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will use
        the airline passengers dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_airline_passengers()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_airline_passengers()

        First we import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast.tsa import ARIMA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = ARIMA(order = (12, 0, 0))

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, "date", "passengers")

        Let's compute the model's score.

        .. ipython:: python
            :okwarning:

            model.score(start = 40, npredictions = 30, method = "forecast")

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.

            Examples:
            :py:class:`~vastorbit.machine_learning.vast.tsa.ARIMA`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.ARMA`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.AR`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.MA`;
        """
        # Initialization
        metric = str(metric).lower()
        if metric in ["r2adj", "r2adjusted"]:
            metric = "r2a"
        adj, root = False, False
        if metric in ("r2a", "r2adj", "r2adjusted", "r2_adj", "rsquared_adj"):
            metric, adj = "r2", True
        elif metric == "rmse":
            metric, root = "mse", True
        fun = mt.FUNCTIONS_REGRESSION_DICTIONNARY[metric]

        # Scoring
        arg = [
            "y_true",
            "y_pred",
            self._evaluation_relation(
                start=start,
                npredictions=npredictions,
                method=method,
            ),
        ]
        if metric in ("aic", "bic") or adj:
            arg += [1]
        if root or adj:
            arg += [True]
        if self._ismultivar():
            res = {"index": [metric]}
            for i in range(len(self.y)):
                arg[0] = f"y_true{i}"
                arg[1] = f"y_pred{i}"
                res[self.y[i]] = [fun(*arg)]
            return TableSample(res)
        else:
            return fun(*arg)

    # Plotting Methods.

    def plot(
        self,
        vdf: Optional[SQLRelation] = None,
        ts: Optional[str] = None,
        y: Optional[SQLColumns] = None,
        start: Optional[int] = None,
        npredictions: int = 10,
        method: Literal["auto", "forecast"] = "auto",
        idx: int = 0,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the model.

        Parameters
        ----------
        vdf: SQLRelation, optional
            Object used to run the prediction.
            You can also specify a customized
            relation, but you must enclose it
            with an alias. For example,
            ``(SELECT 1) x`` is valid, whereas
            ``(SELECT 1)`` and ``SELECT 1``
            are invalid.
        ts: str, optional
            TS (Time Series) :py:class`VastColumn`
            used to order the data. The
            :py:class`VastColumn` type must be
            ``date`` (``date``, ``datetime``,
            ``timestamp``...) or numerical.
        y: SQLColumns, optional
            Response column.

            In the case of multivariate analysis,
            it represents a ``list`` of all the
            predictors.
        start: int, optional
            The behavior of the start parameter and its
            range of accepted values depends on whether
            you provide a timeseries-column (``ts``):

            - No provided timeseries-column:
                ``start`` must be an integer
                greater or equal to 0, where
                zero indicates to start
                prediction at the end of the
                in-sample data. If ``start``
                is a positive value, the function
                predicts the values between the
                end of the in-sample data and
                the start index, and then uses
                the predicted values as time
                series inputs for the subsequent
                ``npredictions``.
            - timeseries-column provided:
                ``start`` must be an ``integer``
                greater or equal to ``1`` and
                identifies the index (row) of
                the timeseries-column at which
                to begin prediction. If the
                ``start`` index is greater than
                the number of rows, ``N``, in the
                input data, the function predicts
                the values between ``N`` and
                ``start`` and uses the predicted
                values as time series inputs for
                the subsequent npredictions.

            Default:

            - No provided timeseries-column:
                prediction begins from the
                end of the in-sample data.
            - timeseries-column provided:
                prediction begins from the
                end of the provided input
                data.

        npredictions: int, optional
            ``integer`` greater or equal to ``1``,
            the number of predicted timesteps.
        method: str, optional
            Forecasting method. One of the following:

            - auto:
                the model initially utilizes the true
                values at each step for forecasting.
                However, when it reaches a point where
                it can no longer rely on true values,
                it transitions to using its own
                predictions for further forecasting.
                This method is often referred to as
                "one step ahead" forecasting.
            - forecast:
                the model initiates forecasting from
                an initial value and entirely disregards
                any subsequent true values. This approach
                involves forecasting based solely on the
                model's own predictions and does not
                consider actual observations after the
                start point.
        idx: int, optional
            It represents the index of the
            predictor for which we want to
            draw the TS plot.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to
            pass to the Plotting functions.

        Returns
        -------
        object
            Plotting Object.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will use
        the airline passengers dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_airline_passengers()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_airline_passengers()

        First we import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast.tsa import ARIMA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = ARIMA(order = (12, 0, 0))

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data, "date", "passengers")

        We can conveniently plot the
        predictions on a line plot
        to observe the efficacy of
        our model:

        .. code-block:: python

            model.plot(data, "date", "passengers", npredictions = 20, start = 140)

        .. ipython:: python
            :suppress:
            :okwarning:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot(data, "date", "passengers", npredictions = 20, start = 140, width = 650)
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_plot_1.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_plot_1.html

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.

            Examples:
            :py:class:`~vastorbit.machine_learning.vast.tsa.ARIMA`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.ARMA`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.AR`;
            :py:class:`~vastorbit.machine_learning.vast.tsa.MA`;
        """
        dataset_provided = not (isinstance(vdf, NoneType))
        y_str, n = self.y, len(self.y)
        prediction = self.predict(
            vdf=vdf,
            ts=ts,
            y=y,
            start=start,
            npredictions=npredictions,
            output_standard_errors=True,
            method=method,
            use_index_as_suffix=True,
        )
        if self._ismultivar() and not (0 <= idx < n):
            raise ValueError(
                "Parameter 'idx' represents the index of the predictor for "
                "which we want to compute the feature importance. It should "
                "be between 0 and the total number of predictors minus one"
                f" ({len(self.y) - 1})"
            )
        if self._ismultivar():
            y_str = self.y[idx]
            prediction = prediction[[f"prediction{idx}"]]
        else:
            columns = prediction.get_columns()
            idx = 0
            while "prediction" not in columns[idx] and idx < len(columns) - 1:
                idx += 1
            columns = columns[idx:]
            if len(columns) > 0:
                prediction = prediction[columns]
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="TSPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.TSPlot(
            vdf=VastFrame(self.input_relation),
            columns=y_str,
            order_by=self.ts,
            prediction=prediction,
            start=start,
            dataset_provided=dataset_provided,
            method=method,
        ).draw(**kwargs)