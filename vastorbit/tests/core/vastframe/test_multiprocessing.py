"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.core.vastframe._multiprocessing import (
    aggregate_parallel_block,
    describe_parallel_block,
)


class TestMultiprocessing:
    """
    test class for Multiprocessing functions test
    """

    def test_aggregate_parallel_block(self, titanic_vd_fun):
        """
        test aggregate_parallel_block function
        """
        _res = aggregate_parallel_block(
            titanic_vd_fun, "max", titanic_vd_fun.get_columns(), 5, 1
        )
        res = dict(zip(_res.values["index"], _res.values["max"]))
        assert res['"age"'] == titanic_vd_fun["age"].max()

    def test_describe_parallel_block(self, titanic_vd_fun):
        """
        test describe_parallel_block function
        """
        res = describe_parallel_block(
            titanic_vd_fun, "numerical", ["age"], False, 10, 1
        )

        assert res.shape() == titanic_vd_fun.describe().shape()
