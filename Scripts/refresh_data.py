"""
refresh_data.py

Convenience script to refresh pipeline outputs using latest available data.
Designed for scheduled execution (cron, task scheduler).

This script:
- Always auto-detects snapshot date
- Rebuilds all downstream artifacts
- Does not delete historical outputs

Usage:
    python scripts/refresh_data.py
"""

from datetime import datetime
from pathlib import Path

from src.services.orchestrator import run_full_system


# =============================================================================
# CONFIGURATION (EDIT HERE)
# =============================================================================

RAW_DATA_PATH = "data/raw/online_retail_II.csv"
OUTPUT_BASE_DIR = "data/processed"


def main() -> None:
    run_date = datetime.utcnow().strftime("%Y-%m-%d")
    output_dir = Path(OUTPUT_BASE_DIR) / f"run_date={run_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Refreshing Customer Lifecycle Intelligence Data")
    print(f"Run date: {run_date}")
    print("=" * 60)

    results = run_full_system(
        raw_transactions_path=RAW_DATA_PATH,
        output_dir=str(output_dir),
        snapshot_date=None,  # auto-detect
    )

    print("\nRefresh completed successfully.")
    print(f"Customers processed: {len(results.get('features_df', [])):,}")
    print(f"Output written to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
