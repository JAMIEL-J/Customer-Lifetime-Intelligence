"""
Action ROI Estimation Module.

Estimates expected cost and benefit of recommended actions using
transparent heuristic assumptions. All calculations are deterministic
and auditable.

NOTE:
These are heuristic estimates for prioritization, not predictions.
"""

import pandas as pd


# =============================================================================
# ACTION COST ASSUMPTIONS
# =============================================================================

ACTION_COSTS = {
    "Retention incentive + personal outreach": 500,
    "Targeted win-back offer": 300,
    "Automated reactivation campaign": 50,
    "Preventive engagement (loyalty program, nudges)": 100,
    "Cross-sell recommendation campaign": 75,
    "Engagement nurture sequence": 25,
    "Upsell premium offerings": 150,
    "Cross-sell complementary products": 50,
    "Maintain relationship (standard communications)": 10,
    "Monitor": 0,
}

DEFAULT_ACTION_COST = 50


# =============================================================================
# RECOVERY RATE ASSUMPTIONS
# =============================================================================

RECOVERY_RATES = {
    "High": 0.25,
    "Medium": 0.40,
    "Low": 0.60,
    "Unknown": 0.10,
}


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _get_action_cost(action: str) -> tuple[float, str]:
    """
    Return action cost and source label.
    """
    if pd.isna(action):
        return DEFAULT_ACTION_COST, "default"

    if action in ACTION_COSTS:
        return ACTION_COSTS[action], "mapped"

    return DEFAULT_ACTION_COST, "default"


def _get_recovery_rate(risk_level: str) -> float:
    """
    Return recovery rate for a given risk level.
    """
    if pd.isna(risk_level):
        return RECOVERY_RATES["Unknown"]

    return RECOVERY_RATES.get(risk_level, RECOVERY_RATES["Unknown"])


# =============================================================================
# PUBLIC API
# =============================================================================

def estimate_action_roi(actions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate ROI for recommended actions using heuristic assumptions.
    """
    required_columns = [
        "customer_id",
        "recommended_action",
        "lifetime_value",
        "risk_level",
    ]

    missing = set(required_columns) - set(actions_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    # Work on a copy only
    df = actions_df[required_columns].copy()

    # -------------------------------------------------------------------------
    # Normalize lifetime value (no negative economics)
    # -------------------------------------------------------------------------
    df["lifetime_value"] = df["lifetime_value"].fillna(0).clip(lower=0)

    # -------------------------------------------------------------------------
    # Action cost lookup
    # -------------------------------------------------------------------------
    cost_info = df["recommended_action"].apply(_get_action_cost)
    df["action_cost"] = cost_info.apply(lambda x: x[0])
    df["action_cost_source"] = cost_info.apply(lambda x: x[1])

    # -------------------------------------------------------------------------
    # Expected benefit estimation
    # -------------------------------------------------------------------------
    df["recovery_rate"] = df["risk_level"].apply(_get_recovery_rate)
    df["expected_benefit"] = (
        df["lifetime_value"] * df["recovery_rate"]
    ).round(2)

    # -------------------------------------------------------------------------
    # ROI computation
    # -------------------------------------------------------------------------
    df["estimated_roi"] = (
        df["expected_benefit"] - df["action_cost"]
    ).round(2)

    # -------------------------------------------------------------------------
    # Feasibility flag (non-optimizing, informational)
    # -------------------------------------------------------------------------
    df["roi_feasible"] = df["estimated_roi"] > 0

    # -------------------------------------------------------------------------
    # Final output (deterministic)
    # -------------------------------------------------------------------------
    result = (
        df[
            [
                "customer_id",
                "action_cost",
                "action_cost_source",
                "expected_benefit",
                "estimated_roi",
                "roi_feasible",
            ]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    return result
