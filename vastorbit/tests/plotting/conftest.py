"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# Standard Python Modules

# vastorbit
from vastorbit.machine_learning.vast.automl import AutoML
from vastorbit.machine_learning.vast.ensemble import RandomForestClassifier


# Expensive models
@pytest.fixture(name="champion_challenger_plot", scope="package")
def load_champion_challenger_plot(schema_loader, dummy_dist_vd):
    """
    Loading the champion challenger plot
    """
    col_name_1 = "binary"
    col_name_2 = "0"
    model = AutoML(f"{schema_loader}.model_automl", lmax=10, print_info=False)
    model.fit(
        dummy_dist_vd,
        [
            col_name_1,
        ],
        col_name_2,
    )
    yield model
    model.drop()


@pytest.fixture(name="randon_forest_model_result", scope="module")
def load_random_forest_model(schema_loader, dummy_dist_vd):
    """
    Load the Random Forest Classifier model
    """
    col_name_1 = "0"
    col_name_2 = "1"
    by_col = "binary"
    model = RandomForestClassifier(f"{schema_loader}.random_forest_plot_test")
    model.drop()
    model.fit(dummy_dist_vd, [col_name_1, col_name_2], by_col)
    yield model
    model.drop()
