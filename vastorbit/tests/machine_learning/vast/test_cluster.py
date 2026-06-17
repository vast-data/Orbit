"""
SPDX-License-Identifier: Apache-2.0
"""

import types

import pytest

import vastorbit._config.config as conf


@pytest.mark.parametrize("model_class", ["KMeans"])
class TestCluster:
    """
    test class - TestCluster
    """

    @pytest.mark.parametrize("return_report", [True, False])
    def test_fit(
        self,
        get_vo_model,
        get_py_model,
        model_class,
        iris_vd_fun,
        return_report,
    ):
        """
        test function - fit
        """
        vo_model_obj, py_model_obj = get_vo_model(model_class), get_py_model(
            model_class
        )
        vo_model_obj.model.drop()
        vo_res = vo_model_obj.model.fit(
            iris_vd_fun, py_model_obj.X, return_report=return_report
        )

        assert (
            isinstance(vo_res, str) if return_report else isinstance(vo_res, type(None))
        )

    def test_plot_voronoi(self, model_class, get_vo_model, get_py_model):
        """
        test function - plot_voronoi
        """
        conf.set_option("plotting_lib", "matplotlib")
        X = list(get_py_model(model_class).X.columns)
        vo_res = get_vo_model(model_class, X=X[:2])[0].plot_voronoi()

        assert isinstance(vo_res, types.ModuleType), "Wrong object created"
        assert vo_res.__name__ == "matplotlib.pyplot", "Not a matplotlib pyplot object"
