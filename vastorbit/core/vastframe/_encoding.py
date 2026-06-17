"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
import math
from typing import Literal, Optional, TYPE_CHECKING

import vastorbit._config.config as conf
from vastorbit._typing import PythonNumber, SQLColumns
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._object import get_VAST_mllib, create_new_vdc
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._cast import to_varchar
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.core.string_sql.base import StringSQL

from vastorbit.core.vastframe._fill import vDFFill, vDCFill

from vastorbit.sql.drop import drop
from vastorbit.sql.functions import case_when, decode

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFEncode(vDFFill):
    @save_vastorbit_logs
    def case_when(self, name: str, *args) -> "VastFrame":
        """
        Creates a new feature by evaluating on
        provided conditions.

        Parameters
        ----------
        name: str
            Name of the new feature.
        args: object
            Any number of Expressions.
            The expression is generated in the following format:

            - even:
                CASE ... WHEN args[2 * i] THEN args[2 * i + 1] ... END
            - odd :
                CASE ... WHEN args[2 * i] THEN args[2 * i + 1] ... ELSE args[n] END

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

        Let's create a new feature "age_category".

        .. code-block:: python

            data.case_when(
                "age_category",
                data["age"] < 12, "children",
                data["age"] < 18, "teenagers",
                data["age"] > 60, "seniors",
                data["age"] < 25, "young adults",
                "adults"
            )
            data[["age", "age_category"]]

        .. ipython:: python
            :suppress:

            data.case_when(
                "age_category",
                data["age"] < 12, "children",
                data["age"] < 18, "teenagers",
                data["age"] > 60, "seniors",
                data["age"] < 25, "young adults",
                "adults"
            )
            res = data[["age", "age_category"]]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_casewhen.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_casewhen.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates an expression.
        """
        return self.eval(name=name, expr=case_when(*args))

    @save_vastorbit_logs
    def one_hot_encode(
        self,
        columns: Optional[SQLColumns] = None,
        max_cardinality: int = 12,
        prefix_sep: str = "_",
        drop_first: bool = True,
        use_numbers_as_suffix: bool = False,
    ) -> "VastFrame":
        """
        Encodes the VastColumns  using the One Hot Encoding
        algorithm.

        Parameters
        ----------
        columns: SQLColumns, optional
            List  of the VastColumns used to train the  One
            Hot Encoding model. If empty, only the VastColumns
            with  a cardinality  less than 'max_cardinality'
            are used.
        max_cardinality: int, optional
            Cardinality  threshold  used to  determine whether the
            VastColumn is taken into account during the encoding
            This parameter is used only if the parameter 'columns'
            is empty.
        prefix_sep: str, optional
            Prefix delimitor of the dummies names.
        drop_first: bool, optional
            Drops  the  first  dummy  to  avoid  the  creation  of
            correlated features.
        use_numbers_as_suffix: bool, optional
            Uses  numbers  as suffix instead of  the  VastColumns
            categories.

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

        Let's select few categorical features

        .. code-block:: python

            data = data.select(["pclass", "sex", "survived", "embarked"])
            data

        .. ipython:: python
            :suppress:

            data = data.select(["pclass", "sex", "survived", "embarked"])
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe1.html

        Let's apply encoding on all the VastColumns of the datasets

        .. code-block:: python

            data.one_hot_encode()

        .. ipython:: python
            :suppress:

            res = data.one_hot_encode()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe2.html

        Let's apply encoding on two specific VastColumns viz. "pclass" and "embarked"

        .. code-block:: python

            data = data.select(["pclass", "sex", "survived", "embarked"])
            data.one_hot_encode(columns = ["pclass", "embarked"])

        .. ipython:: python
            :suppress:

            data = data.select(["pclass", "sex","survived", "embarked"])
            res = data.one_hot_encode(columns = ['pclass', 'embarked'])
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe3.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe3.html

        Let's apply encoding on all features having cardinality less than 3

        .. code-block:: python

            data = data.select(["pclass", "sex", "survived", "embarked"])
            data.one_hot_encode(
                max_cardinality = 3,
                drop_first = False,
            )

        .. ipython:: python
            :suppress:
            :okwarning:

            data = data.select(["pclass", "sex", "survived", "embarked"])
            res = data.one_hot_encode(
                max_cardinality = 3,
                drop_first = False,
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe4.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe4.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.label_encode` : Label Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.mean_encode` : Mean Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.discretize` : Discretization.
        """
        columns = format_type(columns, dtype=list)
        columns = self.format_colnames(columns)
        if len(columns) == 0:
            columns = self.get_columns()
        cols_hand = True if (columns) else False
        for column in columns:
            if self[column].nunique(True) < max_cardinality:
                self[column].one_hot_encode(
                    "", prefix_sep, drop_first, use_numbers_as_suffix
                )
            elif cols_hand:
                warning_message = (
                    f"The VastColumn '{column}' was ignored because of "
                    "its high cardinality.\nIncrease the parameter "
                    "'max_cardinality' to solve this issue or use "
                    "directly the VastColumn one_hot_encode method."
                )
                print_message(warning_message, "warning")
        return self

    get_dummies = one_hot_encode


class vDCEncode(vDCFill):
    @save_vastorbit_logs
    def cut(
        self,
        breaks: list,
        labels: Optional[list] = None,
        include_lowest: bool = True,
        right: bool = True,
    ) -> "VastFrame":
        """
        Discretizes the VastColumn using the input list.

        Parameters
        ----------
        breaks: list
            List of values used to cut the VastColumn.
        labels: list, optional
            Labels used  to name the new categories.  If empty,
            names are generated.
        include_lowest: bool, optional
            If  set to  True,  the lowest element of the  list
            is included.
        right: bool, optional
            How the intervals should be closed. If set to True,
            the intervals are closed on the right.

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

        Let's look at "age" VastColumn

        .. code-block:: python

            data["age"]

        .. ipython:: python
            :suppress:

            res = data["age"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut1.html

        Let's look at the distribution of age.

        .. code-block:: python

            data["age"].bar()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            res = data["age"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut2.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut2.html

        Let's discretize "age" using the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.cut` method.

        .. code-block:: python

            data["age"].cut([0, 15, 80])
            data["age"]

        .. ipython:: python
            :suppress:

            data["age"].cut([0, 15, 80])
            res = data["age"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut3.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut3.html

        Let's look at the distribution of age again.

        .. code-block:: python

            data["age"].bar()

        .. ipython:: python
            :suppress:

            res = data["age"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut4.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut4.html

        Let's discretize "fare" using the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.cut` method.

        .. code-block:: python

            data["fare"].cut(
                [0, 15, 800],
                right = False,
                include_lowest = False
            )
            data["fare"]

        .. ipython:: python
            :suppress:

            data["fare"].cut(
                [0, 15, 800],
                right = False,
                include_lowest = False
            )
            res = data["fare"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut5.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut5.html

        Let's look at the distribution of fare.

        .. code-block:: python

            data["fare"].bar()

        .. ipython:: python
            :suppress:

            res = data["fare"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut6.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut6.html

        Let's discretize "parch" using the ``VastFrame.``:py:meth:`~vastorbit.VastFrame.cut` method.

        .. code-block:: python

            data["parch"].cut(
                [0, 5, 10],
                right = False,
                include_lowest = False,
                labels = ["small", "big"]
            )
            data["parch"]

        .. ipython:: python
            :suppress:
            :okwarning:

            data["parch"].cut(
                [0, 5, 10],
                right = False,
                include_lowest = False,
                labels = ["small", "big"]
            )
            res = data["parch"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut7.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut7.html

        Let's look at the distribution of parch.

        .. code-block:: python

            data["parch"].bar()

        .. ipython:: python
            :suppress:

            res = data["parch"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut8.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_cut8.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.label_encode` : Label Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.mean_encode` : Mean Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.one_hot_encode` : One Hot Encoding.
        """
        labels = format_type(labels, dtype=list)
        assert self.isnum() or self.isdate(), TypeError(
            "cut only works on numerical / date-like VastColumns."
        )
        assert len(breaks) >= 2, ValueError(
            "Length of parameter 'breaks' must be greater or equal to 2."
        )
        assert len(breaks) == len(labels) + 1 or not labels, ValueError(
            "Length of parameter breaks must be equal to the length of parameter "
            "'labels' + 1 or parameter 'labels' must be empty."
        )
        conditions, column = [], self._alias
        for idx in range(len(breaks) - 1):
            first_elem, second_elem = breaks[idx], breaks[idx + 1]
            q = ""
            if isinstance(first_elem, str) or isinstance(second_elem, str):
                q = "'"
            if right:
                op1, op2, close_l, close_r = "<", "<=", "]", "]"
            else:
                op1, op2, close_l, close_r = "<=", "<", "[", "["
            if idx == 0 and include_lowest:
                op1, close_l = "<=", "["
            elif idx == 0:
                op1, close_l = "<", "]"
            if labels:
                label = labels[idx]
            else:
                label = f"{close_l}{first_elem};{second_elem}{close_r}"
            conditions += [
                f"{q}{first_elem}{q} {op1} {column} AND {column} {op2} {q}{second_elem}{q} THEN '{label}'"
            ]
        expr = "CASE WHEN " + " WHEN ".join(conditions) + " END"
        self.apply(func=expr)

    @save_vastorbit_logs
    def decode(self, *args) -> "VastFrame":
        """
        Encodes the VastColumn using a user-defined encoding.

        Parameters
        ----------
        args: object
            Any number of expressions.
            The expression is generated in the following format:

            - even:
                CASE ... WHEN VastColumn = args[2 * i]
                THEN args[2 * i + 1] ... END

            - odd :
                CASE ... WHEN VastColumn = args[2 * i]
                THEN args[2 * i + 1] ... ELSE args[n] END

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

        Let's encode "sex" VastColumn and represent "female" category as 1 and
        "male" category as 0.

        .. code-block:: python

            data["sex"].decode("female", 1, "male", 0, 2)
            data["sex"]

        .. ipython:: python
            :suppress:

            data["sex"].decode("female", 1, "male", 0, 2)
            res = data["sex"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_decode.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_decode.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.case_when` : Conditional Statement.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates an expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.label_encode` : Label Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.mean_encode` : Mean Encoding.
        """
        return self.apply(func=decode(StringSQL("{}"), *args))

    @save_vastorbit_logs
    def discretize(
        self,
        method: Literal["auto", "same_width", "same_freq", "topk"] = "auto",
        h: PythonNumber = 0,
        nbins: int = -1,
        k: int = 6,
        new_category: str = "Others",
        return_enum_trans: bool = False,
    ) -> "VastFrame":
        """
        Discretizes the VastColumn using the input method.

        Parameters
        ----------
        method: str, optional
            The method used to discretize the VastColumn:

            - auto:
                Uses method 'same_width' for numerical
                VastColumns, casts the other types to varchar.
            - same_freq:
                Computes bins  with the same number of elements.
            - same_width:
                Computes regular width bins.
            - topk:
                Keeps the topk most frequent categories
                and  merge the  other  into one  unique
                category.
        h: PythonNumber, optional
            The  interval  size  used  to  convert  the VastColumn.
            If this parameter is equal to 0, an optimised interval is
            computed.
        nbins: int, optional
            Number of bins  used for the discretization  (must be > 1)
        k: int, optional
            The integer k of the 'topk' method.
        new_category: str, optional
            The  name of the  merging  category when using the  'topk'
            method.
        return_enum_trans: bool, optional
            Returns  the transformation instead of the VastFrame parent,
            and does not apply the transformation. This parameter is
            useful for testing the look of the final transformation.

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

        Let's look at "age" VastColumn

        .. code-block:: python

            data["age"]

        .. ipython:: python
            :suppress:

            res = data["age"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize1.html

        Let's look at the distribution of age.

        .. code-block:: python

            data["age"].bar()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            res = data["age"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize2.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize2.html

        Let's discretize "age" using the same bar width.

        .. code-block:: python

            data["age"].discretize(method = "same_width", h = 10)
            data["age"]

        .. ipython:: python
            :suppress:

            data["age"].discretize(method = "same_width", h = 10)
            res = data["age"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize3.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize3.html

        Let's look at the distribution of age again.

        .. code-block:: python

            data["age"].bar()

        .. ipython:: python
            :suppress:

            res = data["age"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize4.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize4.html

        Let's discretize "age" using the same frequency per bin.

        .. code-block:: python

            data = vod.load_titanic() # Reloading the dataset
            data["age"].discretize(method = "same_freq", nbins = 5)
            data["age"]

        .. ipython:: python
            :suppress:

            data = vod.load_titanic()
            data["age"].discretize(method = "same_freq", nbins = 5)
            res = data["age"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize5.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize5.html

        Let's look at the distribution of age again.

        .. code-block:: python

            data["age"].bar()

        .. ipython:: python
            :suppress:

            res = data["age"].bar()
            res.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize6.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_discretize6.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.label_encode` : Label Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.mean_encode` : Mean Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.one_hot_encode` : One Hot Encoding.
        """
        vml = get_VAST_mllib()
        if method == "topk":
            assert k >= 2, ValueError(
                "Parameter 'k' must be greater or equals to 2 in "
                "case of discretization using the method 'topk'"
            )
            distinct = self.topk(k).values["index"]
            category_str = to_varchar(self.category())
            X_str = ", ".join([f"""'{str(x).replace("'", "''")}'""" for x in distinct])
            new_category_str = new_category.replace("'", "''")
            trans = (
                f"""(CASE 
                        WHEN {category_str} IN ({X_str})
                        THEN CAST({category_str} AS VARCHAR)
                        ELSE '{new_category_str}' 
                     END)""",
                "varchar",
                "text",
            )
        elif self.isnum() and method == "same_freq":
            assert nbins >= 2, ValueError(
                "Parameter 'nbins' must be greater or equals to 2 in case "
                "of discretization using the method 'same_freq'"
            )
            count = self.count()
            nb = int(float(count / int(nbins)))
            assert nb != 0, Exception(
                "Not enough values to compute the Equal Frequency discretization"
            )
            total, query, nth_elems = nb, [], []
            while total < int(float(count / int(nbins))) * int(nbins):
                nth_elems += [str(total)]
                total += nb
            possibilities = ", ".join(["1"] + nth_elems + [str(count)])
            where = f"WHERE _vastorbit_row_nb_ IN ({possibilities})"
            query = f"""
                SELECT /*+LABEL('VastColumn.discretize')*/ 
                    {self} 
                FROM (SELECT 
                        {self}, 
                        ROW_NUMBER() OVER (ORDER BY {self}) AS _vastorbit_row_nb_ 
                      FROM {self._parent} 
                      WHERE {self} IS NOT NULL) VASTORBIT_SUBTABLE {where}"""
            result = _executeSQL(
                query=query,
                title="Computing the equal frequency histogram bins.",
                method="fetchall",
            )
            result = [elem[0] for elem in result]
        elif self.isnum() and not (self.isbool()) and method in ("same_width", "auto"):
            if not h or h <= 0:
                if nbins <= 0:
                    h = self.numh()
                else:
                    h = (self.max() - self.min()) * 1.01 / nbins
                if h > 0.01:
                    h = round(h, 2)
                elif h > 0.0001:
                    h = round(h, 4)
                elif h > 0.000001:
                    h = round(h, 6)
                if self.category() == "int":
                    h = int(max(math.floor(h), 1))
            floor_end = -1 if (self.category() == "int") else ""
            if (h > 1) or (self.category() == "float"):
                trans = (
                    f"'[' || CAST(FLOOR({{}} / {h}) * {h} AS VARCHAR) || ';' || CAST((FLOOR({{}} / {h}) * {h} + {h}{floor_end}) AS VARCHAR) || ']'",
                    "varchar",
                    "text",
                )
            else:
                trans = ("CAST(FLOOR({}) AS VARCHAR)", "varchar", "text")
        else:
            trans = ("CAST({} AS VARCHAR)", "varchar", "text")
        if self.isnum() and method == "same_freq":
            n = len(result)
            trans = "(CASE "
            for i in range(1, n):
                trans += f"""
                    WHEN {{}} 
                        BETWEEN {result[i - 1]} 
                        AND {result[i]} 
                    THEN '[{result[i - 1]};{result[i]}]' """
            trans += " ELSE NULL END)"
            trans = (trans, "varchar", "text")
        if return_enum_trans:
            return trans
        else:
            self._transf += [trans]
            sauv = copy.deepcopy(self._catalog)
            self._parent._update_catalog(erase=True, columns=[self._alias])
            if "count" in sauv:
                self._catalog["count"] = sauv["count"]
                parent_cnt = self._parent.shape()[0]
                if parent_cnt == 0:
                    self._catalog["percent"] = 100
                else:
                    self._catalog["percent"] = 100 * sauv["count"] / parent_cnt
            self._parent._add_to_history(
                f"[Discretize]: The VastColumn {self} was discretized."
            )
        return self._parent

    @save_vastorbit_logs
    def one_hot_encode(
        self,
        prefix: Optional[str] = None,
        prefix_sep: str = "_",
        drop_first: bool = True,
        use_numbers_as_suffix: bool = False,
    ) -> "VastFrame":
        """
        Encodes the VastColumn with  the One-Hot Encoding algorithm.

        Parameters
        ----------
        prefix: str, optional
            Prefix of the dummies.
        prefix_sep: str, optional
            Prefix delimitor of the dummies.
        drop_first: bool, optional
            Drops the first dummy to avoid the creation of correlated
            features.
        use_numbers_as_suffix: bool, optional
            Uses  numbers  as  suffix  instead  of  the  VastColumns
            categories.

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

        Let's select few categorical features

        .. code-block:: python

            data = data.select(["pclass", "sex", "survived", "embarked"])
            data

        .. ipython:: python
            :suppress:

            data = data.select(["pclass", "sex", "survived", "embarked"])
            res = data
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe1.html

        Let's apply encoding on "embarked" VastColumn.

        .. code-block:: python

            data["embarked"].one_hot_encode()

        .. ipython:: python
            :suppress:

            res = data["embarked"].one_hot_encode()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe5.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe5.html

        Let's use numbers as suffix instead of category names.

        .. code-block:: python

            data = data.select(["pclass", "sex", "survived", "embarked"])
            data["embarked"].one_hot_encode(use_numbers_as_suffix = True)

        .. ipython:: python
            :suppress:
            :okwarning:

            data = data.select(["pclass", "sex", "survived", "embarked"])
            res = data["embarked"].one_hot_encode(use_numbers_as_suffix = True)
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe6.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_ohe6.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.label_encode` : Label Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.mean_encode` : Mean Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.discretize` : Discretization.
        """
        distinct_elements = self.distinct()
        if distinct_elements not in ([0, 1], [1, 0]) or self.isbool():
            all_new_features = []
            if not prefix:
                prefix = self._alias.replace('"', "") + prefix_sep.replace('"', "_")
            else:
                prefix = prefix.replace('"', "_") + prefix_sep.replace('"', "_")
            n = 1 if drop_first else 0
            for k in range(len(distinct_elements) - n):
                distinct_elements_k = str(distinct_elements[k]).replace('"', "_")
                if use_numbers_as_suffix:
                    name = f'"{prefix}{k}"'
                else:
                    name = f'"{prefix}{distinct_elements_k}"'
                assert not self._parent.is_colname_in(name), NameError(
                    "A VastColumn has already the alias of one of "
                    f"the dummies ({name}).\nIt can be the result "
                    "of using previously the method on the VastColumn "
                    "or simply because of ambiguous columns naming."
                    "\nBy changing one of the parameters ('prefix', "
                    "'prefix_sep'), you'll be able to solve this "
                    "issue."
                )
            for k in range(len(distinct_elements) - n):
                distinct_elements_k = str(distinct_elements[k]).replace("'", "''")
                if use_numbers_as_suffix:
                    name = f'"{prefix}{k}"'
                else:
                    name = f'"{prefix}{distinct_elements_k}"'
                name = (
                    name.replace(" ", "_")
                    .replace("/", "_")
                    .replace(",", "_")
                    .replace("'", "_")
                )
                expr = f"CASE CAST({{}} AS VARCHAR) WHEN '{distinct_elements_k}' THEN 1 ELSE 0 END"
                transformations = self._transf + [(expr, "bool", "int")]
                new_VastColumn = create_new_vdc(
                    name,
                    parent=self._parent,
                    transformations=transformations,
                    catalog={
                        "min": 0,
                        "max": 1,
                        "count": self._parent.shape()[0],
                        "percent": 100.0,
                        "unique": 2,
                        "approx_unique": 2,
                        "prod": 0,
                    },
                )
                setattr(self._parent, name, new_VastColumn)
                setattr(self._parent, name.replace('"', ""), new_VastColumn)
                self._parent._vars["columns"] += [name]
                all_new_features += [name]
            conj = "s were " if len(all_new_features) > 1 else " was "
            self._parent._add_to_history(
                "[Get Dummies]: One hot encoder was applied to the VastColumn "
                f"{self}\n{len(all_new_features)} feature{conj}created: "
                f"{', '.join(all_new_features)}."
            )
        return self._parent

    get_dummies = one_hot_encode

    @save_vastorbit_logs
    def label_encode(self) -> "VastFrame":
        """
        Encodes the  VastColumn using  a bijection from the different
        categories to [0, n - 1] (n being the VastColumn cardinality).

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

        Let's encode "embarked" VastColumn

        .. code-block:: python

            data["embarked"].label_encode()
            data["embarked"]

        .. ipython:: python
            :suppress:

            data["embarked"].label_encode()
            res = data["embarked"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_label_encode.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_label_encode.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.mean_encode` : Mean Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.discretize` : Discretization.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.one_hot_encode` : One Hot Encoding.
        """
        if self.category() in ["date", "float"]:
            warning_message = (
                "label_encode is only available for categorical variables."
            )
            print_message(warning_message, "warning")
        else:
            distinct_elements = self.distinct()
            encoding, text_info = [], "\n"
            for i, elem in enumerate(distinct_elements):
                text_info += f"\t{elem} => {i}"
                encoding += [elem, i]
            encoding += [len(distinct_elements)]
            self.apply(func=decode(StringSQL("{}"), *encoding))
            self._parent._update_catalog(erase=True, columns=[self._alias])
            self._catalog["count"] = self._parent.shape()[0]
            self._catalog["percent"] = 100
            self._parent._add_to_history(
                "[Label Encoding]: Label Encoding was applied to the VastColumn"
                f" {self} using the following mapping:{text_info}"
            )
        return self._parent

    @save_vastorbit_logs
    def mean_encode(self, response: str) -> "VastFrame":
        """
        Encodes the VastColumn using the average of the response
        partitioned by the different VastColumn categories.

        Parameters
        ----------
        response: str
            Response VastColumn.

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

        Let's look at the avg of survived partitioned by embarked

        .. code-block:: python

            data.groupby(["embarked"], ["AVG(survived) AS survived"])

        .. ipython:: python
            :suppress:

            res = data.groupby(["embarked"], ["AVG(survived) AS survived"])
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_mean_encode1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_mean_encode1.html

        Let's apply mean encoding which will replace each category of
        "embarked" VastColumn by the average of the response

        .. code-block:: python

            data["embarked"].mean_encode(response = "survived")
            data["embarked"]

        .. ipython:: python
            :suppress:

            data["embarked"].mean_encode(response = "survived")
            res = data["embarked"]
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_encoding_mean_encode2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_encoding_mean_encode2.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.decode` : User Defined Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.label_encode` : Label Encoding.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.discretize` : Discretization.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.one_hot_encode` : One Hot Encoding.
        """
        response = self._parent.format_colnames(response)
        assert self._parent[response].isnum(), TypeError(
            "The response column must be numerical to use a mean encoding"
        )
        max_floor = len(self._parent[response]._transf) - len(self._transf)
        self._transf += [("{}", self.ctype(), self.category())] * max_floor
        self._transf += [
            (
                f"AVG({response}) OVER (PARTITION BY {{}})",
                "int",
                "float",
            )
        ]
        self._parent._update_catalog(erase=True, columns=[self._alias])
        self._parent._add_to_history(
            f"[Mean Encode]: The VastColumn {self} was transformed "
            f"using a mean encoding with {response} as Response Column."
        )
        print_message("The mean encoding was successfully done.")
        return self._parent
