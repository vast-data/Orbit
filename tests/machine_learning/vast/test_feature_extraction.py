"""
SPDX-License-Identifier: Apache-2.0

Text feature extraction: TfidfVectorizer.
"""

import vastorbit as vo
from vastorbit.machine_learning.vast import TfidfVectorizer


def test_tfidf_vectorizer(name_factory):
    docs = vo.VastFrame(
        {
            "id": [1, 2, 3, 4],
            "text": [
                "the cat sat on the mat",
                "the dog ran in the park",
                "a cat and a dog played",
                "birds fly high above",
            ],
        }
    )
    tf = TfidfVectorizer(name=name_factory("tfidf"))
    tf.fit(docs, "id", "text")
    out = tf.transform(docs, "id", "text")
    assert out is not None
