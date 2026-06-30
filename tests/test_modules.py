"""
SPDX-License-Identifier: Apache-2.0

Import-level smoke for modules that need an IPython / notebook runtime to do
anything meaningful — here we just assert they import and expose their entry
points, which catches import regressions in CI.
"""

import importlib

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "vastorbit.ai",
        "vastorbit.chart",
        "vastorbit.jupyter",
        "vastorbit.jupyter.extensions",
    ],
)
def test_module_imports(module):
    assert importlib.import_module(module) is not None


def test_ipython_extension_entrypoints():
    import vastorbit.ai as ai
    import vastorbit.chart as chart

    assert hasattr(ai, "load_ipython_extension")
    assert hasattr(chart, "load_ipython_extension")
