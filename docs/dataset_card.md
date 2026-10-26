# Dataset Card — Health Claims Sample

- **Dataset:** Health Claims v1 Sample
- **Source:** https://huggingface.co/datasets/quailrobot/health-claims-v1-sample
- **Local filename:** `data/external/claims_sample.csv`
- **Observed shape:** 65,190 rows × 10 columns (verify after each download)
- **Observed columns:** `claim_id`, `provider_id`, `patient_id`, `service_date`, `procedure_category`, `severity`, `diagnosis_group`, `billed_amount`, `fraud_scheme`, `is_fraud`
- **Observed labels:** 63,677 zeros and 1,513 ones in the downloaded copy.
- **Data type:** Synthetic, not real-time data and not real patient/insurance records.
- **License noted on dataset page:** CC BY-NC-SA 4.0. Check the current source page before redistribution or commercial use.
- **Intended use:** Educational evaluation of data preparation and anomaly-screening methods against generated labels.
- **Not intended for:** Clinical use, real insurance decisions, production fraud determinations, or claims denial.
- **Known limitations:** Synthetic generation patterns may be easier to detect than real-world fraud; labels reflect the generator, not independently adjudicated investigations.
