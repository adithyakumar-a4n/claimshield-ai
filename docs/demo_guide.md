# ClaimShield AI Demo Guide

## Before the demo

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m claimshield.cli --rows 1000 --seed 42
```

Open `reports/ClaimShield_AI_Dashboard.pbix` in Power BI Desktop and refresh the CSV sources if the report does not reflect the latest run.

## Suggested 4-minute walkthrough

1. **Problem and scope (30 seconds):** claims teams may need to prioritize data-quality checks and unusual records for human review.
2. **Pipeline (60 seconds):** show synthetic data generation, validation, feature preparation, Isolation Forest scoring, and exported reports.
3. **Executive Overview (60 seconds):** explain claim count, billed/paid totals, denial rate, review-candidate rate, claim status, and provider review rates.
4. **Data Quality & Review Queue (60 seconds):** show duplicate identifier and missing-provider checks, then open a flagged claim and explain its score and label.
5. **Limitations (30 seconds):** emphasize that records are synthetic and anomaly flags are not confirmed fraud.

## Questions to prepare for

- **Why Isolation Forest?** It is an unsupervised baseline that can rank unusual records without fraud labels, but its results need evaluation.
- **Does 5% mean 5% fraud?** No. It reflects the configured contamination assumption used for model thresholding.
- **How was accuracy measured?** Real-world fraud accuracy has not been established because the MVP lacks real labeled fraud outcomes.
- **Why synthetic data?** It supports repeatable development without using sensitive healthcare information.
- **What is next?** Add labeled synthetic scenarios, compare against transparent rules, measure detection and false-positive rates on those scenarios, strengthen validation, and document limitations.

## Demo integrity checklist

- Do not describe review candidates as confirmed fraud.
- Do not claim production readiness or provider misconduct.
- State that financial totals and rates are from synthetic data.
- Distinguish issue counts from unique affected-record counts.
