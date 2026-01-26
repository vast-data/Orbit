"""
SPDX-License-Identifier: Apache-2.0
"""

from itertools import chain
import pytest
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer as py_TfidfVectorizer
import vastorbit as vo
from vastorbit.machine_learning.vast.feature_extraction.text import (
    TfidfVectorizer as vo_TfidfVectorizer,
)
from vastorbit.tests.machine_learning.vast import rel_abs_tol_map


class TestTFIDF:
    """
    test class for base TFIDF
    """

    documents = [
        "Natural language processing is a field of study in artificial intelligence.",
        "TFIDF stands for Term Frequency Inverse Document Frequency.",
        "Machine learning algorithms can be applied to text data for classification.",
        "The 20 Newsgroups dataset is a collection of text documents used for text classification.",
        "Clustering is a technique used to group similar documents together.",
        "Python is a popular programming language for natural language processing tasks.",
        "TFIDF is a technique widely used in information retrieval.",
        "An algorithm is a set of instructions designed to perform a specific task.",
        "Data preprocessing is an important step in preparing data for machine learning.",
    ]

    data = vo.VastFrame(
        {
            "id": (list(range(1, len(documents) + 1))),
            "values": documents,
        }
    )

    def create_tfidf_model(
        self,
        name="test_tfidf",
        overwrite_model=False,
        lowercase=True,
        vocabulary=None,
        max_df=None,
        min_df=None,
        norm="l2",
        smooth_idf=True,
        compute_vocabulary=True,
    ):
        """
        function to create TFIDF
        """
        vo.drop(name)
        vo_model = vo_TfidfVectorizer(
            name=name,
            overwrite_model=overwrite_model,
            lowercase=lowercase,
            vocabulary=vocabulary,
            max_df=max_df,
            min_df=min_df,
            norm=norm,
            smooth_idf=smooth_idf,
            compute_vocabulary=compute_vocabulary,
        )
        vo_model.fit(
            input_relation=self.data,
            index="id",
            x="values",
        )

        # python
        py_model = py_TfidfVectorizer(
            lowercase=lowercase,
            vocabulary=[vocabulary] if vocabulary else None,
            max_df=max_df if max_df else 1.0,
            min_df=min_df if min_df else 1,
            norm=norm,
        )
        py_model.fit(self.documents)

        return vo_model, py_model

    @pytest.mark.parametrize(
        "overwrite_model, lowercase, vocabulary, max_df, min_df, norm, smooth_idf, compute_vocabulary",
        [
            (False, True, None, None, None, "l2", True, True),
            (False, False, None, None, None, "l2", True, True),
            # (False, True, "together", None, None, "l2", True, True),  # getting empty vdf. Need to check
            (False, True, None, 4, 1, "l2", True, True),
            (False, True, None, 4, 2, "l2", True, True),
            (False, True, None, None, None, "l1", True, True),
            (False, True, None, None, None, None, True, True),
            (False, True, None, None, None, "l2", False, True),
            (False, True, None, None, None, "l2", True, False),
        ],
    )
    def test_tfidf(
        self,
        schema_loader,
        overwrite_model,
        lowercase,
        vocabulary,
        max_df,
        min_df,
        norm,
        smooth_idf,
        compute_vocabulary,
    ):
        """
        test function for fit TFIDF
        """
        vo_model, py_model = self.create_tfidf_model(
            name=f"{schema_loader}.test_idf",
            overwrite_model=overwrite_model,
            lowercase=lowercase,
            vocabulary=vocabulary,
            max_df=max_df,
            min_df=min_df,
            norm=norm,
            smooth_idf=smooth_idf,
            compute_vocabulary=compute_vocabulary,
        )

        vdf_merge = vo_model.transform(
            vdf=self.data, index="id", x="values", pivot=False
        )
        vdf_merge_pandas = vdf_merge.to_pandas()

        # python
        py_term_vectors = py_model.transform(self.documents)
        array_len = len(py_term_vectors.toarray())
        merge_pdf = pd.DataFrame()

        for i in range(array_len):
            chain_array = py_term_vectors[i].T.toarray().tolist()
            pdf = pd.DataFrame(
                {
                    "row_id": len(chain_array) * [i + 1],
                    "word": py_model.get_feature_names_out(),
                    "tfidf_py": chain(*chain_array),
                }
            )
            nonzero_pdf = pdf[~pdf["tfidf_py"].isin([0])]
            merge_pdf = pd.concat([merge_pdf, nonzero_pdf])

        # inner join as some of the alphabets (like a) are ignored in sklearn(by default)
        merge_vdf_pdf = vdf_merge_pandas.merge(
            merge_pdf, how="inner", on=["row_id", "word"]
        )

        pd.testing.assert_series_equal(
            merge_vdf_pdf["tfidf"],
            merge_vdf_pdf["tfidf_py"],
            check_names=False,
            atol=rel_abs_tol_map["TFIDF"],
        )
