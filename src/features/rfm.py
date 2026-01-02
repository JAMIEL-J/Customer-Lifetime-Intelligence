"""
RFM Feature Computation Module.

This module computes core RFM-style (Recency, Frequency, Monetary) customer
features from canonical transaction data. All computations are snapshot-based
and deterministic.

Constraints:
    - No ML or clustering
    - No segmentation logic
    - No mutation of input DataFrame
    - Snapshot-based computation
    - One row per customer output
"""

from typing import Optional

import pandas as pd

from src.features.time_windows import (
    get_snapshot_date,
    get_window_start,
    filter_by_window,
)


def compute_rfm_features(
    transactions_df: pd.DataFrame,
    snapshot_date: Optional[str] = None,
    window_days: int = 90,
) -> pd.DataFrame:
    """
    Compute RFM-style customer features from canonical transactions.
    """
    # -------------------------------------------------------------------------
    # 1. Resolve snapshot date and window boundaries
    # -------------------------------------------------------------------------
    snapshot = get_snapshot_date(transactions_df, snapshot_date)
    window_start = get_window_start(snapshot, window_days)

    # -------------------------------------------------------------------------
    # 2. Get all unique customers
    # -------------------------------------------------------------------------
    all_customers = transactions_df[["customer_id"]].drop_duplicates()

    # -------------------------------------------------------------------------
    # 3. Compute recency from full history (clamped at 0)
    # -------------------------------------------------------------------------
    last_tx = (
        transactions_df
        .groupby("customer_id", as_index=False)["transaction_date"]
        .max()
        .rename(columns={"transaction_date": "last_transaction_date"})
    )

    last_tx["recency_days"] = (
        (snapshot - last_tx["last_transaction_date"])
        .dt.days
        .clip(lower=0)
    )

    # -------------------------------------------------------------------------
    # 4. Filter transactions within window (EXCLUSIVE of snapshot)
    # -------------------------------------------------------------------------
    window_tx = filter_by_window(
        transactions_df,
        date_column="transaction_date",
        start_date=window_start,
        end_date=snapshot - pd.Timedelta(days=1),
    )

    # -------------------------------------------------------------------------
    # 5. Compute frequency (transaction count)
    # -------------------------------------------------------------------------
    frequency = (
        window_tx
        .groupby("customer_id", as_index=False)
        .size()
        .rename(columns={"size": "frequency"})
    )

    # -------------------------------------------------------------------------
    # 6. Compute monetary value (window spend)
    # -------------------------------------------------------------------------
    monetary = (
        window_tx
        .groupby("customer_id", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "monetary"})
    )

    # -------------------------------------------------------------------------
    # 7. Compute lifetime value (all-time spend)
    # -------------------------------------------------------------------------
    lifetime = (
        transactions_df
        .groupby("customer_id", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "lifetime_value"})
    )

    # -------------------------------------------------------------------------
    # 8. Merge all features
    # -------------------------------------------------------------------------
    rfm_df = (
        all_customers
        .merge(last_tx[["customer_id", "recency_days"]], on="customer_id", how="left")
        .merge(frequency, on="customer_id", how="left")
        .merge(monetary, on="customer_id", how="left")
        .merge(lifetime, on="customer_id", how="left")
    )

    # -------------------------------------------------------------------------
    # 9. Fill missing values
    # -------------------------------------------------------------------------
    rfm_df["frequency"] = rfm_df["frequency"].fillna(0).astype(int)
    rfm_df["monetary"] = rfm_df["monetary"].fillna(0.0)

    # -------------------------------------------------------------------------
    # 10. Deterministic column order and sorting
    # -------------------------------------------------------------------------
    rfm_df = rfm_df[
        ["customer_id", "recency_days", "frequency", "monetary", "lifetime_value"]
    ].sort_values("customer_id").reset_index(drop=True)

    return rfm_df
