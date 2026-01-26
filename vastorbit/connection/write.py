"""
SPDX-License-Identifier: Apache-2.0
"""

from getpass import getpass
from typing import Dict, Any

try:
    import trino
except ImportError:
    trino = None

try:
    from vastorbit._utils._print import print_message
except ImportError:

    def print_message(msg: str, level: str = "info") -> None:
        print(f"[{level.upper()}] {msg}")


from vastorbit.connection.errors import ConnectionError, OAuthTokenRefreshError
from vastorbit.connection.global_connection import get_global_connection
from vastorbit.connection.oauth_manager import OAuthManager
from vastorbit.connection.read import read_dsn
from vastorbit.connection.utils import get_confparser, get_connection_file


def change_auto_connection(name: str) -> None:
    """
    Changes the current
    auto connection.

    Parameters
    ----------
    name: str
        Name of the new
        auto connection.

    Examples
    --------
    Create a new connection:

    .. code-block:: python

        from vastorbit.connection import new_connection, change_auto_connection

        new_connection(
            {
                "host": "10.211.55.14",
                "port": "8080",
                "catalog": "vast",
                "schema": "default",
                "user": "admin",
            },
            name = "my_auto_connection",
            auto = False,
        )

    Change the auto connection
    to "my_auto_connection":

    .. code-block:: python

        change_auto_connection("my_auto_connection")

    .. seealso::

        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
    """
    gb_conn = get_global_connection()

    confparser = get_confparser()

    if confparser.has_section(name):
        confparser.remove_section(gb_conn.vo_auto_connection)
        confparser.add_section(gb_conn.vo_auto_connection)
        confparser.set(gb_conn.vo_auto_connection, "name", name)
        path = get_connection_file()

        with open(path, "w+", encoding="utf-8") as f:
            confparser.write(f)

    else:
        raise NameError(
            "The input name is incorrect. The connection "
            f"'{name}' has never been created.\nUse the "
            "new_connection function to create a new "
            "connection."
        )


def delete_connection(name: str) -> bool:
    """
    Deletes a specified connection
    from the connection file.

    Parameters
    ----------
    name: str
        Name of the connection.

    Returns
    -------
    bool
        ``True`` if the connection
        was deleted, ``False``
        otherwise.

    Examples
    --------
    Create a connection named
    'My_New_vast_connection':

    .. code-block:: python

        from vastorbit.connection import new_connection

        new_connection(
            {
                "host": "10.20.110.10",
                "port": "8080",
                "catalog": "vast",
                "schema": "default",
                "user": "admin",
            },
            name = "My_New_vast_connection",
        )

    Display all available
    connections:

    .. code-block:: python

        from vastorbit.connection import available_connections

        available_connections()

    ``['VASTDSN', 'My_New_vast_connection']``

    Delete the 'My_New_vast_connection'
    connection:

    .. code-block:: python

        from vastorbit.connection import delete_connection

        delete_connection("My_New_vast_connection")

    Confirm that the connection
    no longer appears in the
    available connections:

    .. code-block:: python

        available_connections()

    ``['VASTDSN']``

    .. seealso::

        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
    """
    gb_conn = get_global_connection()

    confparser = get_confparser()

    if confparser.has_section(name):
        confparser.remove_section(name)
        if confparser.has_section(gb_conn.vo_auto_connection):
            name_auto = confparser.get(gb_conn.vo_auto_connection, "name")
            if name_auto == name:
                confparser.remove_section(gb_conn.vo_auto_connection)
        path = get_connection_file()

        with open(path, "w+", encoding="utf-8") as f:
            confparser.write(f)

        return True

    else:
        print_message(f"The connection {name} does not exist.", "warning")

        return False


def new_connection(
    conn_info: Dict[str, Any],
    name: str = "vast_connection",
    auto: bool = True,
    overwrite: bool = True,
    connect_attempt: bool = True,
    prompt: bool = False,
) -> None:
    """
    Saves the new connection in the vastorbit
    connection file. The information is saved
    as plaintext in the local machine.
    The function
    :py:func:`~vastorbit.connection.get_connection_file`
    returns the associated connection file
    path. If you want a temporary connection,
    you can use the
    :py:func:`~vastorbit.connection.set_connection`
    function.

    Parameters
    ----------
    conn_info: dict
        ``dictionary`` containing
        the information to set up
        the connection.

         - catalog:
            Trino catalog name (default: vast).
         - schema:
            Trino schema name (default: default).
         - host:
            Server hostname or IP.
         - port:
            Server port (default: 8080).
         - user:
            Username (default: admin).
         - password:
            User password (optional).
         - http_scheme:
            HTTP scheme: http or https (default: http).

        ...

         - env:
            ``bool`` to indicate whether the user and
            password are replaced by the associated
            environment variables. If ``True``, vastorbit
            reads the associated environment variables
            instead of writing and directly using the
            username and password.
            For example:
            ``{'user': 'ENV_USER', 'password': 'ENV_PASSWORD'}``

            This works only for the user and password.
            The real values of the other variables are
            stored plaintext in the vastorbit connection
            file. Using the environment variables hides
            the username and password in cases where the
            local machine is shared.

    name: str, optional
        Name of the connection.
    auto: bool, optional
        If set to True, the connection
        will become the new auto-connection.
    overwrite: bool, optional
        If set to ``True`` and the connection
        already exists, the existing connection
        will be overwritten.
    connect_attempt: bool
        If set to False, it will not attempt
        to connect automatically.
    prompt: bool, optional
        If set to True, it will open a prompt
        to ask for ``oauth_refresh_token`` as well as ``client_secret``.

    Examples
    --------
    Create a new connection to vastorbit:

    .. note::

        If no errors are raised, the new connection was
        successful.

    .. code-block:: python

        from vastorbit.connection import new_connection

        conn_info = {
            "host": "10.211.55.14",
            "port": "8080",
            "catalog": "vast",
            "schema": "default",
            "user": "admin",
        }

        new_connection(conn_info, name = "VASTDSN")

    .. seealso::

        | :py:func:`~vastorbit.connection.get_connection_file` :
            Gets the vastorbit connection file.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    if trino is None:
        raise ImportError(
            "The 'trino' package is required for Trino connections. "
            "Install it with: pip install trino"
        )

    path = get_connection_file()
    confparser = get_confparser()

    if confparser.has_section(name):
        if not overwrite:
            raise ValueError(
                f"The section '{name}' already exists. You "
                "can overwrite it by setting the parameter "
                "'overwrite' to True."
            )
        confparser.remove_section(name)
    confparser.add_section(name)

    if prompt:
        if not (oauth_access_token := getpass("Input OAuth Access Token:")):
            print_message("Default value applied: Input left empty.")
        else:
            conn_info["oauth_access_token"] = oauth_access_token
        if not (oauth_refresh_token := getpass("Input OAuth Refresh Token:")):
            print_message("Default value applied: Input left empty.")
        else:
            conn_info["oauth_refresh_token"] = oauth_refresh_token
        if not (
            client_secret := getpass(
                "Input OAuth Client Secret: (Public client users should leave this blank)"
            )
        ):
            print_message("Default value applied: Input left empty.")
        else:
            if "oauth_config" not in conn_info:
                conn_info["oauth_config"] = {}
            conn_info["oauth_config"]["client_secret"] = client_secret

    try:
        if conn_info.get("oauth_refresh_token", False):
            oauth_manager = OAuthManager(conn_info["oauth_refresh_token"])
            oauth_config = conn_info.get("oauth_config", {})
            oauth_manager.set_config(oauth_config)
            conn_info["oauth_access_token"] = oauth_manager.do_token_refresh()
            conn_info["oauth_refresh_token"] = oauth_manager.refresh_token
    except OAuthTokenRefreshError as error:
        print_message("An error occurred while refreshing your OAuth token")
        raise error

    for c in conn_info:
        confparser.set(name, c, str(conn_info[c]))

    with open(path, "w+", encoding="utf-8") as f:
        confparser.write(f)

    if auto:
        change_auto_connection(name)

    if connect_attempt:
        # To prevent auto-connection. Needed for re-prompts in case of errors.
        gb_conn = get_global_connection()
        try:
            conn = _create_trino_connection(read_dsn(name, path))
            gb_conn.set_connection(conn, name, path)
            print_message("Connected Successfully!")
        except OAuthTokenRefreshError:
            print_message(
                "Access Denied: Your authentication credentials are incorrect or have expired. Please retry"
            )
            new_connection(
                conn_info=read_dsn(name, path), prompt=True, connect_attempt=False
            )
            try:
                conn = _create_trino_connection(read_dsn(name, path))
                gb_conn.set_connection(conn, name, path)
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


def _create_trino_connection(config: Dict[str, Any]):
    """Helper function to create a Trino connection from config."""
    if trino is None:
        raise ImportError(
            "The 'trino' package is required. Install it with: pip install trino"
        )

    # Build Trino connection parameters
    trino_params = {
        "host": config.get("host", "localhost"),
        "port": config.get("port", 8080),
        "user": config.get("user", "admin"),
        "catalog": config.get("catalog", "vast"),
        "schema": config.get("schema", "default"),
    }

    # Add optional parameters
    if "http_scheme" in config:
        trino_params["http_scheme"] = config["http_scheme"]

    if "password" in config:
        trino_params["auth"] = trino.auth.BasicAuthentication(
            config["user"], config["password"]
        )

    # OAuth support
    if "oauth_access_token" in config:
        trino_params["http_headers"] = {
            "Authorization": f"Bearer {config['oauth_access_token']}"
        }

    return trino.dbapi.connect(**trino_params)


new_auto_connection = new_connection
