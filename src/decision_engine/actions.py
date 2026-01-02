"""
Decision Action Assignment Module.

Maps customer risk levels and segments to recommended business actions
using deterministic, rule-based logic.
"""

import pandas as pd


# =============================================================================
# ACTION RULES (ORDER MATTERS)
# =============================================================================

ACTION_RULES = [
    # High Risk
    {
        "risk_level": "High",
        "value_contains": "High Value",
        "action": "Retention incentive + personal outreach",
        "priority": "High",
        "rationale": "High-value customers at churn risk need immediate 1:1 attention",
    },
    {
        "risk_level": "High",
        "value_contains": "Medium Value",
        "action": "Targeted win-back offer",
        "priority": "High",
        "rationale": "Medium-value at-risk customers merit targeted retention effort",
    },
    {
        "risk_level": "High",
        "value_contains": "Low Value",
        "action": "Automated reactivation campaign",
        "priority": "Medium",
        "rationale": "Lower-value churning customers handled via scalable automation",
    },

    # Medium Risk
    {
        "risk_level": "Medium",
        "value_contains": "High Value",
        "action": "Preventive engagement (loyalty program, nudges)",
        "priority": "Medium",
        "rationale": "Proactive engagement prevents decay in high-value customers",
    },
    {
        "risk_level": "Medium",
        "value_contains": "Medium Value",
        "action": "Cross-sell recommendation campaign",
        "priority": "Medium",
        "rationale": "Cross-sell strengthens engagement and increases value",
    },
    {
        "risk_level": "Medium",
        "value_contains": "Low Value",
        "action": "Engagement nurture sequence",
        "priority": "Low",
        "rationale": "Low-touch nurturing for lower-value customers",
    },

    # Low Risk
    {
        "risk_level": "Low",
        "value_contains": "High Value",
        "action": "Upsell premium offerings",
        "priority": "Medium",
        "rationale": "Healthy high-value customers are ideal upsell candidates",
    },
    {
        "risk_level": "Low",
        "value_contains": "Medium Value",
        "action": "Cross-sell complementary products",
        "priority": "Low",
        "rationale": "Expand wallet share with engaged customers",
    },
    {
        "risk_level": "Low",
        "value_contains": "Low Value",
        "action": "Maintain relationship (standard communications)",
        "priority": "Low",
        "rationale": "Low-touch maintenance for stable low-value customers",
    },
]

DEFAULT_ACTION = {
    "action": "Monitor",
    "priority": "Low",
    "rationale": "No matching rule; customer requires observation or manual review",
}


# =============================================================================
# PUBLIC API
# =============================================================================

def assign_actions(decision_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign recommended actions based on customer risk and value segment.
    """
    required_columns = ["customer_id", "risk_level", "segment_label"]
    missing = set(required_columns) - set(decision_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    df = decision_df[required_columns].copy()

    # Initialize defaults
    df["recommended_action"] = DEFAULT_ACTION["action"]
    df["action_priority"] = DEFAULT_ACTION["priority"]
    df["action_rationale"] = DEFAULT_ACTION["rationale"]
    df["rule_matched"] = False

    # Apply rules in order
    for rule in ACTION_RULES:
        mask = (
            (df["risk_level"] == rule["risk_level"]) &
            (df["segment_label"].str.contains(rule["value_contains"], na=False)) &
            (~df["rule_matched"])
        )

        df.loc[mask, "recommended_action"] = rule["action"]
        df.loc[mask, "action_priority"] = rule["priority"]
        df.loc[mask, "action_rationale"] = rule["rationale"]
        df.loc[mask, "rule_matched"] = True

    result = (
        df[
            [
                "customer_id",
                "recommended_action",
                "action_priority",
                "action_rationale",
                "rule_matched",
            ]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    return result
