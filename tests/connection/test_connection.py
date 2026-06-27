"""
SPDX-License-Identifier: Apache-2.0

Connection registration and basic round-trip.
"""

from vastorbit.connection import current_connection


def test_connection_is_live(trino_connection):
    cur = trino_connection.cursor()
    cur.execute("SELECT 1")
    assert cur.fetchone()[0] == 1


def test_current_connection_registered(trino_connection):
    assert current_connection() is not None


def test_cursor_multiple_statements(trino_connection):
    cur = trino_connection.cursor()
    cur.execute("SELECT 2 + 3")
    assert cur.fetchone()[0] == 5
