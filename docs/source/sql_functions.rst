.. _api.sql.functions:

=========
Functions
=========

SQL functions for data manipulation, analytics, and transformations.

____

Constants
---------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   E
   INF
   NAN
   PI
   TAU

____

Analytics
---------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   avg
   bool_and
   bool_or
   bool_xor
   conditional_change_event
   conditional_true_event
   count
   lag
   lead
   max
   median
   min
   nth_value
   quantile
   rank
   row_number
   std
   sum
   var

____

Conditional
-----------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   case_when
   decode

____

Date
----

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   date
   day
   dayofweek
   dayofyear
   extract
   getdate
   getutcdate
   hour
   interval
   microsecond
   minute
   month
   overlaps
   quarter
   round_date
   second
   timestamp
   week
   year

____

Math
----

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   apply
   abs
   acos
   asin
   atan
   atan2
   cbrt
   ceil
   comb
   cos
   cosh
   cot
   degrees
   distance
   exp
   factorial
   floor
   gamma
   hash
   isfinite
   isinf
   isnan
   lgamma
   ln
   log
   radians
   round
   sign
   sin
   sinh
   sqrt
   tan
   tanh
   trunc

____

Null Handling
-------------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   coalesce
   nullifzero
   zeroifnull

____

Random
------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   random
   randomint
   seeded_random

____

Regular Expression
------------------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   regexp_count
   regexp_ilike
   regexp_instr
   regexp_like
   regexp_replace
   regexp_substr

____

String
------

.. currentmodule:: vastorbit.sql.functions

.. autosummary:: 
   :toctree: api/
   
   length
   lower
   substr
   upper
   edit_distance
   soundex
   soundex_matches
   jaro_distance
   jaro_winkler_distance