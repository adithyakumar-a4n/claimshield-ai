"""Create compact, Power BI-friendly reporting tables."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from .data_validation import ValidationIssue, validation_issues_frame


def build_kpi_summary(scored_claims: pd.DataFrame) -> pd.DataFrame:
    """Return one-row operational KPI summary with explicit denominators."""
    total = int(len(scored_claims))
    amount = pd.to_numeric(scored_claims.get("claim_amount", pd.Series(dtype=float)), errors="coerce")
    paid = pd.to_numeric(scored_claims.get("paid_amount", pd.Series(dtype=float)), errors="coerce")
    review_count = int(scored_claims.get("review_candidate", pd.Series(False, index=scored_claims.index)).fillna(False).astype(bool).sum())
    denied_count = int(scored_claims.get("claim_status", pd.Series(dtype="string")).astype("string").str.lower().eq("denied").sum())
    return pd.DataFrame([{
        "total_claims": total,
        "total_claim_amount": round(float(amount.sum(min_count=1) or 0), 2),
        "total_paid_amount": round(float(paid.sum(min_count=1) or 0), 2),
        "review_candidate_count": review_count,
        "review_candidate_rate_pct": round((review_count / total * 100), 2) if total else 0.0,
        "denied_claim_count": denied_count,
        "denied_claim_rate_pct": round((denied_count / total * 100), 2) if total else 0.0,
    }])


def build_provider_summary(scored_claims: pd.DataFrame) -> pd.DataFrame:
    """Summarize claim volume and review candidates by provider."""
    required = {"provider_id", "claim_id", "claim_amount", "paid_amount", "review_candidate"}
    if not required.issubset(scored_claims.columns):
        return pd.DataFrame(columns=["provider_id", "claim_count", "claim_amount_sum", "paid_amount_sum", "review_candidate_count", "review_candidate_rate_pct"])
    grouped = scored_claims.groupby("provider_id", dropna=False).agg(
        claim_count=("claim_id", "count"),
        claim_amount_sum=("claim_amount", "sum"),
        paid_amount_sum=("paid_amount", "sum"),
        review_candidate_count=("review_candidate", "sum"),
    ).reset_index()
    grouped["review_candidate_rate_pct"] = (grouped["review_candidate_count"] / grouped["claim_count"] * 100).round(2)
    return grouped.sort_values(["review_candidate_count", "claim_count"], ascending=False).reset_index(drop=True)


def write_reports(output_dir: str | Path, scored_claims: pd.DataFrame, issues: list[ValidationIssue]) -> dict[str, Path]:
    """Write CSV reports and return their paths."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "scored_claims": destination / "scored_claims.csv",
        "kpi_summary": destination / "kpi_summary.csv",
        "provider_summary": destination / "provider_summary.csv",
        "data_quality_issues": destination / "data_quality_issues.csv",
    }
    scored_claims.to_csv(paths["scored_claims"], index=False)
    build_kpi_summary(scored_claims).to_csv(paths["kpi_summary"], index=False)
    build_provider_summary(scored_claims).to_csv(paths["provider_summary"], index=False)
    validation_issues_frame(issues).to_csv(paths["data_quality_issues"], index=False)
    return paths
