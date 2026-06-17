"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from vastorbit._typing import SQLExpression
from vastorbit._utils._sql._format import format_magic

from vastorbit.core.string_sql.base import StringSQL


def length(expr: SQLExpression) -> StringSQL:
    """
    Returns the length of a string.

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

        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["length_x"] = vof.length(df["x"])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})
        df["length_x"] = vof.length(df["x"])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_length.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_length.html

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
    return StringSQL(f"LENGTH({expr})", "int")


def lower(expr: SQLExpression) -> StringSQL:
    """
    Returns  a VARCHAR value containing  the
    argument converted to lowercase letters.

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

        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["lower_x"] = vof.lower(df["x"])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})
        df["lower_x"] = vof.lower(df["x"])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_lower.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_lower.html

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
    return StringSQL(f"LOWER({expr})", "text")


def substr(
    expr: SQLExpression, position: int, extent: Optional[int] = None
) -> StringSQL:
    """
    Returns   VARCHAR  or  VARBINARY  value
    representing a substring of a specified
    string.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    position: int
        Starting position of the substring.
    extent: int, optional
        Length of the substring to extract.

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

        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["substr_x"] = vof.substr(df["x"], 1, 1)
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})
        df["substr_x"] = vof.substr(df["x"], 1, 1)
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_substr.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_substr.html

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
    if extent:
        position = f"{position}, {extent}"
    return StringSQL(f"SUBSTR({expr}, {position})", "text")


def upper(expr: SQLExpression) -> StringSQL:
    """
    Returns  a VARCHAR value containing  the
    argument converted to uppercase letters.

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

        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["upper_x"] = vof.upper(df["x"])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["Badr", "Colin", "Fouad", "Arash"]})
        df["upper_x"] = vof.upper(df["x"])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_upper.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_upper.html

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
    return StringSQL(f"UPPER({expr})", "text")


# Edit Distance & Soundex


def edit_distance(
    expr1: SQLExpression,
    expr2: SQLExpression,
) -> StringSQL:
    """
    Calculates and returns the Levenshtein
    distance  between two  strings.

    Parameters
    ----------
    expr1: SQLExpression
        Expression.
    expr2: SQLExpression
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

        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["edit_distance_x"] = vof.edit_distance(df["x"], 'heyllow')
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})
        df["edit_distance_x"] = vof.edit_distance(df["x"], 'heyllow')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_edit_distance.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_edit_distance.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr1 = format_magic(expr1)
    expr2 = format_magic(expr2)
    return StringSQL(f"LEVENSHTEIN_DISTANCE({expr1}, {expr2})", "int")


levenshtein = edit_distance


def soundex(expr: SQLExpression) -> StringSQL:
    """
    Returns Soundex encoding of a varchar
    strings  as a four character  string.

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

        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["soundex_x"] = vof.soundex(df["x"])
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})
        df["soundex_x"] = vof.soundex(df["x"])
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_soundex.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_soundex.html

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
    return StringSQL(f"SOUNDEX({expr})", "varchar")


def soundex_matches(
    expr1: SQLExpression,
    expr2: SQLExpression,
) -> StringSQL:
    """
    Generates and compares Soundex encodings of
    two  strings,  and  returns a count of  the
    matching characters  (ranging from 0 for no
    match to 4 for an exact match).

    Parameters
    ----------
    expr1: SQLExpression
        Expression.
    expr2: SQLExpression
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

        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["soundex_matches_x"] = vof.soundex_matches(df["x"], 'heyllow')
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})
        df["soundex_matches_x"] = vof.soundex_matches(df["x"], 'heyllow')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_soundex_matches.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_soundex_matches.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr1 = format_magic(expr1)
    expr2 = format_magic(expr2)
    return StringSQL(f"SOUNDEX({expr1}) = SOUNDEX({expr2}))", "int")


# Hamming


def hamming_distance(
    expr1: SQLExpression,
    expr2: SQLExpression,
) -> StringSQL:
    """
    Calculates and returns the Hamming
    distance between two strings.

    Parameters
    ----------
    expr1: SQLExpression
        Expression.
    expr2: SQLExpression
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

        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})

    Now, let's go ahead and apply the function.

    .. code-block:: python

        df["hamming_distance_x"] = vof.hamming_distance(df["x"], 'heyllow')
        display(df)

    .. ipython:: python
        :suppress:

        from vastorbit import VastFrame
        import vastorbit.sql.functions as vof
        df = VastFrame({"x": ["hello", "apple", "heroes", "allo"]})
        df["hamming_distance_x"] = vof.hamming_distance(df["x"], 'heyllow')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_string_hamming_distance.html", "w")
        html_file.write(df._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_string_hamming_distance.html

    .. note::

        It's crucial to utilize vastorbit SQL functions in coding, as
        they can be updated over time with new syntax. While SQL
        functions typically remain stable, they may vary across platforms
        or versions. vastorbit effectively manages these changes, a task
        not achievable with pure SQL.

    .. seealso::

        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates the expression.
    """
    expr1 = format_magic(expr1)
    expr2 = format_magic(expr2)
    return StringSQL(f"HAMMING_DISTANCE({expr1}, {expr2})", "float")
