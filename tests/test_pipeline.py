from pathlib import Path
import pandas as pd
from claimshield.cli import run_pipeline


def test_pipeline_writes_expected_reports(tmp_path: Path):
    # The pipeline creates its demo input under data/raw relative to the current directory.
    # Run in a temporary working directory so tests never touch user project data.
    import os
    previous = Path.cwd()
    try:
        os.chdir(tmp_path)
        paths = run_pipeline(input_path=None, output_dir=tmp_path / "outputs", generate_rows=100, seed=21)
        assert set(paths) == {"scored_claims", "kpi_summary", "provider_summary", "data_quality_issues"}
        for path in paths.values():
            assert path.exists()
        kpis = pd.read_csv(paths["kpi_summary"])
        assert int(kpis.loc[0, "total_claims"]) == 100
    finally:
        os.chdir(previous)
