"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional, Union

import numpy as np

from vastorbit._typing import ArrayLike, NoneType, PythonNumber, SQLRelation
from vastorbit._utils._sql._sys import _executeSQL

from vastorbit.core.vastframe.base import VastFrame
from vastorbit.sql.drop import drop

from vastorbit.machine_learning.vast.base import VASTModel


class TfidfVectorizer(VASTModel):
    """
    [Beta Version]
    Create tfidf representation of documents.

    The formula that is used to compute the tf-idf for a
    term t of a document d in a document set is

    .. math::

        tf-idf(t, d) = tf(t, d) * idf(t),

    and if ``smooth_idf = False``, the idf is computed as

    .. math::

        idf(t) = log [ n / df(t) ] + 1,

    where n is the total number of documents in the document
    set and df(t) is the document frequency of t; the document
    frequency is the number of documents in the document set
    that contain the term t. The effect of adding "1" to the
    idf in the equation above is that terms with zero idf, i.e.,
    terms that occur in all documents in a training set, will
    not be entirely ignored.

    If ``smooth_idf=True`` (the default), the constant "1" is
    added to the numerator and denominator of the idf as if an
    extra document was seen containing every term in the
    collection exactly once, which prevents zero divisions:

    .. math::
        idf(t) = log [ (1 + n) / (1 + df(t)) ] + 1.

    Parameters
    ----------
    name: str, optional
        Name of the model.
    overwrite_model: bool, optional
        If set to True, training a model with the
        same name as an existing model overwrites
        the existing model.
    lowercase: bool, optional
        Converts  all  the elements to lowercase
        before processing.
    vocabulary: list, optional
        A list of string elements to be regarded as the primary
        vocabulary.
    max_df: PythonNumber, optional
        While constructing the vocabulary, exclude terms with
        a document frequency surpassing the specified threshold,
        essentially treating them as corpus-specific stop words.
        If the value is a float within the range [0.0, 1.0], it
        denotes a proportion of documents; if an integer, it
        signifies absolute counts. Note that this parameter is
        disregarded if a custom vocabulary is provided.
    min_df: PythonNumber, optional
        When constructing the vocabulary, omit terms with a
        document frequency below the specified threshold,
        often referred to as the cut-off in literature. If
        the value is a float within the range [0.0, 1.0], it
        denotes a proportion of documents; if an integer, it
        signifies absolute counts. It's important to note that
        this parameter is disregarded if a custom vocabulary
        is provided.
    norm: str, optional
        The tfidf values of each document will have unit norm,
        either:

        - l2:
            Sum of squares of vector elements is 1.

        - l1:
            Sum of absolute values of vector elements is 1.

        - None:
            No normalization.

    smooth_idf: bool, optional
        Smooth idf weights by adding one to document frequencies,
        as if an extra document was seen containing every term in
        the collection exactly once. Prevents zero divisions.
    compute_vocabulary: bool, optional
        If set to true, the vocabulary is computed, making the
        operation more resource-intensive.

    Attributes
    ----------
    Many attributes are created
    during the fitting phase.

    vocabulary_: ArrayLike
        The ultimate vocabulary. If empty, it implies that all
        words are utilized, and the user opted not to compute a
        specific vocabulary.
    fixed_vocabulary_: bool
        Boolean indicating whether a vocabulary was supplied by
        the user.
    idf_: VastFrame
        The IDF table which is computed based on the relation
        used for the fitting process.
    tf_: VastFrame
        The TF table which is computed based on the relation
        used for the fitting process.
    stop_words_: ArrayLike
        Terms are excluded under the following conditions:

        - They appear in an excessive number of documents
        (controlled by ``max_df``).

        - They appear in an insufficient number of documents
        (controlled by ``min_df``).

        This functionality is only applicable when no specific
        vocabulary is provided and ``compute_vocabulary`` is
        set to True.
    n_document_: int
        Total number of document. This functionality is only
        applicable when no specific vocabulary is provided and
        ``compute_vocabulary`` is set to True.

    .. note::

        All attributes can be accessed using the
        :py:meth:`~vastorbit.machine_learning.vast.base.VASTModel.get_attributes`
        method.

    Examples
    --------

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

    For this example, let's generate some text.

    .. ipython:: python

        documents = [
            "Natural language processing is a field of study in artificial intelligence.",
            "TF-IDF stands for Term Frequency-Inverse Document Frequency.",
            "Machine learning algorithms can be applied to text data for classification.",
            "The 20 Newsgroups dataset is a collection of text documents used for text classification.",
            "Clustering is a technique used to group similar documents together.",
            "Python is a popular programming language for natural language processing tasks.",
            "TF-IDF is a technique widely used in information retrieval.",
            "An algorithm is a set of instructions designed to perform a specific task.",
            "Data preprocessing is an important step in preparing data for machine learning.",
        ]

    Next, we can insert this text into a :py:class:`~VastFrame`:

    .. ipython:: python


        data = vo.VastFrame(
            {
                "id": (list(range(1,len(documents)+1))),
                "values": documents,
            }
        )

    Then we can initialize the object and fit the model,
    to learn the idf weigths.

    .. code-block:: python

        from vastorbit.machine_learning.vast.feature_extraction.text import TfidfVectorizer

        model = TfidfVectorizer(name = "test_idf")
        model.fit(
            input_relation = data,
            index = "id",
            x = "values",
        )

    We apply the transform function to obtain the idf representation.

    .. code-block:: python

        model.transform(
            vdf = data,
            index = "id",
            x = "values",
        )

    .. ipython:: python
        :suppress:

        from vastorbit.machine_learning.vast.feature_extraction.text import TfidfVectorizer

        model = TfidfVectorizer(name = "test_idf", overwrite_model = True)
        model.fit(input_relation = data, index = "id", x = "values")
        result = model.transform(vdf = data, index = "id", x = "values")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_feature_extraction_text_tfidf.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_feature_extraction_text_tfidf.html

    Notice how we can get the *idf* weight/score of each word
    in each row. We can also get the results in
    a more convient form by switching the
    ``pivot`` parameter to True. But for large datasets
    this is not ideal.

    Advanced Analysis
    ^^^^^^^^^^^^^^^^^^

    In the above result, we can observe some
    less informative words such as "is" and "a",
    which may not provide meaningful insights.

    To address this issue, we can make use of
    the ``max_df`` parameter to exclude words
    that occur too frequently and might be
    irrelevant. Similarly, we can leverage the
    ``min_df`` parameter to eliminate words with
    low frequency that may not contribute significantly.

    Let's apply these parameters to remove
    common words like "is" and "a."


    .. code-block:: python

        model = TfidfVectorizer(max_df = 4, min_df = 1,)
        model.fit(
            input_relation = data,
            index = "id",
            x = "values",
        )
        model.transform(
            vdf = data,
            index = "id",
            x = "values",
        )

    .. ipython:: python
        :suppress:

        model = TfidfVectorizer(max_df = 4, min_df = 1,)
        model.fit(input_relation = data, index = "id", x = "values")
        result = model.transform(vdf = data, index = "id", x = "values")
        html_file = open("SPHINX_DIRECTORY/figures/machine_learning_feature_extraction_text_tfidf_2.html", "w")
        html_file.write(result._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/machine_learning_feature_extraction_text_tfidf_2.html

    Notice how we have removed the unnecessary words.

    We can also see which words were omitted
    using the ``stop_words_`` attribute:

    .. ipython:: python

        model.stop_words_

    .. seealso::
        | ``VastColumn.``:py:meth:`~vastorbit.VastColumn.pivot` : pivot VastFrame.
    """

    # Properties.

    @property
    def _model_category(self) -> Literal["UNSUPERVISED"]:
        return "UNSUPERVISED"

    @property
    def _model_subcategory(self) -> Literal["TEXT"]:
        return "TEXT"

    @property
    def _model_type(self) -> Literal["TfidfVectorizer"]:
        return "TfidfVectorizer"

    @property
    def _attributes(self) -> list[str]:
        return [
            "idf_",
            "tf_",
            "vocabulary_",
            "fixed_vocabulary_",
            "stop_words_",
            "n_document_",
        ]

    # System & Special Methods.

    def __init__(
        self,
        name: str = None,
        overwrite_model: bool = False,
        lowercase: bool = True,
        vocabulary: Optional[ArrayLike] = None,
        max_df: Optional[PythonNumber] = None,
        min_df: Optional[PythonNumber] = None,
        norm: Literal["l1", "l2", None] = "l2",
        smooth_idf: bool = True,
        compute_vocabulary: bool = True,
    ) -> None:
        self.create_table_ = not (isinstance(name, NoneType))
        super().__init__(name, overwrite_model)
        self.parameters = {
            "lowercase": lowercase,
            "vocabulary": vocabulary,
            "max_df": max_df,
            "min_df": min_df,
            "norm": norm,
            "smooth_idf": smooth_idf,
            "compute_vocabulary": compute_vocabulary,
        }

    # Methods to simplify the code.

    @staticmethod
    def _wbd(vdf: SQLRelation, index: str, text: str):
        """
        Returns the SQL needed to compute the
        final expressions
        """
        query = f"""
            SELECT
                {index} AS row_id,
                {text} AS content,
                SPLIT(
                    TRIM(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                {text}, 
                                '[^\\w ]', 
                                ''
                            ),
                            ' {{2,}}', 
                            ' '
                        )
                    ),
                    ' '
                ) AS words 
            FROM {vdf}"""
        return query

    def _t_norm(self, alias="tf"):
        """
        return the SQL to generate the normalized term.
        """
        if self.parameters["norm"] == "l2":
            return f"SQRT(SUM(POWER(({alias}.term_freq * idf_log), 2)) OVER (PARTITION BY {alias}.row_id))"
        if self.parameters["norm"] == "l1":
            return f"SUM(ABS({alias}.term_freq * idf_log)) OVER (PARTITION BY {alias}.row_id)"
        return "1"

    def _get_filter_df(self):
        """
        Returns the SQL expression to be able to filter
        the final vocabulary
        """
        min_df, max_df = self.parameters["min_df"], self.parameters["max_df"]
        if isinstance(min_df, NoneType) and isinstance(max_df, NoneType):
            where = ""
        else:
            if not (isinstance(min_df, NoneType)) and (isinstance(max_df, NoneType)):
                where = f" WHERE df >= {min_df}"
                if isinstance(min_df, float) and 0.0 <= min_df <= 1.0:
                    where = f"{where} * total_freq"
            elif not (isinstance(max_df, NoneType)) and (isinstance(min_df, NoneType)):
                where = f" WHERE df <= {max_df}"
                if isinstance(max_df, float) and 0.0 <= max_df <= 1.0:
                    where = f"{where} * total_freq"
            elif (
                isinstance(min_df, float)
                and 0.0 <= min_df <= 1.0
                and isinstance(max_df, float)
                and 0.0 <= max_df <= 1.0
            ):
                where = (
                    f" WHERE df BETWEEN {min_df} * total_freq AND {max_df} * total_freq"
                )
            else:
                where = f" WHERE df BETWEEN {min_df} AND {max_df}"
        return where

    # Model Fitting Method.

    def fit(
        self,
        input_relation: SQLRelation,
        index: str,
        x: str,
        return_report: bool = False,
    ) -> None:
        """
        Applies basic pre-processing. Creates table
        with fitted vocabulary and idf values.

        Parameters
        ----------
        input_relation: SQLRelation
            Training relation.
        index: str
            Column name of the document id.
        x: str
            Column name which contains the text.
        """

        if isinstance(input_relation, VastFrame):
            vdf = input_relation.copy()
        else:
            vdf = VastFrame(input_relation)

        if not self.parameters["lowercase"]:
            text = str(x)
        else:
            text = f"LOWER({x})"

        if self.parameters["smooth_idf"]:
            idf_expr = "LN((1.0 + CAST(count_docs AS DOUBLE)) / (1.0 + CAST(word_doc_count AS DOUBLE))) + 1.0"
        else:
            idf_expr = "LN(CAST(count_docs AS DOUBLE) / CAST(word_doc_count AS DOUBLE)) + 1.0"

        self.idf_sql_ = self.model_name

        if self.overwrite_model:
            drop(self.idf_sql_)

        # Total document count
        q_tdc = f"""
            SELECT
                COUNT(DISTINCT {index}) AS count_docs 
            FROM {vdf}"""

        # Words by document
        q_wbd = self._wbd(vdf=vdf, index=index, text=text)

        # Explode words array (Trino syntax)
        q_e = """
            SELECT
                row_id,
                word_element AS value
            FROM words_by_doc
            CROSS JOIN UNNEST(words) AS t(word_element)"""

        create_table = ""
        if self.create_table_:
            create_table = f"CREATE TABLE {self.idf_sql_} AS"

        # IDF calculation - FIX: Move aggregation inside subquery
        q_idf = f"""
            {create_table}
            WITH 
                tdc AS ({q_tdc}),
                words_by_doc AS ({q_wbd}),
                exploded AS ({q_e}),
                word_counts AS (
                    SELECT
                        value AS word,
                        COUNT(DISTINCT row_id) AS word_doc_count
                    FROM exploded
                    GROUP BY value
                )
            SELECT
                word,
                word_doc_count,
                tdc.count_docs,
                {idf_expr} AS idf_log
            FROM word_counts
            CROSS JOIN tdc
            ORDER BY word_doc_count DESC"""

        if not self.create_table_:
            self.idf_sql_ = f"({q_idf}) AS VASTORBIT_SUBTABLE"
        else:
            _executeSQL(q_idf, print_time_sql=False)
        
        self.idf_ = VastFrame(self.idf_sql_)

        # Term frequency
        q_tf = f"""
            WITH 
                words_by_doc AS ({q_wbd}),
                exploded AS ({q_e})
            SELECT
                row_id,
                value AS word,
                COUNT(*) AS tf
            FROM exploded
            GROUP BY row_id, value"""

        self.tf_ = VastFrame(q_tf)

        # Computing the final vocabulary
        self.fixed_vocabulary_ = not isinstance(
            self.parameters["vocabulary"], NoneType
        )

        if self.parameters["compute_vocabulary"] and isinstance(
            self.parameters["vocabulary"], NoneType
        ):
            self.n_document_ = self.tf_["row_id"].nunique()
            where = self._get_filter_df()
            
            q_df = f"""
                SELECT DISTINCT word 
                FROM (
                    SELECT
                        word, 
                        COUNT(*) AS df,
                        CAST({self.n_document_} AS BIGINT) AS total_freq
                    FROM (
                        SELECT
                            row_id,
                            word
                        FROM ({q_tf}) AS sub1
                        GROUP BY row_id, word
                    ) AS sub2
                    GROUP BY word
                ) AS sub3
                {where}"""
            
            result = _executeSQL(
                q_df, 
                title="Computing the final vocabulary", 
                method="fetchall"
            )
            self.vocabulary_ = np.array([row[0] for row in result])
        else:
            self.vocabulary_ = self.parameters["vocabulary"]
            self.stop_words_ = None
            self.n_document_ = None

        self.stop_words_ = None
        if not isinstance(self.vocabulary_, NoneType) and not self.fixed_vocabulary_:
            self.stop_words_ = self.idf_["word"].distinct()
            for w in self.vocabulary_:
                self.stop_words_.remove(w)
            self.stop_words_ = np.array(self.stop_words_)

    # Prediction / Transformation Methods.

    def transform(
        self, vdf: SQLRelation, index: str, x: str, pivot: bool = False
    ) -> VastFrame:
        """
        Transforms input data to tf-idf representation.
        
        Parameters
        ----------
        vdf: SQLRelation
            Object used to run the prediction. You can
            also specify a customized relation, but you
            must enclose it with an alias. For example,
            ``(SELECT 1) x`` is valid, whereas ``(SELECT 1)``
            and "SELECT 1" are invalid.
        index: str
            Column name of the document id.
        x: str
            Column name which contains the text.
        pivot: bool
            If set to True, the final table will be pivoted
            to have one row per document, resulting in a
            sparse matrix. It's important to note that when
            dealing with a large dictionary, the pivot
            operation can be resource-intensive. In such
            cases, it might be more efficient to set ``pivot``
            to False, filter the output as needed, and then
            manually perform the pivot operation.
        
        Returns
        -------
        VastFrame
            object result of the model transformation with columns:
            row_id, word, tf, idf, tfidf
        """
        if isinstance(vdf, VastFrame):
            vdf = vdf.copy()
        else:
            vdf = VastFrame(vdf)
        
        if not self.parameters["lowercase"]:
            text = str(x)
        else:
            text = f"LOWER({x})"
        
        # Words by document
        q_wbd = self._wbd(vdf=vdf, index=index, text=text)
        
        # Explode words array (Trino syntax)
        q_e = """
            SELECT
                row_id,
                word_element AS value
            FROM words_by_doc
            CROSS JOIN UNNEST(words) AS t(word_element)"""
        
        # Term frequency
        q_tf = f"""
            SELECT
                row_id,
                value AS word,
                COUNT(*) AS term_freq
            FROM exploded
            GROUP BY row_id, value"""
        
        # Filter by vocabulary if provided
        if isinstance(self.vocabulary_, NoneType):
            where = ""
        else:
            words = ", ".join(
                [f"""'{w.replace("'", "''")}'""" for w in self.vocabulary_]
            )
            where = f"WHERE idf_table.word IN ({words})"
        
        # Get normalization with correct alias
        t_norm = self._t_norm(alias="term_frequencies")
        
        # TF-IDF calculation with TF and IDF kept
        q_tfidf = f"""
            WITH
                words_by_doc AS ({q_wbd}),
                exploded AS ({q_e}),
                term_frequencies AS ({q_tf})
            SELECT 
                term_frequencies.row_id,
                idf_table.word,
                CAST(term_frequencies.term_freq AS DOUBLE) AS tf,
                idf_table.idf_log AS idf,
                (CAST(term_frequencies.term_freq AS DOUBLE) * idf_table.idf_log) / {t_norm} AS tfidf
            FROM term_frequencies
            INNER JOIN (SELECT * FROM {self.idf_sql_}) AS idf_table
                ON term_frequencies.word = idf_table.word
            {where}
            ORDER BY term_frequencies.row_id"""
        
        result = VastFrame(q_tfidf)
        
        if not pivot:
            return result
        
        # For pivot, only pivot the tfidf column
        return result.pivot(
            index="row_id", 
            columns="word", 
            values="tfidf", 
            prefix=""
        )
