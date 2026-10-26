"""Unsupervised anomaly scoring; scores are review signals, not fraud labels."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from sklearn.ensemble import IsolationForest
from .features import build_claim_features

@dataclass
class AnomalyResult:
    scored_claims: pd.DataFrame
    model: IsolationForest
    feature_columns: list[str]


def score_anomalies(frame: pd.DataFrame, contamination: float = 0.05, random_state: int = 42) -> AnomalyResult:
    """Fit Isolation Forest and return rows with anomaly scores and review flags."""
    if not 0.0 < contamination <= 0.5:
        raise ValueError("contamination must be greater than 0 and at most 0.5")
    if len(frame) < 2:
        raise ValueError("At least two rows are required for anomaly detection")
    features = build_claim_features(frame)
    model = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=200)
    model.fit(features)
    scored = frame.copy(deep=True)
    scored["anomaly_score"] = -model.decision_function(features)
    scored["anomaly_label"] = pd.Series(model.predict(features), index=scored.index).map({1: "typical", -1: "review_candidate"})
    scored["review_candidate"] = scored["anomaly_label"].eq("review_candidate")
    scored["review_reason"] = scored.apply(_review_reason, axis=1)
    return AnomalyResult(scored_claims=scored, model=model, feature_columns=list(features.columns))


def _review_reason(row: pd.Series) -> str:
    reasons: list[str] = []
    claim_amount = pd.to_numeric(pd.Series([row.get("claim_amount")]), errors="coerce").iloc[0]
    paid_amount = pd.to_numeric(pd.Series([row.get("paid_amount")]), errors="coerce").iloc[0]
    if pd.notna(claim_amount) and claim_amount < 0:
        reasons.append("negative_claim_amount")
    if pd.notna(claim_amount) and pd.notna(paid_amount) and paid_amount > claim_amount:
        reasons.append("paid_exceeds_claim")
    if pd.notna(claim_amount) and claim_amount >= 1000:
        reasons.append("high_claim_amount_threshold_for_demo")
    if not reasons and bool(row.get("review_candidate", False)):
        reasons.append("multivariate_anomaly_model")
    return ";".join(reasons)
