# ClaimShield AI — Power BI Dashboard

## 📊 Overview
The Power BI dashboard presents descriptive analytics from the **ClaimShield AI synthetic healthcare claims pipeline**. It supports exploration of claims status, financial totals, provider-level review rates, and data-quality issues.

---

## 📄 Report Pages

### 1. Executive Overview
Displays high-level operational metrics and comparative provider insights:
* **Core Metrics:** Total claims, total billed amount, total paid amount, and total review candidates.
* **Key Ratios:** Denial rate and review-candidate rate.
* **Visualizations:** Claims segmented by status and provider review-rate comparisons.

### 2. Data Quality & Review Queue
Facilitates targeted investigations into anomalies and pipeline health:
* **Data Quality:** Overview of all detected data-quality issues across the pipeline.
* **Review Queue:** Individual claims flagged for further investigation.
* **Queue Details:** Claim identifiers, financial amounts, anomaly scores, and anomaly labels.

---

## 💾 Data Sources
The report consumes generated CSV files from the `outputs/` directory:

* `kpi_summary.csv` — High-level metrics and financial totals.
* `provider_summary.csv` — Provider-level aggregation and review metrics.
* `scored_claims.csv` — Line-level claims enriched with anomaly scores.
* `data_quality_issues.csv` — Pipeline validation logs and error flags.

---

## 🔄 Refresh Procedure
Follow these sequential steps to update the dashboard data:

1. **Activate Environment:** Initialize the project's Python virtual environment.
2. **Regenerate Data:** Execute the documented CLI command to generate fresh outputs.
3. **Open Report:** Launch the ClaimShield AI Power BI desktop file.
4. **Refresh Sources:** Click **Refresh** in the Home ribbon to import the updated CSV files.
5. **Reconcile Totals:** Verify dashboard metrics match the values inside `kpi_summary.csv`.

---

## ⚠️ Interpretation & Limitations
* **Synthetic Data:** The dataset is entirely synthetic and intended solely for educational analytics.
* **Review Flags:** Anomaly flags indicate records selected for manual review, **not** confirmed fraud.
* **Descriptive Metrics:** Provider-level rates are descriptive and must be interpreted alongside total claim volume and data quality.
* **No Performance Claims:** The report does not establish fraud-detection accuracy, financial savings, or operational improvements.
