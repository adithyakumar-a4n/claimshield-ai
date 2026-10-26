"""Reproducibility checks for synthetic generation and anomaly scoring."""
import pandas as pd
from pandas.testing import assert_frame_equal

from claimshield.anomaly_detection import score_anomalies
from claimshield.synthetic_data import generate_synthetic_claims


def test_synthetic_dataset_is_reproducible_for_same_seed() -> None:
    first = generate_synthetic_claims(n_rows=120, random_seed=123)
    second = generate_synthetic_claims(n_rows=120, random_seed=123)

    assert_frame_equal(first, second)


def test_anomaly_scoring_is_reproducible_for_same_input_and_seed() -> None:
    frame = generate_synthetic_claims(n_rows=120, random_seed=123)
    # Keep scoring test data clean to isolate model determinism from cleaning behavior.
    frame["claim_amount"] = pd.to_numeric(frame["claim_amount"], errors="coerce").fillna(0).clip(lower=0)
    frame["paid_amount"] = pd.to_numeric(frame["paid_amount"], errors="coerce").fillna(0).clip(lower=0)

    first = score_anomalies(frame, contamination=0.05, random_state=123).scored_claims
    second = score_anomalies(frame, contamination=0.05, random_state=123).scored_claims

    assert first["review_candidate"].tolist() == second["review_candidate"].tolist()
    assert first["anomaly_score"].tolist() == second["anomaly_score"].tolist()
