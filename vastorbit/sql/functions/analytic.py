"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit._typing import SQLExpression
from vastorbit._utils._sql._format import format_magic

from vastorbit.core.string_sql.base import StringSQL


def avg(expr: SQLExpression) -> StringSQL:
    """
    Computes the average (arithmetic mean) of
    an  expression  over  a  group  of  rows.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.avg(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_avg.html", "w")
        html_file.write(df.select([str(vof.avg(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_avg.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"AVG({expr})", "float")


mean = avg


def bool_and(expr: SQLExpression) -> StringSQL:
    """
    Processes  Boolean  values and returns  a  Boolean
    value  result.  If  all  input  values  are  true,
    BOOL_AND returns True. Otherwise it returns False.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [True, False, True, True]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.bool_and(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [True, False, True, True]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_bool_and.html", "w")
        html_file.write(df.select([str(vof.bool_and(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_bool_and.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"BOOL_AND({expr})", "int")


def bool_or(expr: SQLExpression) -> StringSQL:
    """
    Processes Boolean values and returns a Boolean
    value  result. If at least one input value  is
    true,  BOOL_OR  returns  True.  Otherwise,  it
    returns False.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [True, False, True, True]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.bool_or(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [True, False, True, True]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_bool_or.html", "w")
        html_file.write(df.select([str(vof.bool_or(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_bool_or.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"BOOL_OR({expr})", "int")


def bool_xor(expr: SQLExpression) -> StringSQL:
    """
    Processes  Boolean values and  returns a Boolean
    value  result.  If  specifically only one  input
    value is true, BOOL_XOR returns True. Otherwise,
    it returns False.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [True, False, True, True]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.bool_xor(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [True, False, True, True]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_bool_xor.html", "w")
        html_file.write(df.select([str(vof.bool_xor(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_bool_xor.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"(SUM(IF({expr}, 1, 0)) % 2 = 1)", "int")


def count(expr: SQLExpression) -> StringSQL:
    """
    Returns as a BIGINT the number of rows in each group
    where the expression is not NULL.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, None, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.count(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, None, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_count.html", "w")
        html_file.write(df.select([str(vof.count(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_count.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"COUNT({expr})", "int")


def lag(expr: SQLExpression, offset: int = 1) -> StringSQL:
    """
    Returns the value of the input expression at the given
    offset before the current row within a window.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    offset: int
        Indicates how great is the lag.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [11.4, -2.5, 3.5, -4.2],
            },
        )

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["lag"] = vof.lag(df["y"], 1)._over(order_by = [df["x"]])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, 2, 3, 4],
                          "y": [11.4, -2.5, 3.5, -4.2]})
        df["lag"] = vof.lag(df["y"], 1)._over(order_by = [df["x"]])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_lag.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_lag.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"LAG({expr}, {offset})")


def lead(expr: SQLExpression, offset: int = 1) -> StringSQL:
    """
    Returns values  from the row after the current row within
    a window, letting you access more than one row in a table
    at the same time.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    offset: int
        Indicates how great is the lead.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [11.4, -2.5, 3.5, -4.2],
            },
        )

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["lead"] = vof.lead(df["y"], 1)._over(order_by = [df["x"]])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, 2, 3, 4],
                          "y": [11.4, -2.5, 3.5, -4.2]})
        df["lead"] = vof.lead(df["y"], 1)._over(order_by = [df["x"]])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_lead.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_lead.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"LEAD({expr}, {offset})")


def max(expr: SQLExpression) -> StringSQL:
    """
    Returns the greatest value of an expression
    over a group of rows.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.max(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_max.html", "w")
        html_file.write(df.select([str(vof.max(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_max.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"MAX({expr})", "float")


def median(expr: SQLExpression) -> StringSQL:
    """
    Computes the approximate median of an expression
    over a group of rows.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.median(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_median.html", "w")
        html_file.write(df.select([str(vof.median(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_median.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"APPROX_PERCENTILE({expr}, 0.5)", "float")


def min(expr: SQLExpression) -> StringSQL:
    """
    Returns the smallest value of an expression
    over a group of rows.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.min(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_min.html", "w")
        html_file.write(df.select([str(vof.min(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_min.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"MIN({expr})", "float")


def nth_value(expr: SQLExpression, row_number: int) -> StringSQL:
    """
    Returns the value evaluated at the row that is
    the nth row of the window (counting from 1).

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    row_number: int
        Specifies the row to evaluate.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [11.4, -2.5, 3.5, -4.2],
            },
        )

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["nth_value"] = vof.nth_value(df["y"], 3)._over(order_by = [df["x"]])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, 2, 3, 4],
                          "y": [11.4, -2.5, 3.5, -4.2]})
        df["nth_value"] = vof.nth_value(df["y"], 3)._over(order_by = [df["x"]])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_nth_value.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_nth_value.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"NTH_VALUE({expr}, {row_number})", "int")


def quantile(expr: SQLExpression, number: float) -> StringSQL:
    """
    Computes  the  approximate  percentile of  an
    expression over a group of rows.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    number: float
        Percentile value,  which must be  a FLOAT
        constant ranging from 0 to 1 (inclusive).

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.quantile(df["x"], 0.25))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_quantile.html", "w")
        html_file.write(df.select([str(vof.quantile(df["x"], 0.25))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_quantile.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(
        f"APPROX_PERCENTILE({expr}, {number})",
        "float",
    )


def rank() -> StringSQL:
    """
    Within each window partition, ranks all rows in
    the  query  results set according to the  order
    specified  by  the  window's  ORDER BY  clause.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [1, -10, 1000, 7, 7]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["rank"] = vof.rank()._over(order_by = [df["x"]])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, -10, 1000, 7, 7]})
        df["rank"] = vof.rank()._over(order_by = [df["x"]])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_rank.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_rank.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    return StringSQL("RANK()", "int")


def row_number() -> StringSQL:
    """
    Assigns a sequence of unique numbers, starting
    from 1,  to  each  row in a  window partition.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [1, -10, 1000, 7, 7]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["row_number"] = vof.row_number()._over(order_by = [df["x"]])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, -10, 1000, 7, 7]})
        df["row_number"] = vof.row_number()._over(order_by = [df["x"]])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_row_number.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_row_number.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    return StringSQL("ROW_NUMBER()", "int")


def std(expr: SQLExpression) -> StringSQL:
    """
    Evaluates  the  statistical  sample  standard
    deviation  for  each  member  of  the  group.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.std(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_std.html", "w")
        html_file.write(df.select([str(vof.std(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_std.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"STDDEV({expr})", "float")


stddev = std


def sum(expr: SQLExpression) -> StringSQL:
    """
    Computes the sum of an expression over a group
    of rows.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.sum(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_sum.html", "w")
        html_file.write(df.select([str(vof.sum(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_sum.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"SUM({expr})", "float")


def var(expr: SQLExpression) -> StringSQL:
    """
    Evaluates the sample variance for each row of
    the group.

    Parameters
    ----------
    expr: SQLExpression
        Expression.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    First, let's import the VastFrame in order to
    create a dummy dataset.

    .. code-block:: python

        from vastorbit import VastFrame

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    We can now build a dummy dataset.

    .. code-block:: python

        df = VastFrame({"x": [2, -11, 7, 12]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df.select([str(vof.var(df["x"]))])

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [2, -11, 7, 12]})
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_analytic_var.html", "w")
        html_file.write(df.select([str(vof.var(df["x"]))])._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_analytic_var.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr = format_magic(expr)
    return StringSQL(f"VARIANCE({expr})", "float")


variance = var
