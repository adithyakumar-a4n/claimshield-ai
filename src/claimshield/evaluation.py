"""Evaluate Isolation Forest against labels in a synthetic claims dataset."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, average_precision_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

REQUIRED_COLUMNS = {"is_fraud", "billed_amount", "severity", "procedure_category", "diagnosis_group"}
NUMERIC_FEATURES = ["billed_amount", "severity"]
CATEGORICAL_FEATURES = ["procedure_category", "diagnosis_group"]
FORBIDDEN_FEATURES = {"is_fraud", "fraud_scheme", "claim_id", "patient_id"}


def _prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Select allowed predictors and normalize their basic types."""
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    features = frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    features["billed_amount"] = pd.to_numeric(features["billed_amount"], errors="coerce")
    features["severity"] = pd.to_numeric(features["severity"], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        features[column] = features[column].astype("string").fillna("Unknown").astype(str)
    if features[NUMERIC_FEATURES].isna().all(axis=None):
        raise ValueError("All numeric feature values are missing or invalid")
    return features


def evaluate_dataset(
    input_path: str | Path,
    output_dir: str | Path = "outputs/evaluation",
    *,
    contamination: float = 0.05,
    random_state: int = 42,
    test_size: float = 0.25,
) -> dict[str, Any]:
    """Fit unsupervised Isolation Forest on train features; evaluate held-out labels."""
    if not 0.0 < contamination <= 0.5:
        raise ValueError("contamination must be greater than 0 and at most 0.5")
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be between 0 and 1")
    source = Path(input_path)
    frame = pd.read_csv(source)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    labels_raw = pd.to_numeric(frame["is_fraud"], errors="raise")
    if labels_raw.isna().any() or not set(labels_raw.unique()).issubset({0, 1}):
        raise ValueError("is_fraud must contain only non-null binary labels 0 and 1")
    labels = labels_raw.astype(int)
    if labels.nunique() != 2 or labels.value_counts().min() < 2:
        raise ValueError("At least two rows from each label class are required")
    X = _prepare_features(frame)
    assert not (set(X.columns) & FORBIDDEN_FEATURES)

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, labels, frame.index, test_size=test_size, random_state=random_state, stratify=labels
    )
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
    ])
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("isolation_forest", IsolationForest(
            n_estimators=200, contamination=contamination, random_state=random_state
        )),
    ])
    model.fit(X_train)  # labels are deliberately not used to fit the model
    decision_scores = model.decision_function(X_test)
    anomaly_scores = -decision_scores
    predictions = (decision_scores < 0).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    metrics: dict[str, Any] = {
        "dataset_path": str(source),
        "rows_total": int(len(frame)),
        "rows_train": int(len(X_train)),
        "rows_test": int(len(X_test)),
        "positive_labels_total": int(labels.sum()),
        "positive_rate_pct_total": round(float(labels.mean() * 100), 4),
        "test_positive_labels": int(y_test.sum()),
        "contamination": contamination,
        "random_state": random_state,
        "test_size": test_size,
        "features_used": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "label_columns_excluded_from_features": ["is_fraud", "fraud_scheme"],
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "average_precision_pr_auc": float(average_precision_score(y_test, anomaly_scores)),
        "roc_auc": float(roc_auc_score(y_test, anomaly_scores)),
        "true_negative": int(tn), "false_positive": int(fp),
        "false_negative": int(fn), "true_positive": int(tp),
        "baseline_all_negative_accuracy": float((y_test == 0).mean()),
        "baseline_all_negative_recall": 0.0,
        "interpretation": (
            "Metrics measure agreement with labels in this synthetic dataset only; "
            "they do not establish real-world healthcare fraud detection performance."
        ),
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    predictions_frame = frame.loc[idx_test].copy()
    predictions_frame["evaluation_true_label"] = y_test.loc[idx_test].astype(int)
    predictions_frame["anomaly_score"] = anomaly_scores
    predictions_frame["predicted_review_candidate"] = predictions
    predictions_frame.to_csv(output / "evaluation_predictions.csv", index=False)
    (output / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    pd.DataFrame([metrics]).to_csv(output / "evaluation_metrics.csv", index=False)
    pd.DataFrame(
        [[tn, fp], [fn, tp]],
        index=["actual_non_fraud", "actual_fraud"],
        columns=["predicted_typical", "predicted_review_candidate"],
    ).to_csv(output / "confusion_matrix.csv", index=True)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate ClaimShield Isolation Forest on a labeled dataset.")
    parser.add_argument("--input", default="data/external/claims_sample.csv")
    parser.add_argument("--output-dir", default="outputs/evaluation")
    parser.add_argument("--contamination", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.25)
    args = parser.parse_args()
    metrics = evaluate_dataset(
        args.input, args.output_dir, contamination=args.contamination,
        random_state=args.seed, test_size=args.test_size,
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
