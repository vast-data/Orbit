"""
SPDX-License-Identifier: Apache-2.0
"""

import os
import sys
from configparser import ConfigParser
from typing import Optional


def get_confparser(dsn: Optional[str] = None) -> ConfigParser:
    """
    Parses the input DSN and
    returns the linked Config
    Parser.

    Parameters
    ----------
    dsn: str, optional
        Path to the file containing
        the credentials. If empty,
        the ``vastorbit_CONNECTION``
        environment variable is used.

    Examples
    --------
    Get the Config Parser
    using the ``vastorbit_CONNECTION``
    environment variable:

    .. ipython:: python

        from vastorbit.connection import get_confparser

        get_confparser()

    .. seealso::

        | :py:func:`~vastorbit.connection.get_connection_file` :
            Gets the vastorbit connection file.
    """
    if not dsn:
        dsn = get_connection_file()
    confparser = ConfigParser()
    confparser.optionxform = str
    confparser.read(dsn)
    return confparser


def get_connection_file() -> str:
    """
    Gets (and creates, if necessary) the
    auto-connection file. If the environment
    variable ``vastorbit_CONNECTION`` is set,
    it is assumed to be the full path to the
    auto-connection file.
    Otherwise, we reference "connections.vastorbit"
    in the hidden ".vastorbit" folder in the
    user's home directory.

    Returns
    -------
    string
        the validated full path to the
        auto-connection file.

    Examples
    --------
    The connection file is used
    to store all connections:

    .. warning::

        Connections are stored in plain
        text format. In shared environments,
        it's recommended to create connections
        manually for added security.

    .. code-block:: python

        from vastorbit.connection import get_connection_file

        get_connection_file()

    ``'C:\\Users\\user\\.vastorbit\\connections.vastorbit'``

    .. seealso::

        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
    """
    if "vastorbit_CONNECTION" in os.environ and os.path.exists(
        os.environ["vastorbit_CONNECTION"]
    ):
        path = os.environ["vastorbit_CONNECTION"]
        validated_path = validate_path(path)  # Validate the custom path
        return validated_path
    # Default to the user's home directory
    path = os.path.join(os.path.expanduser("~"), ".vastorbit")
    os.makedirs(path, 0o700, exist_ok=True)
    path = os.path.join(path, "connections.vastorbit")
    return path


def validate_path(path: str) -> str:
    """
    Validates a file path to ensure it is secure and does not
    point to unintended or unsafe locations. This function
    prevents users from saving files in restricted system
    directories, using symbolic links, or engaging in path
    traversal attacks. It also ensures the target directory
    is writable and, on Unix-based systems, owned by the current user.

    Parameters
    ----------
    path : str
        The file path to validate.

    Raises
    ------
    ValueError
        If the file path violates any of the following rules:
        - Points to a restricted system location.
        - Uses a symbolic link.
        - Includes path traversal sequences (`..`).
        - Resides in a directory that is not writable.
        - On Unix-based systems, resides in a directory not owned by the current user.

    Examples
    --------
    Validate a safe file path within the user's home directory:

    >>> validate_path('/home/user/.vastorbit/connections.vastorbit')

    Raise an error for a path in a restricted location:

    >>> validate_path('/etc/passwd')
    ValueError: Cannot use path '/etc/passwd': it is a restricted system location.

    Prevent symbolic links:

    >>> validate_path('/home/user/link_to_connections.vastorbit')
    ValueError: Cannot use path '/home/user/link_to_connections.vastorbit': symbolic links are not allowed.

    Notes
    -----
    This function is intended for use in applications where user-specified
    file paths are allowed. It helps balance user flexibility with security
    by rejecting paths that could lead to vulnerabilities or unauthorized access.
    """
    # Restricted locations
    restricted_locations = [
        "/etc",
        "/usr",
        "/bin",
        "/sbin",
        "/var",
        "/dev",
        "/root",
        "C:\\Windows",
        "C:\\Program Files",
    ]
    if any(path.startswith(loc) for loc in restricted_locations):
        raise ValueError(
            f"Cannot use path '{path}': it is a restricted system location."
        )

    # Ensure directory exists and is writable
    directory = os.path.dirname(path) or "."
    if not os.path.exists(directory):
        # Create directory if it doesn't exist
        try:
            os.makedirs(directory, 0o700, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create directory for path '{path}': {e}") from e

    if not os.access(directory, os.W_OK):
        raise ValueError(f"Cannot use path '{path}': directory is not writable.")

    # Prevent symbolic links (only if file exists)
    if os.path.exists(path) and os.path.islink(path):
        raise ValueError(f"Cannot use path '{path}': symbolic links are not allowed.")

    # Prevent path traversal
    normalized_path = os.path.normpath(path)
    if ".." in normalized_path:
        raise ValueError(f"Cannot use path '{path}': path traversal detected.")

    # Optional: Restrict to user-owned directories (Linux/Unix only)
    if sys.platform != "win32":
        try:
            stat_info = os.stat(directory)
            if stat_info.st_uid != os.getuid():
                raise ValueError(
                    f"Cannot use path '{path}': directory is not owned by the current user."
                )
        except FileNotFoundError:
            # Directory doesn't exist yet, which is OK (we'll create it)
            pass

    return path
