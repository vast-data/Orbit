"""
SPDX-License-Identifier: Apache-2.0
"""

from abc import abstractmethod
import re
from typing import Literal, Optional
import numpy as np
import sklearn

from vastorbit.connection.errors import QueryError

from vastorbit._typing import NoneType, SQLColumns, SQLRelation
from vastorbit._utils._gen import gen_tmp_name
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import (
    clean_query,
    format_type,
    quote_ident,
    schema_relation,
)
from vastorbit._utils._sql._sys import _executeSQL


from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame

import vastorbit.machine_learning.memmodel as mm
from vastorbit.machine_learning.vast.base import Unsupervised, VASTModel

from vastorbit.sql.drop import drop

"""
General Functions.
"""


@save_vastorbit_logs
def balance(
    name: str,
    input_relation: str,
    y: str,
    method: Literal["hybrid", "over", "under"] = "hybrid",
    ratio: float = 0.5,
) -> VastFrame:
    """
    Creates a view with an equal distribution of
    the input data based on the response_column.

    Parameters
    ----------
    name: str
        Name of the view.
    input_relation: str
        Relation used to create the new relation.
    y: str
        Response column.
    method: str, optional
        Method used to do the balancing.

        - hybrid:
            Performs  over-sampling   and
            under-sampling  on  different
            classes so that each class is
            equally represented.
        - over:
            Over-samples on  all classes,
            except the most represented
            class, towards the  most
            represented class's cardinality.
        - under:
            Under-samples on  all classes,
            except the least represented
            class,  towards  the least
            represented class's cardinality.

    ratio: float, optional
        The desired ratio between the majority class
        and the minority class. This value has no
        effect when used with the 'hybrid' balance
        method.

    Returns
    -------
    VastFrame
        VastFrame of the created view.

    Examples
    --------

    The following examples provide a basic understanding
    of usage. For more detailed examples, please refer to
    the :ref:`user_guide.machine_learning` or the
    :ref:`examples`
    section on the website.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

    .. ipython:: python
        :suppress:

        import vastorbit.datasets as vod
        data = vod.load_titanic()

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

    Function Application
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``balance`` function:

    .. ipython:: python

        from vastorbit.machine_learning.vast import balance

    Then we can directly apply it to the dataset:

    .. ipython:: python
        :okwarning:
        :suppress:


        vo.drop("balance_model")
        result = balance(
            name = "balance_model",
            input_relation = data,
            y = "survived",
            method = "under",
        )
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_preprocessing_balance.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        balance(
            name = "balance_model",
            input_relation = data,
            y = "survived",
            method = "under",
        )

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_preprocessing_balance.html

    .. seealso::
        | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.sample` : Sampling the dataset.
    """
    method = str(method).lower()
    if method not in ("hybrid", "over", "under"):
        raise ValueError(
            "Parameter 'method' must be one of 'hybrid', 'over' or 'under'."
        )
    ratio = float(ratio)
    if method != "hybrid" and ratio <= 0:
        raise ValueError("Parameter 'ratio' must be strictly positive.")

    vdf = (
        input_relation
        if isinstance(input_relation, VastFrame)
        else VastFrame(input_relation)
    )
    columns = vdf.get_columns()
    y_q = quote_ident(y)
    cols_csv = ", ".join(columns)
    cols_src = ", ".join([f"_src.{col}" for col in columns])
    rel = f"(SELECT {cols_csv} FROM {vdf})"

    if method == "under":
        target_expr = (
            f"LEAST(c._cnt, CAST(ROUND(CAST(s._mn AS double) / {ratio}) AS bigint))"
        )
    elif method == "over":
        target_expr = (
            f"GREATEST(c._cnt, CAST(ROUND(CAST(s._mx AS double) * {ratio}) AS bigint))"
        )
    else:  # hybrid
        target_expr = "s._av"

    query = f"""
        CREATE TABLE {name} AS
        WITH _counts AS (
            SELECT {y_q} AS _cls, COUNT(*) AS _cnt
            FROM {rel} _c
            GROUP BY {y_q}
        ),
        _stats AS (
            SELECT
                MIN(_cnt) AS _mn,
                MAX(_cnt) AS _mx,
                CAST(ROUND(AVG(CAST(_cnt AS double))) AS bigint) AS _av
            FROM _counts
        ),
        _target AS (
            SELECT c._cls, c._cnt, {target_expr} AS _tgt
            FROM _counts c CROSS JOIN _stats s
        ),
        _expanded AS (
            SELECT {cols_src}, t._tgt AS _tgt, random() AS _rand
            FROM {rel} _src
            JOIN _target t ON _src.{y_q} = t._cls
            CROSS JOIN UNNEST(
                sequence(1, CAST(CEIL(CAST(t._tgt AS double) / t._cnt) AS bigint))
            ) AS u(_r)
        ),
        _ranked AS (
            SELECT {cols_csv}, _tgt,
                   ROW_NUMBER() OVER (PARTITION BY {y_q} ORDER BY _rand) AS _rn
            FROM _expanded
        )
        SELECT {cols_csv}
        FROM _ranked
        WHERE _rn <= _tgt
    """
    _executeSQL(
        query=query,
        title="Computing the Balanced Relation.",
    )
    return VastFrame(name)


"""
General Classes.
"""


class Preprocessing(Unsupervised):
    # Properties.

    @property
    @abstractmethod
    def _transform_sql(self) -> str:
        """Must be overridden in child class"""
        raise NotImplementedError

    @property
    @abstractmethod
    def _inverse_transform_sql(self) -> str:
        """Must be overridden in child class"""
        raise NotImplementedError

    # I/O Methods.

    def _get_names(
        self, inverse: bool = False, X: Optional[SQLColumns] = None
    ) -> SQLColumns:
        """
        Returns the Transformation output names.

        Parameters
        ----------
        inverse: bool, optional
            If set to True, returns the inverse transform
            output names.
        X: list, optional
            List of the columns used to get the model output
            names. If empty, the model predictors names are
            used.

        Returns
        -------
        list
            names.
        """
        X = format_type(X, dtype=list)
        X = quote_ident(X)
        if not X:
            X = self.X
        if self._model_type in ("PCA", "SVD", "MCA") and not inverse:
            if self._model_type in ("PCA", "SVD"):
                n = self.parameters["n_components"]
                if not n:
                    n = len(self.X)
            else:
                n = len(self.X)
            return [f"col{i}" for i in range(1, n + 1)]
        elif self._model_type == "OneHotEncoder" and not inverse:
            names = []
            for column in self.X:
                k = 0
                for i in range(len(self.cat_["category_name"])):
                    if quote_ident(self.cat_["category_name"][i]) == quote_ident(
                        column
                    ):
                        if (k != 0 or not self.parameters["drop_first"]) and (
                            not self.parameters["ignore_null"]
                            or not (
                                isinstance(self.cat_["category_level"][i], NoneType)
                            )
                        ):
                            if self.parameters["column_naming"] == "indices":
                                name = f'"{quote_ident(column)[1:-1]}{self.parameters["separator"]}'
                                name += f'{self.cat_["category_level_index"][i]}"'
                                names += [name]
                            else:
                                if not (
                                    isinstance(self.cat_["category_level"][i], NoneType)
                                ):
                                    category_level = self.cat_["category_level"][
                                        i
                                    ].lower()
                                else:
                                    category_level = self.parameters["null_column_name"]
                                name = f'"{quote_ident(column)[1:-1]}{self.parameters["separator"]}'
                                name += f'{category_level}"'
                                names += [name]
                        k += 1
            return names
        else:
            return X

    def deploySQL(
        self,
        X: Optional[SQLColumns] = None,
        key_columns: Optional[SQLColumns] = None,
        exclude_columns: Optional[SQLColumns] = None,
    ) -> str:
        """
        Returns the SQL code needed
        to deploy the model.

        Parameters
        ----------
        X: SQLColumns, optional
            ``list`` of the columns
            used to deploy the model.
            If empty, the model predictors
            are used.
        key_columns: SQLColumns, optional
            Predictors used during the
            algorithm computation which
            will be deployed with the
            principal components.
        exclude_columns: SQLColumns, optional
            Columns to exclude from
            the prediction.

        Returns
        -------
        str
            the SQL code needed
            to deploy the model.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use a dummy dataset.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "values": [1, 1.01, 1.02, 1.05, 1.024],
                }
            )

        Let's import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import Scaler

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = Scaler(method = "zscore")

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        To get the Model VAST
        SQL, use below:

        .. ipython:: python

            model.deploySQL()

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.
        """
        key_columns, exclude_columns = format_type(
            key_columns, exclude_columns, dtype=list
        )
        X = format_type(X, dtype=list, na_out=self.X)
        X = quote_ident(X)
        exclude = set(quote_ident(exclude_columns)) if exclude_columns else set()
        model_X = quote_ident(self.X)

        transform = self.to_memmodel().transform_sql(model_X)
        flat = []
        for expr in transform:
            if isinstance(expr, (list, tuple)):
                flat.extend(expr)
            else:
                flat.append(expr)
        names = self._get_names(X=model_X)
        model_set = set(model_X)
        # columns the model did not transform are passed through unchanged
        projection = [col for col in X if col not in model_set and col not in exclude]
        # transformed (and, for OneHotEncoder, expanded) columns. Some memmodels
        # (OneHotEncoder) already emit ``<expr> AS "name"``; re-aliasing those
        # produces ``... AS "x" AS "y"`` which is a SQL syntax error, so only add
        # an alias when the expression does not already carry one.
        _has_alias = re.compile(r'\s+AS\s+"[^"]+"\s*$', re.IGNORECASE)
        projection += [
            expr if _has_alias.search(expr) else f"{expr} AS {name}"
            for expr, name in zip(flat, names)
        ]
        return clean_query(", ".join(projection))

    def deployInverseSQL(
        self,
        key_columns: Optional[SQLColumns] = None,
        exclude_columns: Optional[SQLColumns] = None,
        X: Optional[SQLColumns] = None,
    ) -> str:
        """
        Returns the SQL code needed
        to deploy the inverse model.

        Parameters
        ----------
        key_columns: SQLColumns, optional
            Predictors used during
            the algorithm computation
            which will be deployed with
            the principal components.
        exclude_columns: SQLColumns, optional
            Columns to exclude from the
            prediction.
        X: SQLColumns, optional
            ``list`` of the columns used
            to deploy the inverse model.
            If empty, the model predictors
            are used.

        Returns
        -------
        str
            the SQL code needed to
            deploy the inverse model.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use a dummy dataset.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "values": [1, 1.01, 1.02, 1.05, 1.024],
                }
            )

        Let's import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import Scaler

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = Scaler(method = "zscore")

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        To get the Model VAST
        Inverse SQL, use below:

        .. ipython:: python

            model.deployInverseSQL()

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.
        """
        if isinstance(X, NoneType):
            X = self.X
        else:
            X = quote_ident(X)
        X, key_columns, exclude_columns = format_type(
            X, key_columns, exclude_columns, dtype=list
        )
        X = quote_ident(X)
        if self._model_type == "OneHotEncoder":
            raise AttributeError(
                "method 'deployInverseSQL' is not supported for OneHotEncoder models."
            )
        exclude = set(quote_ident(exclude_columns)) if exclude_columns else set()
        model_X = quote_ident(self.X)
        memmodel = self.to_memmodel()

        if hasattr(memmodel, "inverse_transform_sql"):
            inverse = memmodel.inverse_transform_sql(model_X)
            flat = []
            for expr in inverse:
                if isinstance(expr, (list, tuple)):
                    flat.extend(expr)
                else:
                    flat.append(expr)
        elif self._model_type == "Scaler":
            flat = self._inverse_scale_sql(model_X)
        else:
            raise NotImplementedError(
                f"Inverse deployment SQL is not available for {self._model_type}."
            )
        expr_by_col = dict(zip(model_X, flat))
        projection = []
        for col in X:
            if col in expr_by_col and col not in exclude:
                projection.append(f"{expr_by_col[col]} AS {col}")
            else:
                projection.append(col)
        return clean_query(", ".join(projection))

    # Prediction / Transformation Methods.

    def transform(
        self, vdf: SQLRelation = None, X: Optional[SQLColumns] = None
    ) -> VastFrame:
        """
        Applies the model on a
        :py:class:`~VastFrame`.

        Parameters
        ----------
        vdf: SQLRelation, optional
            Input VastFrame. You can also
            specify a customized relation,
            but you must  enclose it with
            an alias. For  example:
            ``(SELECT 1) x`` is valid whereas
            ``(SELECT 1)`` and ``SELECT 1``
            are invalid.
        X: SQLColumns, optional
            ``list`` of the input
            :py:class:`~VastColumn`.

        Returns
        -------
        VastFrame
            object result of the
            model transformation.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use a dummy dataset.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "values": [1, 1.01, 1.02, 1.05, 1.024],
                }
            )

        Let's import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import Scaler

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = Scaler(method = "zscore")

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        To get the scaled dataset,
        we can use the ``transform``
        method. Let us transform
        the data:

        .. ipython:: python
            :suppress:
            :okwarning:

            result = model.transform(data)
            html_file = open("SPHINX_DIRECTORY/figures/machine_learning_preprocessing_scaler_transform_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. code-block:: python

            model.transform(data)

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_preprocessing_scaler_transform_1.html

        Similarly, you can perform the
        inverse transform to get the
        original features using:

        .. code-block:: python

            model.inverse_transform(data_transformed)

        The variable ``data_transformed``
        is the scaled dataset.

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.
        """
        if isinstance(X, NoneType):
            X = self.X
        X = format_type(X, dtype=list)
        if not vdf:
            vdf = self.input_relation
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        X = vdf.format_colnames(X)
        exclude_columns = vdf.get_columns(exclude_columns=X)
        all_columns = vdf.get_columns()
        # Pass non-transformed columns (e.g. the response in a pipeline) through
        # unchanged; excluding them here would silently drop them from the output.
        columns = self.deploySQL(all_columns, exclude_columns, [])
        main_relation = f"(SELECT {columns} FROM {vdf}) VASTORBIT_SUBTABLE"
        return VastFrame(main_relation)

    def inverse_transform(
        self, vdf: SQLRelation, X: Optional[SQLColumns] = None
    ) -> VastFrame:
        """
        Applies the Inverse
        Model on a :py:class:`~VastFrame`.

        Parameters
        ----------
        vdf: SQLRelation
            Input VastFrame. You can also
            specify a customized relation,
            but you must  enclose it with
            an alias. For  example:
            ``(SELECT 1) x`` is valid whereas
            ``(SELECT 1)`` and ``SELECT 1``
            are invalid.
        X: SQLColumns, optional
            ``list`` of the input
            :py:class:`~VastColumn`.

        Returns
        -------
        VastFrame
            object result of the
            model transformation.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use a dummy dataset.

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "values": [1, 1.01, 1.02, 1.05, 1.024],
                }
            )

        Let's import the model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import Scaler

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = Scaler(method = "zscore")

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        To get the scaled dataset,
        we can use the ``transform``
        method. Let us transform
        the data:

        .. ipython:: python
            :suppress:
            :okwarning:

            result = model.transform(data)
            html_file = open("SPHINX_DIRECTORY/figures/machine_learning_preprocessing_scaler_transform_1.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. code-block:: python

            model.transform(data)

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_preprocessing_scaler_transform_1.html

        Similarly, you can perform the
        inverse transform to get the
        original features using:

        .. code-block:: python

            model.inverse_transform(data_transformed)

        The variable ``data_transformed``
        is the scaled dataset.

        .. important::

            For this example, a specific model is
            utilized, and it may not correspond
            exactly to the model you are working
            with. To see a comprehensive example
            specific to your class of interest,
            please refer to that particular class.
        """
        X = format_type(X, dtype=list)
        if self._model_type == "OneHotEncoder":
            raise AttributeError(
                "method 'inverse_transform' is not supported for OneHotEncoder models."
            )
        if not vdf:
            vdf = self.input_relation
        if not X:
            X = self._get_names()
        if isinstance(vdf, str):
            vdf = VastFrame(vdf)
        X = vdf.format_colnames(X)
        exclude_columns = vdf.get_columns(exclude_columns=X)
        all_columns = vdf.get_columns()
        inverse_sql = self.deployInverseSQL(
            exclude_columns, exclude_columns, all_columns
        )
        main_relation = f"(SELECT {inverse_sql} FROM {vdf}) VASTORBIT_SUBTABLE"
        return VastFrame(main_relation)


"""
Algorithms used for scaling.
"""


class Scaler(Preprocessing):
    """
    Creates a VAST Scaler object.

    .. rubric:: Attributes

    Many attributes are created
    during the fitting phase.

    **For StandardScaler:**

    ``mean_``: numpy.array
        Model's features means.
    ``std_``: numpy.array
        Model's features standard deviation.

    **For MinMaxScaler:**

    ``min_``: numpy.array
        Model's features minimums.
    ``max_``: numpy.array
        Model's features maximums.

    **For RobustScaler:**

    ``median_``: numpy.array
        Model's features medians.
    ``mad_``: numpy.array
        Model's features median absolute deviations.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.preprocessing.Preprocessing.get_attributes`
        method.

    .. note::

        Several other attributes can be accessed by using the
        :py:meth:`~vastorbit.machine_learning.vast.preprocessing.Preprocessing.get_attributes`
        method.


    Parameters
    ----------
    name: str, optional
        Name of the model.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.
    method: str, optional
        Method used to scale the data.

        - zscore:

        Scaling   using   the   Z-Score

        .. math::

            Z_score = (x - avg) / std

        - robust_zscore:

        Scaling using the Robust Z-Score.

        .. math::

            Z_rscore = (x - median) / (1.4826 * mad)

        - minmax:

        Normalization  using  the  Min  &  Max.

        .. math::

            Z_minmax = (x - min) / (max - min)

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

    For this example, we will
    use a dummy dataset.

    .. ipython:: python

        data = vo.VastFrame(
            {
                "values": [1, 1.01, 1.02, 1.05, 1.024],
            }
        )

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

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``Scaler`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import Scaler

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = Scaler(method = "zscore")

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Fitting
    ^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(data)

    .. important::

        To fit a model, you can directly use the :py:class:`~VastFrame`
        or the name of the relation stored in the database.

    Model Parameters
    ^^^^^^^^^^^^^^^^^

    To fetch the model parameter (mean) you can use:

    .. ipython:: python

        model.mean_

    Similarly for standard deviation:

    .. ipython:: python

        model.std_

    Conversion/Transformation
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    To get the scaled dataset,
    we can use the ``transform``
    method. Let us transform
    the data:

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.transform(data)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_preprocessing_scaler_transform_3.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.transform(data)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_preprocessing_scaler_transform_3.html

    Please refer to
    :py:meth:`~vastorbit.machine_learning.Scaler.transform`
    for more details on transforming
    a :py:class:`~VastFrame`.

    Similarly, you can perform the
    inverse transform to get the
    original features using:

    .. code-block:: python

        model.inverse_transform(data_transformed)

    The variable ``data_transformed``
    is the scaled dataset.

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory representations of
        machine learning models. They can be used for both in-database
        and in-memory prediction tasks. These objects can be pickled
        in the same way that you would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the model use ``MemModel``,
    and it is recommended to use ``MemModel`` directly.

    **SQL**

    To get the SQL query use below:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in Python syntax, use the
    following code:

    .. ipython:: python

        X = [[1]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.preprocessing.Scaler.to_python`
        method is used to scale the data. For specific details on how
        to use this method for different model types, refer to the
        relevant documentation for each model.

    .. seealso::
        | :py:class:`~vastorbit.machine_learning.vast.preprocessing.StandardScaler` :
            Scalar with method set as ``zscore``.
        | :py:class:`~vastorbit.machine_learning.vast.preprocessing.RobustScaler` :
            Scalar with method set as ``robust_zscore``.
        | :py:class:`~vastorbit.machine_learning.vast.preprocessing.MinMaxScaler` :
            Scalar with method set as ``minmax``.
    """

    # Properties.

    @property
    def _fit_sql(self) -> Literal[""]:
        return ""

    @property
    def _sklearn_model(self):
        method = self.method_
        if method == "minmax":
            return sklearn.preprocessing.MinMaxScaler
        elif method == "robust_zscore":
            return sklearn.preprocessing.RobustScaler
        return sklearn.preprocessing.StandardScaler

    @property
    def _transform_sql(self) -> Literal[""]:
        return ""

    @property
    def _inverse_transform_sql(self) -> Literal[""]:
        return ""

    @property
    def _model_subcategory(self) -> Literal["PREPROCESSING"]:
        return "PREPROCESSING"

    @property
    def _model_type(self) -> Literal["Scaler"]:
        return "Scaler"

    @property
    def _attributes(self) -> list[str]:
        if self.method_ == "minmax":
            return ["min_", "max_"]
        elif self.method_ == "robust_zscore":
            return ["median_", "mad_"]
        else:
            return ["mean_", "std_"]

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        method: Literal["zscore", "robust_zscore", "minmax"] = "zscore",
    ) -> None:
        super().__init__(name, overwrite_model)
        self.method_ = str(method).lower()
        self.parameters = {}

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from the fitted ``scikit-learn`` model.
        """
        if self.method_ == "minmax":
            self.min_ = np.asarray(self._model.data_min_, dtype=float)
            self.max_ = np.asarray(self._model.data_max_, dtype=float)
        elif self.method_ == "robust_zscore":
            self.median_ = np.asarray(self._model.center_, dtype=float)
            self.mad_ = np.asarray(self._model.scale_, dtype=float)
        else:
            self.mean_ = np.asarray(self._model.mean_, dtype=float)
            self.std_ = np.asarray(self._model.scale_, dtype=float)

    def _inverse_scale_sql(self, cols: list) -> list:
        """
        Builds the explicit inverse-transform SQL expressions
        (Trino-compatible) for each scaled column.
        """
        method = self.method_
        out = []
        for j, col in enumerate(cols):
            if method == "minmax":
                lo, hi = float(self.min_[j]), float(self.max_[j])
                out.append(f"({col} * ({hi} - {lo}) + {lo})")
            elif method == "robust_zscore":
                center, scale = float(self.median_[j]), float(self.mad_[j])
                out.append(f"({col} * {scale} + {center})")
            else:
                center, scale = float(self.mean_[j]), float(self.std_[j])
                out.append(f"({col} * {scale} + {center})")
        return out

    # I/O Methods.

    def to_memmodel(self) -> mm.Scaler:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.preprocessing.Scaler`
            for more information.
        """
        if self.method_ == "minmax":
            return mm.MinMaxScaler(self.min_, self.max_)
        elif self.method_ == "robust_zscore":
            return mm.StandardScaler(self.median_, self.mad_)
        else:
            return mm.StandardScaler(self.mean_, self.std_)


class StandardScaler(Scaler):
    """
    i.e. Scaler with param method = 'zscore'

    .. note::

        This is a child class. See
        :py:class:`~vastorbit.machine_learning.vast.preprocessing.Scaler`
        for more details and examples.
    """

    @property
    def _attributes(self) -> list[str]:
        return ["mean_", "std_"]

    def __init__(self, name: str = None, overwrite_model: bool = False) -> None:
        super().__init__(name, overwrite_model, "zscore")


class RobustScaler(Scaler):
    """
    i.e. Scaler with param method = 'robust_zscore'

    .. note::

        This is a child class. See
        :py:class:`~vastorbit.machine_learning.vast.preprocessing.Scaler`
        for more details and examples.
    """

    @property
    def _attributes(self) -> list[str]:
        return ["median_", "mad_"]

    def __init__(self, name: str = None, overwrite_model: bool = False) -> None:
        super().__init__(name, overwrite_model, "robust_zscore")


class MinMaxScaler(Scaler):
    """
    i.e. Scaler with param method = 'minmax'

    .. note::

        This is a child class. See
        :py:class:`~vastorbit.machine_learning.vast.preprocessing.Scaler`
        for more details and examples.
    """

    @property
    def _attributes(self) -> list[str]:
        return ["min_", "max_"]

    def __init__(self, name: str = None, overwrite_model: bool = False) -> None:
        super().__init__(name, overwrite_model, "minmax")


"""
Algorithms used for encoding.
"""


class OneHotEncoder(Preprocessing):
    """
    Creates a VAST OneHotEncoder object.

    Parameters
    ----------

    name: str, optional
        Name of the model.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    ``**kwargs``: SKLEARN model parameters.

    .. rubric:: Attributes

    Many attributes are created
    during the fitting phase.

    ``categories_``: numpy.array
        ArrayLike of the categories of the different features.
    ``column_naming_``: str
        Method used to name the model's outputs.
    ``drop_first_``: bool
        If False, the first dummy of each category was dropped.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.preprocessing.Preprocessing.get_attributes`
        method.

    .. note::

        Several other attributes can be accessed by using the
        :py:meth:`~vastorbit.machine_learning.vast.preprocessing.Preprocessing.get_attributes`
        method.

    Examples
    --------

    The following examples provide a
    basic understanding of usage.
    For more detailed examples, please
    refer to the :ref:`user_guide.machine_learning`
    or the :ref:`examples`
    section on the website.

    Load data for machine learning
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``OneHotEncoder`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import OneHotEncoder

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = OneHotEncoder(
            drop_first = False,
            column_naming = "values",
        )

    .. important::

        The model name is crucial for the model
        management system and versioning. It's
        highly recommended to provide a name if
        you plan to reuse the model later.

    Model Training
    ^^^^^^^^^^^^^^^

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(data, ["sex", "parch"])

    .. important::

        To train a model, you can directly use the :py:class:`~VastFrame`
        or the name of the relation stored in the database.

    Classes
    ^^^^^^^^

    To have a look at the identified classes/categories you
    can use:

    .. ipython:: python

        model.categories_

    Conversion/Transformation
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    To get the transformed dataset in the form that is encoded,
    we can use the ``transform`` function. Let us transform the
    data and display the first datapoints.

    .. ipython:: python
        :suppress:
        :okwarning:

        result = model.transform(data)
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_preprocessing_ooe_transform_1.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. code-block:: python

        model.transform(data)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_preprocessing_ooe_transform_1.html

    Please refer to
    :py:meth:`~vastorbit.machine_learning.OneHotEncoder.transform`
    for more details on transforming
    a :py:class:`~VastFrame`.

    Similarly, you can perform the
    inverse transform to get the
    original features using:

    .. code-block:: python

        model.inverse_transform(data_transformed)

    The variable ``data_transformed``
    includes the ``OneHotEncoder``
    components.

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory representations of
        machine learning models. They can be used for both in-database
        and in-memory prediction tasks. These objects can be pickled
        in the same way that you would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the model use ``MemModel``,
    and it is recommended to use ``MemModel`` directly.

    **SQL**

    To get the SQL query use below:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in Python syntax, use the
    following code:

    .. ipython:: python

        X = [['1', '3']]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.preprocessing.OneHotEncoder.to_python`
        method is used to transform the data and compute the different
        categories. For specific details on how to use this method for
        different model types, refer to the relevant documentation for
        each model.
    """

    # Properties.

    @property
    def _fit_sql(self) -> Literal[""]:
        return ""

    @property
    def _sklearn_model(self):
        return sklearn.preprocessing.OneHotEncoder

    @property
    def _transform_sql(self) -> Literal[""]:
        return ""

    @property
    def _inverse_transform_sql(self) -> Literal[""]:
        return ""

    @property
    def _model_subcategory(self) -> Literal["PREPROCESSING"]:
        return "PREPROCESSING"

    @property
    def _model_type(self) -> Literal["OneHotEncoder"]:
        return "OneHotEncoder"

    @property
    def _attributes(self) -> list[str]:
        return ["categories_", "column_naming_", "drop_first_"]

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        extra_levels: dict = {},
        drop_first: bool = True,
        ignore_null: bool = True,
        separator: str = "_",
        column_naming: str = "indices",
        null_column_name: str = "null",
        **kwargs
    ) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {
            "extra_levels": extra_levels,
            "drop_first": drop_first,
            "ignore_null": ignore_null,
            "separator": separator,
            "column_naming": column_naming,
            "null_column_name": null_column_name,
            **kwargs,
        }

    # Attributes Methods.

    @staticmethod
    def _compute_ohe_list(categories: list) -> list:
        """
        Allows to split the One Hot Encoder Array by
        features categories.
        """
        cat, tmp_cat = [], []
        init_cat, X = categories[0][0], [categories[0][0]]
        for c in categories:
            if c[0] != init_cat:
                init_cat = c[0]
                X += [c[0]]
                cat += [tmp_cat]
                tmp_cat = [c[1]]
            else:
                tmp_cat += [c[1]]
        cat += [tmp_cat]
        return [X, cat]

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes from the fitted ``scikit-learn`` model.
        """
        # scikit-learn stores one array of category levels per input column,
        # aligned with the order of self.X.
        categories = [list(levels) for levels in self._model.categories_]

        # Rebuild the parallel-list layout expected by _get_names / deploySQL.
        category_name, category_level, category_level_index = [], [], []
        for column, levels in zip(self.X, categories):
            col_name = quote_ident(column)[1:-1]
            for idx, level in enumerate(levels):
                category_name.append(col_name)
                category_level.append(level)
                category_level_index.append(idx)
        self.cat_ = {
            "category_name": category_name,
            "category_level": category_level,
            "category_level_index": category_level_index,
        }
        self.categories_ = categories
        self.column_naming_ = self.parameters["column_naming"]
        self.drop_first_ = self.parameters["drop_first"]

    # I/O Methods.

    def to_memmodel(self) -> mm.OneHotEncoder:
        """
        Converts the model to an InMemory object
        that can be used for different types of
        predictions.

        Returns
        -------
        InMemoryModel
            Representation of the model.

        Examples
        --------
        If we consider that you've built a model named
        ``model``, then it is easy to export it using
        the following syntax.

        .. code-block:: python

            model.to_memmodel()

        .. note::

            ``MemModel`` objects serve as in-memory
            representations of machine learning models.
            They can be used for both in-database and
            in-memory prediction tasks. These objects
            can be pickled in the same way that you
            would pickle a ``scikit-learn`` model.

        .. note::

            Look at
            :py:class:`~vastorbit.machine_learning.memmodel.preprocessing.OneHotEncoder`
            for more information.
        """
        return mm.OneHotEncoder(self.categories_, self.column_naming_, self.drop_first_)