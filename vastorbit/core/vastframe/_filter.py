"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import secrets
from typing import Literal, Optional, Union, TYPE_CHECKING
from collections.abc import Iterable

from vastorbit.connection.errors import QueryError

import vastorbit._config.config as conf
from vastorbit._typing import (
    NoneType,
    PythonNumber,
    PythonScalar,
    SQLColumns,
    SQLExpression,
    TimeInterval,
)
from vastorbit._utils._object import create_new_vdf
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import clean_query, format_type, quote_ident
from vastorbit._utils._sql._sys import _executeSQL
from vastorbit._utils._sql._random import _seeded_random_function

from vastorbit.core.vastframe._aggregate import vDFAgg, vDCAgg

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFFilter(vDFAgg):
    @save_vastorbit_logs
    def at_time(self, ts: str, time: TimeInterval) -> "VastFrame":
        """
        Filters the VastFrame  by only keeping the records at the
        input time.

        Parameters
        ----------
        ts: str
            TS (Time Series) VastColumn used to filter the data.
            The VastColumn type must be date (date, datetime,
            timestamp...).
        time: TimeInterval
            Input Time. For example, time = '12:00' will filter the
            data when time('ts') is equal to 12:00.

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

        For this example, we will use a dummy time-series data:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "time": [
                        "1993-11-03 00:00:00",
                        "1993-11-03 00:00:01",
                        "1993-11-03 00:00:02",
                        "1993-11-04 00:00:01",
                        "1993-11-04 00:00:02",
                    ],
                    "val": [0., 1., 2., 4., 5.],
                }
            )["time"].astype("timestamp")

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_at_time_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_at_time_data.html

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

        In the above data, we have values for two dates.
        We can use the ``at_time`` filter to get the required
        time-stamp values:

        .. code-block:: python

            vdf.at_time(ts = "time", time = "00:00:01")

        .. ipython:: python
            :suppress:

            res = vdf.at_time(ts = "time", time = "00:00:01")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_at_time_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_at_time_res.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.between` : Filters between two conditions.
        """
        self.filter(
            f"CAST({self.format_colnames(ts)} AS TIME) = CAST('{time}' AS TIME)"
        )
        return self

    @save_vastorbit_logs
    def balance(
        self,
        column: str,
        method: Literal["over", "under"] = "under",
        x: float = 0.5,
        order_by: Optional[SQLColumns] = None,
    ) -> "VastFrame":
        """
        Balances the dataset using the input method.

        .. warning::

            If the data is not sorted, the generated
            SQL code may differ between attempts.

        Parameters
        ----------
        column: str
            Column used to compute the different categories.
        method: str, optional
            The method with which to sample the data.

             - over:
                Oversampling.
             - under:
                Undersampling.

        x: float, optional
            The desired ratio between the majority class and minority
            classes.
        order_by: SQLColumns, optional
            VastColumns used to sort the data.

        Returns
        -------
        VastFrame
            balanced VastFrame

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

        For this example, we will create a toy imbalanced
        dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "category" : [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                    "val": [12, 12, 14, 15, 10, 9, 10, 12, 12, 14, 16],
                }
            )

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_data.html

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

        In the above data, we can see that there are many more
        0s than 1s in the category column. We can conveniently
        plot the historgram to visualize the skewness:

        .. code-block:: python

            vdf["category"].hist()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = vdf["category"].hist(width = 300)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_hist_before.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_hist_before.html

        Now we can use the ``balance`` function to
        fix this:

        .. ipython:: python

            balanced_vdf = vdf.balance(column="category", x = 0.5)

        .. ipython:: python
            :suppress:

            res = balanced_vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_data_2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_data_2.html

        .. note::

            By giving ``x`` value of 0.5, we have ensured
            that the ratio between the two classes is not
            more skewed than this.

        Let's visualize the distribution after the balancing.

        .. code-block:: python

            balanced_vdf["category"].hist()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = balanced_vdf["category"].hist(width = 300)
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_hist_after.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_balance_hist_after.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.between` : Filters between two conditions.
        """
        if not 0 <= x <= 1:
            raise ValueError("Parameter 'x' must be between 0 and 1")
        order_by = format_type(order_by, dtype=list)
        column, order_by = self.format_colnames(column, order_by)
        topk = self[column].topk()
        min_cnt = topk["count"][-1]
        min_class = topk["index"][-1]
        max_cnt = topk["count"][0]
        n = len(topk["index"])
        dtype = self[column].dtype()
        if method == "under":
            vdf = self.search(f"{column} = CAST('{min_class}' AS {dtype})")
            for i in range(n - 1):
                cnt = int(max(topk["count"][i] * (1.0 - x), min_cnt))
                vdf = vdf.append(
                    self.search(
                        f"{column} = CAST('{topk['index'][i]}' AS {dtype})"
                    ).sample(n=cnt)
                )
        elif method == "over":
            vdf = self.copy()
            for i in range(1, n):
                cnt_i, cnt = topk["count"][i], 0
                limit = int(max_cnt * x) - cnt_i
                while cnt <= limit:
                    vdf_i = self.search(
                        f"{column} = CAST('{topk['index'][i]}' AS {dtype})"
                    )
                    if cnt + cnt_i > limit:
                        vdf = vdf.append(vdf_i.sample(n=limit - cnt))
                        break
                    else:
                        vdf = vdf.append(vdf_i)
                    cnt += cnt_i
        else:
            raise ValueError(f"Unrecognized method: '{method}'.")
        vdf.sort(order_by)
        return vdf

    @save_vastorbit_logs
    def between(
        self,
        column: str,
        start: Optional[PythonScalar] = None,
        end: Optional[PythonScalar] = None,
        inplace: bool = True,
    ) -> "VastFrame":
        """
        Filters the VastFrame by only keeping the records between two
        input elements.

        Parameters
        ----------
        column: str
            TS (Time  Series)  VastColumn  used to filter the  data.
            The VastColumn  type  must be date (date,  datetime,
            timestamp...)
        start: PythonScalar, optional
            Input Python Scalar used to filter.
        end: PythonScalar, optional
            Input Python Scalar used to filter.
        inplace: bool, optional
            If  set  to  True, the  filtering  is applied  to  the
            VastFrame.

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

        For this example, we will use a dummy time-series data:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "time": [
                        "1993-11-01",
                        "1993-11-02",
                        "1993-11-03",
                        "1993-11-04",
                        "1993-11-05",
                    ],
                    "val": [0., 1., 2., 4.,5.],
                }
            )["time"].astype("timestamp")

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_data.html

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

        Using ``between`` we can easily filter through
        time-series values:

        .. code-block:: python

            vdf.between(column = "time", start = "1993-11-02", end = "1993-11-04")

        .. ipython:: python
            :suppress:

            res = vdf.between(column= "time", start= "1993-11-02", end = "1993-11-04")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_res.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.at_time` : Filters the VastFrame at a specific time.
        """
        cast = self[column].ctype().upper()
        if cast == "FLOAT":
            cast = "DOUBLE"
        if not isinstance(start, NoneType) and not isinstance(end, NoneType):
            condition = f"BETWEEN CAST('{start}' AS {cast}) AND CAST('{end}' AS {cast})"
        elif not isinstance(start, NoneType):
            condition = f"> CAST('{start}' AS {cast})"
        elif not isinstance(end, NoneType):
            condition = f"< CAST('{end}' AS {cast})"
        else:
            return self.copy() if inplace else self
        filter_function = self.filter if inplace else self.search
        return filter_function(
            f"{self.format_colnames(column)} {condition}",
        )

    @save_vastorbit_logs
    def between_time(
        self,
        ts: str,
        start_time: Optional[TimeInterval] = None,
        end_time: Optional[TimeInterval] = None,
        inplace: bool = True,
    ) -> "VastFrame":
        """
        Filters the VastFrame by only keeping the records between two
        input times.

        Parameters
        ----------
        ts: str
            TS   (Time Series) VastColumn used to filter the  data.
            The  VastColumn type must be date (date,  datetime,
            timestamp...).
        start_time: TimeInterval
            Input Start Time. For example, time = '12:00' will  filter
            the data when time('ts') is lesser than 12:00.
        end_time: TimeInterval
            Input  End Time. For  example, time = '14:00' will  filter
            the data when time('ts') is greater than 14:00.
        inplace: bool, optional
            If set to True, the filtering is applied to the VastFrame.

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

        For this example, we will use a dummy time-series data:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "time": [
                        "1993-11-03 00:00:00",
                        "1993-11-03 00:00:01",
                        "1993-11-03 00:00:02",
                        "1993-11-03 00:00:03",
                        "1993-11-03 00:00:04",
                        "1993-11-04 00:00:01",
                        "1993-11-04 00:00:02",
                    ],
                    "val": [0., 1., 2., 4., 5., 3., 2.],
                }
            )["time"].astype("timestamp")

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_time_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_time_data.html

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

        Using ``between_time`` we can easily filter through
        time-series values:

        .. code-block:: python

            vdf.between_time(ts= "time", start_time= "00:00:01", end_time = "00:00:03")

        .. ipython:: python
            :suppress:

            res = vdf.between_time(ts= "time", start_time= "00:00:01", end_time = "00:00:03")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_time_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_between_time_res.html

        Notice that the function ignores the dates, and outputs
        all the times in that range. This is because it is
        only using the time information from ``ts`` column
        and ignoring the date information.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.between` : Filters between two conditions.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.at_time` : Filters the VastFrame at a specific time.
        """
        if not isinstance(start_time, NoneType) and not (
            isinstance(end_time, NoneType)
        ):
            condition = (
                f"BETWEEN CAST('{start_time}' AS TIME) AND CAST('{end_time}' AS TIME)"
            )
        elif not isinstance(start_time, NoneType):
            condition = f"> CAST('{start_time}' AS TIME)"
        elif not isinstance(end_time, NoneType):
            condition = f"< CAST('{end_time}' AS TIME)"
        else:
            raise ValueError(
                "One of the parameters 'start_time' or 'end_time' must be defined."
            )
        filter_function = self.filter if inplace else self.search
        return filter_function(
            f"CAST({self.format_colnames(ts)} AS TIME) {condition}",
        )

    @save_vastorbit_logs
    def drop(self, columns: Optional[SQLColumns] = None) -> "VastFrame":
        """
        Drops  the input VastColumns  from the VastFrame.  Dropping
        VastColumns means they are not selected in the final SQL code
        generation.

        .. warning::

            Be careful when using this method. It can make the VastFrame
            structure  heavier if other  VastColumns are  computed
            using the dropped VastColumns.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names.

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

        For this example, we will use a dummy dataset with
        three columns:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "col1": [1, 2, 3],
                    "col2": [3, 3, 1],
                    "col":['a', 'b', 'v']
                }
            )

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_data.html

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

        Using ``drop`` we can take out any column that we
        do not need:

        .. ipython:: python

            vdf.drop("col1")

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_res.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop_duplicates` : Drops the VastFrame duplicates.
        """
        columns = format_type(columns, dtype=list)
        columns = self.format_colnames(columns)
        for column in columns:
            self[column].drop()
        return self

    @save_vastorbit_logs
    def drop_duplicates(self, columns: Optional[SQLColumns] = None) -> "VastFrame":
        """
        Filters the duplicates using a partition by the input
        VastColumns.

        .. warning::

            Dropping  duplicates  will make the  VastFrame
            structure heavier. It is recommended that you
            check the   current   structure   using   the
            ``current_relation``  method and save it using
            the ``to_db`` method, using the parameters
            ``inplace = True`` and ``relation_type = table``.

        Parameters
        ----------
        columns: SQLColumns, optional
            List  of  the VastColumns names.  If empty,  all
            VastColumns are selected.

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

        For this example, we will use a dummy dataset with
        three columns:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "col1": [1, 2, 3, 1],
                    "col2": [3, 3, 1, 3],
                    "col":['a', 'b', 'v', 'a'],
                }
            )

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_duplicates_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_duplicates_data.html

        In the above dataset, notice that the **first**
        and **last** entries are identical i.e. duplicates.

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

        Using ``drop_duplicates`` we can take out any duplicates:

        .. code-block:: python

            vdf.drop_duplicates()

        .. ipython:: python
            :suppress:

            res = vdf.drop_duplicates()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_duplicates_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_drop_duplicates_res.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop` : Drops the VastFrame input columns.
        """
        columns = format_type(columns, dtype=list)
        count = self.duplicated(columns=columns, count=True)
        if count:
            columns = (
                self.get_columns() if not columns else self.format_colnames(columns)
            )
            name = (
                "__vastorbit_duplicated_index__"
                + str(secrets.randbelow(10000001))
                + "_"
            )
            self.eval(
                name=name,
                expr=f"""ROW_NUMBER() OVER (PARTITION BY {", ".join(columns)})""",
            )
            self.filter(f'"{name}" = 1')
            self._vars["exclude_columns"] += [f'"{name}"']
        print_message("No duplicates detected.")
        return self

    @save_vastorbit_logs
    def dropna(self, columns: Optional[SQLColumns] = None) -> "VastFrame":
        """
        Filters the specified VastColumns in a VastFrame for
        missing values.

        Parameters
        ----------
        columns: SQLColumns, optional
            List  of  the VastColumns  names. If  empty,  all
            VastColumns are selected.

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

        For this example, we will use the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        In the above dataset, notice that the **first**
        and **last** entries are identical i.e. duplicates.

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

        We can see the count of each column to check
        if any column has missing values.

        .. code-block:: python

            vdf.count()

        .. ipython:: python
            :suppress:

            res = vdf.count()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_count.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_count.html

        From the above table, we can see that there are
        multiple columns with missing/NA values.

        Using ``dropna``, we can select which columns
        do we want the dataset to filter by:

        .. ipython:: python

            vdf.dropna(columns = ["fare", "embarked", "age"])

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_dropna_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_dropna_res.html

        Now again, if we look at the count, we will
        notice that the total count has decreased.

        .. code-block:: python

            vdf.count()

        .. ipython:: python
            :suppress:

            res = vdf.count()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_count_2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_fillna_count_2.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop` : Drops the VastFrame input columns.
        """
        columns = format_type(columns, dtype=list)
        columns = self.format_colnames(columns)
        if len(columns) == 0:
            columns = self.get_columns()
        total = self.shape()[0]
        print_info = conf.get_option("print_info")
        for column in columns:
            conf.set_option("print_info", False)
            self[column].dropna()
            conf.set_option("print_info", print_info)
            total -= self.shape()[0]
            if total == 0:
                print_message("Nothing was filtered.")
            elif total > 0:
                conj = "s were " if total > 1 else " was "
                print_message(f"{total} element{conj}filtered.")
        return self

    @save_vastorbit_logs
    def filter(
        self, conditions: Union[None, list, str] = None, *args, **kwargs
    ) -> "VastFrame":
        """
        Filters  the VastFrame using the  input  expressions.

        Parameters
        ----------
        conditions: SQLExpression, optional
            List of expressions. For example, to keep only the
            records where the VastColumn 'column' is greater
            than 5 and less than 10, you can write:
            ``['"column" > 5', '"column" < 10']``.
        force_filter: bool, optional
            Default Value: True
            When set to True, the VastFrame will be modified
            even if no filtering occurred. This parameter can
            be used to enforce filtering  and ensure pipeline
            consistency.
        raise_error: bool, optional
            Default Value: False
            If set to True and the input filtering is incorrect,
            an error is raised.

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

        For this example, we will use the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

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

        Using ``filter``, we can create custom filters:

        .. code-block:: python

            vdf.filter("sex = 'female' AND pclass = 1")

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_filter_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_filter_res.html

        .. note::

            Similarly, the same can be done in a Pandas-like way:

            .. code-block:: python

                vdf.filter((vdf["sex"] == "female") && (vdf["pclass"] == 1))

            Or:

            .. code-block:: python

                vdf = vdf[(vdf["sex"] == "female") && (vdf["pclass"] == 1)]

            .. warning::

                Ensure to use the ``&&`` operator and correctly place parentheses.
                The ``and`` operator is specific to Python, and its behavior cannot
                be changed.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop` : Drops the VastFrame input columns.
        """
        force_filter = True
        if "force_filter" in kwargs:
            force_filter = kwargs["force_filter"]
        raise_error = False
        if "raise_error" in kwargs:
            raise_error = kwargs["raise_error"]
        count = self.shape()[0]
        conj = "s were " if count > 1 else " was "
        if not isinstance(conditions, str) or (args):
            if isinstance(conditions, str) or not isinstance(conditions, Iterable):
                conditions = [conditions]
            elif isinstance(conditions, NoneType):
                conditions = []
            else:
                conditions = list(conditions)
            conditions += list(args)
            for condition in conditions:
                self.filter(
                    str(condition),
                    print_info=False,
                    raise_error=raise_error,
                    force_filter=force_filter,
                )
            count -= self.shape()[0]
            if count > 0:
                print_message(f"{count} element{conj}filtered")
                self._add_to_history(
                    f"[Filter]: {count} element{conj}filtered "
                    f"using the filter '{conditions}'"
                )
            print_message("Nothing was filtered.")
        else:
            max_pos = 0
            columns_tmp = copy.deepcopy(self._vars["columns"])
            for column in columns_tmp:
                max_pos = max(max_pos, len(self[column]._transf) - 1)
            new_count = self.shape()[0]
            self._vars["where"] += [(conditions, max_pos)]
            try:
                new_count = _executeSQL(
                    query=f"""
                        SELECT 
                            /*+LABEL('VastFrame.filter')*/ 
                            COUNT(*) 
                        FROM {self}""",
                    title="Computing the new number of elements.",
                    method="fetchfirstelem",
                )
                count -= new_count
            except QueryError as e:
                del self._vars["where"][-1]
                warning_message = (
                    f"The expression '{conditions}' is incorrect.\n"
                    "Nothing was filtered."
                )
                print_message(warning_message, "warning")
                if raise_error:
                    raise (e)
                return self
            if count > 0 or force_filter:
                self._update_catalog(erase=True)
                self._vars["count"] = new_count
                conj = "s were " if count > 1 else " was "
                print_message(f"{count} element{conj}filtered.")
                conditions_clean = clean_query(conditions)
                self._add_to_history(
                    f"[Filter]: {count} element{conj}filtered using "
                    f"the filter '{conditions_clean}'"
                )
            else:
                del self._vars["where"][-1]
                print_message("Nothing was filtered.")
        return self

    @save_vastorbit_logs
    def first(self, ts: str, offset: str) -> "VastFrame":
        """
        Filters the VastFrame by only keeping the first records.

        Parameters
        ----------
        ts: str
            TS (Time Series) VastColumn used to filter the
            data. The VastColumn type must be date (date,
            datetime, timestamp...)
        offset: str
            Interval offset. For example, to filter and keep only
            the first 6 months of records, offset should be set
            to '6 months'.
            Format: '1 day', '6 months', '2 hours', etc.

        Returns
        -------
        VastFrame
            self

        Examples
        --------
        .. code-block:: python

            import vastorbit as vo

            vdf = vo.VastFrame({
                "time": [
                    "1993-11-01",
                    "1993-11-02",
                    "1993-11-03",
                    "1993-11-04",
                    "1993-11-05",
                ],
                "val": [0., 1., 2., 4., 5.],
            })

            vdf["time"].astype("timestamp")

            # Keep first 1 day of records
            vdf.first(ts="time", offset="1 day")

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.last` : Filters the VastFrame by only keeping the last records.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.at_time` : Filters the VastFrame at a specific time.
        """
        ts = self.format_colnames(ts)

        # Parse offset (e.g., "1 day", "6 months")
        interval_value, interval_unit = self._parse_interval(offset)

        first_date = _executeSQL(
            query=f"""
                SELECT 
                    /*+LABEL('VastFrame.first')*/ 
                    CAST(MIN({ts}) + INTERVAL '{interval_value}' {interval_unit} AS VARCHAR)
                FROM {self}""",
            title="Getting the VastFrame first values.",
            method="fetchfirstelem",
        )

        self.filter(f"{ts} <= CAST('{first_date}' AS TIMESTAMP)")
        return self

    @save_vastorbit_logs
    def isin(self, val: dict) -> "VastFrame":
        """
        Checks whether specific records are in the VastFrame
        and returns the new VastFrame of the search.

        Parameters
        ----------
        val: dict
            Dictionary of the different records. Each key of the
            dictionary must represent a VastColumn. For example,
            to check  if Badr Ouali and Fouad Teban  are in  the
            VastFrame. You can write the following dict:
            ``{"name": ["Teban", "Ouali"], "surname": ["Fouad", "Badr"]}``

        Returns
        -------
        VastFrame
            The VastFrame of the search.

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

        For this example, we will use a dummy dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "val": [3, 4, 5, 10, 12, 23],
                    "cat": ['A', 'B', 'A', 'C', 'A', 'C'],
                }
            )

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_isin_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_isin_data.html

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

        Using ``isin`` we can easily filter through
        to get the desired results:

        .. code-block:: python

            vdf.isin({"cat": ['A'], "val": [12]})

        .. ipython:: python
            :suppress:

            res = vdf.isin({"cat": ['A'], "val": [12]})
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_isin_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_isin_res.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.at_time` : Filters the VastFrame at a specific time.
        """
        val = self.format_colnames(val)
        n = len(val[list(val.keys())[0]])
        result = []
        for i in range(n):
            tmp_query = []
            for column in val:
                cast = self[column].ctype().upper()
                if cast == "FLOAT":
                    cast = "DOUBLE"
                if isinstance(val[column][i], NoneType):
                    tmp_query += [f"{quote_ident(column)} IS NULL"]
                else:
                    val_str = str(val[column][i]).replace("'", "''")
                    tmp_query += [
                        f"{quote_ident(column)} = CAST('{val_str}' AS {cast})"
                    ]
            result += [" AND ".join(tmp_query)]
        return self.search(" OR ".join(result))

    @save_vastorbit_logs
    def last(self, ts: str, offset: str) -> "VastFrame":
        """
        Filters the VastFrame by only keeping the last records.

        Parameters
        ----------
        ts: str
            TS (Time Series) VastColumn used to filter the
            data. The VastColumn type must be date (date,
            datetime, timestamp...)
        offset: str
            Interval offset. For example, to filter and keep
            only the last 6 months of records, offset should be
            set to '6 months'.
            Format: '1 day', '6 months', '2 hours', etc.

        Returns
        -------
        VastFrame
            self

        Examples
        --------
        .. code-block:: python

            import vastorbit as vo

            vdf = vo.VastFrame({
                "time": [
                    "1993-11-01",
                    "1993-11-02",
                    "1993-11-03",
                    "1993-11-04",
                    "1993-11-05",
                ],
                "val": [0., 1., 2., 4., 5.],
            })

            vdf["time"].astype("timestamp")

            # Keep last 1 day of records
            vdf.last(ts="time", offset="1 day")

        .. seealso::
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.first` : Filters the VastFrame by only keeping the first records.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.at_time` : Filters the VastFrame at a specific time.
        """
        ts = self.format_colnames(ts)

        # Parse offset (e.g., "1 day", "6 months")
        interval_value, interval_unit = self._parse_interval(offset)

        last_date = _executeSQL(
            query=f"""
                SELECT 
                    /*+LABEL('VastFrame.last')*/ 
                    CAST(MAX({ts}) - INTERVAL '{interval_value}' {interval_unit} AS VARCHAR)
                FROM {self}""",
            title="Getting the VastFrame last values.",
            method="fetchfirstelem",
        )

        self.filter(f"{ts} >= CAST('{last_date}' AS TIMESTAMP)")
        return self

    @save_vastorbit_logs
    def sample(
        self,
        n: Optional[PythonNumber] = None,
        x: Optional[float] = None,
        method: Literal["random", "systematic", "stratified"] = "random",
        by: Optional[SQLColumns] = None,
    ) -> "VastFrame":
        """
        Downsamples the input VastFrame.

        .. warning::

            The result might be inconsistent between
            attempts at SQL code generation if the
            data is not ordered.

        Parameters
        ----------
        n: PythonNumber, optional
            Approximate  number of elements to consider in  the
            sample.
        x: float, optional
            The sample size. For example, if set to 0.33, it
            downsamples to approximatively 33% of the relation.
        method: str, optional
            The Sample method.

             - random:
                Random Sampling.
             - systematic:
                Systematic Sampling.
             - stratified:
                Stratified Sampling.

        by: SQLColumns, optional
            VastColumns used in the partition.

        Returns
        -------
        VastFrame
            sample VastFrame

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

        For this example, we will use the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

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

        We can check the size of the dataset by:

        .. ipython:: python

            len(data)

        For some reason, if we did not need the entire dataset,
        then we can conveniently sample it using the ``sample``
        function:

        .. ipython:: python

            subsample = vdf.sample(x = 0.33)

        .. ipython:: python
            :suppress:

            res = subsample
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_sample_res_1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_sample_res_1.html

        We can check the size of the dataset to confirm
        the size is smaller than the original dataset:

        .. ipython:: python

            len(subsample)

        In the above example, we used the ``x`` parameter
        which corresponds to ratio. We can also use the
        ``n`` parameter which corresponds to the number
        of records to be sampled.

        .. ipython:: python

            subsample = vdf.sample(n = 100)

        To confirm, if we obtained the right size, we can check it:

        .. ipython:: python

            len(subsample)

        In order to tackle data with skewed distributions,
        we can use the ``stratified`` option for the
        ``method``.

        Let us ensure that the classes "pclass" and "sex"
        are proportionally represented:

        .. ipython:: python

            subsample = vdf.sample(
                x = 0.33,
                method = "stratified",
                by = ["pclass", "sex"],
            )

        .. ipython:: python
            :suppress:

            res = subsample
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_sample_res_2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_sample_res_2.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.isin` : Checks whether specific records are in the VastFrame.
        """
        if x == 1:
            return self.copy()
        assert not isinstance(n, NoneType) or not (isinstance(x, NoneType)), ValueError(
            "One of the parameter 'n' or 'x' must not be empty."
        )
        assert isinstance(n, NoneType) or isinstance(x, NoneType), ValueError(
            "One of the parameter 'n' or 'x' must be empty."
        )
        if not isinstance(n, NoneType):
            x = float(n / self.shape()[0])
            if x >= 1:
                return self.copy()
        if isinstance(method, str):
            method = method.lower()
        if method in ("systematic", "random"):
            order_by = ""
            assert not by, ValueError(
                f"Parameter 'by' must be empty when using '{method}' sampling."
            )
        by = format_type(by, dtype=list)
        by = self.format_colnames(by)
        random_int = secrets.randbelow(10000001)
        name = f"__vastorbit_random_{random_int}__"
        name2 = f"__vastorbit_random_{random_int + 1}__"
        vdf = self.copy()
        assert 0 < x < 1, ValueError("Parameter 'x' must be between 0 and 1")
        if method == "random":
            random_state = conf.get_option("random_state")
            random_seed = secrets.randbelow(2000001) - 1000000
            if isinstance(random_state, int):
                random_seed = random_state
            random_func = _seeded_random_function(random_seed)
            vdf.eval(name, random_func)
            q = vdf[name].quantile(x)
            print_info_init = conf.get_option("print_info")
            conf.set_option("print_info", False)
            vdf.filter(f"{name} <= {q}")
            conf.set_option("print_info", print_info_init)
            vdf._vars["exclude_columns"] += [name]
        elif method in ("stratified", "systematic"):
            assert method != "stratified" or (by), ValueError(
                "Parameter 'by' must include at least one "
                "column when using 'stratified' sampling."
            )
            order_by = ""
            if method == "stratified":
                order_by = "ORDER BY " + ", ".join(by)
            vdf.eval(name, f"ROW_NUMBER() OVER({order_by})")
            vdf.eval(
                name2,
                f"""MIN({name}) OVER (PARTITION BY CAST({name} * {x} AS Integer) 
                    ORDER BY {name} ROWS BETWEEN UNBOUNDED PRECEDING AND 0 FOLLOWING)""",
            )
            print_info_init = conf.get_option("print_info")
            conf.set_option("print_info", False)
            vdf.filter(f"{name} = {name2}")
            conf.set_option("print_info", print_info_init)
            vdf._vars["exclude_columns"] += [name, name2]
        return vdf

    @save_vastorbit_logs
    def search(
        self,
        conditions: SQLExpression = "",
        usecols: Optional[SQLColumns] = None,
        expr: Optional[SQLExpression] = None,
        order_by: Union[None, str, dict, list] = None,
    ) -> "VastFrame":
        """
        Searches for elements that match the input
        conditions. This method will return a new VastFrame.

        Parameters
        ----------
        conditions: SQLExpression, optional
            Filters  of  the  search.  It can be a list  of
            conditions or an expression.
        usecols: SQLColumns, optional
            VastColumns   to    select   from  the   final
            VastFrame relation. If empty, all VastColumns
            are selected.
        expr: SQLExpression, optional
            List  of  customized  expressions  in  pure SQL.
            For example: 'column1 * column2 AS my_name'.
        order_by: str / dict / list, optional
            List of the VastColumns used to sort the data,
            using  asc order or a dictionary of all sorting
            methods.  For  example,  to  sort  by  "column1"
            ASC and "column2" DESC, write:
            ``{"column1": "asc", "column2": "desc"}``

        Returns
        -------
        VastFrame
            VastFrame of the search

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

        For this example, we will use the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

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

        We can create a custom search that is looking for
        the family size and survival of the passengers having
        adults of more than 50 year old. We can arrange the
        data in descending order to see who paid the most:

        .. ipython:: python

            vdf.search(
                conditions = ["age > 50"],
                usecols = ["fare", "survived"],
                expr = ["parch + sibsp + 1 AS family_size"],
                order_by = {"fare": "desc"},
            )

        .. ipython:: python
            :suppress:

            res = vdf.search(
                conditions = ["age > 50"],
                usecols = ["fare", "survived"],
                expr = ["parch + sibsp + 1 AS family_size"],
                order_by = {"fare": "desc"},
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_search_res_1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_search_res_1.html

        .. note::

            Similarly, the same can be done in a Pandas-like way:

            .. code-block:: python

                vdf.search(
                    conditions = vdf["age"] > 50,
                    usecols = ["fare", "survived"],
                    expr = ["parch + sibsp + 1 AS family_size"],
                    order_by = {"fare": "desc"},
                )

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.isin` : Checks whether specific records are in the VastFrame.
        """
        order_by, usecols, expr = format_type(order_by, usecols, expr, dtype=list)
        if isinstance(conditions, Iterable) and not isinstance(conditions, str):
            conditions = " AND ".join([f"({c})" for c in conditions])
        if conditions:
            conditions = f" WHERE {conditions}"
        all_cols = ", ".join(["*"] + expr)
        query = f"SELECT {all_cols} FROM {self}{conditions}"
        result = create_new_vdf(query, _clean_query=False)
        if usecols:
            result = result.select(usecols)
        return result.sort(order_by)


class vDCFilter(vDCAgg):
    @save_vastorbit_logs
    def drop(self, add_history: bool = True) -> "VastFrame":
        """
        Drops the  VastColumn from the VastFrame. Dropping a
        VastColumn means it is not selected in the final
        generated SQL code.

        .. warning::

            Dropping a VastColumn  can make the VastFrame
            "heavier" if it is  used to compute other
            VastColumns.

        Parameters
        ----------
        add_history: bool, optional
            If set to True,  the information is stored in
            the VastFrame history.

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

        For this example, we will use a dummy dataset with
        three columns:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "col1": [1, 2, 3],
                    "col2": [3, 3, 1],
                    "col":['a', 'b', 'v'],
                },
            )

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_data.html

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

        Using ``drop`` we can take out any column that we
        do not need:

        .. ipython:: python

            vdf["col1"].drop()

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_res.html

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.drop` : Drops the input VastColumn.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop_duplicates` : Drops the VastFrame duplicates.
        """
        try:
            parent = self._parent
            force_columns = copy.deepcopy(self._parent._vars["columns"])
            force_columns.remove(self._alias)
            _executeSQL(
                query=f"""
                    SELECT 
                        /*+LABEL('VastColumn.drop')*/ * 
                    FROM {self._parent._genSQL(force_columns=force_columns)} 
                    LIMIT 10""",
                print_time_sql=False,
            )
            self._parent._vars["columns"].remove(self._alias)
            delattr(self._parent, self._alias)
        except QueryError:
            self._parent._vars["exclude_columns"] += [self._alias]
        if add_history:
            self._parent._add_to_history(
                f"[Drop]: VastColumn {self} was deleted from the VastFrame."
            )
        return parent

    @save_vastorbit_logs
    def drop_outliers(
        self,
        threshold: PythonNumber = 4.0,
        use_threshold: bool = True,
        alpha: PythonNumber = 0.05,
    ) -> "VastFrame":
        """
        Drops outliers in the VastColumn.

        Parameters
        ----------
        threshold: PythonNumber, optional
            Uses the  Gaussian distribution  to identify outliers.
            After normalizing the data (Z-Score), if the absolute
            value of the record is greater than the threshold, it
            is considered as an outlier.
        use_threshold: bool, optional
            Uses  the threshold instead of the  'alpha' parameter.
        alpha: PythonNumber, optional
            Number  representing  the outliers threshold.  Values
            less   than   quantile(alpha)   or   greater   than
            quantile(1-alpha) are be dropped.

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

            By assigning an alias to :py:mod:`vastorbit`, we mitigate the risk
            of code collisions with other libraries. This precaution is
            necessary because vastorbit uses commonly knowvDC_dropn function names
            like "average" and "median", which can potentially lead to naming
            conflicts. The use of an alias ensures that the functions from
            vastorbit are used as intended without interfering with functions
            from other libraries.

        For this example, we will use a dummy data that has one outlier:

        .. ipython:: python

            vdf = vo.VastFrame({"vals": [20, 10, 0, -20, 10, 20, 1200]})

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_outliers_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_outliers_data.html

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

        Using ``drop_outliers`` we can take out all the outliers in that
        column:

        .. ipython:: python

            vdf["vals"].drop_outliers(threshold = 1.0)

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_outliers_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_drop_outliers_res.html

        .. note::

            By providing a custom threshold value, can have
            more control on the treatment of outliers.

        .. seealso::

            | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.drop` : Drops the input VastColumn.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop_duplicates` : Drops the VastFrame duplicates.
        """
        if use_threshold:
            result = self.aggregate(func=["std", "avg"]).transpose().values
            self._parent.filter(f"""
                    ABS({self} - {result["avg"][0]}) 
                  / {result["std"][0]} < {threshold}""")
        else:
            p_alpha, p_1_alpha = (
                self._parent.quantile([alpha, 1 - alpha], [self._alias])
                .transpose()
                .values[self._alias]
            )
            self._parent.filter(f"({self} BETWEEN {p_alpha} AND {p_1_alpha})")
        return self._parent

    @save_vastorbit_logs
    def dropna(self) -> "VastFrame":
        """
        Filters the VastFrame where the VastColumn is missing.

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

        For this example, we will use the Titanic dataset:

        .. ipython:: python

            from vastorbit.datasets import load_titanic

            vdf = load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        In the above dataset, notice that the **first**
        and **last** entries are identical i.e. duplicates.

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

        We can see the count of each column to check
        if any column has missing values.

        .. code-block:: python

            vdf.count()

        .. ipython:: python
            :suppress:

            res = vdf.count()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_vDC_fillna_count.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_vDC_fillna_count.html

        From the above table, we can see that there are
        a lot of missing values in "boat" column.

        Using ``dropna``, we can filter the entire dataset
        to drop the rows where "boats" does not have a value:

        .. code-block:: python

            vdf["boat"].dropna()

        .. ipython:: python
            :suppress:

            vdf["boat"].dropna()
            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_dropna_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_dropna_res.html

        Now again, if we look at the count, we will
        notice that the total count has decreased
        based on the "boats" column.

        .. code-block:: python

            vdf.count()

        .. ipython:: python
            :suppress:

            res = vdf.count()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_fill_vDC_fillna_count_2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_fill_vDC_fillna_count_2.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.dropna` : Drops the VastFrame missing values.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.drop` : Drops the VastFrame input columns.
        """
        self._parent.filter(f"{self} IS NOT NULL")
        return self._parent

    @save_vastorbit_logs
    def isin(
        self,
        val: Union[PythonScalar, list],
        *args,
    ) -> "VastFrame":
        """
        Checks whether specific records are in the VastColumn and
        returns the new VastFrame of the search.

        Parameters
        ----------
        val: PythonScalar / list
            List of the different  records. For example, to check if
            Badr and Fouad are in the VastColumn, you can write the
            following list: ``["Fouad", "Badr"]``

        Returns
        -------
        VastFrame
            The VastFrame of the search.

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

        For this example, we will use a dummy dataset:

        .. ipython:: python

            vdf = vo.VastFrame(
                {
                    "val": [3, 4, 5, 10, 12, 23],
                    "cat": ['A', 'B', 'A', 'C', 'A', 'C'],
                },
            )

        .. ipython:: python
            :suppress:

            res = vdf
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_isin_data.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_isin_data.html

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

        Using ``isin`` we can easily filter through
        to get the desired results:

        .. code-block:: python

            vdf["cat"].isin('A')

        .. ipython:: python
            :suppress:

            res = vdf["cat"].isin('A')
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_isin_res.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_filter_vDC_isin_res.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.balance` : Balances the VastFrame.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.at_time` : Filters the VastFrame at a specific time.
        """
        if isinstance(val, str) or not isinstance(val, Iterable):
            val = [val]
        val += list(args)
        val = {self._alias: val}
        return self._parent.isin(val)
