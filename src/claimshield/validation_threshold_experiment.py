
"""Select a Random Forest threshold on validation data and evaluate once on test data."""

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def metrics_at_threshold(y_true, scores, threshold):
    predicted = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(
        y_true, predicted, labels=[0, 1]
    ).ravel()

    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, predicted)),
        "precision": float(precision_score(
            y_true, predicted, zero_division=0
        )),
        "recall": float(recall_score(
            y_true, predicted, zero_division=0
        )),
        "f1": float(f1_score(
            y_true, predicted, zero_division=0
        )),
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "average_precision": float(
            average_precision_score(y_true, scores)
        ),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "flagged_count": int(predicted.sum()),
        "flagged_rate_pct": float(predicted.mean() * 100),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", default="data/external/claims_sample.csv"
    )
    parser.add_argument(
        "--output-dir", default="outputs/validation_threshold"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    required = [
        "is_fraud",
        "billed_amount",
        "severity",
        "procedure_category",
        "diagnosis_group",
    ]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[required].dropna(subset=["is_fraud"]).copy()
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"].astype(int)

    if set(y.unique()) != {0, 1}:
        raise ValueError("is_fraud must contain both 0 and 1 labels.")

    # First reserve 20% for the final test set.
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=args.seed,
        stratify=y,
    )

    # Split the remaining 80% into 60% train and 20% validation.
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval,
        test_size=0.25,
        random_state=args.seed,
        stratify=y_trainval,
    )

    numeric = ["billed_amount", "severity"]
    categorical = ["procedure_category", "diagnosis_group"]

    preprocess = ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), numeric),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical),
    ])

    model = Pipeline([
        ("preprocess", preprocess),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=args.seed,
            n_jobs=-1,
        )),
    ])

    # Fit model and preprocessing on training data only.
    model.fit(X_train, y_train)

    # Select threshold using validation data only.
    val_scores = model.predict_proba(X_val)[:, 1]
    thresholds = [i / 100 for i in range(5, 76, 5)]

    validation_rows = [
        metrics_at_threshold(y_val, val_scores, threshold)
        for threshold in thresholds
    ]
    validation_metrics = pd.DataFrame(validation_rows)
    validation_metrics.to_csv(
        output_dir / "validation_threshold_metrics.csv",
        index=False,
    )

    # Choose highest validation F1; break ties by precision, then threshold.
    best = validation_metrics.sort_values(
        ["f1", "precision", "threshold"],
        ascending=[False, False, False],
    ).iloc[0]
    selected_threshold = float(best["threshold"])

    # Evaluate the frozen threshold once on the held-out test set.
    test_scores = model.predict_proba(X_test)[:, 1]
    test_result = metrics_at_threshold(
        y_test, test_scores, selected_threshold
    )

    test_predictions = pd.DataFrame({
        "actual_is_fraud": y_test.to_numpy(),
        "predicted_probability": test_scores,
        "predicted_is_review_candidate": (
            test_scores >= selected_threshold
        ).astype(int),
    }, index=y_test.index)
    test_predictions.sort_index().to_csv(
        output_dir / "test_predictions.csv",
        index_label="row_index",
    )

    summary = {
        "dataset": str(args.input),
        "seed": args.seed,
        "split": {
            "train_rows": int(len(X_train)),
            "validation_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        },
        "features": numeric + categorical,
        "excluded_from_features": [
            "is_fraud", "fraud_scheme", "claim_id", "patient_id"
        ],
        "threshold_selection_metric": "validation F1",
        "selected_threshold": selected_threshold,
        "validation_metrics_at_selected_threshold": {
            key: float(best[key])
            for key in [
                "precision", "recall", "f1",
                "flagged_rate_pct", "flagged_count"
            ]
        },
        "held_out_test_metrics": test_result,
        "limitation": (
            "Synthetic dataset only. The test set was reserved from "
            "threshold selection, but repeated experimentation or "
            "model changes can still lead to test-set overuse."
        ),
    }

    with open(
        output_dir / "experiment_summary.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(summary, file, indent=2)

    print("Split sizes:", summary["split"])
    print("Threshold selected on validation:", selected_threshold)
    print("\nHeld-out test metrics:")
    print(pd.Series(test_result).to_string())
    print(f"\nSaved results to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
