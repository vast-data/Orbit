"""
SPDX-License-Identifier: Apache-2.0

Export to string formats and CSV ingest round-trip.
"""

import os
import tempfile

import vastorbit as vo


def test_to_csv_string(iris):
    out = iris.head(5).to_vdf().to_csv()
    assert isinstance(out, str) and len(out) > 0


def test_to_json_string(iris):
    out = iris.head(5).to_vdf().to_json()
    assert isinstance(out, str) and len(out) > 0


def test_read_csv_round_trip(name_factory):
    tbl = name_factory("csv_tbl")
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "sample.csv")
        with open(path, "w") as f:
            f.write("a,b\n1,x\n2,y\n3,z\n")
        vd = vo.read_csv(path, table_name=tbl)
    assert vd.shape()[0] == 3