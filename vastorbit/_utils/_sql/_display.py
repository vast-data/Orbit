"""
SPDX-License-Identifier: Apache-2.0
"""

import shutil
from typing import Optional

import vastorbit._config.config as conf
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._format import clean_query, indent_vo_sql


def print_query(query: str, title: Optional[str] = None) -> None:
    """
    Displays the input query.

    Parameters
    ----------
    query: str
        SQL Query.
    title: str, optional
        Query title.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._display import print_query

        # Generating a query.
        query = "SELECT col1, SUM(col2) FROM my_table GROUP BY 1;"

        # Function example.
        print_query(
            query,
            title = "Computing the sum of col2 by col1.",
        )

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    screen_columns = shutil.get_terminal_size().columns
    query_print = clean_query(query)
    query_print = indent_vo_sql(query)
    if conf.get_import_success("IPython") and not(conf.get_option("theme") == "sphinx"):
        print_message(f"<h4>{title}</h4>", "display")
        query_print = query_print.replace("\n", " <br>").replace("  ", " &emsp; ")
        print_message(query_print, "display")
    else:
        print_message(f"$ {title} $\n")
        print_message(query_print)
        print_message("-" * int(screen_columns) + "\n")


def print_time(elapsed_time: float) -> None:
    """
    Displays the input time.

    Parameters
    ----------
    elapsed_time: float
        Query Elapsed Time.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._display import elapsed_time

        # Function example.
        elapsed_time(4.12789)

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    screen_columns = shutil.get_terminal_size().columns
    if conf.get_import_success("IPython"):
        print_message(
            f"<div><b>Execution: </b> {round(elapsed_time, 3)}s</div>", "display"
        )
    else:
        print_message(f"Execution: {round(elapsed_time, 3)}s")
        print_message("-" * int(screen_columns) + "\n")
