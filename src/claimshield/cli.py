"""Command-line entry point for the ClaimShield AI MVP."""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
import pandas as pd
import yaml
from .synthetic_data import write_synthetic_claims
from .data_validation import validate_claims
from .preprocessing import preprocess_claims
from .anomaly_detection import score_anomalies
from .reporting import write_reports

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path("configs/config.yaml")


def load_config(config_path: Path | None = None) -> dict:
    """Load YAML config file and return its contents as a dict.

    Falls back to an empty dict if the file does not exist.
    """
    path = config_path or _DEFAULT_CONFIG_PATH
    if path.exists():
        with open(path) as fh:
            return yaml.safe_load(fh) or {}
    logger.warning("Config file not found at %s; using built-in defaults.", path)
    return {}


def run_pipeline(
    input_path: str | Path | None,
    output_dir: str | Path,
    generate_rows: int = 1000,
    seed: int = 42,
    contamination: float = 0.05,
) -> dict[str, Path]:
    """Run the end-to-end pipeline and write all report CSVs."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    if input_path is None:
        source_path = write_synthetic_claims(
            Path("data/raw/synthetic_claims.csv"), n_rows=generate_rows, random_seed=seed
        )
    else:
        source_path = Path(input_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Input dataset not found: {source_path}")

    raw = pd.read_csv(source_path)
    issues = validate_claims(raw)
    cleaned = preprocess_claims(raw)
    result = score_anomalies(cleaned, contamination=contamination, random_state=seed)
    paths = write_reports(output, result.scored_claims, issues)

    logger.info("Input rows: %d", len(raw))
    logger.info("Data-quality issues: %d", len(issues))
    logger.info("Review candidates: %d", int(result.scored_claims["review_candidate"].sum()))
    for name, path in paths.items():
        logger.info("%s: %s", name, path)
    return paths


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    config = load_config()
    anomaly_cfg = config.get("anomaly_detection", {})
    project_cfg = config.get("project", {})

    parser = argparse.ArgumentParser(description="Run the ClaimShield AI claims analytics MVP.")
    parser.add_argument("--input", default=None, help="CSV input path. If omitted, generate synthetic demo data.")
    parser.add_argument("--output-dir", default=config.get("paths", {}).get("outputs", "outputs"),
                        help="Directory for report CSVs (default: outputs).")
    parser.add_argument("--rows", type=int, default=1000,
                        help="Number of synthetic rows if --input is omitted.")
    parser.add_argument("--seed", type=int, default=project_cfg.get("random_seed", 42),
                        help="Random seed for reproducible demo data and model.")
    parser.add_argument("--contamination", type=float,
                        default=anomaly_cfg.get("contamination", 0.05),
                        help="IsolationForest contamination parameter (default: 0.05).")
    args = parser.parse_args()

    run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        generate_rows=args.rows,
        seed=args.seed,
        contamination=args.contamination,
    )


if __name__ == "__main__":
    main()
