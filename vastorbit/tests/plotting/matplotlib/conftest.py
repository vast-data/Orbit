"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# Standard Python Modules

# vastorbit
import vastorbit._config.config as conf

# Other Modules
import matplotlib.pyplot as plt


@pytest.fixture(scope="module")
def plotting_library_object():
    """
    Set default plotting object to matplotlib
    """
    return plt.Axes


@pytest.fixture(scope="session", autouse=True)
def load_plotlib():
    """
    Set default plotting library to matplotlib
    """
    conf.set_option("plotting_lib", "matplotlib")
    yield
    conf.set_option("plotting_lib", "plotly")
