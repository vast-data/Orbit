"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional, Any

try:
    import trino
except ImportError:
    trino = None

from vastorbit._utils._print import print_message

from vastorbit.connection.errors import ConnectionError, OAuthTokenRefreshError
from vastorbit.connection.global_connection import (
    get_global_connection,
    GlobalConnection,
)
from vastorbit.connection.read import read_dsn
from vastorbit.connection.utils import get_confparser, get_connection_file
from vastorbit.connection.write import new_connection
from vastorbit.connection.oauth_manager import OAuthManager

"""
Connecting to the DB.
"""


def auto_connect() -> None:
    """
    Automatically creates
    a connection using the
    auto-connection.

    Examples
    --------
    Connects using an existing
    auto-connection:

    .. code-block:: python

        from vastorbit.connection import auto_connect

        auto_connect()

    .. seealso::

        | :py:func:`~vastorbit.connection.available_connections` :
            Displays all available connections.
    """
    gb_conn = get_global_connection()
    confparser = get_confparser()

    if confparser.has_section(gb_conn.vo_auto_connection):
        section = confparser.get(gb_conn.vo_auto_connection, "name")
    else:
        raise ConnectionError(
            "No Auto Connection available. You can create one using "
            "the 'new_connection' function or set manually a connection"
            " using the 'set_connection' function."
        )
    connect(section)


read_auto_connect = auto_connect


def connect(section: str, dsn: Optional[str] = None) -> None:
    """
    Connects to the database.

    Parameters
    ----------
    section: str
        Name of the section in the
        configuration file.
    dsn: str, optional
        Path to the file containing
        the credentials. If empty,
        the Connection File will be
        used.

    Examples
    --------
    Display all available connections:

    .. code-block:: python

        from vastorbit.connection import available_connections

        available_connections()

    ``['VML', 'VASTDSN', 'VASTDSN_test']``

    Connect using the VASTDSN connection:

    .. code-block:: python

        from vastorbit.connection import connect

        connect("VASTDSN")

    .. seealso::

        | :py:func:`~vastorbit.connection.available_connections` :
            Displays all available connections.
        | :py:func:`~vastorbit.connection.get_connection_file` :
            Gets the vastorbit connection file.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    gb_conn = get_global_connection()
    prev_conn = gb_conn.get_connection()
    if not dsn:
        dsn = get_connection_file()
    if prev_conn and not _is_connection_closed(prev_conn):
        _close_connection_safe(prev_conn)

    try:
        connection_config = read_dsn(section, dsn)
        # if the user has provided a refresh token, do token refresh, update the config's oauth access token
        if connection_config.get("oauth_refresh_token", False):
            oauth_manager = OAuthManager(connection_config["oauth_refresh_token"])
            oauth_config = connection_config.get("oauth_config", {})
            oauth_manager.set_config(oauth_config)
            connection_config["oauth_access_token"] = oauth_manager.do_token_refresh()
            gb_conn.set_connection(
                vast_connection(section=None, dsn=None, config=connection_config)
            )
        else:
            gb_conn.set_connection(
                vast_connection(section, dsn, config=None), section, dsn
            )
        print_message("Connected Successfully!")
    except OAuthTokenRefreshError as error:
        print_message(
            "Access Denied: Your authentication credentials are incorrect or have expired. Please retry"
        )
        new_connection(
            conn_info=read_dsn(section, dsn), prompt=True, connect_attempt=False
        )
        try:
            gb_conn.set_connection(
                vast_connection(section, dsn, config=None), section, dsn
            )
            print_message("Connected Successfully!")
        except OAuthTokenRefreshError as error:
            print_message("Error persists:")
            raise error
    except ConnectionError as error:
        print_message(
            "A connection error occurred. Common reasons may be an invalid host, port, or, if requiring "
            "OAuth and token refresh, this may be due to an incorrect or malformed token url."
        )
        raise error
    except Exception as e:
        if "The DSN Section" in str(e) or "doesn't exist" in str(e):
            raise ConnectionError(
                f"The connection '{section}' does not exist. To create "
                "a new connection, you use the 'new_connection' "
                "function with your credentials: {'catalog': ..., "
                "'host': ..., 'user': ...}.\n"
                "To view available connections, use the "
                "the 'available_connections' function."
            )
        raise e


def set_connection(conn: Any) -> None:
    """
    Saves a custom connection to the
    vastorbit object. This allows you
    to specify, for example, a custom
    Trino connection. This should not be
    confused with a native vastorbit
    connection created by the
    :py:func:`~vastorbit.connection.new_connection`
    function.

    Examples
    --------
    Create a connection using the
    Trino Python client:

    .. note::

        You can use any connector as long
        as it has both ``fetchone`` and
        ``fetchall`` methods (DBAPI 2.0 compliant).

    .. code-block:: python

        import trino

        conn = trino.dbapi.connect(
            host='10.211.55.14',
            port=8080,
            user='admin',
            catalog='vast',
            schema='default',
        )

    Set up the connector:

    .. warning::

        As this connector is used
        throughout the entire API,
        if it's closed, you'll need
        to create a new one. This is
        why, in some cases, it's better
        to use auto-connection, which
        automatically creates a new
        connection if the current one
        is closed.

    .. code-block:: python

        from vastorbit.connection import set_connection

        set_connection(conn)

    .. seealso::

        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        res = cursor.fetchone()[0]
        cursor.close()
        assert res == 1
    except Exception as e:
        raise ConnectionError(f"The input connector is not working properly.\n{e}")
    gb_conn = get_global_connection()
    gb_conn.set_connection(conn)


"""
Closing DB Connection.
"""


def close_connection() -> None:
    """
    Closes the connection
    to the database.

    Examples
    --------
    Close all current connections:

    .. warning::

        When you close the connection,
        your session will terminate and
        all temporary elements will be
        automatically dropped.

    .. code-block:: python

        from vastorbit.connection import close_connection

        close_connection()

    .. seealso::

        | :py:func:`~vastorbit.connection.current_connection` :
            Returns the current vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    gb_conn = get_global_connection()
    connection = gb_conn.get_connection()
    if connection and not _is_connection_closed(connection):
        _close_connection_safe(connection)


"""
Connections & Cursors Objects.
"""

# Global Connection.


def current_connection() -> Any:
    """
    Returns the current database
    connection. If the connection
    is closed, vastorbit attempts
    to reconnect with the existing
    connection.

    If the connection attempt fails,
    vastorbit attempts to reconnect
    using stored credentials.
    If this also fails, vastorbit
    attempts to connect using an
    auto connection. Otherwise,
    vastorbit attempts to connect
    to a VASTLab Environment.

    Examples
    --------
    Get the current vastorbit connection:

    .. code-block:: python

        from vastorbit.connection import current_connection

        conn = current_connection()
        conn

    ``<trino.dbapi.Connection object at 0x118c1f8d0>``

    After the connection is
    established, you can execute
    SQL queries directly:

    .. note::

        Please refer to your connector's
        API reference for a comprehensive
        list of its functionalities.

    .. code-block:: python

        conn.cursor().execute("SELECT version()").fetchone()

    ``['Trino version 450']``

    .. seealso::

        | :py:func:`~vastorbit.connection.current_cursor` :
            Returns the current vastorbit cursor.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    gb_conn = get_global_connection()
    conn = gb_conn.get_connection()
    dsn = gb_conn.get_dsn()
    section = gb_conn.get_dsn_section()

    # Look if the connection does not exist or is closed

    if not conn or _is_connection_closed(conn):
        # Connection using the existing credentials

        if (section) and (dsn):
            connect(section, dsn)

        else:
            try:
                # Connection using the Auto Connection

                auto_connect()

            except Exception as e:
                try:
                    # Connection to the VASTLab environment

                    conn = vastorbitlab_connection()
                    gb_conn.set_connection(conn)

                except:
                    raise e

    return gb_conn.get_connection()


def current_cursor() -> Any:
    """
    Returns the current
    database cursor.

    Examples
    --------
    Get the current cursor:

    .. code-block:: python

        from vastorbit.connection import current_cursor

        cur = current_cursor()
        cur

    ``<trino.dbapi.Cursor object at 0x11a7b4748>``

    Directly execute an SQL query:

    .. code-block:: python

        cur.execute("SELECT version()").fetchone()

    ``['Trino version 450']``

    .. seealso::

        | :py:func:`~vastorbit.connection.current_connection` :
            Returns the current vastorbit connection.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    return current_connection().cursor()


# Local Connection.


def vast_connection(
    section: Optional[str] = None,
    dsn: Optional[str] = None,
    config: Optional[dict] = None,
) -> Any:
    """
    Reads the input DSN and
    creates a VAST Database
    connection using Trino.

    Parameters
    ----------
    section: str, optional
        Name of the section in
        the configuration file.
    dsn: str, optional
        Path to the file containing
        the credentials. If empty,
        the ``vastorbit_CONNECTION``
        environment variable will
        be used.
    config: dict, optional
        Configuration object override
        used to create a connection.
        If specified, will ignore the
        section and dsn properties.

    Returns
    -------
    conn
        Database connection.

    Examples
    --------
    Create a connection using the input DSN:

    .. note::

        This example utilizes a Data
        Source Name (DSN) to establish
        the connection, which is stored
        in the file specified by the
        global variable ``vastorbit_CONNECTION``.
        However, if you prefer a customized
        file with a different location, you
        can specify the file path accordingly.

    .. code-block:: python

        from vastorbit.connection import vast_connection

        vast_connection("VASTDSN")

    ``<trino.dbapi.Connection object at 0x106526198>``

    .. seealso::

        | :py:func:`~vastorbit.connection.current_connection` :
            Returns the current vastorbit connection.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    if trino is None:
        raise ImportError(
            "The 'trino' package is required. Install it with: pip install trino"
        )

    connection_config = config if config else read_dsn(section, dsn)

    # Build Trino connection parameters
    trino_params = {
        "host": connection_config.get("host", "localhost"),
        "port": connection_config.get("port", 8080),
        "user": connection_config.get("user", "admin"),
        "catalog": connection_config.get("catalog", "vast"),
        "schema": connection_config.get("schema", "default"),
    }

    # Add optional parameters
    if connection_config.get("http_scheme"):
        trino_params["http_scheme"] = connection_config["http_scheme"]

    # Authentication
    if "password" in connection_config:
        trino_params["auth"] = trino.auth.BasicAuthentication(
            connection_config["user"], connection_config["password"]
        )

    # OAuth support
    if "oauth_access_token" in connection_config:
        trino_params["http_headers"] = {
            "Authorization": f"Bearer {connection_config['oauth_access_token']}"
        }

    return trino.dbapi.connect(**trino_params)


# vastorbit Lab Connection.


def vastorbitlab_connection() -> Any:
    """
    Returns the vastorbitLab
    connection, if possible.

    Returns
    -------
    conn
        Database connection.

    Examples
    --------
    Get the vastorbitLab connection:

    .. note::

        vastorbitLab is a Dockerized
        environment designed for
        seamlessly using vastorbit.
        This function returns the
        connection to the VAST
        instance within the lab,
        allowing for necessary
        environment customization.

    .. code-block:: python

        from vastorbit.connection import vastorbitlab_connection

        vastorbitlab_connection()

    ``<trino.dbapi.Connection object at 0x106526198>``

    .. seealso::

        | :py:func:`~vastorbit.connection.current_connection` :
            Returns the current vastorbit connection.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
        | :py:func:`~vastorbit.connection.vast_connection` :
            Reads the input DSN and creates a
            VAST Database connection.
    """
    if trino is None:
        raise ImportError(
            "The 'trino' package is required. Install it with: pip install trino"
        )

    conn_info = {
        "host": "VASTdb",
        "port": 8080,
        "user": "admin",
        "catalog": "vast",
        "schema": "default",
    }
    return trino.dbapi.connect(**conn_info)


# Helper functions for connection management


def _is_connection_closed(conn: Any) -> bool:
    """Check if a connection is closed."""
    try:
        # For Trino connections, try to execute a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return False
    except Exception:
        return True


def _close_connection_safe(conn: Any) -> None:
    """Safely close a connection."""
    try:
        if hasattr(conn, "close"):
            conn.close()
    except Exception:
        pass  # Ignore errors when closing
