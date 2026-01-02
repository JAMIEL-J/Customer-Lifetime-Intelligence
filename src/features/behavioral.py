"""
Behavioral Trend Feature Computation Module.

This module computes behavioral trend features that compare customer activity
across consecutive time windows. All computations are snapshot-based,
deterministic, and purely historical.

Purpose:
    - Measure customer engagement trends over time
    - Compare recent vs. prior period behavior
    - Support lifecycle stage identification

Constraints:
    - No ML or forecasting
    - No smoothing or prediction
    - No mutation of input DataFrame
    - Historical comparison only

Feature Definitions:
    - spend_trend: Percentage change in spend between current and previous window
    - frequency_trend: Percentage change in transaction count between windows

Window Layout:
    - Current window:  [snapshot_date - window_days, snapshot_date]
    - Previous window: [snapshot_date - 2*window_days, snapshot_date - window_days)

Usage:
    from src.features.behavioral import compute_behavioral_trends

    trends_df = compute_behavioral_trends(transactions_df, window_days=90)
"""

from typing import Optional

import pandas as pd

from src.features.time_windows import (
    get_snapshot_date,
    get_window_start,
    filter_by_window,
)


def _compute_window_metrics(
    transactions_df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """
    Compute spend and frequency within a specified window.

    Args:
        transactions_df: Canonical transactions DataFrame.
        start_date: Window start (inclusive).
        end_date: Window end (inclusive).

    Returns:
        pd.DataFrame with columns: customer_id, spend, frequency
    """
    window_df = filter_by_window(
        transactions_df,
        date_column="transaction_date",
        start_date=start_date,
        end_date=end_date,
    )

    if window_df.empty:
        return pd.DataFrame(columns=["customer_id", "spend", "frequency"])

    metrics = (
        window_df
        .groupby("customer_id", as_index=False)
        .agg(
            spend=("amount", "sum"),
            frequency=("transaction_date", "count"),
        )
    )

    return metrics


def _safe_percentage_change(current: float, previous: float) -> float:
    """
    Compute percentage change avoiding division by zero.

    Formula: ((current - previous) / previous) * 100

    Args:
        current: Current period value.
        previous: Previous period value.

    Returns:
        float: Percentage change, or 0.0 if previous is zero or missing.
    """
    if previous == 0 or pd.isna(previous):
        return 0.0
    return ((current - previous) / previous) * 100


def compute_behavioral_trends(
    transactions_df: pd.DataFrame,
    snapshot_date: Optional[str] = None,
    window_days: int = 90,
) -> pd.DataFrame:
    """
    Compute behavioral trend features comparing consecutive time windows.

    Computes spend_trend and frequency_trend as percentage changes between:
        - Current window:  [snapshot - window_days, snapshot]
        - Previous window: [snapshot - 2*window_days, snapshot - window_days)

    Args:
        transactions_df: Canonical transactions DataFrame with columns:
            - customer_id (str)
            - transaction_date (datetime64[ns])
            - amount (float)
        snapshot_date: Reference date for calculations. If None, uses
            max(transaction_date) from the data.
        window_days: Length of each comparison window in days (default: 90).

    Returns:
        pd.DataFrame: Customer-level trend features with columns:
            - customer_id (str): Unique customer identifier
            - spend_trend (float): Percentage change in spend
            - frequency_trend (float): Percentage change in frequency

    Notes:
        - If previous window has zero spend/frequency, trend is set to 0.0
        - Customers with no activity in either window will have 0.0 trends
        - Input DataFrame is not mutated
    """
    # -------------------------------------------------------------------------
    # 1. Resolve snapshot date and window boundaries
    # -------------------------------------------------------------------------
    snapshot = get_snapshot_date(transactions_df, snapshot_date)

    # Current window: [snapshot - window_days, snapshot]
    current_start = get_window_start(snapshot, window_days)
    current_end = snapshot

    # Previous window: [snapshot - 2*window_days, snapshot - window_days)
    # Note: previous_end is exclusive (day before current_start)
    previous_start = get_window_start(snapshot, 2 * window_days)
    previous_end = current_start - pd.Timedelta(days=1)

    # -------------------------------------------------------------------------
    # 2. Get all unique customers
    # -------------------------------------------------------------------------
    all_customers = transactions_df[["customer_id"]].drop_duplicates()

    # -------------------------------------------------------------------------
    # 3. Compute metrics for current window
    # -------------------------------------------------------------------------
    current_metrics = _compute_window_metrics(
        transactions_df, current_start, current_end
    )
    current_metrics = current_metrics.rename(columns={
        "spend": "current_spend",
        "frequency": "current_frequency",   
    })

    # -------------------------------------------------------------------------
    # 4. Compute metrics for previous window
    # -------------------------------------------------------------------------
    previous_metrics = _compute_window_metrics(
        transactions_df, previous_start, previous_end
    )
    previous_metrics = previous_metrics.rename(columns={
        "spend": "previous_spend",
        "frequency": "previous_frequency",
    })

    # -------------------------------------------------------------------------
    # 5. Merge all data
    # -------------------------------------------------------------------------
    trends_df = all_customers.merge(current_metrics, on="customer_id", how="left")
    trends_df = trends_df.merge(previous_metrics, on="customer_id", how="left")

    # -------------------------------------------------------------------------
    # 6. Fill missing values with zeros
    # -------------------------------------------------------------------------
    trends_df["current_spend"] = trends_df["current_spend"].fillna(0.0)
    trends_df["current_frequency"] = trends_df["current_frequency"].fillna(0)
    trends_df["previous_spend"] = trends_df["previous_spend"].fillna(0.0)
    trends_df["previous_frequency"] = trends_df["previous_frequency"].fillna(0)

    # -------------------------------------------------------------------------
    # 7. Compute percentage change trends (vectorized)
    # -------------------------------------------------------------------------
    trends_df["spend_trend"] = 0.0
    mask = trends_df["previous_spend"] > 0
    trends_df.loc[mask, "spend_trend"] = (
        (trends_df.loc[mask, "current_spend"]
        - trends_df.loc[mask, "previous_spend"])
        / trends_df.loc[mask, "previous_spend"]
    ) * 100

    trends_df["frequency_trend"] = 0.0
    mask = trends_df["previous_frequency"] > 0
    trends_df.loc[mask, "frequency_trend"] = (
        (trends_df.loc[mask, "current_frequency"]
        - trends_df.loc[mask, "previous_frequency"])
        / trends_df.loc[mask, "previous_frequency"]
    ) * 100

    # -------------------------------------------------------------------------
    # 8. Select output columns
    # -------------------------------------------------------------------------
    result = trends_df[[
        "customer_id",
        "spend_trend",
        "frequency_trend",
    ]].copy()

    return result
