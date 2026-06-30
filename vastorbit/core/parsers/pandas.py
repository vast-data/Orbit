"""
SPDX-License-Identifier: Apache-2.0
"""

import csv
import logging
import os
from typing import Optional

import pandas as pd

import vastorbit._config.config as conf
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident


from vastorbit.core.parsers.csv import read_csv
from vastorbit.core.vastframe.base import VastFrame


@save_vastorbit_logs
def read_pandas(
    df: pd.DataFrame,
    name: Optional[str] = None,
    schema: Optional[str] = None,
    catalog: Optional[str] = None,
    dtype: Optional[dict] = None,
    parse_nrows: int = 10000,
    temp_path: Optional[str] = None,
    insert: bool = False,
    temporary_table: bool = False,
) -> VastFrame:
    """
    Ingests a ``pandas.DataFrame`` into
    the VAST database via Trino by creating
    a temporary CSV file and using the CSV
    parser to load the data.

    Parameters
    ----------
    df: pandas.DataFrame
        The ``pandas.DataFrame`` to
        ingest.
    name: str, optional
        Name of the new relation or
        the relation in which to
        insert the data.
        If unspecified, a temporary
        local table is created. This
        temporary table is dropped at
        the end of the local session.
    schema: str, optional
        Schema of the new relation.
        Supports formats:
        - 'schema_name' (uses default catalog from config)
        - 'catalog.schema_name' (catalog and schema)
        If empty, a temporary schema
        is used. To modify the temporary
        schema, use the :py:func:`~set_option`
        function.
    catalog: str, optional
        Target catalog (overrides catalog from schema parameter)
        Examples: 'hive', 'postgresql', 'vast', 'memory'
    dtype: dict, optional
        Dictionary of input types.
        Providing a dictionary can
        increase ingestion speed and
        precision. If specified,
        rather than parsing the
        intermediate CSV and guessing
        the input types, vastorbit
        uses the specified input
        types instead.
    parse_nrows: int, optional
        If this parameter is greater
        than zero, vastorbit creates
        and ingests a temporary file
        containing ``parse_nrows``
        number of rows to determine
        the input data types before
        ingesting the intermediate
        CSV file containing the rest
        of the data. This method of
        data type identification is
        less accurate, but is much
        faster for large datasets.
    temp_path: str, optional
        The path to which to write
        the intermediate CSV file.
        This is useful in cases
        where the user does not
        have write permissions
        on the current directory.
    insert: bool, optional
        If set to ``True``, the
        data are ingested into the
        input relation. The column
        names of your table and the
        ``pandas.DataFrame`` must
        match.
    temporary_table: bool, optional
        If True, create temporary table

    Returns
    -------
    VastFrame
        :py:class:`~VastFrame`
        of the new relation.

    Examples
    --------

    In this example, we will first create
    a ``pandas.DataFrame`` using
    ``VastFrame.``:py:meth:`~vastorbit.VastFrame.to_pandas`
    and ingest it into VAST database.

    We import :py:mod:`vastorbit`:

    .. ipython:: python

        import vastorbit as vo

    .. hint::

        By assigning an alias to :py:mod:`vastorbit`,
        we mitigate the risk of code collisions with
        other libraries. This precaution is necessary
        because vastorbit uses commonly known function
        names like "average" and "median", which can
        potentially lead to naming conflicts. The use
        of an alias ensures that the functions from
        :py:mod:`vastorbit` are used as intended
        without interfering with functions from other
        libraries.

    We will use the Titanic dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_titanic()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

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

    .. ipython:: python
        :suppress:

        import vastorbit.datasets as vod

        data = vod.load_titanic()

    Let's convert the :py:class:`~VastFrame`
    to a ``pandas.DataFrame``.

    .. code-block:: python

        pandas_df = data.to_pandas()
        display(pandas_df)

    .. ipython:: python
        :suppress:

        pandas_df = data.to_pandas()
        res = pandas_df
        html_file = open("figures/core_parsers_pandas_1.html", "w")
        html_file.write(res.to_html(max_rows = 6, justify = "center"))
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/core_parsers_pandas_1.html

    Now, we will ingest the
    ``pandas.DataFrame``
    into the VAST database.

    .. code-block:: python

        from vastorbit.core.parsers import read_pandas

        read_pandas(
            df = pandas_df,
            name = "titanic_pandas",
            schema = "public",
        )

    .. ipython:: python
        :suppress:
        :okexcept:

        from vastorbit.core.parsers import read_pandas
        res = read_pandas(
            df = pandas_df,
            name = "titanic_pandas",
            schema = "public",
        )
        html_file = open("figures/core_parsers_pandas_2.html", "w")
        html_file.write(res._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/core_parsers_pandas_2.html

    Let's specify data types using
    "dtype" parameter.

    .. code-block:: python

        read_pandas(
            df = pandas_df,
            name = "titanic_pandas_dtypes",
            schema = "public",
            dtype = {
                "pclass": "INTEGER",
                "survived": "INTEGER",
                "name": "VARCHAR(164)",
                "sex": "VARCHAR(20)",
                "age": "DOUBLE",
                "sibsp": "INTEGER",
                "parch": "INTEGER",
                "ticket": "VARCHAR(36)",
                "fare": "DOUBLE",
                "cabin": "VARCHAR(30)",
                "embarked": "VARCHAR(20)",
                "boat": "VARCHAR(100)",
                "body": "INTEGER",
                "home.dest": "VARCHAR(100)",
            },
        )

    .. ipython:: python
        :suppress:
        :okexcept:

        res = read_pandas(
            df = pandas_df,
            name = "titanic_pandas_dtypes",
            schema = "public",
            dtype = {
                "pclass": "INTEGER",
                "survived": "INTEGER",
                "name": "VARCHAR(164)",
                "sex": "VARCHAR(20)",
                "age": "DOUBLE",
                "sibsp": "INTEGER",
                "parch": "INTEGER",
                "ticket": "VARCHAR(36)",
                "fare": "DOUBLE",
                "cabin": "VARCHAR(30)",
                "embarked": "VARCHAR(20)",
                "boat": "VARCHAR(100)",
                "body": "INTEGER",
                "home.dest": "VARCHAR(100)",
            },
        )
        html_file = open("figures/core_parsers_pandas_3.html", "w")
        html_file.write(res._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/core_parsers_pandas_3.html

    .. important::

        A limited number of rows, determined by the
        ``parse_nrows`` parameter, is ingested. If
        your dataset is large and you want to ingest
        the entire dataset, increase its value.

    .. note::

        During the ingestion process, an intermediate
        CSV file is created. You can retrieve its
        location by using the temp_path parameter.

    .. note::

        If you want to ingest into an existing table,
        set the insert parameter to ``True``.

    .. seealso::

        | :py:func:`~vastorbit.read_csv` :
            Ingests a CSV file into the VAST DB.
        | :py:func:`~vastorbit.read_json` :
            Ingests a JSON file into the VAST DB.
    """
    dtype = format_type(dtype, dtype=dict)
    if not schema:
        schema = conf.get_option("temp_schema")
    if insert and not name:
        raise ValueError(
            "Parameter 'name' can not be empty when "
            "parameter 'insert' is set to True."
        )
    if not name:
        tmp_name = gen_tmp_name(name="df")[1:-1]
    else:
        tmp_name = name

    # Set up temp path
    if temp_path:
        sep = "/" if temp_path[-1] != "/" else ""
        path = f"{temp_path}{sep}{tmp_name}.csv"
    else:
        # Use system temp directory
        import tempfile

        temp_dir = tempfile.gettempdir()
        path = os.path.join(temp_dir, f"{tmp_name}.csv")

    try:
        # Check for empty DataFrame
        if df.empty or len(df.columns) == 0:
            raise ValueError("Empty DataFrame or no columns provided.")

        # Check if all columns are null
        null_columns = []
        for c in df.columns:
            if df[c].isna().all():
                null_columns.append(c)

        if len(df.columns) == len(null_columns):
            # All columns are null - create empty VastFrame
            names = ", ".join([f"NULL AS {quote_ident(col)}" for col in df.columns])
            q = " UNION ALL ".join([f"(SELECT {names})" for i in range(len(df))])
            if q == "":
                if len(df.columns) > 0:
                    joins = ", ".join(
                        [
                            f"CAST(NULL AS VARCHAR) AS {quote_ident(col)}"
                            for col in df.columns
                        ]
                    )
                    q = f"SELECT {joins} WHERE 1=0"
                else:
                    raise ValueError(
                        "There are no columns or values. Invalid DataFrame."
                    )
            return VastFrame(q)

        # Write DataFrame to CSV using standard format
        df.to_csv(
            path,
            index=False,
            quoting=csv.QUOTE_MINIMAL,
            escapechar="\\",
            sep=",",
        )

        # Use read_csv to load the data
        if insert:
            vdf = read_csv(
                path,
                table_name=tmp_name,
                schema=schema,
                catalog=catalog,
                dtype=dtype,
                parse_nrows=parse_nrows,
                insert=True,
                temporary_table=temporary_table,
            )
        else:
            vdf = read_csv(
                path,
                table_name=tmp_name,
                schema=schema,
                catalog=catalog,
                dtype=dtype,
                parse_nrows=parse_nrows,
                insert=False,
                temporary_table=temporary_table,
            )

    finally:
        # Clean up temporary CSV file
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logging.warning("Could not remove temporary file %s: %s", path, e)

    return vdf
