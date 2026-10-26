"""Schema and data-quality validation for claims-like tabular data."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import pandas as pd

REQUIRED_COLUMNS = (
    "claim_id", "member_id", "provider_id", "service_date", "submission_date",
    "procedure_code", "diagnosis_group", "place_of_service", "claim_amount",
    "paid_amount", "claim_status",
)
ALLOWED_STATUSES = {"paid", "denied", "pending", "adjusted"}

@dataclass(frozen=True)
class ValidationIssue:
    check: str
    severity: str
    affected_rows: int
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_claims(frame: pd.DataFrame) -> list[ValidationIssue]:
    """Return all detectable quality issues; do not mutate the supplied DataFrame."""
    issues: list[ValidationIssue] = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        issues.append(ValidationIssue("required_columns", "error", len(missing_columns),
                                      f"Missing required columns: {', '.join(missing_columns)}"))
        return issues
    if frame.empty:
        issues.append(ValidationIssue("empty_dataset", "error", 0, "Dataset has no rows."))
        return issues

    for column in ("claim_id", "member_id", "provider_id"):
        count = int(frame[column].isna().sum())
        if count:
            issues.append(ValidationIssue(f"missing_{column}", "warning", count,
                                          f"{column} contains missing values."))
    duplicate_count = int(frame["claim_id"].duplicated(keep=False).sum())
    if duplicate_count:
        issues.append(ValidationIssue("duplicate_claim_id", "warning", duplicate_count,
                                      "Claim identifiers are not unique; inspect before downstream use."))

    for column in ("claim_amount", "paid_amount"):
        numeric = pd.to_numeric(frame[column], errors="coerce")
        invalid_count = int(numeric.isna().sum())
        if invalid_count:
            issues.append(ValidationIssue(f"invalid_{column}", "error", invalid_count,
                                          f"{column} contains non-numeric or missing values."))
        negative_count = int((numeric < 0).fillna(False).sum())
        if negative_count:
            issues.append(ValidationIssue(f"negative_{column}", "warning", negative_count,
                                          f"{column} contains negative values."))
    claim_amount = pd.to_numeric(frame["claim_amount"], errors="coerce")
    paid_amount = pd.to_numeric(frame["paid_amount"], errors="coerce")
    overpaid = int((paid_amount > claim_amount).fillna(False).sum())
    if overpaid:
        issues.append(ValidationIssue("paid_exceeds_claim", "warning", overpaid,
                                      "Paid amount exceeds submitted claim amount."))

    service_dates = pd.to_datetime(frame["service_date"], errors="coerce")
    submission_dates = pd.to_datetime(frame["submission_date"], errors="coerce")
    bad_dates = int((service_dates.isna() | submission_dates.isna()).sum())
    if bad_dates:
        issues.append(ValidationIssue("invalid_dates", "error", bad_dates,
                                      "Service or submission date is missing or invalid."))
    submitted_before_service = int((submission_dates < service_dates).fillna(False).sum())
    if submitted_before_service:
        issues.append(ValidationIssue("submission_before_service", "warning", submitted_before_service,
                                      "Submission date occurs before service date."))
    unknown_statuses = sorted(set(frame["claim_status"].dropna().astype(str).str.lower()) - ALLOWED_STATUSES)
    if unknown_statuses:
        issues.append(ValidationIssue("unknown_claim_status", "warning", len(unknown_statuses),
                                      f"Unrecognized statuses: {', '.join(unknown_statuses)}"))
    return issues


def validation_issues_frame(issues: list[ValidationIssue]) -> pd.DataFrame:
    """Convert validation issues to a stable tabular report."""
    return pd.DataFrame([issue.to_dict() for issue in issues], columns=["check", "severity", "affected_rows", "message"])
