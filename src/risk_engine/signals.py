"""
Risk Signal Computation Module.

Converts customer behavioral features into normalized risk signals
used for early warning and prioritization (not prediction).

All signals are deterministic, explainable, and scaled to [0, 1].

Assumptions:
- Customers inactive for 365+ days are at maximum recency risk
- A 100% drop in spend or frequency represents maximum trend risk
"""

import pandas as pd


# =============================================================================
# NORMALIZATION CONSTANTS (DOCUMENTED ASSUMPTIONS)
# =============================================================================

_RECENCY_CAP_DAYS = 365
"""
Maximum recency_days used for normalization.
recency_days >= 365 → recency_signal = 1.0
"""

_TREND_DROP_CAP_PERCENT = 100.0
"""
Maximum negative trend percentage used for normalization.
trend <= -100% → drop_signal = 1.0
"""


# =============================================================================
# INTERNAL NORMALIZATION HELPERS
# =============================================================================

def _normalize_recency(recency_days: float) -> float:
    """
    Normalize recency_days into a [0, 1] risk signal.

    Higher recency → higher risk.
    Missing or invalid values are treated as maximum risk.
    """
    if pd.isna(recency_days) or recency_days < 0:
        return 1.0

    return min(recency_days / _RECENCY_CAP_DAYS, 1.0)


def _normalize_negative_trend(trend_percent: float) -> float:
    """
    Normalize a negative trend percentage into a [0, 1] risk signal.

    Only declines contribute to risk.
    Positive or zero trends → 0 risk.
    """
    if pd.isna(trend_percent) or trend_percent >= 0:
        return 0.0

    drop_magnitude = abs(trend_percent)
    return min(drop_magnitude / _TREND_DROP_CAP_PERCENT, 1.0)


# =============================================================================
# PUBLIC API
# =============================================================================

def compute_risk_signals(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute normalized risk signals from behavioral customer features.

    Required columns:
        - customer_id
        - recency_days
        - spend_trend
        - frequency_trend

    Returns:
        DataFrame with:
            - customer_id
            - recency_signal
            - frequency_drop_signal
            - spend_drop_signal
    """
    required_columns = {
        "customer_id",
        "recency_days",
        "spend_trend",
        "frequency_trend",
    }

    missing = required_columns - set(features_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    # Work on a copy only
    df = features_df[list(required_columns)].copy()

    # -------------------------------------------------------------------------
    # Recency signal (vectorized)
    # -------------------------------------------------------------------------
    df["recency_signal"] = (
        df["recency_days"]
        .apply(_normalize_recency)
    )

    # -------------------------------------------------------------------------
    # Frequency drop signal (vectorized)
    # -------------------------------------------------------------------------
    df["frequency_drop_signal"] = (
        df["frequency_trend"]
        .apply(_normalize_negative_trend)
    )

    # -------------------------------------------------------------------------
    # Spend drop signal (vectorized)
    # -------------------------------------------------------------------------
    df["spend_drop_signal"] = (
        df["spend_trend"]
        .apply(_normalize_negative_trend)
    )

    # -------------------------------------------------------------------------
    # Final output
    # -------------------------------------------------------------------------
    result = (
        df[
            [
                "customer_id",
                "recency_signal",
                "frequency_drop_signal",
                "spend_drop_signal",
            ]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    return result
