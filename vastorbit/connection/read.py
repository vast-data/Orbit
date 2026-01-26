"""
SPDX-License-Identifier: Apache-2.0
"""

import ast
import os
from typing import Optional, Dict, Any

from vastorbit.connection.global_connection import get_global_connection
from vastorbit.connection.utils import get_confparser


def available_connections() -> list[str]:
    """
    Displays all available connections.

    Returns
    -------
    list
        all available connections.

    Examples
    --------
    Displays all available connections:

    .. ipython:: python

        from vastorbit.connection import available_connections

        available_connections()

    .. seealso::

        | :py:func:`~vastorbit.connection.get_connection_file` :
            Gets the vastorbit connection file.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    gb_conn = get_global_connection()

    confparser = get_confparser()
    if confparser.has_section(gb_conn.vo_auto_connection):
        confparser.remove_section(gb_conn.vo_auto_connection)
    all_connections = confparser.sections()
    return all_connections


available_auto_connection = available_connections


def read_dsn(section: str, dsn: Optional[str] = None) -> Dict[str, Any]:
    """
    Reads the DSN information from
    the ``vastorbit_CONNECTION``
    environment variable or the
    input file.

    Parameters
    ----------
    section: str
        Name of the section in the
        configuration file that contains
        the credentials.
    dsn: str, optional
        Path to the file containing the
        credentials.If empty, the
        ``vastorbit_CONNECTION``
        environment variable is
        used.

    Returns
    -------
    dict
        ``dictionary`` with
        all the credentials.

    Examples
    --------
    Read the DSN information
    from the connection file:

    .. code-block:: python

        from vastorbit.connection import read_dsn

        dsn = read_dsn("VASTDSN")
        dsn

    | ``{``
    | ``'database': 'testdb',``
    | ``'host': '10.211.55.14',``
    | ``'password': 'XxX',``
    | ``'port': 8080,``
    | ``'user': 'dbadmin'``
    | ``}``

    Read the DSN information from a input file:

    .. code-block:: python

        dsn = read_dsn(
            "vp_test_config",
            "/Users/Badr/Library/Python/3.6/lib/python/site-packages/vastorbit/tests/vastorbit_test.conf",
        )
        dsn

    | ``{``
    | ``'password': 'XxX',``
    | ``'port': 8080,``
    | ``'user': 'dbadmin',``
    | ``'vp_test_database': 'testdb',``
    | ``'vp_test_host': '10.211.55.14',``
    | ``'vp_test_log_dir': 'mylog/vp_tox_tests_log',``
    | ``'vp_test_password': 'XxX',``
    | ``'vp_test_port': '8080',``
    | ``'vp_test_user': 'dbadmin'``
    | ``}``

    .. seealso::

        | :py:func:`~vastorbit.connection.get_connection_file` :
            Gets the vastorbit connection file.
        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
        | :py:func:`~vastorbit.connection.set_connection` :
            Sets the vastorbit connection.
    """
    confparser = get_confparser(dsn)

    if confparser.has_section(section):
        options = confparser.items(section)

        gb_conn = get_global_connection()
        conn_info: Dict[str, Any] = {
            "port": 8080,  # Default Trino port
            "user": "admin",
            "catalog": "vast",
            "schema": "default",
        }

        env = False
        for option_name, option_val in options:
            if option_name.lower().startswith("env"):
                if option_val.lower() in ("true", "t", "yes", "y"):
                    env = True
                break

        for option_name, option_val in options:
            option_name = option_name.lower()

            if option_name in ("pwd", "password", "uid", "user") and env:
                if option_name == "pwd":
                    option_name = "password"
                elif option_name == "uid":
                    option_name = "user"
                env_val = os.getenv(option_val)
                if env_val is not None:
                    conn_info[option_name] = env_val
                else:
                    raise ValueError(
                        f"The '{option_name}' environment variable "
                        f"'{option_val}' does not exist and the 'env' "
                        "option is set to True.\nImpossible to set up "
                        "the final DSN.\nTips: You can manually set "
                        "it up by importing os and running the following "
                        f"command:\nos.environ['{option_val}'] = '******'"
                    )

            elif option_name in ("servername", "server", "hostname"):
                conn_info["host"] = option_val

            elif option_name == "uid":
                conn_info["user"] = option_val

            elif (
                option_name in ("port", "connection_timeout") and option_val.isnumeric()
            ):
                conn_info[option_name] = int(option_val)

            elif option_name == "pwd":
                conn_info["password"] = option_val

            elif option_name == "backup_server_node":
                try:
                    conn_info["backup_server_node"] = ast.literal_eval(option_val)
                except Exception:
                    conn_info["backup_server_node"] = option_val

            elif option_name == "kerberosservicename":
                conn_info["kerberos_service_name"] = option_val

            elif option_name == "kerberoshostname":
                conn_info["kerberos_host_name"] = option_val

            elif "vp_test_" in option_name:
                conn_info[option_name[8:]] = option_val

            elif option_name in (
                "ssl",
                "autocommit",
                "use_prepared_statements",
                "connection_load_balance",
                "disable_copy_local",
                "http_scheme",
            ):
                option_val_lower = option_val.lower()
                conn_info[option_name] = option_val_lower in ("true", "t", "yes", "y")

            elif option_name == "oauth_config":
                try:
                    conn_info[option_name] = ast.literal_eval(option_val)
                except Exception:
                    conn_info[option_name] = option_val

            elif not option_name.startswith("env"):
                # Store other options as-is
                conn_info[option_name] = option_val

        return conn_info

    else:
        raise NameError(f"The DSN Section '{section}' doesn't exist.")
