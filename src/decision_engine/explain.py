"""
Decision Explanation Module.

Generates plain-English explanations for customer decisions based on
risk signals, segmentation, and recommended actions.

All explanations are deterministic, factual, and suitable for
business stakeholders.
"""

import pandas as pd


# =============================================================================
# SIGNAL THRESHOLDS (EXPLANATION AIDES, NOT DECISION LOGIC)
# =============================================================================

SIGNAL_THRESHOLDS = {
    "recency_signal": 0.3,
    "spend_drop_signal": 0.2,
    "frequency_drop_signal": 0.2,
}

SIGNAL_DESCRIPTIONS = {
    "recency_signal": "prolonged inactivity",
    "spend_drop_signal": "declining spend",
    "frequency_drop_signal": "reduced purchase frequency",
}


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _identify_dominant_signals(row: pd.Series) -> list[str]:
    """Identify which risk signals are notably elevated."""
    dominant = []

    for signal, threshold in SIGNAL_THRESHOLDS.items():
        if signal in row and pd.notna(row[signal]) and row[signal] >= threshold:
            dominant.append(SIGNAL_DESCRIPTIONS[signal])

    return dominant


def _extract_value_segment(segment_label: str) -> str:
    """Extract value category from combined segment label."""
    if pd.isna(segment_label):
        return "Unknown"
    if "High Value" in segment_label:
        return "High Value"
    if "Medium Value" in segment_label:
        return "Medium Value"
    if "Low Value" in segment_label:
        return "Low Value"
    return "Unknown"


def _build_explanation(row: pd.Series) -> str:
    """Construct a concise, factual decision explanation."""
    parts = []

    risk_level = row.get("risk_level", "Unknown")
    risk_score = row.get("risk_score", None)
    segment_label = row.get("segment_label", "")
    action = row.get("recommended_action", "Monitor")

    dominant_signals = _identify_dominant_signals(row)

    # -------------------------------------------------------------------------
    # Risk explanation
    # -------------------------------------------------------------------------
    if risk_level in {"High", "Medium"}:
        if dominant_signals:
            signal_text = " and ".join(dominant_signals)
            parts.append(
                f"Customer is classified as {risk_level} Risk due to {signal_text}."
            )
        else:
            parts.append(
                f"Customer is classified as {risk_level} Risk based on overall behavior."
            )
    elif risk_level == "Low":
        parts.append("Customer shows stable behavior and is classified as Low Risk.")
    else:
        parts.append("Customer risk level could not be confidently determined.")

    if risk_score is not None and pd.notna(risk_score):
        parts.append(f"Overall risk score is {risk_score:.1f} out of 100.")

    # -------------------------------------------------------------------------
    # Value context and action rationale
    # -------------------------------------------------------------------------
    value_segment = _extract_value_segment(segment_label)

    if value_segment != "Unknown":
        parts.append(
            f"As a {value_segment} customer, the recommended action is {action.lower()}."
        )
    else:
        parts.append(f"Recommended action is {action.lower()}.")

    return " ".join(parts)


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_decision_explanations(decision_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate plain-English explanations for customer decisions.
    """
    required_columns = {
        "customer_id",
        "risk_level",
        "segment_label",
        "recommended_action",
    }

    missing = required_columns - set(decision_df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    df = decision_df.copy()

    df["decision_explanation"] = df.apply(_build_explanation, axis=1)

    result = (
        df[
            [
                "customer_id",
                "decision_explanation",
            ]
        ]
        .sort_values("customer_id")
        .reset_index(drop=True)
    )

    return result
