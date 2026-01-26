"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

import vastorbit._config.config as conf
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit.errors import ExtensionError

from vastorbit.core.vastframe.base import VastFrame


@save_vastorbit_logs
def read_shp(
    path: str,
    schema: Optional[str] = None,
    table_name: Optional[str] = None,
) -> VastFrame:
    """
    Ingests a SHP file. At the
    moment, only files located
    in the VAST server can
    be ingested.

    Parameters
    ----------
    path: str
        Absolute path where
        the SHP file is located.
    schema: str, optional
        Schema where the SHP
        file will be ingested.
    table_name: str, optional
        Final relation name.

    Returns
    -------
    VastFrame
        The :py:class:`~VastFrame`
        of the relation.

    Examples
    --------
    Let's consider you have access
    to the following shape file
    located in the server:
    ``/shapefiles/tl_2010_us_state10.shp``

    You can easily ingest it in
    the table 'my_table' in the
    'my_schema' schema:

    .. code-block:: python

        read_shp(
            path = '/shapefiles/tl_2010_us_state10.shp',
            schema = 'my_schema',
            table_name = 'my_table',
        )

    The file will be parsed and
    store in the database.
    The output will be a
    :py:class:`~VastFrame`.

    .. note::

        vastorbit provides a set of
        geospatial functions in the
        :py:mod:`vastorbit.sql.geo`
        module.

    .. seealso::

        | :py:func:`~vastorbit.sql.geo.create_index` :
            Creates the geo index.
        | :py:func:`~vastorbit.sql.geo.describe_index` :
            Describes the geo index.
        | :py:func:`~vastorbit.sql.geo.intersect` :
            Spatially intersects a point
            or points with a set of polygons.
        | :py:func:`~vastorbit.sql.geo.rename_index` :
            Renames the geo index.
    """
    if not (schema):
        schema = conf.get_option("temp_schema")
    file = path.split("/")[-1]
    file_extension = file[-3 : len(file)]
    if file_extension != "shp":
        raise ExtensionError("The file extension is incorrect !")
    result = _executeSQL(
        query=f"""
            SELECT 
                /*+LABEL('read_shp')*/ 
                STV_ShpCreateTable(USING PARAMETERS file='{path}')
                OVER() AS create_shp_table;""",
        title="Getting SHP definition.",
        method="fetchall",
    )
    if not table_name:
        table_name = file[:-4]
    result[0] = [f'CREATE TABLE "{schema}"."{table_name}"(']
    result = [elem[0] for elem in result]
    result = "".join(result)
    _executeSQL(result, title="Creating the relation.")
    _executeSQL(
        query=f"""
            COPY "{schema}"."{table_name}" 
            WITH SOURCE STV_ShpSource(file=\'{path}\')
            PARSER STV_ShpParser();""",
        title="Ingesting the data.",
    )
    print_message(f'The table "{schema}"."{table_name}" has been successfully created.')
    return VastFrame(table_name, schema=schema)
