# Labeled-dataset evaluation protocol

## Purpose
This experiment evaluates whether an unsupervised Isolation Forest flags records carrying the `is_fraud` label in the selected **synthetic** claims dataset. It is a controlled benchmark, not evidence of real-world fraud-detection capability.

## Dataset and licensing
Source: https://huggingface.co/datasets/quailrobot/health-claims-v1-sample

The downloaded sample is synthetic and its dataset page specifies CC BY-NC-SA 4.0. Review the source's current license and attribution requirements before redistributing data or using project artifacts commercially. Do not commit the raw CSV by default.

## Split and leakage controls
- A stratified train/test split is created with a fixed random seed.
- Isolation Forest is fitted on training features without using labels.
- `is_fraud` is used only for stratified splitting and test metrics.
- `fraud_scheme`, identifiers, and target labels are excluded from model features.
- Numeric features: `billed_amount`, `severity`.
- Categorical features: `procedure_category`, `diagnosis_group`.
- Preprocessing is fitted on the training split through a scikit-learn pipeline.

## Metrics
Precision, recall, F1, average precision (PR-AUC summary), ROC-AUC, confusion matrix, and all-negative baseline accuracy are reported. The baseline illustrates why accuracy alone is misleading with imbalanced labels.

The Isolation Forest threshold is set by `contamination`; it is not learned from fraud labels. Do not tune on the test set.

## Interpretation limits
All labels in this dataset are synthetic. Metrics measure alignment with generated labels only. They do not establish performance on real insurance claims, identify confirmed fraud, or justify automated denial of claims.
