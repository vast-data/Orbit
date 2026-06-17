"""
SPDX-License-Identifier: Apache-2.0
"""

import datetime
import decimal
from typing import Annotated, Literal, Union, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.pyplot import Figure as mFigure
    from plotly.graph_objs._figure import Figure

    from vastorbit.core.vastframe.base import VastFrame
    from vastorbit.core.string_sql.base import StringSQL
    from vastorbit.core.tablesample.base import TableSample

    from vastorbit.plotting.base import PlottingBase


# Pythonic data types.

ArrayLike = Annotated[Union[list, np.ndarray], "Array Like Structure"]
NoneType = type(None)
PythonNumber = Annotated[Union[int, float, decimal.Decimal], "Python Numbers"]
PythonScalar = Annotated[
    Union[bool, float, str, datetime.timedelta, datetime.datetime],
    "Python Scalar",
]
TimeInterval = Annotated[Union[str, datetime.timedelta], "Time Interval"]
Datetime = Annotated[Union[str, datetime.datetime], ""]

# SQL data types.

SQLColumns = Annotated[
    Union[str, list[str]], "STRING representing one column or a list of columns"
]
SQLExpression = Annotated[Union[str, list[str], "StringSQL", list["StringSQL"]], ""]
SQLRelation = Annotated[Union[str, "VastFrame"], ""]

# Plotting data types.
PlottingObject = Union["PlottingBase", "TableSample", "Axes", "mFigure", "Figure"]
PlottingMethod = Union[
    Literal[None, "density", "count", "avg", "min", "max", "sum"], str
]
ColorType = str
