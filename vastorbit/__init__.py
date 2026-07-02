"""
SPDX-License-Identifier: Apache-2.0
"""

__author__: str = "Badr Ouali"
__author_email__: str = "badr.ouali@outlook.fr"
__description__: str = (
    "vastorbit simplifies data exploration, data cleaning"
    " AI and machine learning in VAST."
)
__url__: str = "https://github.com/vast-data/Orbit/"
__license__: str = "Apache License, Version 2.0"
__version__: str = "0.1.0b2"
__codecov__: float = 0.5

from vastorbit._config.config import get_option, set_option
from vastorbit._utils._sql._vast_version import vast_version
from vastorbit._utils._logo import vastorbit_logo_html, vastorbit_logo_str
from vastorbit._help import help_start

from vastorbit.connection.connect import (
    close_connection,
    connect,
    current_connection,
    current_cursor,
    set_connection,
)
from vastorbit.connection.read import available_connections
from vastorbit.connection.write import (
    change_auto_connection,
    delete_connection,
    new_connection,
)

from vastorbit.core.parsers.csv import read_csv, pcsv
from vastorbit.core.parsers.json import read_json, pjson
from vastorbit.core.parsers.pandas import read_pandas
from vastorbit.core.string_sql.base import StringSQL
from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame, VastColumn

from vastorbit.sql.create import create_schema, create_table
from vastorbit.sql.drop import drop
from vastorbit.sql.dtypes import get_data_types, vast_python_dtype
from vastorbit.sql.insert import insert_into
from vastorbit.sql.sys import (
    current_session,
    username,
    does_table_exist,
    has_privileges,
)
