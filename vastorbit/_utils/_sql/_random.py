"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

import vastorbit._config.config as conf
from vastorbit._utils._sql._vast_version import vast_version


def _seeded_random_function(random_seed: int) -> str:
    """
    Returns the text of an appropriate seeded
    random function based on the version of
    the connected VAST server.

    Parameters
    ----------
    random_seed: int
        Integer used to generate the seed.

    Returns
    -------
    str
        Representation of the seeded
        random function.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._random import _seeded_random_function

        # function example
        _seeded_random_function(666)

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """

    return f"""
        (ABS(FROM_BIG_ENDIAN_64(XXHASH64(
            TO_UTF8(CONCAT(
                CAST(ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS VARCHAR),
                '|{random_seed}'
            ))
        ))) % 100) / 100.0
    """


def _current_random(rand_int: Optional[int] = None) -> str:
    """
    Returns the 'random' function to be
    used in the query. The returned
    function depends on the input
    parameter ``rand_int`` and whether
    the random state has been changed.

    Parameters
    ----------
    rand_int: int
        Integer used to generate the
        random function.

    Returns
    -------
    str
        Representation of the random
        function.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._sql._random import _current_random

        # function example
        _current_random(666)

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    random_state = conf.get_option("random_state")
    if isinstance(rand_int, int):
        if isinstance(random_state, int):
            seeded_function = _seeded_random_function(random_state)
            random_func = f"FLOOR({rand_int} * {seeded_function})"
        else:
            random_func = f"RANDOM({rand_int})"
    else:
        if isinstance(random_state, int):
            random_func = _seeded_random_function(random_state)
        else:
            random_func = "RANDOM()"
    return random_func
