.. _api.stats:

=====================
Statistical Functions
=====================

Statistical tests for model diagnostics and time series analysis.

____

Heteroscedasticity
------------------

.. currentmodule:: vastorbit.machine_learning.model_selection.statistical_tests

.. autosummary:: 
   :toctree: api/
   
   tsa.het_arch
   ols.het_breuschpagan
   ols.het_goldfeldquandt
   ols.het_white

____

Multicollinearity
-----------------

.. currentmodule:: vastorbit.machine_learning.model_selection.statistical_tests

.. autosummary:: 
   :toctree: api/
   
   ols.variance_inflation_factor

____

Normal Distribution
-------------------

.. currentmodule:: vastorbit.machine_learning.model_selection.statistical_tests

.. autosummary:: 
   :toctree: api/
   
   norm.jarque_bera
   norm.kurtosistest
   norm.skewtest
   norm.normaltest

____

Time Series - Stationarity/Trend
---------------------------------

.. currentmodule:: vastorbit.machine_learning.model_selection.statistical_tests

.. autosummary:: 
   :toctree: api/
   
   tsa.mkt
   tsa.adfuller

____

Time Series - Correlations
---------------------------

.. currentmodule:: vastorbit.machine_learning.model_selection.statistical_tests

.. autosummary:: 
   :toctree: api/
   
   tsa.cochrane_orcutt
   tsa.ljungbox
   tsa.durbin_watson

____

Time Series - Decomposition
----------------------------

.. currentmodule:: vastorbit.machine_learning.model_selection.statistical_tests

.. autosummary:: 
   :toctree: api/
   
   tsa.seasonal_decompose