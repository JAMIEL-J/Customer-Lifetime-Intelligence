"""
System Orchestrator.

High-level execution controller for the Customer Lifecycle Intelligence Platform.
Prepares runtime inputs, invokes the pipeline, and records execution metadata.

This module contains no business logic and no data transformations.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.services.pipeline import run_pipeline
from src.utils.logger import get_logger


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class PipelineConfig:
    """
    Configuration for pipeline execution.

    Attributes:
        raw_transactions_path: Path to raw transactions CSV.
        snapshot_date: Optional reference date for analysis.
    """
    raw_transactions_path: str
    snapshot_date: Optional[str] = None


# =============================================================================
# PUBLIC API
# =============================================================================

def run_full_system(
    raw_transactions_path: str,
    snapshot_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the complete Customer Lifecycle Intelligence system.

    Args:
        raw_transactions_path: Path to raw transactions CSV.
        snapshot_date: Optional reference date for analysis.

    Returns:
        Dictionary containing:
            - pipeline outputs
            - execution_metadata
    """
    logger = get_logger("orchestrator")

    config = PipelineConfig(
        raw_transactions_path=raw_transactions_path,
        snapshot_date=snapshot_date,
    )

    logger.info("=" * 60)
    logger.info("CUSTOMER LIFECYCLE INTELLIGENCE SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Raw transactions: {config.raw_transactions_path}")
    logger.info(f"Snapshot date: {config.snapshot_date or 'auto-detect'}")

    start_time = datetime.utcnow()

    try:
        logger.info("Starting pipeline execution")

        results = run_pipeline(
            raw_transactions_path=config.raw_transactions_path,
            snapshot_date=config.snapshot_date,
        )

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        logger.info("Pipeline completed successfully")
        logger.info(f"Execution time: {duration:.2f} seconds")

        results["execution_metadata"] = {
            "start_time_utc": start_time.isoformat(),
            "end_time_utc": end_time.isoformat(),
            "duration_seconds": duration,
            "config": {
                "raw_transactions_path": config.raw_transactions_path,
                "snapshot_date": config.snapshot_date,
            },
        }

        logger.info(f"Transactions processed: {len(results['transactions_df']):,}")
        logger.info(f"Customers analyzed: {len(results['features_df']):,}")
        logger.info(f"Actions assigned: {len(results['actions_df']):,}")

        logger.info("=" * 60)

        return results

    except Exception as exc:
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        logger.error("Pipeline execution FAILED")
        logger.error(f"Duration: {duration:.2f} seconds")
        logger.exception(exc)
        logger.info("=" * 60)

        raise


def run_from_config(config: PipelineConfig) -> Dict[str, Any]:
    """
    Execute system using a PipelineConfig object.
    """
    return run_full_system(
        raw_transactions_path=config.raw_transactions_path,
        snapshot_date=config.snapshot_date,
    )
