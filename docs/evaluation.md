# Evaluation plan

## Current baseline

The MVP uses Isolation Forest as an unsupervised anomaly-detection baseline. The configured contamination parameter controls the expected fraction of training rows the model labels as outliers; it is not a measured fraud rate.

## What is measured

- Dataset row count and data-quality issue counts.
- Claim amount and paid amount totals.
- Review-candidate count and rate.
- Claim status distribution and provider-level descriptive summaries.
- Automated test outcomes for validation, model output shape, invalid parameters, and report generation.

## What is not yet established

There is no labeled fraud outcome in the synthetic data, so precision, recall, F1, ROC-AUC, and PR-AUC for fraud detection cannot be honestly reported. The synthetic outlier injection is a development aid, not validated ground truth. Any future supervised evaluation must use a documented label definition, a leakage-aware split, and suitable class-imbalance metrics.

## Reproducibility

Use the same random seed for data generation and model fitting. Record dependency versions and the exact command used to generate outputs. Results are descriptive and suitable for a demo, not for operational decision-making.
