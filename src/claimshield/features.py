"""Feature engineering for claims analytics and anomaly detection."""
from __future__ import annotations
import numpy as np
import pandas as pd


def build_claim_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create numeric features used by anomaly detection without using labels."""
    required = {"claim_amount", "paid_amount", "service_date", "submission_date"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns required for feature engineering: {', '.join(missing)}")
    claims = frame.copy()
    claim_amount = pd.to_numeric(claims["claim_amount"], errors="coerce")
    paid_amount = pd.to_numeric(claims["paid_amount"], errors="coerce")
    service_date = pd.to_datetime(claims["service_date"], errors="coerce")
    submission_date = pd.to_datetime(claims["submission_date"], errors="coerce")
    delay_days = (submission_date - service_date).dt.total_seconds() / 86400
    features = pd.DataFrame(index=claims.index)
    features["claim_amount"] = claim_amount
    features["paid_amount"] = paid_amount
    features["paid_to_claim_ratio"] = (paid_amount / claim_amount.where(claim_amount != 0)).fillna(0).clip(lower=0, upper=10)
    features["submission_delay_days"] = delay_days.fillna(0).clip(lower=0, upper=3650)
    features["claim_amount_log1p"] = np.log1p(claim_amount.clip(lower=0).fillna(0))
    return features.replace([float("inf"), float("-inf")], 0).fillna(0)
