
"""Compare unsupervised and supervised models on synthetic claims labels."""

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
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
from sklearn.dummy import DummyClassifier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/external/claims_sample.csv")
    parser.add_argument("--output-dir", default="outputs/model_comparison")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--contamination", type=float, default=0.05)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
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
    y = df["is_fraud"].astype(int)
    X = df.drop(columns=["is_fraud"])

    if set(y.unique()) != {0, 1}:
        raise ValueError("is_fraud must contain both 0 and 1 labels.")

    numeric = ["billed_amount", "severity"]
    categorical = ["procedure_category", "diagnosis_group"]

    preprocess = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                ]),
                numeric,
            ),
            (
                "categorical",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical,
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=args.seed,
        stratify=y,
    )

    # All preprocessing is fitted on training data only.
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)

    supervised = Pipeline([
        ("preprocess", preprocess),
        (
            "model",
            RandomForestClassifier(
                n_estimators=300,
                class_weight="balanced",
                random_state=args.seed,
                n_jobs=-1,
            ),
        ),
    ])
    supervised.fit(X_train, y_train)

    # Isolation Forest uses the same features but does not use labels to fit.
    unsupervised_preprocess = preprocess.fit(X_train)
    X_train_transformed = unsupervised_preprocess.transform(X_train)
    X_test_transformed = unsupervised_preprocess.transform(X_test)

    isolation = IsolationForest(
        n_estimators=200,
        contamination=args.contamination,
        random_state=args.seed,
        n_jobs=-1,
    )
    isolation.fit(X_train_transformed)

    results = []
    predictions = pd.DataFrame({
        "actual_is_fraud": y_test.to_numpy(),
    }, index=y_test.index)

    def record(name, predicted, score):
        tn, fp, fn, tp = confusion_matrix(
            y_test, predicted, labels=[0, 1]
        ).ravel()

        row = {
            "model": name,
            "accuracy": accuracy_score(y_test, predicted),
            "precision": precision_score(
                y_test, predicted, zero_division=0
            ),
            "recall": recall_score(
                y_test, predicted, zero_division=0
            ),
            "f1": f1_score(y_test, predicted, zero_division=0),
            "roc_auc": (
                roc_auc_score(y_test, score)
                if score is not None else None
            ),
            "average_precision": (
                average_precision_score(y_test, score)
                if score is not None else None
            ),
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
            "flagged_count": int(predicted.sum()),
        }
        results.append(row)
        predictions[f"{name}_prediction"] = pd.Series(
            predicted, index=y_test.index
        )

    dummy_pred = dummy.predict(X_test)
    record("dummy", dummy_pred, None)

    rf_pred = supervised.predict(X_test)
    rf_scores = supervised.predict_proba(X_test)[:, 1]
    record("random_forest", rf_pred, rf_scores)

    # Isolation Forest's lower decision scores indicate more anomalous rows.
    if_scores = -isolation.decision_function(X_test_transformed)
    if_pred = (isolation.predict(X_test_transformed) == -1).astype(int)
    record("isolation_forest", if_pred, if_scores)

    metrics = pd.DataFrame(results)
    metrics = metrics.sort_values(
        "average_precision", ascending=False, na_position="last"
    )

    metrics.to_csv(output_dir / "comparison_metrics.csv", index=False)
    predictions.sort_index().to_csv(
        output_dir / "comparison_predictions.csv", index_label="row_index"
    )

    summary = {
        "dataset": str(input_path),
        "rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "positive_rate_pct": round(float(y.mean() * 100), 4),
        "seed": args.seed,
        "contamination": args.contamination,
        "features": numeric + categorical,
        "excluded_label_columns": ["is_fraud", "fraud_scheme"],
        "results": results,
        "limitation": (
            "All evaluation is on synthetic labels and does not establish "
            "real-world healthcare fraud detection performance."
        ),
    }

    with open(output_dir / "comparison_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(metrics.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nSaved results to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
