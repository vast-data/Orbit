"""
SPDX-License-Identifier: Apache-2.0

Scalers and one-hot encoding.
"""

import pytest

from vastorbit.machine_learning.vast import (
    Scaler,
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    OneHotEncoder,
)
from tests.helpers import WINE_X, cols_lower

SCALERS = [
    ("StandardScaler", lambda n: StandardScaler(name=n)),
    ("MinMaxScaler", lambda n: MinMaxScaler(name=n)),
    ("RobustScaler", lambda n: RobustScaler(name=n)),
    ("Scaler-zscore", lambda n: Scaler(name=n, method="zscore")),
    ("Scaler-minmax", lambda n: Scaler(name=n, method="minmax")),
]


@pytest.mark.parametrize("label, factory", SCALERS, ids=[s[0] for s in SCALERS])
def test_scaler(winequality, name_factory, label, factory):
    model = factory(name_factory(f"scale_{label}"))
    model.fit(winequality, WINE_X)
    out = model.transform(winequality)
    assert out.shape()[0] == winequality.shape()[0]
    assert model.inverse_transform(out) is not None


def test_one_hot_encoder(titanic, name_factory):
    enc = OneHotEncoder(name=name_factory("ohe"))
    enc.fit(titanic, ["sex", "pclass"])
    out = enc.transform(titanic)
    assert out.shape()[0] == titanic.shape()[0]
    # one-hot expands the 2 categorical inputs into multiple indicator columns
    assert len(out.get_columns()) > 2
