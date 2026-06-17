"""
SPDX-License-Identifier: Apache-2.0
"""

from functools import wraps
from typing import Any, Callable, Optional

from vastorbit._utils._sql._format import format_type
from vastorbit.connection.connect import current_cursor
from vastorbit.errors import VersionError


def vast_version(condition: Optional[list] = None) -> tuple[int, int, int, int]:
    """
    Returns the VAST Version.

    Parameters
    ----------
    condition: list, optional
        List of the minimal version
        information. If the current
        version is not greater or
        equal to this version, the
        function raises an error.

    Returns
    -------
    tuple
        List containing the version
        information.
        ``(MAJOR, MINOR, PATCH, POST)``

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._vast_version import vast_version

        # Function Example.
        vast_version()

    .. note::

        Utilize the condition parameter if you want
        to raise an error when the condition is not
        met. The following code will raise an error
        if the VAST version is less than 23.3.

        .. code-block:: python

            vast_version(condition = (23, 3, 0))

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    condition = format_type(condition, dtype=list)
    if len(condition) > 0:
        condition = condition + [0 for elem in range(4 - len(condition))]
    current_version = int(
        current_cursor()
        .execute("SELECT /*+LABEL('_version')*/ version()")
        .fetchone()[0]
    )
    res = [current_version, 0, 0]
    if condition:
        if condition[0] < res[0]:
            test = True
        elif condition[0] == res[0]:
            if condition[1] < res[1]:
                test = True
            elif condition[1] == res[1]:
                if condition[2] <= res[2]:
                    test = True
                else:
                    test = False
            else:
                test = False
        else:
            test = False
        if not test:
            v0, v1, v2 = res[0], res[1], str(res[2]).split("-", maxsplit=1)[0]
            v = ".".join([str(c) for c in condition[:3]])
            raise VersionError(
                (
                    "This Function is not available for VAST version "
                    f"{v0}.{v1}.{v2}.\nPlease upgrade your VAST "
                    f"version to at least {v} to get this functionality."
                )
            )
    return tuple(res)
