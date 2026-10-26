"""Command-line entry point for the ClaimShield AI MVP."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import yaml
from .synthetic_data import write_synthetic_claims
from .data_validation import validate_claims
from .preprocessing import preprocess_claims
from .anomaly_detection import score_anomalies
from .reporting import write_reports


def run_pipeline(input_path: str | Path | None, output_dir: str | Path, generate_rows: int = 1000, seed: int = 42) -> dict[str, Path]:
    """Run the end-to-end pipeline and write all report CSVs."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if input_path is None:
        source_path = write_synthetic_claims(Path("data/raw/synthetic_claims.csv"), n_rows=generate_rows, random_seed=seed)
    else:
        source_path = Path(input_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Input dataset not found: {source_path}")
    raw = pd.read_csv(source_path)
    issues = validate_claims(raw)
    cleaned = preprocess_claims(raw)
    result = score_anomalies(cleaned, contamination=0.05, random_state=seed)
    paths = write_reports(output, result.scored_claims, issues)
    print(f"Input rows: {len(raw)}")
    print(f"Data-quality issues: {len(issues)}")
    print(f"Review candidates: {int(result.scored_claims['review_candidate'].sum())}")
    for name, path in paths.items():
        print(f"{name}: {path}")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ClaimShield AI claims analytics MVP.")
    parser.add_argument("--input", default=None, help="CSV input path. If omitted, generate synthetic demo data.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for report CSVs (default: outputs).")
    parser.add_argument("--rows", type=int, default=1000, help="Number of synthetic rows if --input is omitted.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible demo data and model.")
    args = parser.parse_args()
    run_pipeline(args.input, args.output_dir, args.rows, args.seed)

if __name__ == "__main__":
    main()
