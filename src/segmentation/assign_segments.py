"""
Customer Segmentation Assignment Module.

Applies lifecycle and value segmentation rules to customer feature data.
All logic is deterministic, explainable, and rule-based.
"""

import pandas as pd

from src.segmentation.lifecycle_rules import (
    LIFECYCLE_STAGE_RULES,
    VALUE_SEGMENT_RULES,
    RULE_METADATA,
)


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _assign_lifecycle_stage(recency_days: float) -> str:
    """Assign lifecycle stage based on recency_days."""
    if pd.isna(recency_days):
        return "Unknown"

    recency = int(recency_days)

    for rule in LIFECYCLE_STAGE_RULES:
        min_r = rule.get("recency_min", 0)
        max_r = rule.get("recency_max", float("inf"))

        if min_r <= recency <= max_r:
            return rule["stage"]

    return "Unknown"


def _assign_value_segment_from_percentile(
    percentile: float,
    monetary: float,
) -> str:
    """Assign value segment using percentile and monetary edge cases."""
    if monetary <= 0 or pd.isna(monetary):
        return "Low Value"

    if pd.isna(percentile):
        return "Low Value"

    for rule in VALUE_SEGMENT_RULES:
        if rule["percentile_min"] <= percentile <= rule["percentile_max"]:
            return rule["segment"]

    return "Low Value"


# =============================================================================
# PUBLIC API
# =============================================================================

def assign_customer_segments(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign lifecycle and value segments to customers.

    Required columns:
        - customer_id
        - recency_days
        - monetary
    """
    required_columns = {"customer_id", "recency_days", "monetary"}
    missing = required_columns - set(features_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    # Work on a copy only
    df = features_df[["customer_id", "recency_days", "monetary"]].copy()

    # -------------------------------------------------------------------------
    # 1. Lifecycle stage assignment
    # -------------------------------------------------------------------------
    df["lifecycle_stage"] = df["recency_days"].apply(_assign_lifecycle_stage)

    # -------------------------------------------------------------------------
    # 2. Monetary percentile computation (rank-based, deterministic)
    # -------------------------------------------------------------------------
    if df["monetary"].sum() == 0 or len(df) == 1:
        df["monetary_percentile"] = 0.0
    else:
        df["monetary_percentile"] = (
            df["monetary"]
            .rank(method="average", pct=True)
            .mul(100)
        )

    # -------------------------------------------------------------------------
    # 3. Value segment assignment (vectorized)
    # -------------------------------------------------------------------------
    df["value_segment"] = "Low Value"

    mask = df["monetary"] > 0
    df.loc[mask, "value_segment"] = df.loc[mask].apply(
        lambda row: _assign_value_segment_from_percentile(
            row["monetary_percentile"],
            row["monetary"],
        ),
        axis=1,
    )

    # -------------------------------------------------------------------------
    # 4. Combined segment label
    # -------------------------------------------------------------------------
    df["segment_label"] = df["lifecycle_stage"] + " " + df["value_segment"]

    # -------------------------------------------------------------------------
    # 5. Rule version for traceability
    # -------------------------------------------------------------------------
    df["segment_version"] = RULE_METADATA["version"]

    # -------------------------------------------------------------------------
    # 6. Final output (deterministic order)
    # -------------------------------------------------------------------------
    result = (
        df[
            [
                "customer_id",
                "lifecycle_stage",
                "value_segment",
                "segment_label",
                "segment_version",
            ]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    return result
