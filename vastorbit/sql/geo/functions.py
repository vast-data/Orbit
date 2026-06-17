"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from vastorbit._typing import PythonNumber
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit._typing import SQLRelation

from vastorbit.datasets.generators import gen_meshgrid

from vastorbit.core.vastframe.base import VastFrame

import vastorbit.sql.functions.math as mt


@save_vastorbit_logs
def coordinate_converter(
    vdf: SQLRelation,
    x: str,
    y: str,
    x0: float = 0.0,
    earth_radius: PythonNumber = 6371,
    reverse: bool = False,
) -> VastFrame:
    """
    Converts between geographic coordinates (latitude
    and longitude)  and  Euclidean coordinates (x,y).

    Parameters
    ----------
    vdf: SQLRelation
        Input VastFrame.
    x: str
        VastColumn used as the abscissa (longitude).
    y: str
        VastColumn used as the ordinate  (latitude).
    x0: float, optional
        The initial abscissa.
    earth_radius: PythonNumber, optional
        Earth radius in km.
    reverse: bool, optional
        If set to True, the Euclidean coordinates are
        converted to latitude and longitude.

    Returns
    -------
    VastFrame
        result of the transformation.

    Examples
    --------
    For this example, we will use the Cities dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        cities = vod.load_cities()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_cities.html

    .. note::

        vastorbit offers a wide range of sample
        datasets that are ideal for training
        and testing purposes. You can explore
        the full list of available datasets in
        the :ref:`api.datasets`, which provides
        detailed information on each dataset and
        how to use them effectively. These datasets
        are invaluable resources for honing your
        data analysis and machine learning skills
        within the vastorbit environment.

    Let's extract the latitude and longitude.

    .. code-block:: python

        cities["lat"] = "ST_X(geometry)"
        cities["lon"] = "ST_Y(geometry)"
        display(cities)

    .. ipython:: python
        :suppress:

        from vastorbit.sql.geo import coordinate_converter
        from vastorbit.datasets import load_cities
        from vastorbit import set_option
        cities = load_cities()
        cities["lat"] = "ST_X(geometry)"
        cities["lon"] = "ST_Y(geometry)"
        #limit display rows because hit unicode decoding error
        set_option("max_rows", 20)
        html_file = open("SPHINX_DIRECTORY/figures/sql_geo_functions_coordinate_converter_1.html", "w")
        html_file.write(cities._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_geo_functions_coordinate_converter_1.html

    Let's leverage the coordinate_converter function to
    calculate Euclidean distances. We'll project the
    latitude and longitude into x, y coordinates.

    .. code-block:: python

        from vastorbit.sql.geo import coordinate_converter

        convert_xy = coordinate_converter(cities, "lon", "lat")
        display(convert_xy)

    .. ipython:: python
        :suppress:

        convert_xy = coordinate_converter(cities, "lon", "lat")
        html_file = open("SPHINX_DIRECTORY/figures/sql_geo_functions_coordinate_converter_2.html", "w")
        html_file.write(convert_xy._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_geo_functions_coordinate_converter_2.html

    We can effortlessly reverse the operation.

    .. code-block:: python

        convert_reverse_xy = coordinate_converter(convert_xy, "lon", "lat", reverse = True)
        display(convert_reverse_xy)

    .. ipython:: python
        :suppress:

        html_file = open("SPHINX_DIRECTORY/figures/sql_geo_functions_coordinate_converter_3.html", "w")
        html_file.write(coordinate_converter(convert_xy, "lon", "lat", reverse=True)._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/sql_geo_functions_coordinate_converter_3.html

    .. note::

        This function can be employed to operate on the Euclidean
        plane instead of a sphere, significantly improving
        computation speed.
    """
    x, y = vdf.format_colnames(x, y)

    result = vdf.copy()

    if reverse:
        result[x] = result[x] / earth_radius * 180 / mt.PI + x0
        result[y] = (
            (mt.atan(mt.exp(result[y] / earth_radius)) - mt.PI / 4) / mt.PI * 360
        )

    else:
        result[x] = earth_radius * ((result[x] - x0) * mt.PI / 180)
        result[y] = earth_radius * mt.ln(mt.tan(result[y] * mt.PI / 360 + mt.PI / 4))

    return result
