"""
Risk Score Computation Module.

Aggregates normalized risk signals into a single customer risk score
using an explicit, explainable weighted sum approach.
"""

import pandas as pd

from src.risk_engine.thresholds import RISK_SCORE_THRESHOLDS


# =============================================================================
# SIGNAL WEIGHTS (MUST SUM TO 1.0)
# =============================================================================

SIGNAL_WEIGHTS = {
    "recency_signal": 0.40,
    "frequency_drop_signal": 0.25,
    "spend_drop_signal": 0.35,
}

# Defensive check (fail fast)
if round(sum(SIGNAL_WEIGHTS.values()), 5) != 1.0:
    raise ValueError(
        f"SIGNAL_WEIGHTS must sum to 1.0, got {sum(SIGNAL_WEIGHTS.values())}"
    )


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _assign_risk_level(score: float) -> str:
    """Assign risk level using centralized thresholds."""
    if pd.isna(score):
        return "Unknown"

    for threshold in RISK_SCORE_THRESHOLDS:
        if threshold["score_min"] <= score <= threshold["score_max"]:
            return threshold["category"]

    return "Unknown"


# =============================================================================
# PUBLIC API
# =============================================================================

def compute_risk_scores(signals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregated customer risk scores from normalized risk signals.
    """
    required_columns = [
        "customer_id",
        "recency_signal",
        "frequency_drop_signal",
        "spend_drop_signal",
    ]

    missing = set(required_columns) - set(signals_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    # Work on a copy only
    df = signals_df[required_columns].copy()

    # -------------------------------------------------------------------------
    # Fill missing signals conservatively
    # -------------------------------------------------------------------------
    for signal in SIGNAL_WEIGHTS:
        df[signal] = df[signal].fillna(0.0)

    # -------------------------------------------------------------------------
    # Weighted aggregation
    # -------------------------------------------------------------------------
    df["raw_score"] = (
        df["recency_signal"] * SIGNAL_WEIGHTS["recency_signal"]
        + df["frequency_drop_signal"] * SIGNAL_WEIGHTS["frequency_drop_signal"]
        + df["spend_drop_signal"] * SIGNAL_WEIGHTS["spend_drop_signal"]
    )

    # -------------------------------------------------------------------------
    # Scale and clamp to [0, 100]
    # -------------------------------------------------------------------------
    df["risk_score"] = (
        df["raw_score"]
        .mul(100)
        .clip(lower=0, upper=100)
        .round(2)
    )

    # -------------------------------------------------------------------------
    # Risk level assignment
    # -------------------------------------------------------------------------
    df["risk_level"] = df["risk_score"].apply(_assign_risk_level)

    # -------------------------------------------------------------------------
    # Final output (deterministic)
    # -------------------------------------------------------------------------
    result = (
        df[
            [
                "customer_id",
                "risk_score",
                "risk_level",
            ]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    return result
