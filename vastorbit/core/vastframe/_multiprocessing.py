"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import TYPE_CHECKING

from vastorbit._typing import SQLColumns

from vastorbit.core.tablesample.base import TableSample

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


def aggregate_parallel_block(
    vdf: "VastFrame", func: list, columns: SQLColumns, ncols_block: int, i: int
) -> TableSample:
    """
    Parallelizes the computations of the aggregate VastFrame
    method. This allows the VastFrame to send multiple
    queries at the same time.
    """
    return vdf.aggregate(
        func=func, columns=columns[i : i + ncols_block], ncols_block=ncols_block
    )


def describe_parallel_block(
    vdf: "VastFrame",
    method: str,
    columns: SQLColumns,
    unique: bool,
    ncols_block: int,
    i: int,
) -> TableSample:
    """
    Parallelizes the computations of the describe VastFrame
    method. This allows the VastFrame to send multiple
    queries at the same time.
    """
    return vdf.describe(
        method=method,
        columns=columns[i : i + ncols_block],
        unique=unique,
        ncols_block=ncols_block,
    )
