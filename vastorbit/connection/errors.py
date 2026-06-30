"""
SPDX-License-Identifier: Apache-2.0
"""

from trino.exceptions import TrinoUserError


class ConnectionError(Exception):
    """
    Error class for database connection errors.
    """


class DuplicateObject(Exception):
    """
    Error class for database duplicate object.
    """


class MissingRelation(Exception):
    """
    Error class for database missing relations.
    """


"""
Error class for database query errors.
"""

QueryError = TrinoUserError


class OAuthConfigurationError(ConnectionError):
    """
    Error class which covers errors pertaining to
    OAuth configuration setup.
    """


class OAuthEndpointDiscoveryError(ConnectionError):
    """
    Error class which covers errors pertaining to
    failure to get token url from discovery url.
    """


class OAuthTokenRefreshError(ConnectionError):
    """
    Error class which covers errors pertaining to
    failure to authenticate using Refresh Token.
    """
