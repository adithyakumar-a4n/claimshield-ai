
import pandas as pd
import pytest

from sklearn.metrics import f1_score, precision_score, recall_score


def test_threshold_predictions_use_greater_than_or_equal():
    scores = pd.Series([0.20, 0.50, 0.80])
    predictions = (scores >= 0.50).astype(int)

    assert predictions.tolist() == [0, 1, 1]


def test_higher_threshold_does_not_increase_flagged_count():
    scores = pd.Series([0.10, 0.30, 0.50, 0.70, 0.90])

    low_threshold_count = int((scores >= 0.30).sum())
    high_threshold_count = int((scores >= 0.70).sum())

    assert high_threshold_count <= low_threshold_count


def test_metrics_are_calculated_for_imbalanced_labels():
    actual = [0, 0, 0, 1, 1]
    predicted = [0, 0, 1, 1, 0]

    assert precision_score(actual, predicted) == pytest.approx(0.5)
    assert recall_score(actual, predicted) == pytest.approx(0.5)
    assert f1_score(actual, predicted) == pytest.approx(0.5)
