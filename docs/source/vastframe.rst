.. _api.vastframe:

============
VastFrame
============

.. include:: logo_include.rst

Main data structure for working with VAST DataBase - pandas-like API for data at scale.

____

Core Classes
------------

.. tab-set::

   .. tab-item:: VastFrame

      **VastFrame** - DataFrame-like object for VAST DataBase tables
      
      .. currentmodule:: vastorbit

      .. autoclass:: VastFrame
         :members:

   .. tab-item:: VastColumn

      **VastColumn** - Column operations and transformations
      
      .. currentmodule:: vastorbit

      .. autoclass:: VastColumn
         :members:

____

📊 Visualization
----------------

Create interactive charts with Plotly, Highcharts, or Matplotlib backends.

General Plots
~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         bar
         barh
         boxplot
         contour
         density
         heatmap
         hexbin
         hist
         outliers_plot
         pie
         pivot_table
         plot
         scatter
         scatter_matrix
         pivot_table_chi2
         range_plot

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary:: 
         :toctree: api/

         bar
         barh
         candlestick
         boxplot
         density
         hist
         pie
         plot
         range_plot
         spider

Animated Plots
~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         animated_bar
         animated_pie
         animated_plot
         animated_scatter

Plotting Backend Classes
~~~~~~~~~~~~~~~~~~~~~~~~

.. dropdown:: Advanced: Internal Plotting Classes
   :color: secondary

   .. tab-set::

      .. tab-item:: Plotly

         .. currentmodule:: vastorbit.plotting._plotly

         .. autosummary:: 
            :toctree: api/

            ACFPlot
            BarChart
            BarChart2D
            BoxPlot
            CandleStick
            ChampionChallengerPlot
            ContourPlot
            CutoffCurve
            DensityPlot
            ElbowCurve
            HeatMap
            Histogram
            HorizontalBarChart
            HorizontalBarChart2D
            ImportanceBarChart
            LiftChart
            LinePlot
            LogisticRegressionPlot
            LOFPlot
            MultiDensityPlot
            MultiLinePlot
            NestedPieChart
            OutliersPlot
            PCACirclePlot
            PieChart
            PlotlyBase
            PRCCurve
            RangeCurve
            RegressionPlot
            RegressionTreePlot
            ROCCurve
            ScatterPlot
            SpiderChart
            StepwisePlot
            SVMClassifierPlot
            TSPlot
            VoronoiPlot

      .. tab-item:: Highcharts

         .. currentmodule:: vastorbit.plotting._highcharts

         .. autosummary:: 
            :toctree: api/

            ACFPlot
            ACFPACFPlot
            BarChart
            BarChart2D
            BoxPlot
            CandleStick
            ChampionChallengerPlot
            ContourPlot
            CutoffCurve
            DensityPlot
            ElbowCurve
            HeatMap
            Histogram
            HighchartsBase
            HorizontalBarChart
            HorizontalBarChart2D
            ImportanceBarChart
            LiftChart
            LinePlot
            LogisticRegressionPlot
            LOFPlot
            MultiDensityPlot
            MultiLinePlot
            NestedPieChart
            OutliersPlot
            PCACirclePlot
            PieChart
            PRCCurve
            RangeCurve
            RegressionPlot
            RegressionTreePlot
            ROCCurve
            ScatterPlot
            SpiderChart
            StepwisePlot
            SVMClassifierPlot
            TSPlot

      .. tab-item:: Matplotlib

         .. currentmodule:: vastorbit.plotting._matplotlib

         .. autosummary:: 
            :toctree: api/

            ACFPlot
            ACFPACFPlot
            AnimatedBarChart
            AnimatedBase
            AnimatedBubblePlot
            AnimatedLinePlot
            AnimatedPieChart
            BarChart
            BarChart2D
            BoxPlot
            CandleStick
            ChampionChallengerPlot
            ContourPlot
            CutoffCurve
            DensityPlot
            DensityPlot2D
            ElbowCurve
            HeatMap
            Histogram
            HorizontalBarChart
            HorizontalBarChart2D
            ImportanceBarChart
            LiftChart
            LinePlot
            LogisticRegressionPlot
            LOFPlot
            MatplotlibBase
            MultiDensityPlot
            MultiLinePlot
            NestedPieChart
            OutliersPlot
            PCACirclePlot
            PieChart
            PRCCurve
            RangeCurve
            RegressionPlot
            RegressionTreePlot
            ROCCurve
            ScatterMatrix
            ScatterPlot
            SpiderChart
            StepwisePlot
            SVMClassifierPlot
            TSPlot
            VoronoiPlot

____

📈 Descriptive Statistics
--------------------------

In-database aggregations and statistical summaries.

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         aad
         aggregate
         all
         any
         avg
         count
         count_percent
         describe
         duplicated
         kurtosis
         mad
         max
         median
         min
         nunique
         product
         quantile
         score
         sem
         skewness
         std
         sum
         var

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         aad
         aggregate
         avg
         count
         describe
         distinct
         kurtosis
         mad
         max
         median
         min
         mode
         nlargest
         nsmallest
         nunique
         product
         quantile
         sem
         skewness
         std
         sum
         topk
         value_counts
         var

____

🔗 Correlation & Dependencies
------------------------------

General Correlation
~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         acf
         corr
         corr_pvalue
         cov
         iv_woe
         pacf
         regr

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         iv_woe

Time Series Analysis
~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         acf
         pacf

____

🛠️ Data Preprocessing
----------------------

Encoding
~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         case_when
         one_hot_encode

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         cut
         decode
         discretize
         label_encode
         mean_encode
         one_hot_encode

Missing Values
~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         dropna
         fillna
         interpolate

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         dropna
         fillna

Duplicate Values
~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         drop_duplicates

Normalization & Outliers
~~~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         outliers
         scale

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         clip
         fill_outliers
         normalize

Data Type Conversion
~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         astype
         bool_to_int

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         astype

Formatting
~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         format_colnames
         get_match_index
         is_colname_in
         merge_similar_names
         explode_array

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         astype
         rename

Train/Test Split
~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         train_test_split

Working with Weights
~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         add_duplicates

Complete Disjunctive Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         cdt

____

⚙️ Feature Engineering
-----------------------

Analytic Functions
~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         analytic
         interpolate
         sessionize

Custom Feature Creation
~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         case_when
         eval

Feature Transformations
~~~~~~~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         abs
         apply
         applymap
         polynomial_comb
         swap

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         abs
         add
         apply
         apply_fun
         date_part
         div
         mul
         round
         slice
         sub

Moving Windows
~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary::
         :toctree: api/

         cummax
         cummin
         cumprod
         cumsum
         rolling

Text Operations
~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         regexp

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         str_contains
         str_count
         str_extract
         str_replace
         str_slice

Binary Operators
~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary:: 
         :toctree: api/

         add
         div
         mul
         sub

Feature Selection
~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         chaid
         chaid_columns

____

🔀 Join, Sort & Transform
--------------------------

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         append
         copy
         groupby
         join
         narrow
         pivot
         recommend
         sort

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         add_copy

____

🔍 Filter & Sample
-------------------

Search
~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         search

Sample
~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         sample

Balance
~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         balance

Filter Columns
~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         drop
         select

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         drop
         drop_outliers

Filter Records
~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         at_time
         between
         between_time
         filter
         first
         isin
         last

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         isin

____

💾 Serialization & Export
--------------------------

General Formats
~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         to_csv
         to_json

In-Memory Objects
~~~~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         to_numpy
         to_pandas
         to_list
         to_geopandas

Databases
~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         to_db

Binary Formats
~~~~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         to_pickle

____

ℹ️ Utilities & Information
----------------------------

Information
~~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         catcol
         current_relation
         datecol
         dtypes
         empty
         explain
         get_columns
         head
         idisplay
         iloc
         info
         memory_usage
         expected_store_usage
         numcol
         shape
         tail

   .. tab-item:: VastColumn

      .. currentmodule:: vastorbit.VastColumn

      .. autosummary::
         :toctree: api/

         category
         ctype
         dtype
         get_len
         head
         iloc
         isarray
         isbool
         isdate
         isnum
         memory_usage
         store_usage
         tail

Management
~~~~~~~~~~

.. tab-set::

   .. tab-item:: VastFrame

      .. currentmodule:: vastorbit.VastFrame

      .. autosummary:: 
         :toctree: api/

         del_catalog
         load
         save