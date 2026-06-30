"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Union

from vastorbit._typing import PythonNumber
from vastorbit._utils._sql._collect import save_vastorbit_logs

from vastorbit.core.vastframe.base import VastFrame

from vastorbit.machine_learning.vast.tsa.base import TimeSeriesModelBase

"""
General Classes.
"""


class ARIMA(TimeSeriesModelBase):
    """
    Creates a inDB ARIMA model.

    Parameters
    ----------
    name: str, optional
        Name of the model. The  model is stored  in the
        database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.
    order: tuple, optional
        The (p,d,q) order of the model for the autoregressive,
        differences, and moving average components.
    tol: float, optional
        Determines  whether the algorithm has reached
        the specified accuracy result.
    max_iter: int, optional
        Determines  the maximum number of  iterations
        the  algorithm performs before  achieving the
        specified accuracy result.
    init: str, optional
        Initialization method, one of the following:

        - 'zero':
            Coefficients are initialized to zero.
        - 'hr':
            Coefficients are initialized using the
            Hannan-Rissanen algorithm.

    missing: str, optional
        Method for handling missing values, one of the
        following strings:

        - 'drop':
            Missing values are ignored.
        - 'error':
            Missing values raise an error.
        - 'zero':
            Missing values are set to zero.
        - 'linear_interpolation':
            Missing values are replaced by a linearly
            interpolated value based on the nearest
            valid entries before and after the missing
            value. In cases where the first or last
            values in a dataset are missing, the function
            errors.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``phi_``: numpy.array
        The coefficient of the AutoRegressive process.
        It represents the strength and direction of the
        relationship between a variable and its past
        values.
    ``theta_``: numpy.array
        The theta coefficient of the Moving Average
        process. It signifies the impact and contribution
        of the lagged error terms in determining the
        current value within the time series model.
    ``mean_``: float
        The mean of the time series values.
    ``feature_importances_``: numpy.array
        The importance of features is computed through
        the AutoRegressive part coefficients, which
        are normalized based on their range. Subsequently,
        an activation function calculates the final score.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.linear_model.LinearModel.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``mse_``: float
        The mean squared error (MSE) of the model, based
        on one-step forward forecasting, may not always
        be relevant. Utilizing a full forecasting approach
        is recommended to compute a more meaningful and
        comprehensive metric.
    ``n_``: int
        The number of rows used to fit the model.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.tsa.TimeSeriesModelBase.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    Initialization
    ^^^^^^^^^^^^^^^

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
        :py:mod:`vastorbit` are used as intended without
        interfering with functions from other libraries.

    For this example, we will use
    the airline passengers dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_airline_passengers()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_airline_passengers.html

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
        data = vod.load_airline_passengers()

    We can plot the data to visually inspect it for the
    presence of any trends:

    .. code-block::

        data["passengers"].plot(ts = "date")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = data["passengers"].plot(ts = "date", width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arma_data_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arma_data_plot.html

    Though the increasing trend is obvious in our example,
    we can confirm it by the
    :py:meth:`~vastorbit.machine_learning.model_selection.statistical_tests.mkt`
    (Mann Kendall test) test:

    .. code-block:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt

        mkt(data, column = "passengers", ts = "date")

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt
        result = mkt(data, column = "passengers", ts = "date")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arma_data_mkt_result.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arma_data_mkt_result.html

    The above tests gives us some more insights into the data
    such as that the data is monotonic, and is increasing.
    Furthermore, the low p-value confirms the presence of
    a trend with respect to time. Now we are sure of the trend
    so we can apply the appropriate time-series model to fit it.

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``ARIMA`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast.tsa import ARIMA

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = ARIMA(order = (12, 0, 0))

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Fitting
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(data, "date", "passengers")

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

    We can conveniently get the features importance:

    .. ipython:: python
        :okwarning:

        model.features_importance()

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_features.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_features.html

    .. important::

        Feature importance is determined by using the coefficients of the
        auto-regressive (AR) process and normalizing them. This method
        tends to be precise when your time series primarily consists of an
        auto-regressive component. However, its accuracy may be a topic of
        discussion if the time series contains other components as well._____

    One important thing in time-series forecasting is that it has two
    types of forecasting:

    - One-step ahead forecasting
    - Full forecasting

    .. important::

        The default method is one-step ahead forecasting.
        To use full forecasting, use ``method = "forecast"``.

    One-step ahead
    ---------------

    In this type of forecasting, the algorithm utilizes the
    true value of the previous timestamp (t-1) to predict the
    immediate next timestamp (t). Subsequently, to forecast
    additional steps into the future (t+1), it relies on the
    actual value of the immediately preceding timestamp (t).

    A notable drawback of this forecasting method is its
    tendency to exhibit exaggerated accuracy, particularly
    when predicting more than one step into the future.

    Metrics
    ^^^^^^^^

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

    You can also choose the number of predictions and where to start the forecast.
    For example, the following code will allow you to generate a report with 30
    predictions, starting the forecasting process at index 40.

    .. code-block:: python

        model.report(start = 40, npredictions = 30)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 40, npredictions = 30)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_report_pred_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_report_pred_2.html

    .. note::

        No matter what value you give for npredictons, in the
        report, the comparison will only be until the extent
        of the availability of true value. For exaxmple, even if
        we give ``n_predictions = 300``, the report result will
        be the same as ``n_predictions = 104`` starting from 40.
        This is because there are only 104 values beyond 40 in the
        dataset.

    .. important::

        Most metrics are computed using a single SQL query, but some of them might
        require multiple SQL queries. Selecting only the necessary metrics in the
        report can help optimize performance.
        E.g. ``model.report(metrics = ["mse", "r2"])``.

    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.tsa.ARIMA.score`
    function to calculate various regression metrics, with the explained
    variance being the default.

    .. ipython:: python
        :okwarning:

        model.score()

    The same applies to the score. You can choose where to start and
    the number of predictions to use.

    .. ipython:: python
        :okwarning:

        model.score(start = 40, npredictions = 30)

    .. important::

        If you do not specify a starting point and the number of
        predictions, the forecast will begin at one-fourth of the
        dataset, which can result in an inaccurate score, especially
        for large datasets. It's important to choose these parameters
        carefully.

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. code-block:: python

        model.predict()

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_prediction.html

    .. hint::

        You can control the number of prediction steps by changing
        the ``npredictions`` parameter:
        ``model.predict(npredictions = 30)``.

    .. note::

        Predictions can be made automatically
        by using the training set, in which
        case you don't need to specify the
        predictors. Alternatively, you can
        pass only the :py:class:`~VastFrame`
        to the
        :py:meth:`~vastorbit.machine_learning.vast.tsa.ARIMA.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    If you would like to have the 'time-stamps' (ts) in the output then
    you can switch the ``output_estimated_ts`` the parameter. And if you
    also would like to see the standard error then you can switch the
    ``output_standard_errors`` parameter:

    .. code-block:: python

        model.predict(output_estimated_ts = True, output_standard_errors = True)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(output_estimated_ts = True, output_standard_errors = True)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_prediction_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_prediction_2.html

    .. important::

        The ``output_estimated_ts`` parameter provides an estimation of
        'ts' assuming that 'ts' is regularly spaced.

    If you don't provide any input, the function will begin forecasting
    after the last known value. If you want to forecast starting from a
    specific value within the input dataset or another dataset, you can
    use the following syntax.

    .. code-block:: python

        model.predict(
            data,
            "date",
            "passengers",
            start = 40,
            npredictions = 20,
            output_estimated_ts = True,
            output_standard_errors = True,
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(data, "date", "passengers", start = 40, npredictions = 20, output_estimated_ts = True, output_standard_errors = True)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_prediction_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_prediction_3.html

    Plots
    ^^^^^^

    We can conveniently plot the
    predictions on a line plot to
    observe the efficacy of our
    model:

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

    .. note::

        You can control the number of prediction steps by changing
        the ``npredictions`` parameter:
        ``model.plot(npredictions = 30)``.

    Please refer to  :ref:`chart_gallery.tsa` for more examples.

    Full forecasting
    -----------------

    In this forecasting approach, the algorithm relies solely
    on a chosen true value for initiation. Subsequently, all
    predictions are established based on a series of previously
    predicted values.

    This methodology aligns the accuracy of predictions more
    closely with reality. In practical forecasting scenarios,
    the goal is to predict all future steps, and this technique
    ensures a progressive sequence of predictions.

    Metrics
    ^^^^^^^^

    We can get the report using:

    .. code-block:: python

        model.report(start = 40, method = "forecast")

    By selecting ``start = 40``, we will measure the accuracy from
    40th time-stamp and continue the assessment until the last
    available time-stamp.

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 40, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_report.html

    Notice that the accuracy using ``method = forecast`` is poorer
    than the one-step ahead forecasting.

    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.tsa.ARIMA.score`
    function to calculate various regression metrics, with the explained
    variance being the default.

    .. ipython:: python
        :okwarning:

        model.score(start = 40, npredictions = 30, method = "forecast")

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. code-block:: python

        model.predict(start = 50, npredictions = 40, method = "forecast")

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(start = 50, npredictions = 40, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_prediction.html

    If you want to forecast starting from a specific value within
    the input dataset or another dataset, you can use the following syntax.

    .. code-block:: python

        model.predict(
            data,
            "date",
            "passengers",
            start = 40,
            npredictions = 20,
            output_estimated_ts = True,
            output_standard_errors = True,
            method = "forecast"
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(data, "date", "passengers", start = 40, npredictions = 20, output_estimated_ts = True, output_standard_errors = True, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_prediction_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_prediction_3.html

    Plots
    ^^^^^^

    We can conveniently plot the
    predictions on a line plot to
    observe the efficacy of our
    model:

    .. code-block:: python

        model.plot(data, "date", "passengers", npredictions = 40, start = 120, method = "forecast")

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(data, "date", "passengers", npredictions = 40, start = 120, method = "forecast", width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_plot_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_arima_f_plot_1.html
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["TIMESERIES"]:
        return "TIMESERIES"

    @property
    def _model_type(self) -> Literal["ARIMA"]:
        return "ARIMA"


class AR(TimeSeriesModelBase):
    """
    Creates a inDB Autoregressor model.

    .. important::

        The vastorbit ``AR`` model also implements the
        ``VAR`` method; use ``AR`` to build a vector
        autoregressor.

    .. note::

        The AR model is much faster than ARIMA(p, 0, 0)
        because the underlying algorithm of AR is quite 
        different.

    Parameters
    ----------
    name: str, optional
        Name of the model. The  model is stored  in the
        database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.
    p: int, optional
        Integer in the range [1, 1999], the number of
        lags to consider in the computation. Larger
        values for p weaken the correlation.
    method: str, optional
        One of the following algorithms for training the
        model:

        - ols:
            Ordinary Least Squares
        - yule-walker:
            Yule-Walker
    penalty: str, optional
        Method of regularization.

        - none:
            No regularization.
        - l2:
            L2 regularization.
    C: PythonNumber, optional
        The regularization parameter value. The value
        must be zero or non-negative.
    missing: str, optional
        Method for handling missing values, one of the
        following strings:

        - 'drop':
            Missing values are ignored.
        - 'error':
            Missing values raise an error.
        - 'zero':
            Missing values are set to zero.
        - 'linear_interpolation':
            Missing values are replaced by a linearly
            interpolated value based on the nearest
            valid entries before and after the missing
            value. In cases where the first or last
            values in a dataset are missing, the function
            errors.
    subtract_mean: bool, optional
        For Yule Walker, if ``subtract_mean is True``, then
        the mean of the column will be subtracted before
        calculating the coefficients. If ``False`` (default),
        then the calculations will be performed directly on
        the data, this often gives a more accurate model.
        Note that the means saved in the model will be saved
        as all 0s if this parameter is set to ``False``.
        This parameter has no effect for OLS.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``phi_``: numpy.array
        The coefficient of the AutoRegressive process.
        It represents the strength and direction of the
        relationship between a variable and its past
        values.
    ``intercept_``: float
        Represents the expected value of the time series
        when the lagged values are zero. It signifies the
        baseline or constant term in the model, capturing
        the average level of the series in the absence of
        any historical influence.
    ``feature_importances_``: numpy.array
        The importance of features is computed through
        the AutoRegressive part coefficients, which
        are normalized based on their range. Subsequently,
        an activation function calculates the final score.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.linear_model.LinearModel.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``mse_``: float
        The mean squared error (MSE) of the model, based
        on one-step forward forecasting, may not always
        be relevant. Utilizing a full forecasting approach
        is recommended to compute a more meaningful and
        comprehensive metric.
    ``n_``: int
        The number of rows used to fit the model.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.tsa.TimeSeriesModelBase.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    Initialization
    ^^^^^^^^^^^^^^^

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
        :py:mod:`vastorbit` are used as intended without
        interfering with functions from other libraries.

    For this example, we will generate a dummy time-series
    dataset.

    .. ipython:: python

        data = vo.VastFrame(
            {
                "month": [i for i in range(1, 41)],
                "GB": [5, 10, 20, 35, 55, 80, 110, 145, 185, 230,
                        280, 330, 380, 430, 480, 530, 580, 630, 680, 730,
                        780, 830, 880, 930, 980, 1030, 1080, 1130, 1180, 1230,
                        1280, 1330, 1380, 1430, 1480, 1530, 1580, 1630, 1680, 1730],
            }
        )

    .. ipython:: python
        :suppress:

        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_data.html", "w")
        html_file.write(data._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_data.html

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

    We can plot the data to visually inspect it for the
    presence of any trends:

    .. code-block::

        data["GB"].plot(ts = "month")

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = data["GB"].plot(ts = "month", width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_data_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_data_plot.html

    Though the increasing trend is obvious in our example,
    we can confirm it by the
    :py:meth:`~vastorbit.machine_learning.model_selection.statistical_tests.mkt`
    (Mann Kendall test) test:

    .. code-block:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt

        mkt(data, column = "GB", ts = "month")

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt
        result = mkt(data, column = "GB", ts = "month")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_data_mkt_result.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_data_mkt_result.html

    The above tests gives us some more insights into the data
    such as that the data is monotonic, and is increasing.
    Furthermore, the low p-value confirms the presence of
    a trend with respect to time. Now we are sure of the trend
    so we can apply the appropriate time-series model to fit it.

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``AR`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast.tsa import AR

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = AR(p = 2)

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Fitting
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(data, "month", "GB")

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

    We can conveniently get the features importance:

    .. ipython:: python
        :okwarning:

        model.features_importance()

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_features.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_features.html

    One important thing in time-series forecasting is that it has two
    types of forecasting:

    - One-step ahead forecasting
    - Full forecasting

    .. important::

        The default method is one-step ahead forecasting.
        To use full forecasting, use ``method = "forecast"``.

    One-step ahead
    ---------------

    In this type of forecasting, the algorithm utilizes the
    true value of the previous timestamp (t-1) to predict the
    immediate next timestamp (t). Subsequently, to forecast
    additional steps into the future (t+1), it relies on the
    actual value of the immediately preceding timestamp (t).

    A notable drawback of this forecasting method is its
    tendency to exhibit exaggerated accuracy, particularly
    when predicting more than one step into the future.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. code-block:: python

        model.report(start = 4)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 4)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_report.html

    .. important::

        The value for ``start`` cannot be less than the
        ``p`` value selected for the AR model.

    You can also choose the number of predictions and where to start the forecast.
    For example, the following code will allow you to generate a report with 30
    predictions, starting the forecasting process at index 40.

    .. code-block:: python

        model.report(start = 4, npredictions = 10)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 4, npredictions = 10)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_report_pred_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_report_pred_2.html

    .. important::

        Most metrics are computed using a single SQL query, but some of them might
        require multiple SQL queries. Selecting only the necessary metrics in the
        report can help optimize performance.
        E.g. ``model.report(metrics = ["mse", "r2"])``.

    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.tsa.AR.score`
    function to calculate various regression metrics, with the explained
    variance being the default.

    .. ipython:: python
        :okwarning:

        model.score(start = 3, npredictions = 30)

    .. important::

        If you do not specify a starting point and the number of
        predictions, the forecast will begin at one-fourth of the
        dataset, which can result in an inaccurate score, especially
        for large datasets. It's important to choose these parameters
        carefully.

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. code-block:: python

        model.predict()

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_prediction.html

    .. hint::

        You can control the number of prediction steps by changing
        the ``npredictions`` parameter:
        ``model.predict(npredictions = 30)``.

    .. note::

        Predictions can be made automatically
        by using the training set, in which
        case you don't need to specify the
        predictors. Alternatively, you can
        pass only the :py:class:`~VastFrame`
        to the
        :py:meth:`~vastorbit.machine_learning.vast.tsa.AR.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    If you would like to have the 'time-stamps' (ts) in the output then
    you can switch the ``output_estimated_ts`` the parameter.

    .. code-block:: python

        model.predict(output_estimated_ts = True)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(output_estimated_ts = True)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_prediction_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_prediction_2.html

    .. important::

        The ``output_estimated_ts`` parameter provides an estimation of
        'ts' assuming that 'ts' is regularly spaced.

    If you don't provide any input, the function will begin forecasting
    after the last known value. If you want to forecast starting from a
    specific value within the input dataset or another dataset, you can
    use the following syntax.

    .. code-block:: python

        model.predict(
            data,
            "month",
            "GB",
            start = 7,
            npredictions = 10,
            output_estimated_ts = True,
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(data, "month", "GB", start = 7, npredictions = 10, output_estimated_ts = True)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_prediction_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_prediction_3.html

    Plots
    ^^^^^^

    We can conveniently plot the
    predictions on a line plot to
    observe the efficacy of our
    model:

    .. code-block:: python

        model.plot(data, "month", "GB", npredictions = 10, start=7)

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(data, "month", "GB", npredictions = 10, start = 7, width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_plot_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_plot_1.html

    .. note::

        You can control the number of prediction steps by changing
        the ``npredictions`` parameter:
        ``model.plot(npredictions = 30)``.

    Please refer to  :ref:`chart_gallery.tsa` for more examples.

    Full forecasting
    -----------------

    In this forecasting approach, the algorithm relies solely
    on a chosen true value for initiation. Subsequently, all
    predictions are established based on a series of previously
    predicted values.

    This methodology aligns the accuracy of predictions more
    closely with reality. In practical forecasting scenarios,
    the goal is to predict all future steps, and this technique
    ensures a progressive sequence of predictions.


    Metrics
    ^^^^^^^^

    We can get the report using:

    .. code-block:: python

        model.report(start = 4, method = "forecast")

    By selecting ``start = 4``, we will measure the accuracy from
    40th time-stamp and continue the assessment until the last
    available time-stamp.

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 4, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_report.html

    Notice that the accuracy using ``method = forecast`` is poorer
    than the one-step ahead forecasting.


    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.tsa.AR.score`
    function to calculate various regression metrics, with the explained
    variance being the default.

    .. ipython:: python
        :okwarning:

        model.score(start = 4, npredictions = 6, method = "forecast")


    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. code-block:: python

        model.predict(start = 40, npredictions = 10, method = "forecast")

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(start = 40, npredictions = 10, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_prediction.html

    If you want to forecast starting from a specific value within
    the input dataset or another dataset, you can use the following syntax.

    .. code-block:: python

        model.predict(
            data,
            "month",
            "GB",
            start = 4,
            npredictions = 20,
            output_estimated_ts = True,
            output_standard_errors = True,
            method = "forecast",
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(data, "month", "GB", start = 4, npredictions = 20, output_estimated_ts = True, output_standard_errors = True, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_prediction_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_prediction_3.html

    Plots
    ^^^^^^

    We can conveniently plot the
    predictions on a line plot to
    observe the efficacy of our
    model:

    .. code-block:: python

        model.plot(data, "month", "GB", npredictions = 10, start = 5, method = "forecast")

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(data, "month", "GB", npredictions = 10, start = 5, method = "forecast", width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_plot_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_ar_f_plot_1.html
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["TIMESERIES"]:
        return "TIMESERIES"

    @property
    def _model_type(self) -> Literal["AR"]:
        return "AR"

# Multivariate models


class VAR(AR):
    """
    Creates a inDB VectorAutoregressor model.

    Parameters
    ----------
    name: str, optional
        Name of the model. The  model is stored  in the
        database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.
    p: int, optional
        Integer in the range [1, 1999], the number of
        lags to consider in the computation. Larger
        values for p weaken the correlation.
    method: str, optional
        One of the following algorithms for training the
        model:

        - ols:
            Ordinary Least Squares
        - yule-walker:
            Yule-Walker
    penalty: str, optional
        Method of regularization.

        - none:
            No regularization.
        - l2:
            L2 regularization.
    C: PythonNumber, optional
        The regularization parameter value. The value
        must be zero or non-negative.
    missing: str, optional
        Method for handling missing values, one of the
        following strings:

        - 'drop':
            Missing values are ignored.
        - 'error':
            Missing values raise an error.
        - 'zero':
            Missing values are set to zero.
        - 'linear_interpolation':
            Missing values are replaced by a linearly
            interpolated value based on the nearest
            valid entries before and after the missing
            value. In cases where the first or last
            values in a dataset are missing, the function
            errors.
    subtract_mean: bool, optional
        For Yule Walker, if ``subtract_mean is True``, then
        the mean of the column(s) will be subtracted before
        calculating the coefficients. If ``False`` (default),
        then the calculations will be performed directly on
        the data, this often gives a more accurate model.
        Note that the means saved in the model will be saved
        as all 0s if this parameter is set to ``False``.
        This parameter has no effect for OLS.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``phi_``: numpy.array
        The coefficient of the AutoRegressive process.
        It represents the strength and direction of the
        relationship between a variable and its past
        values.

        .. note::

            In the case of multivariate analysis, each
            coefficient is represented by a matrix of
            numbers.
    ``intercept_``: float
        Represents the expected value of the time series
        when the lagged values are zero. It signifies the
        baseline or constant term in the model, capturing
        the average level of the series in the absence of
        any historical influence.

        .. note::

            In the case of multivariate analysis, the
            intercept is represented by a vector of
            numbers.
    ``feature_importances_``: numpy.array
        The importance of features is computed through
        the AutoRegressive part coefficients, which
        are normalized based on their range. Subsequently,
        an activation function calculates the final score.
        It is necessary to use the
        :py:meth:`~vastorbit.machine_learning.vast.linear_model.LinearModel.features_importance`
        method to compute it initially, and the computed
        values will be subsequently utilized for subsequent
        calls.
    ``mse_``: float
        The mean squared error (MSE) of the model, based
        on one-step forward forecasting, may not always
        be relevant. Utilizing a full forecasting approach
        is recommended to compute a more meaningful and
        comprehensive metric.
    ``n_``: int
        The number of rows used to fit the model.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.tsa.TimeSeriesModelBase.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    Initialization
    ^^^^^^^^^^^^^^^

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
        :py:mod:`vastorbit` are used as intended without
        interfering with functions from other libraries.

    For this example, we will generate a dummy time-series
    dataset.

    .. ipython:: python

        data = vo.VastFrame(
            {
                "month": [i for i in range(1, 19)],
                "GB1": [5, 10, 20, 35, 55, 80, 110, 145, 185, 230,
                        280, 335, 395, 460, 530, 605, 685, 770],
                "GB2": [3, 7, 12, 18, 22, 30, 37, 39, 51, 80,
                        95, 112, 130, 150, 172, 196, 222, 250],
            }
        )

    .. ipython:: python
        :suppress:

        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_data.html", "w")
        html_file.write(data._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_data.html

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

    We can plot the data to visually inspect it for the
    presence of any trends:

    .. code-block::

        data.plot(ts = "month", columns = ["GB1", "GB2"])

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = data.plot(ts = "month", columns = ["GB1", "GB2"], width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_data_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_data_plot.html

    Though the increasing trend is obvious in our example,
    we can confirm it by the
    :py:meth:`~vastorbit.machine_learning.model_selection.statistical_tests.mkt`
    (Mann Kendall test) test:

    .. code-block:: python

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt

        mkt(data, column = "GB1", ts = "month")

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.model_selection.statistical_tests import mkt
        result = mkt(data, column = "GB1", ts = "month")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_data_mkt_result.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_data_mkt_result.html

    The above tests gives us some more insights into the data
    such as that the data is monotonic, and is increasing.
    Furthermore, the low p-value confirms the presence of
    a trend with respect to time. Now we are sure of the trend
    so we can apply the appropriate time-series model to fit it.

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``VAR`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast.tsa import VAR

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = VAR(p = 2)

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Fitting
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(data, "month", ["GB1", "GB2"])

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

    We can conveniently get the features importance
    of the first predictor:

    .. ipython:: python
        :okwarning:

        model.features_importance(idx=0)

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.features_importance()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_features.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_features.html

    .. note::

        We use ``idx=0`` to choose the first predictor.
        In our case, it is ``GB1``. We can set ``idx=1``
        to switch to ``GB2`` ..._____

    One important thing in time-series forecasting is that it has two
    types of forecasting:

    - One-step ahead forecasting
    - Full forecasting

    .. important::

        The default method is one-step ahead forecasting.
        To use full forecasting, use ``method = "forecast"``.

    One-step ahead
    ---------------

    In this type of forecasting, the algorithm utilizes the
    true value of the previous timestamp (t-1) to predict the
    immediate next timestamp (t). Subsequently, to forecast
    additional steps into the future (t+1), it relies on the
    actual value of the immediately preceding timestamp (t).

    A notable drawback of this forecasting method is its
    tendency to exhibit exaggerated accuracy, particularly
    when predicting more than one step into the future.

    Metrics
    ^^^^^^^^

    We can get the entire report using:

    .. code-block:: python

        model.report(start = 4)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 4)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_report.html

    .. important::

        The value for ``start`` cannot be less than the
        ``p`` value selected for the ``VAR`` model.

    You can also choose the number of predictions and where to start the forecast.
    For example, the following code will allow you to generate a report with 30
    predictions, starting the forecasting process at index 40.

    .. code-block:: python

        model.report(start = 4, npredictions = 10)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 4, npredictions = 10)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_report_pred_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_report_pred_2.html

    .. important::

        Most metrics are computed using a single SQL query, but some of them might
        require multiple SQL queries. Selecting only the necessary metrics in the
        report can help optimize performance.
        E.g. ``model.report(metrics = ["mse", "r2"])``.

    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.tsa.VAR.score`
    function to calculate various regression metrics, with the explained
    variance being the default.

    .. ipython:: python
        :okwarning:

        model.score(start = 3, npredictions = 10)

    .. important::

        If you do not specify a starting point and the number of
        predictions, the forecast will begin at one-fourth of the
        dataset, which can result in an inaccurate score, especially
        for large datasets. It's important to choose these parameters
        carefully.

    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. code-block:: python

        model.predict()

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict()
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_prediction.html

    .. hint::

        You can control the number of prediction steps by changing
        the ``npredictions`` parameter:
        ``model.predict(npredictions = 30)``.

    .. note::

        Predictions can be made automatically
        by using the training set, in which
        case you don't need to specify the
        predictors. Alternatively, you can
        pass only the :py:class:`~VastFrame`
        to the
        :py:meth:`~vastorbit.machine_learning.vast.tsa.VAR.predict`
        function, but in this case, it's
        essential that the column names of
        the :py:class:`~VastFrame` match the
        predictors and response name in the
        model.

    If you would like to have the 'time-stamps' (ts) in the output then
    you can switch the ``output_estimated_ts`` the parameter.

    .. code-block:: python

        model.predict(output_estimated_ts = True)

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(output_estimated_ts = True)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_prediction_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_prediction_2.html

    .. important::

        The ``output_estimated_ts`` parameter provides an estimation of
        'ts' assuming that 'ts' is regularly spaced.

    If you don't provide any input, the function will begin forecasting
    after the last known value. If you want to forecast starting from a
    specific value within the input dataset or another dataset, you can
    use the following syntax.

    .. code-block:: python

        model.predict(
            data,
            "month",
            ["GB1", "GB2"],
            start = 4,
            npredictions = 3,
            output_estimated_ts = True,
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(data, "month", ["GB1", "GB2"], start = 4, npredictions = 3, output_estimated_ts = True)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_prediction_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_prediction_3.html

    Plots
    ^^^^^^

    We can conveniently plot the
    predictions on a line plot to
    observe the efficacy of our
    model:

    .. code-block:: python

        model.plot(data, "month", ["GB1", "GB2"], npredictions = 3, start=4)

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(data, "month", ["GB1", "GB2"], npredictions = 3, start = 4, width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_plot_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_plot_1.html

    .. note::

        You can control the number of prediction steps by changing
        the ``npredictions`` parameter:
        ``model.plot(npredictions = 30)``.

    Please refer to  :ref:`chart_gallery.tsa` for more examples.

    .. note::

        We use ``idx=0`` to choose the first predictor.
        In our case, it is ``GB1``. We can set ``idx=1``
        to switch to ``GB2`` ...

    Full forecasting
    -----------------

    In this forecasting approach, the algorithm relies solely
    on a chosen true value for initiation. Subsequently, all
    predictions are established based on a series of previously
    predicted values.

    This methodology aligns the accuracy of predictions more
    closely with reality. In practical forecasting scenarios,
    the goal is to predict all future steps, and this technique
    ensures a progressive sequence of predictions.

    Metrics
    ^^^^^^^^

    We can get the report using:

    .. code-block:: python

        model.report(start = 4, method = "forecast")

    By selecting ``start = 4``, we will measure the accuracy from
    40th time-stamp and continue the assessment until the last
    available time-stamp.

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.report(start = 4, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_report.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_report.html

    Notice that the accuracy using ``method = forecast`` is poorer
    than the one-step ahead forecasting.


    You can utilize the
    :py:meth:`~vastorbit.machine_learning.vast.tsa.VAR.score`
    function to calculate various regression metrics, with the explained
    variance being the default.

    .. ipython:: python
        :okwarning:

        model.score(start = 4, npredictions = 6, method = "forecast")


    Prediction
    ^^^^^^^^^^^

    Prediction is straight-forward:

    .. code-block:: python

        model.predict(start = 10, npredictions = 3, method = "forecast")

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(start = 10, npredictions = 3, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_prediction.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_prediction.html

    If you want to forecast starting from a specific value within
    the input dataset or another dataset, you can use the following syntax.

    .. code-block:: python

        model.predict(
            data,
            "month",
            ["GB1", "GB2"],
            start = 4,
            npredictions = 4,
            output_estimated_ts = True,
            output_standard_errors = True,
            method = "forecast",
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.predict(data, "month", ["GB1", "GB2"], start = 4, npredictions = 4, output_estimated_ts = True, output_standard_errors = True, method = "forecast")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_prediction_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_prediction_3.html

    Plots
    ^^^^^^

    We can conveniently plot the
    predictions on a line plot to
    observe the efficacy of our
    model:

    .. code-block:: python

        model.plot(
            data,
            "month",
            ["GB1", "GB2",
            npredictions = 4,
            start = 5,
            method = "forecast",
        )

    .. ipython:: python
        :suppress:
        :okwarning:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(data, "month", ["GB1", "GB2"], npredictions = 4, start = 5, method = "forecast", width = 650)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_plot_1.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_tsa_var_f_plot_1.html

    """

    # Properties.

    @property
    def _model_type(self) -> Literal["VAR"]:
        return "VAR"