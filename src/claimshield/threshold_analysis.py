
"""Evaluate Random Forest decision thresholds on saved test predictions."""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="outputs/model_comparison/comparison_predictions.csv",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/threshold_analysis",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    required = {
        "actual_is_fraud",
        "random_forest_score",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing columns: {missing}. "
            "Rerun model_comparison after saving random_forest_score."
        )

    y_true = df["actual_is_fraud"].astype(int)
    scores = df["random_forest_score"].astype(float)

    if not scores.between(0, 1).all():
        raise ValueError("Random Forest scores must be between 0 and 1.")

    thresholds = [
        0.05, 0.10, 0.15, 0.20, 0.25,
        0.30, 0.35, 0.40, 0.45, 0.50,
        0.55, 0.60, 0.65, 0.70, 0.75,
    ]

    rows = []

    for threshold in thresholds:
        predicted = (scores >= threshold).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_true, predicted, labels=[0, 1]
        ).ravel()

        rows.append({
            "threshold": threshold,
            "precision": precision_score(
                y_true, predicted, zero_division=0
            ),
            "recall": recall_score(
                y_true, predicted, zero_division=0
            ),
            "f1": f1_score(
                y_true, predicted, zero_division=0
            ),
            "average_precision": average_precision_score(
                y_true, scores
            ),
            "true_positive": int(tp),
            "false_positive": int(fp),
            "true_negative": int(tn),
            "false_negative": int(fn),
            "flagged_count": int(predicted.sum()),
            "flagged_rate_pct": float(predicted.mean() * 100),
        })

    results = pd.DataFrame(rows)
    results.to_csv(
        output_dir / "threshold_metrics.csv", index=False
    )

    print(results.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}",
    ))
    print(f"\nSaved threshold results to: {output_dir.resolve()}")
    print(
        "\nNote: average precision is ranking-based and remains "
        "constant across thresholds; precision, recall and F1 "
        "change with the threshold."
    )
    print(
        "Results describe synthetic labels only; they do not "
        "establish real-world fraud detection performance."
    )


if __name__ == "__main__":
    main()
