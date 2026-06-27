"""
SPDX-License-Identifier: Apache-2.0

Shared constants and small helpers, importable from any test module as
``from tests.helpers import ...``.
"""

import uuid


# --------------------------------------------------------------------------- #
# Column / target shortcuts for the built-in datasets
# --------------------------------------------------------------------------- #
TITANIC_NUM_X = ["age", "fare"]
TITANIC_BINARY_Y = "survived"          # 0 / 1

IRIS_X = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
IRIS_MULTI_Y = "Species"               # 3 classes

WINE_X = ["fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar"]
WINE_REG_Y = "quality"                 # numeric


# --------------------------------------------------------------------------- #
# Naming
# --------------------------------------------------------------------------- #
def unique_name(prefix="vo_test"):
    """A collision-free object name for a single test."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def cols_lower(vdf):
    """Lower-cased, unquoted column names (Trino lowercases unquoted ids)."""
    return [c.lower().strip('"') for c in vdf.get_columns()]


# --------------------------------------------------------------------------- #
# Tiny synthetic series for time-series tests (no external loader needed)
# --------------------------------------------------------------------------- #
def trend_series(n=40):
    """A single increasing series: columns ``month`` and ``value``."""
    return {
        "month": list(range(1, n + 1)),
        "value": [round(5 + 7.8 * i, 2) for i in range(n)],
    }


def multivariate_series(n=30):
    """Two correlated series for VAR: columns ``t``, ``a``, ``b``."""
    return {
        "t": list(range(1, n + 1)),
        "a": [float(i) + (i % 3) for i in range(1, n + 1)],
        "b": [float(i) * 0.5 + (i % 2) for i in range(1, n + 1)],
    }
