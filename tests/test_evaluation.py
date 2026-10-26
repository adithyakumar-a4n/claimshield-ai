from pathlib import Path
import pandas as pd
import pytest
from claimshield.evaluation import _prepare_features, evaluate_dataset


def _sample_dataset(path: Path) -> Path:
    rows = []
    for i in range(80):
        fraud = int(i % 10 == 0)
        rows.append({
            "claim_id": f"C{i}", "patient_id": f"P{i % 20}",
            "billed_amount": 5000.0 if fraud else 100.0 + (i % 17),
            "severity": 5 if fraud else 1 + (i % 3),
            "procedure_category": "rare" if fraud else "common",
            "diagnosis_group": "group_x" if fraud else "group_y",
            "fraud_scheme": "test_scheme" if fraud else None, "is_fraud": fraud,
        })
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_labels_and_fraud_scheme_are_not_features():
    frame = pd.DataFrame({
        "is_fraud": [0, 1], "fraud_scheme": [None, "scheme"],
        "billed_amount": [100, 5000], "severity": [1, 5],
        "procedure_category": ["common", "rare"], "diagnosis_group": ["x", "y"],
    })
    features = _prepare_features(frame)
    assert "is_fraud" not in features.columns
    assert "fraud_scheme" not in features.columns


def test_evaluation_writes_metrics_and_predictions(tmp_path):
    dataset = _sample_dataset(tmp_path / "sample.csv")
    out = tmp_path / "out"
    metrics = evaluate_dataset(dataset, out, random_state=7)
    assert metrics["rows_total"] == 80
    assert metrics["rows_train"] + metrics["rows_test"] == 80
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["average_precision_pr_auc"] <= 1
    assert (out / "evaluation_metrics.json").exists()
    assert (out / "evaluation_metrics.csv").exists()
    assert (out / "evaluation_predictions.csv").exists()
    assert (out / "confusion_matrix.csv").exists()


def test_invalid_contamination_raises(tmp_path):
    dataset = _sample_dataset(tmp_path / "sample.csv")
    with pytest.raises(ValueError, match="contamination"):
        evaluate_dataset(dataset, tmp_path / "out", contamination=0)


def test_missing_required_column_raises(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"is_fraud": [0, 1]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        evaluate_dataset(path, tmp_path / "out")
