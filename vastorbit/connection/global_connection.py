"""
SPDX-License-Identifier: Apache-2.0
"""

import uuid
from typing import Optional, Any

from vastorbit import __version__

VASTORBIT_AUTO_CONNECTION: str = "VASTORBIT_AUTO_CONNECTION"
VASTORBIT_SESSION_IDENTIFIER: str = str(uuid.uuid1()).replace("-", "")
VASTORBIT_SESSION_LABEL: str = f"vastorbit-{__version__}-{VASTORBIT_SESSION_IDENTIFIER}"


class GlobalConnection:
    """
    Main Class to store the
    Global Connection used
    by all vastorbit objects.
    """

    # Properties.

    @property
    def vo_auto_connection(self) -> str:
        return VASTORBIT_AUTO_CONNECTION

    @property
    def vo_session_identifier(self) -> str:
        return VASTORBIT_SESSION_IDENTIFIER

    @property
    def vo_session_label(self) -> str:
        return VASTORBIT_SESSION_LABEL

    # System Methods.

    def __init__(self) -> None:
        self._connection = {
            "conn": None,
            "section": None,
            "dsn": None,
        }

    # Main Methods.

    def get_connection(self) -> Optional[Any]:
        """
        Returns the current connection.

        Examples
        --------
        The following code demonstrates
        the usage of the function.

        .. ipython:: python

            # Import the Global Connection.
            from vastorbit.connection.global_connection import get_global_connection

            # Example
            get_global_connection().get_connection()

        .. note::

            These functions serve as utilities to
            construct others, simplifying the overall
            code.
        """
        return self._connection["conn"]

    def get_dsn(self) -> Optional[str]:
        """
        Returns the current dsn.

        Examples
        --------
        The following code demonstrates
        the usage of the function.

        .. ipython:: python

            # Import the Global Connection.
            from vastorbit.connection.global_connection import get_global_connection

            # Example
            get_global_connection().get_dsn()

        .. note::

            These functions serve as utilities to
            construct others, simplifying the overall
            code.
        """
        return self._connection["dsn"]

    def get_dsn_section(self) -> Optional[str]:
        """
        Returns the current dsn section.

        Examples
        --------
        The following code demonstrates
        the usage of the function.

        .. ipython:: python

            # Import the Global Connection.
            from vastorbit.connection.global_connection import get_global_connection

            # Example
            get_global_connection().get_dsn_section()

        .. note::

            These functions serve as utilities to
            construct others, simplifying the overall
            code.
        """
        return self._connection["section"]

    def set_connection(
        self,
        conn: Any,
        section: Optional[str] = None,
        dsn: Optional[str] = None,
    ) -> None:
        """
        Sets the current connection.

        Examples
        --------
        The following code demonstrates
        the usage of the function.

        .. code-block:: python

            # Import the Global Connection.
            from vastorbit.connection.global_connection import get_global_connection

            # Import the VAST connection function
            from vastorbit.connection import vast_connection

            # Building a connection
            conn = vast_connection("VASTDSN")

            # Example
            get_global_connection().set_connection(conn)

        .. note::

            These functions serve as utilities to
            construct others, simplifying the overall
            code.
        """
        self._connection["conn"] = conn
        self._connection["section"] = section
        self._connection["dsn"] = dsn


_global_connection: GlobalConnection = GlobalConnection()


def get_global_connection() -> GlobalConnection:
    """
    Returns the Global connection.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit.connection.global_connection import get_global_connection

        # Example
        get_global_connection()

    .. note::

        These functions serve as utilities to
        construct others, simplifying the overall
        code.
    """
    return _global_connection
