"""
run_pipeline.py

CLI entry point to execute the full Customer Lifecycle Intelligence pipeline.

This script is intentionally thin:
- No business logic
- No data manipulation
- No configuration logic beyond CLI args

Usage:
    python scripts/run_pipeline.py \
        --input data/raw/online_retail_II.csv \
        --output data/processed \
        --snapshot 2024-01-10
"""

import argparse
import sys
from pathlib import Path

from src.services.orchestrator import run_full_system


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Customer Lifecycle Intelligence Pipeline"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw transactions CSV file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Directory for pipeline outputs",
    )

    parser.add_argument(
        "--snapshot",
        required=False,
        default=None,
        help="Snapshot date (YYYY-MM-DD). Defaults to auto-detect.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Running Customer Lifecycle Intelligence Pipeline")
    print("=" * 60)

    results = run_full_system(
        raw_transactions_path=str(input_path),
        output_dir=str(output_dir),
        snapshot_date=args.snapshot,
    )

    print("\nPipeline completed successfully.")
    print(f"Customers processed: {len(results.get('features_df', [])):,}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nPipeline failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
