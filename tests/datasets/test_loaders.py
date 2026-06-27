"""
SPDX-License-Identifier: Apache-2.0

Every dataset loader returns a non-empty VastFrame with the expected schema.
"""

import pytest

from vastorbit.datasets import (
    load_titanic,
    load_iris,
    load_winequality,
    load_airline_passengers,
    load_amazon,
    load_pop_growth,
    load_commodities,
    load_gapminder,
    load_cities,
    load_world,
    load_market,
    load_laliga,
    load_africa_education,
    load_smart_meters,
    load_dataset_cl,
    load_dataset_num,
    load_dataset_reg,
)
from tests.helpers import cols_lower


@pytest.mark.parametrize(
    "loader, must_have",
    [
        (load_titanic, "survived"),
        (load_iris, "species"),
        (load_winequality, "quality"),
        (load_airline_passengers, None),
        (load_amazon, None),
        (load_pop_growth, None),
        (load_commodities, None),
        (load_gapminder, None),
        (load_cities, None),
        (load_world, None),
        (load_market, None),
        (load_laliga, None),
        (load_africa_education, None),
        (load_smart_meters, None),
        (load_dataset_cl, None),
        (load_dataset_num, None),
        (load_dataset_reg, None),
    ],
)
def test_loader(loader, must_have):
    vd = loader()
    assert len(vd.get_columns()) > 0
    assert vd.shape()[0] > 0
    if must_have is not None:
        assert must_have in cols_lower(vd)


def test_session_fixtures_match(titanic, iris, winequality):
    assert titanic.shape()[0] > 0
    assert iris.shape()[0] == 150
    assert winequality.shape()[0] > 0
