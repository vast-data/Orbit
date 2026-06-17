"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.core.string_sql.base import StringSQL


def random() -> StringSQL:
    """
    Returns a Random Number.

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

        df = VastFrame({"x": [1, 2, 3, 4]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["split"] = vof.random()
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, 2, 3, 4]})
        df["split"] = vof.random()
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_random_random.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_random_random.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    return StringSQL("RANDOM()", "float")


def randomint(n: int) -> StringSQL:
    """
    Returns a Random Number from 0 through n - 1.

    Parameters
    ----------
    n: int
        Integer Value.

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

        df = VastFrame({"x": [1, 2, 3, 4]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["split"] = vof.randomint(10)
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, 2, 3, 4]})
        df["split"] = vof.randomint(10)
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_random_randomint.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_random_randomint.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    return StringSQL(f"RANDOM({n})", "int")


def seeded_random(random_state: int) -> StringSQL:
    """
    Returns a Seeded Random Number using the input
    random state.

    Parameters
    ----------
    random_state: int
        Integer used to seed the randomness.

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

        df = VastFrame({"x": [1, 2, 3, 4]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["split"] = vof.seeded_random(10)
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": [1, 2, 3, 4]})
        df["split"] = vof.seeded_random(10)
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_random_seeded_random.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_random_seeded_random.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    return StringSQL(
        f"""
        (ABS(FROM_BIG_ENDIAN_64(XXHASH64(
            TO_UTF8(CONCAT(
                CAST(ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS VARCHAR),
                '|{random_state}'
            ))
        ))) % 100) / 100.0
    """,
        "float",
    )
