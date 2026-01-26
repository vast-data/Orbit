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


@pytest.fixture(scope="module", autouse=False)
def load_matplotlib():
    """
    Set default plotting library to matplotlib
    """
    conf.set_option("plotting_lib", "matplotlib")
    yield
    conf.set_option("plotting_lib", "plotly")
