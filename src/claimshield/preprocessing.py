"""Conservative preprocessing helpers for claims analytics."""
from __future__ import annotations
import pandas as pd

DATE_COLUMNS = ("service_date", "submission_date")
NUMERIC_COLUMNS = ("claim_amount", "paid_amount")


def preprocess_claims(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy with normalized dates, statuses, and numeric fields.

    This function deliberately does not drop rows: potentially meaningful defects
    remain inspectable and are reported by the validation module.
    """
    cleaned = frame.copy(deep=True)
    for column in DATE_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")
    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    for column in ("claim_id", "member_id", "provider_id", "procedure_code", "diagnosis_group", "place_of_service"):
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype("string").str.strip()
            cleaned[column] = cleaned[column].replace({"": pd.NA, "<NA>": pd.NA})
    if "claim_status" in cleaned.columns:
        cleaned["claim_status"] = cleaned["claim_status"].astype("string").str.strip().str.lower()
    return cleaned
