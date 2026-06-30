"""
SPDX-License-Identifier: Apache-2.0

Root fixtures for the VastOrbit test-suite.

Connection
----------
Tests connect to a **local Trino** by default (``localhost:8080``) using the
``memory`` connector, which needs no external database and supports
``CREATE TABLE`` / ``INSERT`` (what the loaders and VastOrbit's temp tables
require). Every detail is overridable with environment variables so the same
suite runs unchanged in CI:

    TRINO_HOST     (default: localhost)
    TRINO_PORT     (default: 8080)
    TRINO_USER     (default: admin)
    TRINO_CATALOG  (default: memory)
    TRINO_SCHEMA   (default: default)
"""

import os

import pytest

import trino

import vastorbit as vo
from vastorbit.connection import set_connection
from vastorbit.datasets import (
    load_titanic,
    load_iris,
    load_winequality,
    load_airline_passengers,
)

from tests.helpers import unique_name


# --------------------------------------------------------------------------- #
# Connection
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session", autouse=True)
def trino_connection():
    """Open one Trino connection for the whole session and register it."""
    conn = trino.dbapi.connect(
        host=os.getenv("TRINO_HOST", "localhost"),
        port=int(os.getenv("TRINO_PORT", "8080")),
        user=os.getenv("TRINO_USER", "admin"),
        catalog=os.getenv("TRINO_CATALOG", "memory"),
        schema=os.getenv("TRINO_SCHEMA", "default"),
    )
    set_connection(conn)
    vo.set_option("temp_schema", os.getenv("TRINO_SCHEMA", "default"))
    yield conn
    try:
        conn.close()
    except Exception:
        pass


@pytest.fixture(scope="session", autouse=True)
def plotting_lib():
    """Force the non-interactive matplotlib backend during tests."""
    import matplotlib

    matplotlib.use("Agg")
    vo.set_option("plotting_lib", "matplotlib")
    yield


# --------------------------------------------------------------------------- #
# Naming / cleanup
# --------------------------------------------------------------------------- #
@pytest.fixture
def name_factory():
    """Hand out unique object names and drop everything created at teardown."""
    created = []

    def _make(prefix="vo_test"):
        n = unique_name(prefix)
        created.append(n)
        return n

    yield _make
    for n in created:
        for method in ("model", "table", "view"):
            try:
                vo.drop(n, method=method)
            except Exception:
                pass


# --------------------------------------------------------------------------- #
# Datasets (loaded once per session, read-only)
# --------------------------------------------------------------------------- #
# Loaded once per session, then handed to each test as a fresh ``.copy()`` so
# that in-place mutations (e.g. ``model.predict(vdf, name="pred")`` adding a
# column) cannot leak between tests or parametrizations.
@pytest.fixture(scope="session")
def _titanic_raw(trino_connection):
    return load_titanic()


@pytest.fixture
def titanic(_titanic_raw):
    return _titanic_raw.copy()


@pytest.fixture(scope="session")
def _iris_raw(trino_connection):
    return load_iris()


@pytest.fixture
def iris(_iris_raw):
    return _iris_raw.copy()


@pytest.fixture(scope="session")
def _winequality_raw(trino_connection):
    return load_winequality()


@pytest.fixture
def winequality(_winequality_raw):
    return _winequality_raw.copy()


@pytest.fixture(scope="session")
def _airline_raw(trino_connection):
    return load_airline_passengers()


@pytest.fixture
def airline(_airline_raw):
    return _airline_raw.copy()
