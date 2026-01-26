"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit._typing import SQLExpression
from vastorbit._utils._sql._cast import to_dtype_category
from vastorbit._utils._sql._format import format_magic

from vastorbit.core.string_sql.base import StringSQL


def coalesce(expr: SQLExpression, *args) -> StringSQL:
    """
    Returns the value of the first non-null
    expression in the list.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    args: SQLExpression
        A number of expressions.

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

        df = VastFrame({"x": [0.8, -1, None, -2, None]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["coalesce_x"] = vof.coalesce(df["x"], 777)
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [0.8, -1, None, -2, None]})
        df["coalesce_x"] = vof.coalesce(df["x"], 777)
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_null_handling_coalesce.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_null_handling_coalesce.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    category = to_dtype_category(expr)
    expr = [format_magic(expr)]
    for arg in args:
        expr += [format_magic(arg)]
    expr = ", ".join([str(elem) for elem in expr])
    return StringSQL(f"COALESCE({expr})", category)


def nullifzero(expr: SQLExpression) -> StringSQL:
    """
    Evaluates to NULL if the value in the
    expression is 0.

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

        df = VastFrame({"x": [0, 0, 0.7, 15]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["nullifzero_x"] = vof.nullifzero(df["x"])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [0, 0, 0.7, 15]})
        df["nullifzero_x"] = vof.nullifzero(df["x"])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_null_handling_nullifzero.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_null_handling_nullifzero.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr, cat = format_magic(expr, True)
    return StringSQL(f"NULLIF({expr}, 0)", cat)


def zeroifnull(expr: SQLExpression) -> StringSQL:
    """
    Evaluates to 0 if the expression is NULL.

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

        df = VastFrame({"x": [0, None, 0.7, None]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["zeroifnull_x"] = vof.zeroifnull(df["x"])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [0, None, 0.7, None]})
        df["zeroifnull_x"] = vof.zeroifnull(df["x"])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_null_handling_zeroifnull.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_null_handling_zeroifnull.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr, cat = format_magic(expr, True)
    return StringSQL(f"COALESCE({expr}, 0)", cat)
