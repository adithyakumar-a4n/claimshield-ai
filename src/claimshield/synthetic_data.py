"""Generate a reproducible, explicitly synthetic claims dataset for development."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

CLAIM_COLUMNS = [
    "claim_id", "member_id", "provider_id", "service_date", "submission_date",
    "procedure_code", "diagnosis_group", "place_of_service", "claim_amount",
    "paid_amount", "claim_status", "reviewed_by_human", "source_is_synthetic",
]


def generate_synthetic_claims(n_rows: int = 1_000, random_seed: int = 42) -> pd.DataFrame:
    """Create synthetic claim-like records; no real people or providers are represented."""
    if n_rows < 20:
        raise ValueError("n_rows must be at least 20 to create a useful demo dataset")
    rng = np.random.default_rng(random_seed)
    service_dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(
        rng.integers(0, 365, size=n_rows), unit="D"
    )
    submission_lag = rng.integers(0, 22, size=n_rows)
    claim_amount = np.round(rng.lognormal(mean=5.0, sigma=0.75, size=n_rows), 2)
    # Inject a small, deterministic set of unusual amounts for anomaly-demo purposes.
    n_injected = max(2, n_rows // 100)
    injected_indices = rng.choice(n_rows, size=n_injected, replace=False)
    claim_amount[injected_indices] = np.round(claim_amount[injected_indices] * rng.uniform(8, 16, size=n_injected), 2)
    paid_fraction = rng.uniform(0.55, 1.0, size=n_rows)
    paid_amount = np.round(claim_amount * paid_fraction, 2)
    statuses = rng.choice(["paid", "denied", "pending", "adjusted"], size=n_rows, p=[0.68, 0.12, 0.12, 0.08])
    paid_amount[statuses == "denied"] = 0.0
    paid_amount[statuses == "pending"] = 0.0
    # Small, intentional data-quality defects allow validation to be demonstrated.
    defect_count = max(1, n_rows // 200)
    missing_provider_indices = rng.choice(n_rows, size=defect_count, replace=False)
    provider_ids = np.array([f"PRV-{x:04d}" for x in rng.integers(1, 121, size=n_rows)], dtype=object)
    provider_ids[missing_provider_indices] = None
    rows = pd.DataFrame({
        "claim_id": [f"CLM-{i+1:06d}" for i in range(n_rows)],
        "member_id": [f"MBR-{x:05d}" for x in rng.integers(1, max(200, n_rows // 2), size=n_rows)],
        "provider_id": provider_ids,
        "service_date": service_dates,
        "submission_date": service_dates + pd.to_timedelta(submission_lag, unit="D"),
        "procedure_code": rng.choice(["99213", "99214", "93000", "80053", "71046", "36415"], size=n_rows),
        "diagnosis_group": rng.choice(["general", "cardiology", "respiratory", "metabolic", "musculoskeletal"], size=n_rows),
        "place_of_service": rng.choice(["office", "outpatient", "emergency", "telehealth"], size=n_rows),
        "claim_amount": claim_amount,
        "paid_amount": paid_amount,
        "claim_status": statuses,
        "reviewed_by_human": rng.choice([True, False], size=n_rows, p=[0.22, 0.78]),
        "source_is_synthetic": True,
    })
    # Duplicate a small number of claim identifiers to exercise the duplicate check.
    if n_rows >= 100:
        rows.loc[n_rows - 1, "claim_id"] = rows.loc[n_rows - 2, "claim_id"]
    return rows[CLAIM_COLUMNS]


def write_synthetic_claims(output_path: str | Path, n_rows: int = 1_000, random_seed: int = 42) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_synthetic_claims(n_rows=n_rows, random_seed=random_seed)
    frame.to_csv(path, index=False)
    return path
