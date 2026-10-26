import pandas as pd
import pytest
from claimshield.anomaly_detection import score_anomalies
from claimshield.synthetic_data import generate_synthetic_claims


def test_anomaly_detector_returns_scores_and_labels():
    frame = generate_synthetic_claims(n_rows=100, random_seed=11)
    result = score_anomalies(frame, contamination=0.05, random_state=11)
    assert len(result.scored_claims) == len(frame)
    assert "anomaly_score" in result.scored_claims.columns
    assert set(result.scored_claims["anomaly_label"].unique()).issubset({"typical", "review_candidate"})
    assert result.scored_claims["review_candidate"].any()


def test_invalid_contamination_is_rejected():
    frame = generate_synthetic_claims(n_rows=30, random_seed=12)
    with pytest.raises(ValueError, match="contamination"):
        score_anomalies(frame, contamination=0)


def test_too_few_rows_is_rejected():
    frame = generate_synthetic_claims(n_rows=30, random_seed=13).head(1)
    with pytest.raises(ValueError, match="At least two rows"):
        score_anomalies(frame)
