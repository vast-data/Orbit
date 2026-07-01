"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastColumn, VastFrame
    import vastorbit.machine_learning.vast as vml


def create_new_vdc(*args, **kwargs) -> "VastColumn":
    """
    Creates a :py:class:`~VastColumn`.

    .. note::

        This function is used to bring main features
        across different files and avoid import errors.
        It is the only file where we use imports inside
        the function. For more information about the object,
        please refer to the link above.
    """
    from vastorbit.core.vastframe.base import VastColumn

    return VastColumn(*args, **kwargs)


def create_new_vdf(*args, **kwargs) -> "VastFrame":
    """
    Creates a :py:class:`~VastFrame`.

    .. note::

        This function is used to bring main features
        across different files and avoid import errors.
        It is the only file where we use imports inside
        the function. For more information about the object,
        please refer to the link above.
    """
    from vastorbit.core.vastframe.base import VastFrame

    return VastFrame(*args, **kwargs)


def get_VAST_mllib() -> Literal["vml"]:
    """
    Gets the VAST machine learning module:
    :py:mod:`vastorbit.machine_learning.vast`.

    .. note::

        This function is used to bring main features
        across different files and avoid import errors.
        It is the only file where we use imports inside
        the function. For more information about the object,
        please refer to the link above.
    """
    import vastorbit.machine_learning.vast as vml

    return vml


def read_pd(*args, **kwargs) -> "VastFrame":
    """
    Reads a pandas DataFrame into a vastorbit
    VastFrame. It uses the
    :py:func:`~vastorbit.pandas.read_pandas`
    function.

    .. note::

        This function is used to bring main features
        across different files and avoid import errors.
        It is the only file where we use imports inside
        the function. For more information about the object,
        please refer to the link above.
    """
    from vastorbit.core.parsers.pandas import read_pandas

    return read_pandas(*args, **kwargs)
