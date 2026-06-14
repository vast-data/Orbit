"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import math
from typing import Literal, Optional, TYPE_CHECKING

from vastorbit.connection.errors import QueryError

from vastorbit._typing import NoneType, SQLColumns
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.core.vastframe._text import vDFText, vDCText

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFScaler(vDFText):
    @save_vastorbit_logs
    def scale(
        self,
        columns: Optional[SQLColumns] = None,
        method: Literal["zscore", "robust_zscore", "minmax"] = "zscore",
    ) -> "VastFrame":
        """
        Scales the input VastColumns using the input method.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all
            numerical VastColumns are used.
        method: str, optional
            Method used to scale the data.
             - zscore:
                Normalization using the Z-Score.

                .. math::

                    Z_{score}(x) = (x - x_{avg}) / x_{std}

             - robust_zscore:
                Normalization using the Robust Z-Score.

                .. math::

                    Z_{rscore}(x) = (x - x_{med}) / (1.4826 * x_{mad})

             - minmax:
                Normalization using the MinMax.

                .. math::

                    Z_{minmax}(x) = (x - x_{min}) / (x_{max} - x_{min})

        Returns
        -------
        VastFrame
            self

        Examples
        ---------

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

        For this example, we will use the Titanic dataset.

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

        Let's look at the "fare" and "age" of the passengers.

        .. code-block:: python

            data[["age", "fare"]]

        .. ipython:: python
            :suppress:

            res = data.select(["age", "fare"])
            html_file = open("figures/core_VastFrame_scaler_scale1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_scaler_scale1.html

        .. note::
            You can observe that "age" and "fare" features lie in
            different numerical intervals so it's probably a good
            idea to normalize them.

        Let's use the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.scale` method to
        normalize the data.

        .. code-block:: python

            data.scale(
                method = "minmax",
                columns = ["age", "fare"],
            )
            data[["age", "fare"]]

        .. ipython:: python
            :suppress:

            data.scale(
                method = "minmax",
                columns = ["age", "fare"],
            )
            res = data[["age", "fare"]]
            html_file = open("figures/core_VastFrame_scaler_scale2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_scaler_scale2.html

        .. note::

            You can observe that both "age" and "fare" features now scale
            in [0,1] interval.
        """
        columns = format_type(columns, dtype=list)
        no_cols = len(columns) == 0
        columns = self.numcol() if not columns else self.format_colnames(columns)
        for column in columns:
            if self[column].isnum() and not self[column].isbool():
                self[column].scale(method=method)
            elif (no_cols) and (self[column].isbool()):
                pass
            else:
                warning_message = (
                    f"The VastColumn {column} was skipped.\n"
                    "Scaler only accept numerical data types."
                )
                print_message(warning_message, "warning")
        return self

    normalize = scale


class vDCScaler(vDCText):
    @save_vastorbit_logs
    def scale(
        self,
        method: Literal["zscore", "robust_zscore", "minmax"] = "zscore",
        by: Optional[SQLColumns] = None,
        return_trans: bool = False,
    ) -> "VastFrame":
        """
        Scales the input VastColumns using the input method.

        Parameters
        ----------
        method: str, optional
            Method used to scale the data.
             - zscore:
                Normalization using the Z-Score.

                .. math::

                    Z_{score}(x) = (x - x_{avg}) / x_{std}

             - robust_zscore:
                Normalization using the Robust Z-Score.

                .. math::

                    Z_{rscore}(x) = (x - x_{med}) / (1.4826 * x_{mad})

             - minmax:
                Normalization using the MinMax.

                .. math::

                    Z_{minmax}(x) = (x - x_{min}) / (x_{max} - x_{min})
        by: SQLColumns, optional
            VastColumns used in the partition.
        return_trans: bool, optimal
            If  set to True,  the method  returns the  transformation
            used instead of the parent VastFrame. This parameter is used
            for testing purposes.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

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

        For this example, we will use the Titanic dataset.

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

        Let's look at the "fare" and "age" of the passengers.

        .. code-block:: python

            data[["age", "fare"]]

        .. ipython:: python
            :suppress:

            res = data.select(["age", "fare"])
            html_file = open("figures/core_VastFrame_scaler_scale1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_scaler_scale1.html

        .. note::
            You can observe that "age" and "fare" features lie
            in different numerical intervals so it's probably a
            good idea to normalize them.

        Let's use the ``VastColumn.``:py:meth:`~vastorbit.VastColumn.scale` method to
        normalize the data.

        .. code-block:: python

            data["age"].scale(method = "minmax")
            data["fare"].scale(method = "minmax")
            data[["age", "fare"]]

        .. ipython:: python
            :suppress:

            data["age"].scale(method = "minmax")
            data["fare"].scale(method = "minmax")
            res = data[["age", "fare"]]
            html_file = open("figures/core_VastFrame_scaler_scale2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_scaler_scale2.html

        .. note::
            You can observe that both "age" and "fare" features now scale
            in [0,1] interval.
        """
        method = method.lower()
        by = format_type(by, dtype=list)
        by = self._parent.format_colnames(by)
        nullifzero, n = 1, len(by)

        if self.isbool():
            warning_message = "Scaler doesn't work on booleans"
            print_message(warning_message, "warning")

        elif self.isnum():
            if method == "zscore":
                if n == 0:
                    nullifzero = 0
                    avg, stddev = self.aggregate(["avg", "std"]).values[self._alias]
                    if stddev == 0:
                        warning_message = (
                            f"Can not scale {self} using a "
                            "Z-Score - The Standard Deviation is null !"
                        )
                        print_message(warning_message, "warning")
                        return self
                elif (n == 1) and (self._parent[by[0]].nunique() < 50):
                    try:
                        result = _executeSQL(
                            query=f"""
                                SELECT 
                                    /*+LABEL('VastColumn.scale')*/ 
                                    {by[0]}, 
                                    AVG({self}), 
                                    STDDEV({self}) 
                                FROM {self._parent} GROUP BY {by[0]}""",
                            title="Computing the different categories to scale.",
                            method="fetchall",
                        )
                        for i in range(len(result)):
                            if not isinstance(result[i][2], NoneType) and math.isnan(
                                result[i][2]
                            ):
                                result[i][2] = None
                        cast = self._parent[by[0]].ctype().upper()
                        if cast == "FLOAT":
                            cast = "DOUBLE"
                        avg = "CASE {} {} END".format(
                            by[0],
                            " ".join(
                                [
                                    "WHEN {} THEN {}".format(
                                        (
                                            "CAST('{}' AS {})".format(
                                                str(x[0]).replace("'", "''"), cast
                                            )
                                            if not isinstance(x[0], NoneType)
                                            else "NULL"
                                        ),
                                        (
                                            x[1]
                                            if not isinstance(x[1], NoneType)
                                            else "NULL"
                                        ),
                                    )
                                    for x in result
                                    if not isinstance(x[1], NoneType)
                                ]
                            ),
                        )
                        stddev = "CASE {} {} END".format(
                            by[0],
                            " ".join(
                                [
                                    "WHEN {} THEN {}".format(
                                        (
                                            "CAST('{}' AS {})".format(
                                                str(x[0]).replace("'", "''"), cast
                                            )
                                            if not isinstance(x[0], NoneType)
                                            else "NULL"
                                        ),
                                        (
                                            x[2]
                                            if not isinstance(x[2], NoneType)
                                            else "NULL"
                                        ),
                                    )
                                    for x in result
                                    if not isinstance(x[2], NoneType)
                                ]
                            ),
                        )
                        _executeSQL(
                            query=f"""
                                SELECT 
                                    /*+LABEL('VastColumn.scale')*/ 
                                    {avg},
                                    {stddev} 
                                FROM {self._parent} 
                                LIMIT 1""",
                            print_time_sql=False,
                        )
                    except QueryError:
                        avg, stddev = (
                            f"AVG({self}) OVER (PARTITION BY {', '.join(by)})",
                            f"STDDEV({self}) OVER (PARTITION BY {', '.join(by)})",
                        )
                else:
                    avg, stddev = (
                        f"AVG({self}) OVER (PARTITION BY {', '.join(by)})",
                        f"STDDEV({self}) OVER (PARTITION BY {', '.join(by)})",
                    )
                nullifzero = "NULLIF" if (nullifzero) else ""
                nullifzero_end = ", 0" if (nullifzero) else ""
                if return_trans:
                    return f"({self} - {avg}) / {nullifzero}({stddev}{nullifzero_end})"
                else:
                    final_transformation = [
                        (
                            f"({{}} - {avg}) / {nullifzero}({stddev}{nullifzero_end})",
                            "float",
                            "float",
                        )
                    ]

            elif method == "robust_zscore":
                if n > 0:
                    warning_message = (
                        "The method 'robust_zscore' is available only if the "
                        "parameter 'by' is empty\nIf you want to scale the data by "
                        "grouping by elements, please use a method in zscore|minmax"
                    )
                    print_message(warning_message, "warning")
                    return self
                mad, med = self.aggregate(["mad", "approx_median"]).values[self._alias]
                mad *= 1.4826
                if mad != 0:
                    if return_trans:
                        return f"({self} - {med}) / ({mad})"
                    else:
                        final_transformation = [
                            (
                                f"({{}} - {med}) / ({mad})",
                                "float",
                                "float",
                            )
                        ]
                else:
                    warning_message = (
                        f"Can not scale {self} using a "
                        "Robust Z-Score - The MAD is null !"
                    )
                    print_message(warning_message, "warning")
                    return self

            elif method == "minmax":
                if n == 0:
                    nullifzero = 0
                    cmin, cmax = self.aggregate(["min", "max"]).values[self._alias]
                    if cmax - cmin == 0:
                        warning_message = (
                            f"Can not scale {self} using "
                            "the MIN and the MAX. MAX = MIN !"
                        )
                        print_message(warning_message, "warning")
                        return self
                elif n == 1:
                    try:
                        result = _executeSQL(
                            query=f"""
                                SELECT 
                                    /*+LABEL('VastColumn.scale')*/ 
                                    {by[0]}, 
                                    MIN({self}), 
                                    MAX({self})
                                FROM {self._parent} 
                                GROUP BY {by[0]}""",
                            title=f"Computing the different categories {by[0]} to scale.",
                            method="fetchall",
                        )
                        cast = self._parent[by[0]].ctype().upper()
                        if cast == "FLOAT":
                            cast = "DOUBLE"
                        cmin = "CASE {} {} END".format(
                            by[0],
                            " ".join(
                                [
                                    "WHEN {} THEN {}".format(
                                        (
                                            "CAST('{}' AS {})".format(
                                                str(x[0]).replace("'", "''"), cast
                                            )
                                            if not isinstance(x[0], NoneType)
                                            else "NULL"
                                        ),
                                        (
                                            x[1]
                                            if not isinstance(x[1], NoneType)
                                            else "NULL"
                                        ),
                                    )
                                    for x in result
                                    if not isinstance(x[1], NoneType)
                                ]
                            ),
                        )
                        cmax = "CASE {} {} END".format(
                            by[0],
                            " ".join(
                                [
                                    "WHEN {} THEN {}".format(
                                        (
                                            "CAST('{}' AS {})".format(
                                                str(x[0]).replace("'", "''"), cast
                                            )
                                            if not isinstance(x[0], NoneType)
                                            else "NULL"
                                        ),
                                        (
                                            x[2]
                                            if not isinstance(x[2], NoneType)
                                            else "NULL"
                                        ),
                                    )
                                    for x in result
                                    if not isinstance(x[2], NoneType)
                                ]
                            ),
                        )
                        _executeSQL(
                            query=f"""
                                SELECT 
                                    /*+LABEL('VastColumn.scale')*/ 
                                    {cmax}, 
                                    {cmin} 
                                FROM {self._parent} 
                                LIMIT 1""",
                            print_time_sql=False,
                        )
                    except QueryError:
                        cmax, cmin = (
                            f"MAX({self}) OVER (PARTITION BY {', '.join(by)})",
                            f"MIN({self}) OVER (PARTITION BY {', '.join(by)})",
                        )
                else:
                    cmax, cmin = (
                        f"MAX({self}) OVER (PARTITION BY {', '.join(by)})",
                        f"MIN({self}) OVER (PARTITION BY {', '.join(by)})",
                    )
                nullifzero = "NULLIF" if (nullifzero) else ""
                nullifzero_end = ", 0" if (nullifzero) else ""
                if return_trans:
                    return f"({self} - {cmin}) / {nullifzero}({cmax} - {cmin}{nullifzero_end})"
                else:
                    final_transformation = [
                        (
                            f"({{}} - {cmin}) / {nullifzero}({cmax} - {cmin}{nullifzero_end})",
                            "float",
                            "float",
                        )
                    ]

            if method != "robust_zscore":
                max_floor = 0
                for elem in by:
                    if len(self._parent[elem]._transf) > max_floor:
                        max_floor = len(self._parent[elem]._transf)
                max_floor -= len(self._transf)
                self._transf += [("{}", self.ctype(), self.category())] * max_floor
            self._transf += final_transformation
            sauv = copy.deepcopy(self._catalog)
            self._parent._update_catalog(erase=True, columns=[self._alias])

            parent_cnt = self._parent.shape()[0]

            if "count" in sauv:
                self._catalog["count"] = sauv["count"]
                if parent_cnt == 0:
                    self._catalog["percent"] = 100
                else:
                    self._catalog["percent"] = 100 * sauv["count"] / parent_cnt

            for elem in sauv:
                if "top" in elem:
                    if "percent" in elem:
                        self._catalog[elem] = sauv[elem]
                    elif isinstance(elem, NoneType):
                        self._catalog[elem] = None
                    elif method == "robust_zscore":
                        self._catalog[elem] = (sauv[elem] - sauv["approx_50%"]) / (
                            1.4826 * sauv["mad"]
                        )
                    elif method == "zscore":
                        self._catalog[elem] = (sauv[elem] - sauv["mean"]) / sauv["std"]
                    elif method == "minmax":
                        self._catalog[elem] = (sauv[elem] - sauv["min"]) / (
                            sauv["max"] - sauv["min"]
                        )

            if method == "robust_zscore":
                self._catalog["median"] = 0
                self._catalog["mad"] = 1 / 1.4826
            elif method == "zscore":
                self._catalog["mean"] = 0
                self._catalog["std"] = 1
            elif method == "minmax":
                self._catalog["min"] = 0
                self._catalog["max"] = 1
            self._parent._add_to_history(
                f"[Scaler]: The VastColumn '{self}' was "
                f"scaled with the method '{method}'."
            )
        else:
            raise TypeError("The VastColumn must be numerical for Normalization")
        return self._parent

    normalize = scale
