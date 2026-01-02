"""
Snapshot-Based Time Window Utilities.

This module provides reusable utilities for calculating time windows
relative to a snapshot date. These are foundational building blocks
for time-based feature engineering.

Purpose:
    - Determine snapshot dates for point-in-time analysis
    - Calculate rolling window boundaries
    - Filter DataFrames by date ranges

Constraints:
    - No file I/O
    - No aggregations or groupby operations
    - No hardcoded dates
    - No mutation of input DataFrames
    - Deterministic behavior only
"""

from typing import Optional

import pandas as pd


def get_snapshot_date(
    transactions_df: pd.DataFrame,
    snapshot_date: Optional[str] = None,
) -> pd.Timestamp:
    """
    Determine the snapshot date for point-in-time calculations.

    If snapshot_date is provided, it is converted to a pandas Timestamp.
    If None, the snapshot date is inferred as the maximum transaction_date
    in the DataFrame.

    Raises:
        ValueError: If transactions_df is empty and snapshot_date is None.
    """
    if snapshot_date is not None:
        return pd.Timestamp(snapshot_date)

    if transactions_df.empty:
        raise ValueError("Cannot infer snapshot_date from empty DataFrame.")

    return transactions_df["transaction_date"].max()


def get_window_start(snapshot_date: pd.Timestamp, days: int) -> pd.Timestamp:
    """
    Calculate the start date of a rolling window.
    """
    if days < 0:
        raise ValueError(f"days must be non-negative, got {days}")

    return snapshot_date - pd.Timedelta(days=days)


def filter_by_window(
    df: pd.DataFrame,
    date_column: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """
    Filter DataFrame to rows within a date range (inclusive).
    """
    if date_column not in df.columns:
        raise KeyError(
            f"Column '{date_column}' not found. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )

    if start_date > end_date:
        raise ValueError(
            f"start_date ({start_date}) must not be after end_date ({end_date})"
        )

    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df.loc[mask].copy()
