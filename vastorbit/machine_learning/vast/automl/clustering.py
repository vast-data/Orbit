"""
SPDX-License-Identifier: Apache-2.0
"""

import copy
from typing import Literal, Optional, Union
from tqdm.auto import tqdm

import vastorbit._config.config as conf
from vastorbit._typing import ArrayLike, SQLColumns, SQLRelation
from vastorbit._utils._print import print_message
from vastorbit._utils._sql._collect import save_vastorbit_logs

from vastorbit.machine_learning.model_selection import best_k
from vastorbit.machine_learning.vast.automl.dataprep import AutoDataPrep
from vastorbit.machine_learning.vast.base import VASTModel
from vastorbit.machine_learning.vast.cluster import KMeans


class AutoClustering(VASTModel):
    """
    Automatically creates k different groups with which to
    generalize the data.

    Parameters
    ----------
    name: str, optional
        Name of the model.
    overwrite_model: bool, optional
        If set to True, training a model with the same name
        as an existing model overwrites the existing model.
    n_clusters: int, optional
        Number  of clusters. If empty, an optimal number  of
        clusters  are determined using multiple  k-means
        models.
    init: str | list, optional
        The method for finding the initial cluster  centers.
            k-means++ : Uses   the    k-means++   method   to
                       initialize the centers.
            random   : Randomly  subsamples the data to find
                       initial centers.

        Alternatively,  you  can  specify  a list  with  the
        initial cluster centers.
    max_iter: int, optional
        The maximum number of  iterations for the algorithm.
    tol: float, optional
        Determines whether the algorithm has converged. The
        algorithm  is considered converged after no  center
        has  moved more than  a distance of 'tol' from  the
        previous
        iteration.
    preprocess_data: bool, optional
        If True, the data will be preprocessed.
    preprocess_dict: dict, optional
        Dictionary  to pass to  the  AutoDataPrep class  in
        order to preprocess the data before clustering.
    print_info: bool
        If True, prints the model information at each step.

    Attributes
    ----------
    ``preprocess_``: object
        Model used to preprocess the data.
    ``model_``: object
        Final model used for clustering.
    """

    # Properties.

    @property
    def _is_native(self) -> Literal[False]:
        return False

    @property
    def _fit_sql(self) -> Literal[""]:
        return ""

    @property
    def _predict_sql(self) -> Literal[""]:
        return ""

    @property
    def _model_category(self) -> Literal["UNSUPERVISED"]:
        return "UNSUPERVISED"

    @property
    def _model_subcategory(self) -> Literal["CLUSTERING"]:
        return "CLUSTERING"

    @property
    def _model_type(self) -> Literal["AutoClustering"]:
        return "AutoClustering"

    @property
    def _attributes(self) -> list[str]:
        return ["preprocess_", "model_"]

    # System & Special Methods.

    @save_vastorbit_logs
    def __init__(
        self,
        name: Optional[str] = None,
        overwrite_model: bool = False,
        n_clusters: Optional[int] = None,
        init: Union[Literal["k-means++", "random"], ArrayLike] = "k-means++",
        max_iter: int = 300,
        tol: float = 1e-4,
        preprocess_data: bool = True,
        preprocess_dict: dict = {
            "identify_ts": False,
            "standardize_min_cat": 0,
            "outliers_threshold": 3.0,
            "na_method": "drop",
        },
        print_info: bool = True,
    ) -> None:
        super().__init__(name, overwrite_model)
        self.parameters = {
            "n_clusters": n_clusters,
            "init": init,
            "max_iter": max_iter,
            "tol": tol,
            "print_info": print_info,
            "preprocess_data": preprocess_data,
            "preprocess_dict": preprocess_dict,
        }

    # Model Fitting Method.

    def fit(
        self,
        input_relation: SQLRelation,
        X: Optional[SQLColumns] = None,
        return_report: bool = False,
    ) -> None:
        """
        Trains the model.

        Parameters
        ----------
        input_relation: SQLRelation
            Training Relation.
        X: SQLColumns, optional
            List of the predictors.
        """
        if self.overwrite_model:
            self.drop()
        else:
            self._is_already_stored(raise_error=True)
        if self.parameters["print_info"]:
            print_message(f"\033[1m\033[4mStarting AutoClustering\033[0m\033[0m\n")
        if self.parameters["preprocess_data"]:
            model_preprocess = AutoDataPrep(**self.parameters["preprocess_dict"])
            model_preprocess.fit(input_relation, X=X)
            input_relation = model_preprocess.final_relation_
            X = copy.deepcopy(model_preprocess.X_out_)
            self.preprocess_ = model_preprocess
        else:
            self.preprocess_ = None
        if not self.parameters["n_clusters"]:
            if self.parameters["print_info"]:
                print_message(
                    f"\033[1m\033[4mFinding a suitable number of clusters\033[0m\033[0m\n"
                )
            self.parameters["n_clusters"] = best_k(
                input_relation=input_relation,
                X=X,
                n_clusters=(1, 100),
                init=self.parameters["init"],
                max_iter=self.parameters["max_iter"],
                tol=self.parameters["tol"],
                elbow_score_stop=0.9,
                tqdm=self.parameters["print_info"],
            )
        if self.parameters["print_info"]:
            print_message(f"\033[1m\033[4mBuilding the Final Model\033[0m\033[0m\n")
        if conf.get_option("tqdm") and self.parameters["print_info"]:
            loop = tqdm(range(1))
        else:
            loop = range(1)
        for i in loop:
            self.model_ = KMeans(
                self.model_name,
                n_clusters=self.parameters["n_clusters"],
                init=self.parameters["init"],
                max_iter=self.parameters["max_iter"],
                tol=self.parameters["tol"],
            )
            self.model_.fit(input_relation, X=X)
