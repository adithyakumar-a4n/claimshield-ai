# ClaimShield AI

**Healthcare Claims Analytics, Data Quality & Anomaly Detection**

ClaimShield AI is a portfolio project exploring how healthcare-claims-style data can be validated, summarized, and prioritized for human review. The initial MVP focuses on reproducible data-quality checks, SQL profiling, exploratory analysis, and an anomaly-detection baseline.

> **Important:** This is an educational analytics project, not a clinical or insurance decision system. An anomaly is a signal for investigation, not proof of fraud, abuse, or improper payment. Use synthetic or appropriately licensed, de-identified data only.

## Project goals

- Validate claim-like records and surface data-quality issues.
- Produce clear, reproducible operational summaries.
- Establish transparent rule-based checks and an unsupervised anomaly-detection baseline.
- Evaluate outputs honestly and document limitations.
- Prepare dashboard-ready outputs for Power BI.

## Planned technology

- Python, Pandas, NumPy
- SQL for schema definition and profiling
- scikit-learn for anomaly detection
- pytest for automated tests
- Power BI for interactive reporting

## Repository layout

```text
claimshield-ai/
├── configs/                 # Project configuration
├── data/
│   ├── raw/                 # Local source data; not committed
│   └── processed/            # Generated/cleaned data; not committed
├── docs/                    # Architecture, data dictionary, evaluation notes
├── outputs/                 # Generated reports; not committed
├── sql/                     # SQL schema and profiling queries
├── src/claimshield/          # Python package
├── tests/                   # Automated tests
├── .env.example
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

## Setup on Windows (PowerShell)

Run these commands from the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the `py` launcher is unavailable, use `python` instead of `py -3` when creating the environment.

## Verification

After the project implementation is added, run the test suite from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

At the foundation stage, this command may report that no tests are collected if implementation/test files are not yet complete. Do not describe the project as verified until the tests actually pass.

## Data handling

- Do not commit real patient data, insurance member identifiers, credentials, or private datasets.
- Keep local source data under `data/raw/`; generated and cleaned data belong under `data/processed/`.
- Large generated outputs should stay out of Git unless a small, explicitly documented sample is needed.
- Record dataset provenance, permitted use, and any synthetic-data assumptions in `docs/data_dictionary.md`.

## Current status

The repository foundation is being established. Features, metrics, and test results will be documented only after they have been implemented and run.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
