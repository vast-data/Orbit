"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
import vastorbit._config.config as conf

# Other Modules
import plotly


@pytest.fixture(scope="module")
def plotting_library_object():
    """
    Set default plotting object to plotly
    """
    return plotly.graph_objs.Figure


@pytest.fixture(scope="session", autouse=True)
def load_plotlib():
    """
    Set default plotting library to plotly
    """
    conf.set_option("plotting_lib", "plotly")
    yield
