"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.connection.global_connection import get_global_connection


def set_external_connection(cid: str, rowset: int = 500, symbol: str = "$") -> None:
    """
    Sets a Connection Identifier
    Database. It connects to an
    external source using connectors.

    Parameters
    ----------
    cid: str
        Connection Identifier Database.
    rowset: int, optional
        Number of rows retrieved
        from the remote database
        during each fetch cycle.
    symbol: str, optional
        A special character to identify
        the connection. One of the following:
        ``"$", "€", "£", "%", "@", "&", "§", "?", "!"``

        For example, if the symbol is
        '$', you can call external tables
        with the input cid by writing
        $$$QUERY$$$, where QUERY represents
        a custom query.

    Examples
    --------
    Set up a connection with a
    database using the alias
    "pgdb".

    .. note::

        When configuring an external
        connection, you'll need to
        assign a unique symbol to
        identify it. This symbol will
        subsequently allow you to extract
        data from the target database
        using the associated identifier.

    .. code-block:: python

        import vastorbit as vo

        vo.set_external_connection(
            cid = "pgdb",
            rowset = 500,
            symbol = "&",
        )

    .. seealso::

        | :py:func:`~vastorbit.connection.new_connection` :
            Creates a new vastorbit connection.
    """
    gb_conn = get_global_connection()
    gb_conn.set_external_connections(symbol, cid, rowset)
