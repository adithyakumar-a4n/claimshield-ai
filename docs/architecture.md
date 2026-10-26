# Architecture

## Current MVP flow

```text
Synthetic CSV or permitted CSV input
              |
              v
     Schema / data-quality checks
              |
              v
       Conservative preprocessing
              |
              v
       Numeric feature engineering
              |
              v
      Isolation Forest baseline
              |
              v
 CSV outputs for review and Power BI
```

## Components

- `synthetic_data.py`: deterministic, fictional claim-like records for development.
- `data_validation.py`: reports missing required columns, missing identifiers, duplicate claim IDs, invalid amounts, date issues, and unknown statuses.
- `preprocessing.py`: normalizes types and strings without silently dropping records.
- `features.py`: creates numeric features for the anomaly baseline.
- `anomaly_detection.py`: fits Isolation Forest and marks a configurable proportion of rows as review candidates.
- `reporting.py`: writes scored records, overall KPIs, provider summaries, and quality issues as CSV.
- `cli.py`: runs the end-to-end pipeline.
- `sql/`: SQLite-compatible schema and profiling queries.

## Important limitations

This is a portfolio MVP. Synthetic patterns are not representative of real insurance data. Isolation Forest identifies unusual combinations in the provided features; it does not determine fraud, medical necessity, or payment correctness. Production use would require domain review, data governance, privacy/security controls, robust monitoring, and validation on appropriately authorized real-world data.
