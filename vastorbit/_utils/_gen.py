"""
SPDX-License-Identifier: Apache-2.0
"""

import uuid
import secrets
import string
from typing import Optional

from vastorbit._utils._sql._format import quote_ident

from vastorbit.connection.connect import current_cursor


def gen_name(L: list) -> str:
    """
    Generates a name using the input ``list``.

    Parameters
    ----------
    L: list
        List of elements to use in the
        generated name.

    Returns
    -------
    str
        generated name.

    Examples
    --------
    The following code demonstrates the
    usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._gen import gen_name

        # only strs
        gen_name(['How', 'are', 'you'])

        # different data types
        gen_name(['A', None, 666])

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    return "_".join(
        [
            "".join(ch for ch in str(elem).lower() if ch.isalnum() or ch == "_")
            for elem in L
        ]
    )


def gen_col_name(n: int = 5) -> str:
    """
    Generate a name using ``n`` characters.

    Parameters
    ----------
    n: int, optional
        Number of characters.

    Returns
    -------
    str
        generated name.

    Examples
    --------
    The following code demonstrates the
    usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._gen import gen_col_name

        # n = 10
        gen_col_name(n = 10)

        # n = 20
        gen_col_name(n = 10)

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    return "".join(secrets.choice(string.ascii_letters) for _ in range(n)).lower()


def gen_tmp_name(schema: Optional[str] = None, name: Optional[str] = None) -> str:
    """
    Generates a temporary name using the
    input ``schema`` and name``.

    Parameters
    ----------
    schema: str, optional
        Schema name.
    name: str, optional
        Relation name.

    Returns
    -------
    str
        generated name.

    Examples
    --------
    The following code demonstrates the
    usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._gen import gen_tmp_name

        # only name
        gen_tmp_name(name = 'tmp_name')

        # name and schema
        gen_tmp_name(
            schema = 'my_schema',
            name = 'tmp_name',
        )

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    cursor = current_cursor()
    cursor.execute("SELECT CURRENT_CATALOG, CURRENT_USER")
    current_catalog, username = cursor.fetchone()
    session_user = f"{current_catalog}_{username}"
    L = session_user.split("_")
    L[0] = "".join(filter(str.isalnum, L[0]))
    L[1] = "".join(filter(str.isalnum, L[1]))
    universal_unique_id = str(uuid.uuid1()).replace("-", "")
    name = f'"_vastorbit_tmp_{name.lower()}_{L[0]}_{L[1]}_{universal_unique_id}_"'
    if schema:
        name = f"{quote_ident(schema)}.{name}"
    return name
