"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit._utils._sql._cast import to_dtype_category
from vastorbit._utils._sql._format import format_magic
from vastorbit._typing import SQLExpression


from vastorbit.core.string_sql.base import StringSQL


def case_when(*args) -> StringSQL:
    """
    Returns the conditional statement of the input
    arguments.

    Parameters
    ----------
    args: SQLExpression
        Infinite number of Expressions.
        The expression generated will look like:

        **even**:
                CASE ... WHEN args[2 * i]
                THEN args[2 * i + 1] ... END

        **odd** :
                CASE ... WHEN args[2 * i]
                THEN args[2 * i + 1] ...
                ELSE args[n] END

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

        df = VastFrame({"x": [0.8, -1, 0, -2, 0.5]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["x_pos"] = vof.case_when(
            df["x"] > 0, 1,
            df["x"] == 0, 0,
            -1,
        )
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [0.8, -1, 0, -2, 0.5]})
        df["x_pos"] = vof.case_when(df["x"] > 0, 1,
                                   df["x"] == 0, 0,
                                   -1)
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_conditional_case_when.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_conditional_case_when.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    n = len(args)
    if n < 2:
        raise ValueError(
            "The number of arguments of the 'case_when' function must be strictly greater than 1."
        )
    category = to_dtype_category(args[1])
    i = 0
    expr = "CASE"
    while i < n:
        if i + 1 == n:
            expr += " ELSE " + str(format_magic(args[i]))
            i += 1
        else:
            expr += (
                " WHEN "
                + str(format_magic(args[i]))
                + " THEN "
                + str(format_magic(args[i + 1]))
            )
            i += 2
    expr += " END"
    return StringSQL(expr, category)


def decode(expr: SQLExpression, *args) -> StringSQL:
    """
    Compares the expressions to each search value.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    args: SQLExpression
        Infinite number of Expressions.
        The expression generated will look like:

        **even**:
                CASE ... WHEN expr = args[2 * i]
                THEN args[2 * i + 1] ... END

        **odd**:
                CASE ... WHEN expr = args[2 * i]
                THEN args[2 * i + 1] ...
                ELSE args[n] END

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

        df = VastFrame({"x": ['banana', 'apple', 'onion', 'potato']})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["type_x"] = vof.decode(
            df["x"],
            'banana', 'fruit',
            'apple', 'fruit',
            'vegetable',
        )
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ['banana', 'apple', 'onion', 'potato']})
        df["type_x"] = vof.decode(df["x"],
                        'banana', 'fruit',
                        'apple', 'fruit',
                        'vegetable')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_conditional_decode.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_conditional_decode.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    n = len(args)
    if n < 2:
        raise ValueError(
            "The number of arguments of the 'decode' function must be greater than 3."
        )
    category = to_dtype_category(args[1])
    if n % 2 == 1:
        decode_else = f"ELSE {str(format_magic(args[-1]))}"
        L = args[0:-1]
    else:
        decode_else = ""
        L = args
    expr = f"(CASE {str(format_magic(expr))} "
    for i in range(0, len(L), 2):
        expr += f"WHEN {str(format_magic(L[i]))} THEN {str(format_magic(L[i+1]))} "
    expr += f"{decode_else} END)"
    return StringSQL(expr, category)
