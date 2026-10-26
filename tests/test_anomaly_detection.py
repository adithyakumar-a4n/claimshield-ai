import pandas as pd
import pytest
from claimshield.anomaly_detection import score_anomalies
from claimshield.synthetic_data import generate_synthetic_claims


def test_anomaly_detector_returns_correct_columns_and_labels():
    frame = generate_synthetic_claims(n_rows=100, random_seed=11)
    result = score_anomalies(frame, contamination=0.05, random_state=11)
    scored = result.scored_claims
    assert len(scored) == len(frame)
    assert "anomaly_score" in scored.columns
    assert "review_candidate" in scored.columns
    assert set(scored["anomaly_label"].unique()).issubset({"typical", "review_candidate"})


def test_review_candidates_have_higher_anomaly_scores_than_typical():
    """Review candidates must have a higher mean anomaly score than typical rows.

    This verifies that the anomaly_score column is meaningful, not just a label copy.
    IsolationForest by design assigns higher scores to more isolated (outlier) points,
    so this assertion must hold regardless of seed.
    """
    frame = generate_synthetic_claims(n_rows=200, random_seed=11)
    result = score_anomalies(frame, contamination=0.05, random_state=11)
    scored = result.scored_claims
    review_scores = scored.loc[scored["review_candidate"], "anomaly_score"]
    typical_scores = scored.loc[~scored["review_candidate"], "anomaly_score"]
    assert review_scores.mean() > typical_scores.mean(), (
        "Review candidates should have higher anomaly scores than typical rows."
    )


def test_invalid_contamination_is_rejected():
    frame = generate_synthetic_claims(n_rows=30, random_seed=12)
    with pytest.raises(ValueError, match="contamination"):
        score_anomalies(frame, contamination=0)


def test_too_few_rows_is_rejected():
    frame = generate_synthetic_claims(n_rows=30, random_seed=13).head(1)
    with pytest.raises(ValueError, match="At least two rows"):
        score_anomalies(frame)
