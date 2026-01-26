"""
SPDX-License-Identifier: Apache-2.0
"""

import re
from typing import Any, Union, TYPE_CHECKING

from vastorbit.connection.errors import QueryError

from vastorbit._utils._object import create_new_vdc
from vastorbit._utils._sql._cast import to_category
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import quote_ident
from vastorbit.errors import QueryError as vQueryError

from vastorbit.core.string_sql.base import StringSQL

from vastorbit.core.vastframe._io import vDFInOut
from vastorbit.core.vastframe._sys import vDCSystem

from vastorbit.sql.dtypes import get_data_types

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFEval(vDFInOut):
    def __setattr__(self, attr: str, val: Any) -> None:
        obj_type = None
        if hasattr(val, "object_type"):
            obj_type = val.object_type

        if isinstance(val, (str, StringSQL, int, float)) and obj_type != "VastColumn":
            val = str(val)
            if self.is_colname_in(attr):
                self[attr].apply(func=val)
            else:
                self.eval(name=attr, expr=val)
        elif obj_type == "VastColumn" and not val._init:
            final_trans, n = val._init_transf, len(val._transf)
            for i in range(1, n):
                final_trans = val._transf[i][0].replace("{}", final_trans)
            self.eval(name=attr, expr=final_trans)
        else:
            self.__dict__[attr] = val

    def __setitem__(self, index: str, val: Any) -> None:
        setattr(self, index, val)

    @save_vastorbit_logs
    def eval(self, name: str, expr: Union[str, StringSQL]) -> "VastFrame":
        """
        Evaluates a customized expression.

        Parameters
        ----------
        name: str
            Name of the new VastColumn.
        expr: str
            Expression  in pure SQL used to compute the new
            feature.
            For example:
            'CASE WHEN "column" > 3 THEN 2 ELSE NULL END' and
            'POWER("column", 2)' will work.

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

        Let's create a new feature named "family_size".

        .. code-block:: python

            data.eval(
                name = "family_size",
                expr = "parch + sibsp + 1",
            )

        .. ipython:: python
            :suppress:

            res = data.eval(
                name = "family_size",
                expr = "parch + sibsp + 1",
            )
            html_file = open("figures/core_VastFrame_eval1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_eval1.html

        .. note::
            You can observe that a new feature "family_size" is added
            to the VastFrame.

        .. note::

            You can also create a feature in a Pandas-like way by assigning
            a result to a VastColumn. For example, similar to the above,
            the ``eval`` operation can be expressed as:

            .. code-block:: python

                data["family_size"] = data["parch"] + data["sibsp"] + 1

            Or:

            .. code-block:: python

                data["family_size"] = "parch + sibsp + 1"

        Let's use custom SQL code evaluation to create a new feature
        named "has_life_boat".

        .. code-block:: python

            data.eval(
                name = "has_life_boat",
                expr = "CASE WHEN boat IS NULL THEN 0 ELSE 1 END",
            )

        .. ipython:: python
            :suppress:

            res = data.eval(
                name = "has_life_boat",
                expr = "CASE WHEN boat IS NULL THEN 0 ELSE 1 END",
            )
            html_file = open("figures/core_VastFrame_eval2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_eval2.html

        .. note::

            You can also create a feature in a Pandas-like way by assigning
            a result to a VastColumn. For example, similar to the above,
            the ``eval`` operation can be expressed as:

            .. code-block:: python

                data["has_life_boat"] = "CASE WHEN boat IS NULL THEN 0 ELSE 1 END"

            Or:

            .. code-block:: python

                from vastorbit.sql.functions import case_when

                data["has_life_boat"] = case_when(data["boat"] == None, 0, 1)

        .. note::

            You can observe that a new feature "has_life_boat" is added
            to the VastFrame.

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.analytic` : Advanced analytical function.
        """
        if isinstance(expr, StringSQL):
            expr = str(expr)
        name = quote_ident(name.replace('"', "_"))
        if self.is_colname_in(name):
            raise NameError(
                f"A VastColumn has already the alias {name}.\n"
                "By changing the parameter 'name', you'll "
                "be able to solve this issue."
            )
        try:
            query = f"SELECT {expr} AS {name} FROM {self} LIMIT 0"
            ctype = get_data_types(
                query,
                name[1:-1].replace("'", "''"),
            )
        except QueryError:
            raise vQueryError(
                f"The expression '{expr}' seems to be incorrect.\nBy "
                "turning on the SQL with the 'set_option' function, "
                "you'll print the SQL code generation and probably "
                "see why the evaluation didn't work."
            )

        category = "undefined"
        if not ctype:
            ctype = "undefined"
        else:
            category = to_category(ctype=ctype)
        all_cols, max_floor = self.get_columns(), 0
        for column in all_cols:
            column_str = column.replace('"', "")
            if (quote_ident(column) in expr) or (
                re.search(re.compile(f"\\b{column_str}\\b"), expr)
            ):
                max_floor = max(len(self[column]._transf), max_floor)
        transformations = [
            (
                "___vastorbit_UNDEFINED___",
                "___vastorbit_UNDEFINED___",
                "___vastorbit_UNDEFINED___",
            )
            for i in range(max_floor)
        ] + [(expr, ctype, category)]
        new_VastColumn = create_new_vdc(
            name, parent=self, transformations=transformations
        )
        setattr(self, name, new_VastColumn)
        setattr(self, name.replace('"', ""), new_VastColumn)
        new_VastColumn._init = False
        new_VastColumn._init_transf = name
        self._vars["columns"] += [name]
        self._add_to_history(
            f"[Eval]: A new VastColumn {name} was added to the VastFrame."
        )
        return self


class vDCEval(vDCSystem):
    def __setattr__(self, attr: str, val: Any) -> None:
        self.__dict__[attr] = val
