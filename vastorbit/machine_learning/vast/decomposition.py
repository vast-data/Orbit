"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional
import numpy as np
import sklearn

from vastorbit._typing import (
    NoneType,
    PlottingObject,
    PythonNumber,
    SQLColumns,
    SQLRelation,
)
from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._sql._format import format_type, quote_ident

from vastorbit.core.tablesample.base import TableSample
from vastorbit.core.vastframe.base import VastFrame

import vastorbit.machine_learning.memmodel as mm
from vastorbit.machine_learning.vast.preprocessing import Preprocessing

"""
General Classes.
"""


class Decomposition(Preprocessing):
    # I/O Methods.

    def deploySQL(
        self,
        X: Optional[SQLColumns] = None,
        n_components: int = 0,
        cutoff: PythonNumber = 1,
    ) -> str:
        """
        Returns the SQL code needed to deploy the model.

        Parameters
        ----------
        X: SQLColumns, optional
            ``list`` of the columns used to
            deploy the model. If empty, the
            model predictors are used.
        n_components: int, optional
            Number of components to return.
            If set to ``0``, all the components
            are deployed.
        cutoff: PythonNumber, optional
            Specifies the minimum accumulated
            explained variance. Components are
            taken until the accumulated explained
            variance reaches this value.

        Returns
        -------
        str
            the SQL code needed
            to deploy the model.

        Examples
        --------
        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        We can drop the "color"
        column as it is varchar
        type.

        .. code-block::

            data.drop("color")

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data.drop("color")

        Let's import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import PCA

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import PCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = PCA(
                n_components = 3,
            )

        And train it:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        Once the model is trained, we can
        extract the SQL conveniently:

        .. ipython:: python

            model.deploySQL()

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.PCA`
            or
            :py:class:`~vastorbit.machine_learning.vast.decomposition.SVD`
            for a more detailed example.
        """
        X = format_type(X, dtype=list, na_out=self.X)
        res = self.to_memmodel().transform_sql(X)
        if n_components > 0:
            res = res[:n_components]
        elif 0 < cutoff < 1:
            tot = 0.0
            k = 0
            while tot < cutoff:
                tot += self.explained_variance_ratio_[k]
                k += 1
            res = res[:k]
        return res

    # Model Evaluation Methods.

    def score(
        self,
        X: Optional[SQLColumns] = None,
        input_relation: Optional[str] = None,
        metric: Literal["avg", "median"] = "avg",
        p: int = 2,
    ) -> TableSample:
        """
        Returns the decomposition score
        on a dataset for  each  transformed
        column. It is the average / median
        of the ``p``-distance between the
        real column and  its  result after
        applying the  decomposition model
        and its inverse.

        Parameters
        ----------
        X: SQLColumns, optional
            ``list`` of the columns used to
            deploy the model. If empty, the
            model  predictors are used.
        input_relation: str, optional
            Input Relation. If empty, the
            model input relation are used.
        metric: str, optional
            Distance metric used to do the
            scoring.

            - avg:
                The average is used as
                aggregation.
            - median:
                The median is used as
                aggregation.

        p: int, optional
            The ``p`` of the ``p``-distance.

        Returns
        -------
        TableSample
            PCA scores.

        Examples
        --------
        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        We can drop the "color"
        column as it is varchar
        type.

        .. code-block::

            data.drop("color")

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data.drop("color")

        Let's import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import PCA

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import PCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = PCA(
                n_components = 3,
            )

        And train it:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        The decomposition score on the
        dataset for each transformed
        column can be calculated by:

        .. ipython:: python
            :suppress:

            result = model.score()
            html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_decomposition_score.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. code-block:: python

            model.score()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_decomposition_score.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.PCA`
            or
            :py:class:`~vastorbit.machine_learning.vast.decomposition.SVD`
            for a more detailed example.
        """
        if isinstance(X, NoneType):
            X = self.X
        X = format_type(X, dtype=list)
        if not input_relation:
            input_relation = self.input_relation
        metric = str(metric).lower()
        if self._model_type in ("PCA", "SVD"):
            n_components = self.parameters["n_components"]
            if not n_components:
                n_components = len(X)
        else:
            n_components = len(X)

        memmodel = self.to_memmodel()

        components = memmodel.transform_sql(self.X)
        flat_components = []
        for expr in components:
            if isinstance(expr, (list, tuple)):
                flat_components.extend(expr)
            else:
                flat_components.append(expr)
        components = flat_components[:n_components]
        comp_cols = [f"col{i + 1}" for i in range(len(components))]

        # Keep the original columns alongside the components so we can compare
        # them against the reconstruction.
        col_init_select = [f"{X[idx]} AS col_init{idx}" for idx in range(len(X))]
        comp_select = [f"{expr} AS {name}" for expr, name in zip(components, comp_cols)]
        inner = f"""
            SELECT {', '.join(col_init_select + comp_select)}
            FROM {input_relation}"""

        # Inverse transform: reconstruct the original space from the components.
        if not hasattr(memmodel, "inverse_transform_sql"):
            raise NotImplementedError(
                f"score() needs an inverse transform, unavailable for {self._model_type}."
            )
        recon = memmodel.inverse_transform_sql(comp_cols)
        flat_recon = []
        for expr in recon:
            if isinstance(expr, (list, tuple)):
                flat_recon.extend(expr)
            else:
                flat_recon.append(expr)
        recon_select = [f"{expr} AS {X[idx]}" for idx, expr in enumerate(flat_recon)]
        keep_init = [f"col_init{idx}" for idx in range(len(X))]
        mid = f"""
            SELECT {', '.join(keep_init + recon_select)}
            FROM ({inner}) VASTORBIT_SUBTABLE"""

        # Reconstruction error per column: the (avg | median) p-distance between
        # the original value and its reconstruction. This is the power-mean of
        # the absolute differences -> MAE when p = 1, RMSE when p = 2.
        #
        # NB: the previous formula compared POWER(x, p) - POWER(x', p), i.e.
        # |x^p - x'^p|^(1/p), which is not a distance and produced wrong scores.
        def _agg(expr: str) -> str:
            if metric == "median":
                return f"approx_percentile({expr}, 0.5)"
            return f"avg({expr})"

        p_distances = [
            f"POWER({_agg(f'POWER(ABS({X[idx]} - col_init{idx}), {p})')}, {1 / p}) "
            f"AS {X[idx]}"
            for idx in range(len(X))
        ]
        query = f"""
            SELECT
                'Score' AS "index",
                {', '.join(p_distances)}
            FROM ({mid}) z"""
        return TableSample.read_sql(query, title="Getting Model Score.").transpose()

    # Prediction / Transformation Methods.

    def transform(
        self,
        vdf: SQLRelation = None,
        X: Optional[SQLColumns] = None,
        n_components: int = 0,
        cutoff: PythonNumber = 1,
    ) -> VastFrame:
        """
        Applies the model on a
        :py:class:`~VastFrame`.

        Parameters
        ----------
        vdf: SQLRelation, optional
            Input :py:class:`~VastFrame`.
            You can also specify a customized
            relation, but you must enclose
            it with an alias. For example:
            ``(SELECT 1) x`` is valid whereas
            ``(SELECT 1)`` and ``SELECT 1``
            are invalid.
        X: SQLColumns, optional
            ``list`` of the input
            :py:class:`~VastColumn`.
        n_components: int, optional
            Number  of components to return.
            If set to 0, all the components
            are deployed.
        cutoff: PythonNumber, optional
            Specifies the minimum accumulated
            explained variance. Components
            are taken until the accumulated
            explained variance reaches this
            value.

        Returns
        -------
        VastFrame
            object result of the
            model transformation.

        Examples
        --------
        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        We can drop the "color"
        column as it is varchar
        type.

        .. code-block::

            data.drop("color")

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data.drop("color")

        Let's import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import PCA

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import PCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = PCA(
                n_components = 3,
            )

        And train it:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        To get the transformed dataset in
        the form of principal components:

        .. ipython:: python
            :suppress:

            result = model.score()
            html_file = open("SPHINX_DIRECTORY/figures/machine_learning_VAST_decomposition_transform.html", "w")
            html_file.write(result._repr_html_())
            html_file.close()

        .. code-block:: python

            model.transform(data)

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_decomposition_transform.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.PCA`
            or
            :py:class:`~vastorbit.machine_learning.vast.decomposition.SVD`
            for a more detailed example.
        """
        X = format_type(X, dtype=list, na_out=self.X)
        X = quote_ident(X)
        columns = self.deploySQL(
            X,
            n_components,
            cutoff,
        )
        columns = ", ".join([f"{col} AS col{i}" for i, col in enumerate(columns)])
        if not (vdf):
            vdf = self.input_relation
        main_relation = f"(SELECT *, {columns} FROM {vdf}) VASTORBIT_SUBTABLE"
        return VastFrame(main_relation)

    # Plotting Methods.

    def plot(
        self,
        dimensions: tuple = (1, 2),
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws a decomposition scatter plot.

        Parameters
        ----------
        dimensions: tuple, optional
            Tuple of two elements
            representing the IDs
            of the model's components.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to
            pass to the Plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        We can drop the "color"
        column as it is varchar
        type.

        .. code-block::

            data.drop("color")

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data.drop("color")

        Let's import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import PCA

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import PCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = PCA(
                n_components = 3,
            )

        And train it:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        You can plot the first two
        components conveniently using:

        .. code-block:: python

            model.plot()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot(width = 550)
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_pca_plot.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_pca_plot.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.PCA`
            or
            :py:class:`~vastorbit.machine_learning.vast.decomposition.SVD`
            for a more detailed example.
        """
        vdf = self.transform(VastFrame(self.input_relation))
        dim_perc = []
        for d in dimensions:
            if not self.explained_variance_ratio_[d - 1]:
                dim_perc += [""]
            else:
                dim_perc += [
                    f" ({round(self.explained_variance_ratio_[d - 1] * 100, 1)}%)"
                ]
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="ScatterPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        return vo_plt.ScatterPlot(
            vdf=vdf,
            columns=[f"col{dimensions[0]}", f"col{dimensions[1]}"],
            max_nb_points=100000,
            misc_layout={
                "columns": [
                    f"Dim{dimensions[0]}{dim_perc[0]}",
                    f"Dim{dimensions[1]}{dim_perc[1]}",
                ]
            },
        ).draw(**kwargs)

    def plot_circle(
        self,
        dimensions: tuple = (1, 2),
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws a decomposition circle.

        Parameters
        ----------
        dimensions: tuple, optional
            Tuple of two elements
            representing the IDs
            of the model's components.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to
            pass to the Plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        We can drop the "color"
        column as it is varchar
        type.

        .. code-block::

            data.drop("color")

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data.drop("color")

        Let's import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import PCA

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import PCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = PCA(
                n_components = 3,
            )

        And train it:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        You can plot the Decomposition
        Circles:

        .. code-block:: python

            model.plot_circle()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot_circle()
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_circle.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_circle.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.PCA`
            or
            :py:class:`~vastorbit.machine_learning.vast.decomposition.SVD`
            for a more detailed example.
        """
        if self._model_type == "SVD":
            x = self.vectors_[:, dimensions[0] - 1]
            y = self.vectors_[:, dimensions[1] - 1]
        else:
            x = self.principal_components_[:, dimensions[0] - 1]
            y = self.principal_components_[:, dimensions[1] - 1]
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="PCACirclePlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        data = {
            "x": x,
            "y": y,
            "explained_variance": [
                self.explained_variance_ratio_[dimensions[0] - 1],
                self.explained_variance_ratio_[dimensions[1] - 1],
            ],
            "dim": dimensions,
        }
        layout = {
            "columns": self.X,
        }
        return vo_plt.PCACirclePlot(data=data, layout=layout).draw(**kwargs)

    def plot_scree(
        self, chart: Optional[PlottingObject] = None, **style_kwargs
    ) -> PlottingObject:
        """
        Draws a decomposition scree plot.

        Parameters
        ----------
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to
            pass to the Plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        For this example, we will
        use the winequality dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_winequality()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

        We can drop the "color"
        column as it is varchar
        type.

        .. code-block::

            data.drop("color")

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_winequality()
            data.drop("color")

        Let's import the model:

        .. code-block::

            from vastorbit.machine_learning.vast import PCA

        .. ipython:: python
            :suppress:

            from vastorbit.machine_learning.vast import PCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = PCA(
                n_components = 3,
            )

        And train it:

        .. ipython:: python
            :okwarning:

            model.fit(data)

        You can plot the Scree plot:

        .. code-block:: python

            model.plot_scree()

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot_scree()
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_scree.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_scree.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.PCA`
            or
            :py:class:`~vastorbit.machine_learning.vast.decomposition.SVD`
            for a more detailed example.
        """
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="PCAScreePlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        n = len(self.explained_variance_ratio_)
        data = {
            "x": np.array([i + 1 for i in range(n)]),
            "y": 100 * self.explained_variance_ratio_,
            "adj_width": 0.94,
        }
        layout = {
            "labels": [i + 1 for i in range(n)],
            "x_label": "dimensions",
            "y_label": "percentage_explained_variance (%)",
            "title": None,
            "plot_scree": True,
            "plot_line": False,
        }
        return vo_plt.PCAScreePlot(data=data, layout=layout).draw(**kwargs)


"""
Algorithms used for decomposition.
"""


class PCA(Decomposition):
    """
    Creates an ``PCA`` object
    using ``scikit-learn`` for training and
    the scalability of VAST DataBase for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.
    ``**kwargs``: ``scikit-learn`` model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``principal_components_``: numpy.array
        Matrix of the principal components.
    ``mean_``: numpy.array
        List of the averages of each input feature.
    ``cos2_``: numpy.array
        Quality of representation of each observation in
        the principal component space. A high cos2 value
        indicates that the observation is well-represented
        in the reduced-dimensional space defined by the
        principal components, while a low value suggests
        poor representation.
    ``explained_variance_``: numpy.array
        Represents the proportion of the total variance in
        the original dataset that is captured by a specific
        principal component or a combination of principal
        components.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.decomposition.Decomposition.get_attributes`
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

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

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

    We can drop the "color" column as it is varchar type.

    .. code-block::

        data.drop("color")

    .. ipython:: python
        :suppress:

        import vastorbit.datasets as vod
        data = vod.load_winequality()
        data.drop("color")

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``PCA`` model:

    .. code-block::

        from vastorbit.machine_learning.vast import PCA

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast import PCA

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = PCA(
            n_components = 3,
        )

    You can select the number of components by the ``n_component``
    parameter. If it is not provided, then all are considered.

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

        model.fit(data)

    .. important::

        To train a model, you can directly
        use the :py:class:`~VastFrame` or
        the name of the relation stored in
        the database.

    Scores
    ^^^^^^^

    The decomposition  score  on  the  dataset for  each
    transformed column can be calculated by:

    .. ipython:: python

        model.score()

    For more details on the function, check out
    :py:meth:`~vastorbit.machine_learning.PCA.score`

    You can also fetch the explained variance by:

    .. ipython:: python

        model.explained_variance_ratio_

    Principal Components
    ^^^^^^^^^^^^^^^^^^^^^

    To get the transformed dataset in the form of principal
    components:

    .. ipython:: python

        model.transform(data)

    Please refer to
    :py:meth:`~vastorbit.machine_learning.PCA.transform`
    for more details on transforming
    a :py:class:`~VastFrame`.

    Similarly, you can perform the inverse tranform to get
    the original features using:

    .. code-block:: python

        model.inverse_transform(data_transformed)

    The variable ``data_transformed`` includes the PCA components.

    Plots - PCA
    ^^^^^^^^^^^^

    You can plot the first two components conveniently using:

    .. code-block:: python

        model.plot()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_pca_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_pca_plot.html

    Plots - Scree
    ^^^^^^^^^^^^^^

    You can also plot the Scree plot:

    .. code-block:: python

        model.plot_scree()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot_scree()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_pca_plot_scree.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_pca_plot_scree.html

    Parameter Modification
    ^^^^^^^^^^^^^^^^^^^^^^^

    In order to see the parameters:

    .. ipython:: python

        model.get_params()

    And to manually change some of the parameters:

    .. ipython:: python

        model.set_params({'n_components': 3})

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the
    model use ``MemModel``, and it is
    recommended to use ``MemModel`` directly.

    **SQL**

    To get the SQL query use below:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[3.8, 0.3, 0.02, 11, 0.03, 20, 113, 0.99, 3, 0.4, 12, 6, 0]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.decomposition.PCA.to_python`
        method is used to retrieve the
        Principal Component values.
        For specific details on how to
        use this method for different
        model types, refer to the relevant
        documentation for each model.
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["DECOMPOSITION"]:
        return "DECOMPOSITION"

    @property
    def _model_type(self) -> Literal["PCA"]:
        return "PCA"

    @property
    def _attributes(self) -> list[str]:
        return [
            "principal_components_",
            "mean_",
            "cos2_",
            "explained_variance_",
            "explained_variance_ratio_",
        ]

    @property
    def _sklearn_model(self) -> Literal[sklearn.decomposition.PCA]:
        return sklearn.decomposition.PCA

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes.
        """
        # 1. Principal components (loadings/eigenvectors). Stored as
        # (n_features, n_components): the memmodel transform/inverse and the
        # plotting/contribution helpers all index columns as components, so the
        # sklearn-native (n_components, n_features) must be transposed here.
        self.principal_components_ = (
            self._model.components_.T
        )  # Shape: (n_features, n_components)

        # 2. Mean (feature means)
        self.mean_ = self._model.mean_

        # 3. Explained variance
        self.explained_variance_ = self._model.explained_variance_
        self.explained_variance_ratio_ = self._model.explained_variance_ratio_

        # 4. Cos2 (squared cosines - contribution of each variable to each PC)
        # cos2[i,j] = (component[i,j])^2 / sum of squared components for variable j
        cos2 = self._model.components_**2  # Square all loadings

        # Normalize by column sum (each variable's total contribution across all PCs)
        col_sums = np.sum(cos2, axis=0)  # Sum across PCs for each variable
        self.cos2_ = cos2 / col_sums  # Normalize each column

    # I/O Methods.

    def to_memmodel(self) -> mm.PCA:
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
            :py:class:`~vastorbit.machine_learning.memmodel.decomposition.PCA`
            for more information.
        """
        return mm.PCA(self.principal_components_, self.mean_)


class MCA(PCA):
    """
    Creates a MCA  (multiple correspondence analysis) object
    using  the VAST PCA  algorithm. MCA is a PCA applied
    to a complete disjunctive table.  The  input relation is
    transformed to a TCDT (transformed  complete  disjunctive
    table) before applying the PCA.

    .. important::

        This algorithm is not VAST
        Native and relies solely on SQL
        for attribute computation. While
        this model does not take advantage
        of the benefits provided by a model
        management system, including versioning
        and tracking, the SQL code it generates
        can still be used to create a pipeline.

    Parameters
    ----------
    name: str, optional
        Name of the model.  The model is stored in the
        database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``principal_components_``: numpy.array
        Matrix of the principal components.
    ``mean_``: numpy.array
        List of the averages of each input feature.
    ``cos2_``: numpy.array
        Quality of representation of each observation in
        the principal component space. A high cos2 value
        indicates that the observation is well-represented
        in the reduced-dimensional space defined by the
        principal components, while a low value suggests
        poor representation.
    ``explained_variance_``: numpy.array
        Represents the proportion of the total variance in
        the original dataset that is captured by a specific
        principal component or a combination of principal
        components.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.decomposition.Decomposition.get_attributes`
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

    For this example, we will
    use the Titanic dataset.

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

    First we import the ``MCA`` model:

    .. ipython:: python

        from vastorbit.machine_learning.vast import MCA

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = MCA()

    You can select the number of components
    by the ``n_component`` parameter. If it
    is not provided, then all are considered.

    .. important::

        As this model is not native, it solely
        relies on SQL statements to compute
        various attributes, storing them within
        the object. No data is saved in the database.

    Model Training
    ^^^^^^^^^^^^^^^

    Before fitting the model, we need to
    calculate the Transformed Completely
    Disjontive Table before fitting the
    model:

    .. ipython:: python
        :okwarning:

        tcdt = data[["survived", "pclass", "sex"]].cdt()

    We can now fit the model:

    .. ipython:: python
        :okwarning:

        model.fit(tcdt)

    .. important::

        To train a model, you can directly
        use the :py:class:`~VastFrame` or
        the name of the relation stored in
        the database.

    Scores
    ^^^^^^

    The decomposition score on the dataset
    for each transformed column can be
    calculated by:

    .. ipython:: python

        model.score()

    For more details on the function, check out
    :py:meth:`~vastorbit.machine_learning.MCA.score`

    You can also fetch the explained variance by:

    .. ipython:: python

        model.explained_variance_ratio_

    Principal Components
    ^^^^^^^^^^^^^^^^^^^^^^

    To get the transformed dataset
    in the form of principal
    components:

    .. ipython:: python

        model.transform(tcdt)

    Please refer to
    :py:meth:`~vastorbit.machine_learning.MCA.transform`
    for more details on transforming
    a :py:class:`~VastFrame`.

    Similarly, you can perform the inverse tranform to get
    the original features using:

    .. code-block:: python

        model.inverse_transform(data_transformed)

    The variable ``data_transformed`` includes the MCA components.

    Plots - MCA
    ^^^^^^^^^^^^

    You can plot the first two
    dimensions conveniently using:

    .. code-block:: python

        model.plot()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot(width = 550)
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot.html

    Plots - Scree
    ^^^^^^^^^^^^^^

    You can also plot the Scree plot:

    .. code-block:: python

        model.plot_scree()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot_scree()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_scree.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_scree.html

    Plots - Decomposition Circle
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    You can also plot the Decomposition Circles:

    .. code-block:: python

        model.plot_circle()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot_circle()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_circle.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_circle.html

    Model Register
    ^^^^^^^^^^^^^^

    As this model is not native, it does not
    support model management and versioning.
    However, it is possible to use the SQL
    code it generates for deployment.

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the
    model use ``MemModel``, and it is
    recommended to use ``MemModel`` directly.

    **SQL**

    To get the SQL query use below:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[0, 1, 0, 1, 1, 0, 1]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.decomposition.MCA.to_python`
        method is used to retrieve the
        Principal Component values.
        For specific details on how to
        use this method for different
        model types, refer to the relevant
        documentation for each model.
    """

    # Properties.

    @property
    def _is_native(self) -> Literal[False]:
        return False

    @property
    def _is_using_native(self) -> Literal[True]:
        return True

    @property
    def _fit_sql(self) -> Literal["PCA"]:
        return "PCA"

    @property
    def _VAST_transform_sql(self) -> Literal["APPLY_PCA"]:
        return "APPLY_PCA"

    @property
    def _VAST_inverse_transform_sql(self) -> Literal["APPLY_INVERSE_PCA"]:
        return "APPLY_INVERSE_PCA"

    @property
    def _model_subcategory(self) -> Literal["DECOMPOSITION"]:
        return "DECOMPOSITION"

    @property
    def _model_type(self) -> Literal["MCA"]:
        return "MCA"

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(self, name: str = None, overwrite_model: bool = False) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {}

    # Plotting Methods.

    def plot_contrib(
        self, dimension: int = 1, chart: Optional[PlottingObject] = None, **style_kwargs
    ) -> PlottingObject:
        """
        Draws a decomposition contribution
        plot of the input dimension.

        Parameters
        ----------
        dimension: int, optional
            Integer representing the IDs
            of the model's
            component.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to pass
            to the Plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_titanic()

        We import the ``MCA`` model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import MCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = MCA()

        Before fitting the model, we need to
        calculate the Transformed Completely
        Disjontive Table before fitting the
        model:

        .. ipython:: python
            :okwarning:

            tcdt = data[["survived", "pclass", "sex"]].cdt()

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(tcdt)

        You can also decomposition
        contribution of dimension 1.

        .. code-block:: python

            model.plot_contrib(dimension = 1)

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot_contrib(dimension = 1)
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_contrib.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_contrib.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.MCA`
            for more information about the
            different methods and usages.
        """
        contrib = self.principal_components_[:, dimension - 1] ** 2
        contrib = 100 * contrib / contrib.sum()
        variables, contribution = zip(
            *sorted(zip(self.X, contrib), key=lambda t: t[1], reverse=True)
        )
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="PCAScreePlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        n = len(contribution)
        data = {
            "x": np.array([i + 1 for i in range(n)]),
            "y": contribution,
            "adj_width": 0.94,
        }
        layout = {
            "labels": variables,
            "x_label": None,
            "y_label": "Contribution (%)",
            "title": f"Contribution of variables to Dim {dimension}",
            "plot_scree": True,
            "plot_line": True,
        }
        return vo_plt.PCAScreePlot(data=data, layout=layout).draw(**kwargs)

    def plot_cos2(
        self,
        dimensions: tuple = (1, 2),
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws a MCA (multiple correspondence analysis) cos2
        plot of the two input dimensions.

        Parameters
        ----------
        dimensions: tuple, optional
            Tuple of two IDs of the
            model's components.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to pass
            to the Plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_titanic()

        We import the ``MCA`` model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import MCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = MCA()

        Before fitting the model, we need to
        calculate the Transformed Completely
        Disjontive Table before fitting the
        model:

        .. ipython:: python
            :okwarning:

            tcdt = data[["survived", "pclass", "sex"]].cdt()

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(tcdt)

        You can also decomposition cos2
        plot of dimensions 1 and 2.

        .. code-block:: python

            model.plot_cos2(dimensions = (1, 2))

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot_cos2(dimensions = (1, 2))
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_cos2.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_cos2.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.MCA`
            for more information about the
            different methods and usages.
        """
        cos2_1 = self.cos2_[:, dimensions[0] - 1]
        cos2_2 = self.cos2_[:, dimensions[1] - 1]
        n = len(cos2_1)
        quality = []
        for i in range(n):
            quality += [cos2_1[i] + cos2_2[i]]
        variables, quality = zip(
            *sorted(zip(self.X, quality), key=lambda t: t[1], reverse=True)
        )
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="PCAScreePlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        n = len(self.explained_variance_ratio_)
        data = {
            "x": np.array([i + 1 for i in range(n)]),
            "y": 100 * np.array(quality),
            "adj_width": 1.0,
        }
        layout = {
            "labels": variables,
            "x_label": None,
            "y_label": "Cos2 - Quality of Representation (%)",
            "title": f"Cos2 of variables to Dim {dimensions[0]}-{dimensions[1]}",
            "plot_scree": False,
            "plot_line": False,
        }
        return vo_plt.PCAScreePlot(data=data, layout=layout).draw(**kwargs)

    def plot_var(
        self,
        dimensions: tuple = (1, 2),
        method: Literal["auto", "cos2", "contrib"] = "auto",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Draws the MCA (multiple
        correspondence analysis)
        graph.

        Parameters
        ----------
        dimensions: tuple, optional
            ``tuple`` of two IDs  of
            the model's  components.
        method: str, optional
            Method used to draw the plot.

             - auto:
                Only the  variables are
                displayed.
             - cos2:
                The cos2 is used as CMAP.
             - contrib :
                The feature contribution
                is used as CMAP.
        chart: PlottingObject, optional
            The chart object to plot on.
        ``**style_kwargs``
            Any optional parameter to pass
            to the Plotting functions.

        Returns
        -------
        obj
            Plotting Object.

        Examples
        --------
        We import :py:mod:`vastorbit`:

        .. ipython:: python

            import vastorbit as vo

        For this example, we will
        use the Titanic dataset.

        .. code-block:: python

            import vastorbit.datasets as vod

            data = vod.load_titanic()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_titanic.html

        .. ipython:: python
            :suppress:

            import vastorbit.datasets as vod
            data = vod.load_titanic()

        We import the ``MCA`` model:

        .. ipython:: python

            from vastorbit.machine_learning.vast import MCA

        Then we can create the model:

        .. ipython:: python
            :okwarning:

            model = MCA()

        Before fitting the model, we need to
        calculate the Transformed Completely
        Disjontive Table before fitting the
        model:

        .. ipython:: python
            :okwarning:

            tcdt = data[["survived", "pclass", "sex"]].cdt()

        We can now fit the model:

        .. ipython:: python
            :okwarning:

            model.fit(tcdt)

        You can also decomposition
        graph of dimensions 1 and 2.

        .. code-block:: python

            model.plot_var(dimensions = (1, 2))

        .. ipython:: python
            :suppress:

            vo.set_option("plotting_lib", "plotly")
            fig = model.plot_var(dimensions = (1, 2))
            fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_var.html")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_mca_plot_var.html

        .. note::

            Refer to
            :py:class:`~vastorbit.machine_learning.vast.decomposition.MCA`
            for more information about the
            different methods and usages.
        """
        x = self.principal_components_[:, dimensions[0] - 1]
        y = self.principal_components_[:, dimensions[1] - 1]
        n = len(self.cos2_[:, dimensions[0] - 1])
        c = None
        has_category = False
        if method in ("cos2", "contrib"):
            has_category = True
            if method == "cos2":
                c = np.array(
                    [
                        self.cos2_[:, dimensions[0] - 1][i]
                        + self.cos2_[:, dimensions[1] - 1][i]
                        for i in range(n)
                    ]
                )
            else:
                sum_1, sum_2 = (
                    sum(self.cos2_[:, dimensions[0] - 1]),
                    sum(self.cos2_[:, dimensions[1] - 1]),
                )
                c = np.array(
                    [
                        0.5
                        * 100
                        * (
                            self.cos2_[:, dimensions[0] - 1][i] / sum_1
                            + self.cos2_[:, dimensions[1] - 1][i] / sum_2
                        )
                        for i in range(n)
                    ]
                )
        vo_plt, kwargs = self.get_plotting_lib(
            class_name="PCAVarPlot",
            chart=chart,
            style_kwargs=style_kwargs,
        )
        data = {
            "x": x,
            "y": y,
            "c": c,
            "explained_variance": [
                self.explained_variance_ratio_[dimensions[0] - 1],
                self.explained_variance_ratio_[dimensions[1] - 1],
            ],
            "dim": dimensions,
        }
        layout = {
            "columns": self.X,
            "method": method,
            "has_category": has_category,
        }
        return vo_plt.PCAVarPlot(data=data, layout=layout).draw(**kwargs)


class SVD(Decomposition):
    """
    Creates an ``SVD`` object
    using ``scikit-learn`` for training and
    the scalability of VAST DataBase for
    the inferences.

    Parameters
    ----------
    name: str, optional
        Name of the model. The model
        is stored in the database.
    overwrite_model: bool, optional
        If set to ``True``, training a
        model with the same name as an
        existing model overwrites the
        existing model.
    ``**kwargs``: ``scikit-learn`` model parameters.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    ``values_``: numpy.array
        Matrix of the right
        singular vectors.
    ``values_``: numpy.array
        Array of the singular
        values for each input
        feature.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.decomposition.Decomposition.get_attributes`
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

    For this example, we will
    use the winequality dataset.

    .. code-block:: python

        import vastorbit.datasets as vod

        data = vod.load_winequality()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_winequality.html

    We can drop the "color" column as it is varchar type.

    .. code-block::

        data.drop("color")

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
        data = vod.load_winequality()
        data.drop("color")

    Model Initialization
    ^^^^^^^^^^^^^^^^^^^^^

    First we import the ``SVD`` model:

    .. code-block::

        from vastorbit.machine_learning.vast import SVD

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast import SVD

    Then we can create the model:

    .. ipython:: python
        :okwarning:

        model = SVD(
            n_components = 3,
        )

    You can select the number of components by the ``n_component``
    parameter. If it is not provided, then all are considered.

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

        model.fit(data)

    .. important::

        To train a model, you can directly
        use the :py:class:`~VastFrame` or
        the name of the relation stored in
        the database.

    Scores
    ^^^^^^

    The decomposition  score  on  the  dataset for  each
    transformed column can be calculated by:

    .. ipython:: python

        model.score()

    For more details on the function, check out
    :py:meth:`~vastorbit.machine_learning.SVD.score`

    You can also fetch the explained variance by:

    .. ipython:: python

        model.explained_variance_

    Principal Components
    ^^^^^^^^^^^^^^^^^^^^^^

    To get the transformed dataset in the form of principal
    components:

    .. ipython:: python

        model.transform(data)

    Please refer to
    :py:meth:`~vastorbit.machine_learning.SVD.transform`
    for more details on transforming
    a :py:class:`~VastFrame`.

    Similarly, you can perform the inverse tranform to get
    the original features using:

    .. code-block:: python

        model.inverse_transform(data_transformed)

    The variable ``data_transformed`` includes the PCA components.

    Plots - SVD
    ^^^^^^^^^^^^

    You can plot the first two dimensions conveniently using:

    .. code-block:: python

        model.plot()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_svd_plot.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_svd_plot.html

    Plots - Scree
    ^^^^^^^^^^^^^^

    You can also plot the Scree plot:

    .. code-block:: python

        model.plot_scree()

    .. ipython:: python
        :suppress:

        vo.set_option("plotting_lib", "plotly")
        fig = model.plot_scree()
        fig.write_html("SPHINX_DIRECTORY/figures/machine_learning_VAST_svd_plot_scree.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_VAST_svd_plot_scree.html

    Parameter Modification
    ^^^^^^^^^^^^^^^^^^^^^^^

    In order to see the parameters:

    .. ipython:: python

        model.get_params()

    And to manually change some of the parameters:

    .. ipython:: python

        model.set_params({'n_components': 3})

    Model Exporting
    ^^^^^^^^^^^^^^^^

    **To Memmodel**

    .. code-block:: python

        model.to_memmodel()

    .. note::

        ``MemModel`` objects serve as in-memory
        representations of machine learning models.
        They can be used for both in-database and
        in-memory prediction tasks. These objects
        can be pickled in the same way that you
        would pickle a ``scikit-learn`` model.

    The preceding methods for exporting the
    model use ``MemModel``, and it is
    recommended to use ``MemModel`` directly.

    **SQL**

    To get the SQL query use below:

    .. ipython:: python

        model.to_sql()

    **To Python**

    To obtain the prediction function in
    Python syntax, use the following code:

    .. ipython:: python

        X = [[3.8, 0.3, 0.02, 11, 0.03, 20, 113, 0.99, 3, 0.4, 12, 6, 0]]
        model.to_python()(X)

    .. hint::

        The
        :py:meth:`~vastorbit.machine_learning.vast.decomposition.SVD.to_python`
        method is used to retrieve the Principal Component values.
        For specific details on how to
        use this method for different model types, refer to the relevant
        documentation for each model.
    """

    # Properties.

    @property
    def _model_subcategory(self) -> Literal["DECOMPOSITION"]:
        return "DECOMPOSITION"

    @property
    def _model_type(self) -> Literal["SVD"]:
        return "SVD"

    @property
    def _attributes(self) -> list[str]:
        return [
            "vectors_",
            "values_",
            "explained_variance_",
            "explained_variance_ratio_",
        ]

    @property
    def _sklearn_model(self) -> Literal[sklearn.decomposition.TruncatedSVD]:
        return sklearn.decomposition.TruncatedSVD

    # Attributes Methods.

    def _compute_attributes(self) -> None:
        """
        Computes the model's attributes.
        """
        # 1. Right singular vectors (V matrix). Stored as
        # (n_features, n_components) to match the memmodel transform/inverse and
        # plotting helpers, which index columns as components; sklearn exposes
        # components_ as (n_components, n_features), so transpose it.
        self.vectors_ = self._model.components_.T  # Shape: (n_features, n_components)

        # 2. Singular values
        self.values_ = self._model.singular_values_

        # 3. Explained variance
        self.explained_variance_ = self._model.explained_variance_
        self.explained_variance_ratio_ = self._model.explained_variance_ratio_

    # I/O Methods.

    def to_memmodel(self) -> mm.SVD:
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
            :py:class:`~vastorbit.machine_learning.memmodel.decomposition.SVD`
            for more information.
        """
        return mm.SVD(self.vectors_, self.values_)
