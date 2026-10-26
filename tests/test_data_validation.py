import pandas as pd
from claimshield.data_validation import validate_claims
from claimshield.synthetic_data import generate_synthetic_claims


def test_generated_dataset_has_expected_required_columns():
    frame = generate_synthetic_claims(n_rows=100, random_seed=7)
    issues = validate_claims(frame)
    assert "claim_id" in frame.columns
    assert any(issue.check == "duplicate_claim_id" for issue in issues)
    assert any(issue.check == "missing_provider_id" for issue in issues)


def test_missing_required_column_is_reported():
    frame = pd.DataFrame({"claim_id": ["A"]})
    issues = validate_claims(frame)
    assert len(issues) == 1
    assert issues[0].check == "required_columns"
    assert issues[0].severity == "error"


def test_paid_amount_above_claim_amount_is_reported():
    frame = generate_synthetic_claims(n_rows=50, random_seed=8)
    frame.loc[0, "claim_amount"] = 10.0
    frame.loc[0, "paid_amount"] = 20.0
    issues = validate_claims(frame)
    assert any(issue.check == "paid_exceeds_claim" for issue in issues)
