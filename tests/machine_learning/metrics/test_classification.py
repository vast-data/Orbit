"""
SPDX-License-Identifier: Apache-2.0

Classification metrics on a small hand-built frame (predictable, trivial).
"""

import pytest

import vastorbit as vo
from vastorbit.machine_learning.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_auc_score,
    log_loss,
)


@pytest.fixture(scope="module")
def preds():
    return vo.VastFrame({
        "y_true": [0, 0, 1, 1, 0, 1, 1, 0, 1, 0],
        "y_pred": [0, 1, 1, 1, 0, 0, 1, 0, 1, 0],
        "y_prob": [0.1, 0.6, 0.8, 0.7, 0.2, 0.4, 0.9, 0.3, 0.85, 0.15],
    })


def test_accuracy(preds):
    assert 0.0 <= accuracy_score("y_true", "y_pred", preds) <= 1.0


def test_precision(preds):
    assert 0.0 <= precision_score("y_true", "y_pred", preds) <= 1.0


def test_recall(preds):
    assert 0.0 <= recall_score("y_true", "y_pred", preds) <= 1.0


def test_confusion_matrix(preds):
    assert confusion_matrix("y_true", "y_pred", preds) is not None


def test_roc_auc(preds):
    assert 0.0 <= roc_auc_score("y_true", "y_prob", preds) <= 1.0


def test_log_loss(preds):
    assert log_loss("y_true", "y_prob", preds) >= 0.0
