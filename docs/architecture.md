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


# ClaimShield AI Architecture

```mermaid
flowchart TD
    A[CLI arguments: rows and seed] --> B[Synthetic data generator]
    B --> C[Raw synthetic claims CSV]
    C --> D[Data validation]
    D --> E[Data-quality findings]
    D --> F[Preprocessing]
    F --> G[Feature engineering]
    G --> H[Isolation Forest]
    H --> I[Anomaly score and review label]
    I --> J[Scored claims CSV]
    I --> K[KPI summary CSV]
    I --> L[Provider summary CSV]
    E --> M[Data-quality issues CSV]
    J --> N[Power BI report]
    K --> N
    L --> N
    M --> N
```

## Components

- **Synthetic data generator:** creates claims-like records for repeatable development and demonstrations.
- **Data validation:** checks selected data-quality conditions and emits findings.
- **Preprocessing and feature engineering:** prepares fields used by the analytics model.
- **Anomaly detection:** uses Isolation Forest to score records and label review candidates.
- **Reporting:** exports row-level results and summary CSV files.
- **Power BI:** presents descriptive KPIs, claim status, provider comparisons, data-quality findings, and the review queue.

## Data flow

The CLI orchestrates generation, validation, scoring, and report export. CSV files connect Python outputs to Power BI. Generated files are local artifacts and ignored by Git by default; source code, tests, documentation, and the `.pbix` report are version-controlled.

## Design boundaries

This is a portfolio MVP, not a production service. It does not make claim payment decisions, establish fraud, or replace human investigation. Real deployment would require secure ingestion, access controls, audit trails, privacy review, monitoring, model governance, and evaluation against appropriately labeled data.
