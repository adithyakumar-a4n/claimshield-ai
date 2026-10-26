# Evaluation Protocol

## Current scope

ClaimShield AI is an educational claims-analytics MVP that uses synthetic claims-like records. It is not a validated fraud detector or a production insurance decision system. The Isolation Forest output is an anomaly-review signal only.

## Reproducibility

- Synthetic data generation should return the same records for the same row count and random seed.
- Anomaly scoring should return the same scores and review flags for the same input and model seed.
- Automated tests cover these expectations. Results must be run locally before they are described as passing.

## Reporting invariants

KPI outputs are checked against a small known dataset. This verifies that total claim counts, claim and paid amounts, review candidate rates, and denied-claim rates reconcile to the input rows. Provider-level counts and rates are checked independently.

## Interpreting the 5% contamination setting

The Isolation Forest contamination parameter is an assumed outlier proportion used by the model to set its decision threshold. It is not a measured fraud prevalence, model accuracy, or estimate of financial loss. A 5% review-candidate rate must not be reported as a 5% fraud rate.

## Limitations

- The current synthetic dataset does not establish ground-truth fraud labels.
- No precision, recall, F1, ROC-AUC, or PR-AUC fraud-detection claim is justified without suitable labeled evaluation data and a documented split strategy.
- Rule-based thresholds are illustrative and require domain review before operational use.
- KPI summaries are descriptive and do not establish causation or savings.
- Synthetic data may not reflect real healthcare claims distributions.

## Next evaluation steps

1. Compare anomaly flags with transparent rule-based baselines.
2. Add labeled synthetic scenarios with explicit injected anomaly categories, separate from ordinary random variation.
3. Report detection recall on injected cases and false-positive rate on non-injected cases, clearly labeled as synthetic-scenario metrics.
4. Test malformed input files, missing columns, duplicates, and invalid numeric/date fields.
5. Validate all dashboard metrics against the generated CSVs.
