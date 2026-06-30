"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit._typing import SQLExpression
from vastorbit._utils._sql._format import format_magic

from vastorbit.core.string_sql.base import StringSQL


def regexp_count(
    expr: SQLExpression,
    pattern: SQLExpression,
    position: int = 1,
) -> StringSQL:
    """
    Returns the number of times a regular expression
    matches a string.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    pattern: SQLExpression
        The regular expression to search for within
        the string.
    position: int, optional
        The number of characters from the start  of
        the  string where the function should start
        searching for matches.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    For this example, we will use the Titanic dataset.

    .. code-block:: python

        from vastorbit.datasets import load_titanic

        titanic = load_titanic()

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

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    Now, let's go ahead and apply the function.

    .. code-block:: python

        titanic["has_title"] = vof.regexp_count(
            titanic["name"],
            r'([A-Za-z])+\\.',
        )
        display(titanic[["name", "has_title"]])

    .. ipython:: python
        :suppress:
        :okwarning:

        from vastorbit.datasets import load_titanic
        import vastorbit.sql.functions as vof
        titanic = load_titanic()
        titanic["has_title"] = vof.regexp_count(titanic["name"], r'([A-Za-z])+\\.')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_count.html", "w")
        html_file.write(titanic[["name", "has_title"]]._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_count.html

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
    pattern = format_magic(pattern)
    src = f"SUBSTR({expr}, {position})" if position != 1 else expr
    return StringSQL(f"REGEXP_COUNT({src}, {pattern})", "int")


def regexp_ilike(expr: SQLExpression, pattern: SQLExpression) -> StringSQL:
    """
    Returns true if the string contains a match for
    the regular expression.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    pattern: SQLExpression
        A  string containing the regular expression
        to match against the string.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    For this example, we will use the Titanic dataset.

    .. code-block:: python

        from vastorbit.datasets import load_titanic

        titanic = load_titanic()

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

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    Now, let's go ahead and apply the function.

    .. code-block:: python

        titanic["has_title"] = vof.regexp_ilike(
            titanic["name"],
            r'([A-Za-z])+\\.',
        )
        display(titanic[["name", "has_title"]])

    .. ipython:: python
        :suppress:
        :okwarning:

        from vastorbit.datasets import load_titanic
        import vastorbit.sql.functions as vof
        titanic = load_titanic()
        titanic["has_title"] = vof.regexp_ilike(titanic["name"], r'([A-Za-z])+\\.')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_ilike.html", "w")
        html_file.write(titanic[["name", "has_title"]]._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_ilike.html

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
    pattern = format_magic(pattern)
    return StringSQL(f"REGEXP_LIKE({expr}, '(?i)' || {pattern})", "bool")


def regexp_instr(
    expr: SQLExpression,
    pattern: SQLExpression,
    position: int = 1,
    occurrence: int = 1,
    return_position: int = 0,
) -> StringSQL:
    """
    Returns the  starting or  ending position  in a
    string  where  a  regular  expression  matches.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    pattern: SQLExpression
        The regular  expression to search for within
        the string.
    position: int, optional
        The number  of characters from the start  of
        the string where the  function should  start
        searching for matches.
    occurrence: int, optional
        Controls which occurrence of a pattern match
        in the string to return.
    return_position: int, optional
        Sets  the  position  within  the  string  to
        return.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    For this example, we will use the Titanic dataset.

    .. code-block:: python

        from vastorbit.datasets import load_titanic

        titanic = load_titanic()

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

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    Now, let's go ahead and apply the function.

    .. code-block:: python

        titanic["title_start"] = vof.regexp_instr(
            titanic["name"],
            r'([A-Za-z])+\\.',
            return_position = 0,
        )
        display(titanic[["name", "title_start"]])

    .. ipython:: python
        :suppress:
        :okwarning:

        from vastorbit.datasets import load_titanic
        import vastorbit.sql.functions as vof
        titanic = load_titanic()
        titanic["title_start"] = vof.regexp_instr(titanic["name"], r'([A-Za-z])+\\.', return_position = 0)
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_instr.html", "w")
        html_file.write(titanic[["name", "title_start"]]._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_instr.html

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
    pattern = format_magic(pattern)
    pos = f"REGEXP_POSITION({expr}, {pattern}, {position}, {occurrence})"
    if return_position == 0:
        return StringSQL(f"(CASE WHEN {pos} = -1 THEN 0 ELSE {pos} END)", "int")
    # return_position = 1 -> position just past the end of the match
    matched = f"REGEXP_EXTRACT({expr}, {pattern})"
    return StringSQL(
        f"(CASE WHEN {pos} = -1 THEN 0 ELSE {pos} + LENGTH({matched}) END)", "int"
    )


def regexp_like(expr: SQLExpression, pattern: SQLExpression) -> StringSQL:
    """
    Returns true if the string matches the regular
    expression.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    pattern: SQLExpression
        A string containing the regular expression
        to match against the string.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    For this example, we will use the Titanic dataset.

    .. code-block:: python

        from vastorbit.datasets import load_titanic

        titanic = load_titanic()

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

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    Now, let's go ahead and apply the function.

    .. code-block:: python

        titanic["has_title"] = vof.regexp_like(
            titanic["name"],
            r'([A-Za-z])+\\.',
        )
        display(titanic[["name", "has_title"]])

    .. ipython:: python
        :suppress:
        :okwarning:

        from vastorbit.datasets import load_titanic
        import vastorbit.sql.functions as vof
        titanic = load_titanic()
        titanic["has_title"] = vof.regexp_like(titanic["name"], r'([A-Za-z])+\\.')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_like.html", "w")
        html_file.write(titanic[["name", "has_title"]]._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_like.html

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
    pattern = format_magic(pattern)
    return StringSQL(f"REGEXP_LIKE({expr}, {pattern})", "bool")


def regexp_replace(
    expr: SQLExpression,
    target: SQLExpression,
    replacement: SQLExpression,
    position: int = 1,
    occurrence: int = 1,
) -> StringSQL:
    """
    Replace all occurrences of a substring that  match
    a  regular   expression  with  another  substring.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    target: SQLExpression
        The  regular  expression to search for  within
        the string.
    replacement: SQLExpression
        The string to replace matched substrings.
    position: int, optional
        The number of characters from the start of the
        string   where  the   function  should   start
        searching for matches.
    occurrence: int, optional
        Controls  which occurrence of a pattern  match
        in the string to return.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    For this example, we will use the Titanic dataset.

    .. code-block:: python

        from vastorbit.datasets import load_titanic

        titanic = load_titanic()

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

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    Now, let's go ahead and apply the function.

    .. code-block:: python

        titanic["new_title"] = vof.regexp_replace(
            titanic["name"],
            r'([A-Za-z])+\\.',
            '[title here] ',
        )
        display(titanic[["name", "new_title"]])

    .. ipython:: python
        :suppress:
        :okwarning:

        from vastorbit.datasets import load_titanic
        import vastorbit.sql.functions as vof
        titanic = load_titanic()
        titanic["new_title"] = vof.regexp_replace(titanic["name"], r'([A-Za-z])+\\.', '[title here] ')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_replace.html", "w")
        html_file.write(titanic[["name", "new_title"]]._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_replace.html

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
    target = format_magic(target)
    replacement = format_magic(replacement)
    if occurrence != 1:
        raise NotImplementedError(
            "Trino's REGEXP_REPLACE replaces all matches and cannot target a "
            "single occurrence; 'occurrence' other than 1 is not supported."
        )
    if position != 1:
        # Replace only within the tail starting at `position`, keeping the
        # untouched prefix intact.
        prefix = f"SUBSTR({expr}, 1, {position} - 1)"
        tail = f"REGEXP_REPLACE(SUBSTR({expr}, {position}), {target}, {replacement})"
        return StringSQL(f"CONCAT({prefix}, {tail})")
    return StringSQL(f"REGEXP_REPLACE({expr}, {target}, {replacement})")


def regexp_extract(
    expr: SQLExpression, pattern: SQLExpression, position: int = 1, occurrence: int = 1
) -> StringSQL:
    """
    Returns the  substring  that matches a regular
    expression within a string.

    Parameters
    ----------
    expr: SQLExpression
        Expression.
    pattern: SQLExpression
        The regular expression to find a substring
        to extract.
    position: int, optional
        The number of characters from the start of
        the string where the function should start
        searching for matches.
    occurrence: int, optional
        Controls  which  occurrence  of a  pattern
        match in the string to return.

    Returns
    -------
    StringSQL
        SQL string.

    Examples
    --------
    For this example, we will use the Titanic dataset.

    .. code-block:: python

        from vastorbit.datasets import load_titanic

        titanic = load_titanic()

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

    Now, let's import the vastorbit SQL functions.

    .. code-block:: python

        import vastorbit.sql.functions as vof

    Now, let's go ahead and apply the function.

    .. code-block:: python

        titanic["title"] = vof.regexp_extract(
            titanic["name"],
            r'([A-Za-z])+\\.',
        )
        display(titanic[["name", "title"]])

    .. ipython:: python
        :suppress:
        :okwarning:

        from vastorbit.datasets import load_titanic
        import vastorbit.sql.functions as vof
        titanic = load_titanic()
        titanic["title"] = vof.regexp_extract(titanic["name"], r'([A-Za-z])+\\.')
        html_file = open("SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_extract.html", "w")
        html_file.write(titanic[["name", "title"]]._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_functions_regexp_regexp_extract.html

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
    pattern = format_magic(pattern)
    src = f"SUBSTR({expr}, {position})" if position != 1 else expr
    if occurrence == 1:
        return StringSQL(f"REGEXP_EXTRACT({src}, {pattern})")
    return StringSQL(f"ELEMENT_AT(REGEXP_EXTRACT_ALL({src}, {pattern}), {occurrence})")
