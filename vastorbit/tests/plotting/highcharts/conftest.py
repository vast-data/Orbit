"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# Standard Python Modules

# vastorbit
import vastorbit._config.config as conf

# Other Modules
try:
    from vertica_highcharts import Highchart
except:
    Highchart = type(None)


@pytest.fixture(scope="module")
def plotting_library_object():
    """
    Set default plotting object to highcharts
    """
    return Highchart


@pytest.fixture(scope="session", autouse=True)
def load_plotlib():
    """
    Set default plotting library to highcharts
    """
    conf.set_option("plotting_lib", "highcharts")
    yield
    conf.set_option("plotting_lib", "plotly")
