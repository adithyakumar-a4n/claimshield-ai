"""Reporting invariants: summary metrics must reconcile with scored rows."""
import pandas as pd

from claimshield.reporting import build_kpi_summary, build_provider_summary


def _sample_scored_claims() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "claim_id": ["C1", "C2", "C3", "C4"],
            "provider_id": ["P1", "P1", "P2", "P2"],
            "claim_amount": [100.0, 200.0, 300.0, 400.0],
            "paid_amount": [80.0, 0.0, 250.0, 100.0],
            "claim_status": ["paid", "denied", "paid", "denied"],
            "review_candidate": [False, True, True, False],
        }
    )


def test_kpis_reconcile_to_source_rows() -> None:
    frame = _sample_scored_claims()
    kpi = build_kpi_summary(frame).iloc[0]

    assert kpi["total_claims"] == 4
    assert kpi["total_claim_amount"] == 1000.0
    assert kpi["total_paid_amount"] == 430.0
    assert kpi["review_candidate_count"] == 2
    assert kpi["review_candidate_rate_pct"] == 50.0
    assert kpi["denied_claim_count"] == 2
    assert kpi["denied_claim_rate_pct"] == 50.0


def test_provider_summary_counts_and_rates_reconcile() -> None:
    summary = build_provider_summary(_sample_scored_claims()).set_index("provider_id")

    assert summary.loc["P1", "claim_count"] == 2
    assert summary.loc["P1", "review_candidate_count"] == 1
    assert summary.loc["P1", "review_candidate_rate_pct"] == 50.0
    assert summary.loc["P2", "claim_count"] == 2
    assert summary.loc["P2", "review_candidate_count"] == 1
    assert summary.loc["P2", "review_candidate_rate_pct"] == 50.0


def test_empty_kpi_frame_has_zero_count_and_rate() -> None:
    empty = pd.DataFrame(
        columns=[
            "claim_amount", "paid_amount", "claim_status", "review_candidate"
        ]
    )
    kpi = build_kpi_summary(empty).iloc[0]

    assert kpi["total_claims"] == 0
    assert kpi["review_candidate_count"] == 0
    assert kpi["review_candidate_rate_pct"] == 0.0
    assert kpi["denied_claim_rate_pct"] == 0.0
