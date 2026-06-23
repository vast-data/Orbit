"""
SPDX-License-Identifier: Apache-2.0
"""

import datetime

from vastorbit._utils._sql._collect import save_vastorbit_logs


from vastorbit.core.vastframe.base import VastFrame


@save_vastorbit_logs
def gen_dataset(features_ranges: dict, nrows: int = 1000) -> VastFrame:
    """
    Generates a dataset using the input parameters.

    Parameters
    ----------
    features_ranges: dict
        Dictionary including the features types
        and ranges.

         - For str:
            The  subdictionary must  include
            two keys: "type" must be set  to
            'str'  and 'value' must  include
            the feature categories.
         - For int:
            The subdictionary must include
            two keys: "type"  must be set to
            'int' and 'range'  must  include
            two integers  that represent the
            lower and the upper bounds.
         - For reals:
            The subdictionary must
            include two keys: "type" must be
            set to'real' and 'range' must
            include two floats that represent
            the lower and the upper bounds.
         - For date:
            The subdictionary must include
            two keys: "type"  must be set to
            'date' and 'range'  must include
            the start date and the number of
            days after.
         - For datetime:
            The  subdictionary must
            include two keys: "type" must be
            set to 'date' and 'range'  must
            include the start date and the
            number of days after.
    nrows: int, optional
        The maximum number of rows in the dataset.

    Returns
    -------
    VastFrame
        Generated dataset.

    Examples
    --------
    .. code-block:: python

        import datetime

        from vastorbit.datasets import gen_dataset

        gen_dataset(
            features_ranges = {
                "name": {"type": str, "values": ["Badr", "Badr", "Raghu", "Waqas",]},
                "age": {"type": int, "range": [20, 40]},
                "distance": {"type": float, "range": [1000, 4000]},
                "date": {"type": datetime.date, "range": ["1993-11-03", 365]},
                "datetime": {"type": datetime.datetime, "range": ["1993-11-03", 365]},
            },
        )

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import gen_dataset
        import datetime
        import vastorbit as vo
        html_file = open("SPHINX_DIRECTORY/figures/datasets_generators_gen_dataset.html", "w")
        html_file.write(
            gen_dataset(
                features_ranges = {
                    "name": {"type": str, "values": ["Badr", "Badr", "Raghu", "Waqas",]},
                    "age": {"type": int, "range": [20, 40]},
                    "distance": {"type": float, "range": [1000, 4000]},
                    "date": {"type": datetime.date, "range": ["1993-11-03", 365]},
                    "datetime": {"type": datetime.datetime, "range": ["1993-11-03", 365]},
                },
            )._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_generators_gen_dataset.html

    """
    sql = []

    for param in features_ranges:
        if features_ranges[param]["type"] == str:
            val = features_ranges[param]["values"]
            if isinstance(val, str):
                sql += [f"'{val}' AS \"{param}\""]
            else:
                n = len(val)
                arr = ", ".join(["'" + str(v) + "'" for v in val])
                sql += [
                    f"ELEMENT_AT(ARRAY[{arr}], "
                    f'CAST(FLOOR(RANDOM() * {n}) AS INTEGER) + 1) AS "{param}"'
                ]

        elif features_ranges[param]["type"] == float:
            lower, upper = features_ranges[param]["range"]
            sql += [
                f'CAST({lower} + RANDOM() * ({upper} - {lower}) AS DOUBLE) AS "{param}"'
            ]

        elif features_ranges[param]["type"] == int:
            lower, upper = features_ranges[param]["range"]
            sql += [
                f'CAST({lower} + RANDOM() * ({upper} - {lower}) AS INTEGER) AS "{param}"'
            ]

        elif features_ranges[param]["type"] == datetime.date:
            start_date, number_of_days = features_ranges[param]["range"]
            sql += [
                f"DATE_ADD('day', CAST(FLOOR(RANDOM() * {number_of_days}) AS INTEGER), "
                f"DATE '{start_date}') AS \"{param}\""
            ]

        elif features_ranges[param]["type"] == datetime.datetime:
            start_date, number_of_days = features_ranges[param]["range"]
            sql += [
                f"DATE_ADD('second', "
                f"CAST(FLOOR(RANDOM() * {number_of_days} * 86400) AS BIGINT), "
                f"CAST(DATE '{start_date}' AS TIMESTAMP)) AS \"{param}\""
            ]

        elif features_ranges[param]["type"] == bool:
            sql += [f'(RANDOM() < 0.5) AS "{param}"']

        else:
            ptype = features_ranges[param]["type"]
            raise ValueError(f"Parameter {param}: Type {ptype} is not supported.")

    query = f"""
        SELECT
            {', '.join(sql)}
        FROM UNNEST(SEQUENCE(1, {nrows})) AS _gen(_row)"""

    return VastFrame(query)


@save_vastorbit_logs
def gen_meshgrid(features_ranges: dict) -> VastFrame:
    """
    Generates a dataset using regular steps.

    Parameters
    ----------
    features_ranges: dict
        Dictionary including the features types and ranges.

         - For str:
            The  subdictionary must  include
            two keys: "type" must be set  to
            'str'  and 'value' must  include
            the feature categories.
         - For int:
            The subdictionary must include
            two keys: "type"  must be set to
            'int' and 'range'  must  include
            two integers  that represent the
            lower and the upper bounds.
         - For float:
            The subdictionary must
            include two keys:  "type" must be
            set to 'float' and 'range' must
            include two floats that represent
            the lower and the upper bounds.
         - For date:
            The subdictionary must
            include two keys: "type" must be
            set to 'date' and 'range'  must
            include the start date and the
            number of days after.
         - For datetime:
            The  subdictionary must
            include two keys: "type" must be
            set to 'date' and 'range'  must
            include the start date and the
            number of days after.

        Numerical and date-like features must have an extra
        key in the  dictionary named 'nbins', which
        corresponds to the number of bins used to compute
        the different categories.

    Returns
    -------
    VastFrame
        Generated dataset.

    Examples
    --------
    .. code-block:: python

        import datetime

        from vastorbit.datasets import gen_meshgrid

        gen_meshgrid(
            features_ranges = {
                "name": {"type": str, "values": ["Badr", "Raghu", "Waqas",]},
                "age": {"type": int, "range": [20, 40]},
                "distance": {"type": float, "range": [1000, 4000]},
                "date": {"type": datetime.date, "range": ["1993-11-03", 365]},
            },
        )

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import gen_meshgrid
        import datetime
        import vastorbit as vo
        html_file = open("SPHINX_DIRECTORY/figures/datasets_generators_gen_meshgrid.html", "w")
        html_file.write(
            gen_meshgrid(
                features_ranges = {
                    "name": {"type": str, "values": ["Badr", "Badr", "Raghu", "Waqas",]},
                    "age": {"type": int, "range": [20, 40]},
                    "distance": {"type": float, "range": [1000, 4000]},
                    "datetime": {"type": datetime.datetime, "range": ["1993-11-03", 365]},
                },
            )._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_generators_gen_meshgrid.html
    """
    sql = []

    for idx, param in enumerate(features_ranges):
        nbins = 100
        if "nbins" in features_ranges[param]:
            nbins = features_ranges[param]["nbins"]
        ts_table = f"""
            (SELECT _i AS tm
             FROM UNNEST(SEQUENCE(0, {nbins})) AS _u(_i)) y"""

        if features_ranges[param]["type"] == str:
            val = features_ranges[param]["values"]
            if isinstance(val, str):
                val = [val]
            val = " UNION ALL ".join([f"(SELECT '{v}' AS \"{param}\")" for v in val])
            sql += [f"({val}) x{idx}"]

        elif features_ranges[param]["type"] == float:
            lower, upper = features_ranges[param]["range"]
            h = (upper - lower) / nbins
            sql += [
                f'(SELECT CAST({lower} + {h} * tm AS DOUBLE) AS "{param}" '
                f"FROM {ts_table}) x{idx}"
            ]

        elif features_ranges[param]["type"] == int:
            lower, upper = features_ranges[param]["range"]
            h = (upper - lower) / nbins
            sql += [
                f'(SELECT CAST({lower} + {h} * tm AS INTEGER) AS "{param}" '
                f"FROM {ts_table}) x{idx}"
            ]

        elif features_ranges[param]["type"] == datetime.date:
            start_date, number_of_days = features_ranges[param]["range"]
            h = number_of_days / nbins
            sql += [
                f"(SELECT DATE_ADD('day', CAST({h} * tm AS INTEGER), "
                f"DATE '{start_date}') AS \"{param}\" FROM {ts_table}) x{idx}"
            ]

        elif features_ranges[param]["type"] == datetime.datetime:
            start_date, number_of_days = features_ranges[param]["range"]
            h = number_of_days / nbins
            sql += [
                f"(SELECT DATE_ADD('second', CAST({h} * tm * 86400 AS BIGINT), "
                f"CAST(DATE '{start_date}' AS TIMESTAMP)) AS \"{param}\" "
                f"FROM {ts_table}) x{idx}"
            ]

        elif features_ranges[param]["type"] == bool:
            sql += [
                f'((SELECT false AS "{param}") UNION ALL '
                f'(SELECT true AS "{param}")) x{idx}'
            ]

        else:
            ptype = features_ranges[param]["type"]
            raise ValueError(f"Parameter {param}: Type {ptype} is not supported.")

    query = f"SELECT * FROM {' CROSS JOIN '.join(sql)}"

    return VastFrame(query)
