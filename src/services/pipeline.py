"""
Customer Lifecycle Intelligence Pipeline.

Defines the end-to-end execution flow from raw transactions
to customer decisions. This module orchestrates domain logic
and does not contain business rules or persistence logic.
"""

from typing import Dict, Any, Optional

import pandas as pd

# Ingestion
from src.ingestion.loaders import build_transactions

# Validation
from src.validation.data_quality import validate_transactions

# Features
from src.features.time_windows import get_snapshot_date
from src.features.rfm import compute_rfm_features
from src.features.behavioral import compute_behavioral_trends

# Segmentation
from src.segmentation.assign_segments import assign_customer_segments

# Risk Engine
from src.risk_engine.signals import compute_risk_signals
from src.risk_engine.scoring import compute_risk_scores

# Decision Engine
from src.decision_engine.actions import assign_actions
from src.decision_engine.roi import estimate_action_roi
from src.decision_engine.explain import generate_decision_explanations


def run_pipeline(
    raw_transactions_path: str,
    snapshot_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the full Customer Lifecycle Intelligence pipeline.

    Args:
        raw_transactions_path: Path to raw transactions CSV.
        snapshot_date: Optional reference date for analysis.

    Returns:
        Dictionary with standardized outputs:
            - transactions_df
            - validation_summary
            - features_df
            - segments_df
            - risk_df
            - actions_df
            - roi_df
            - explanations_df
    """
    results: Dict[str, Any] = {}

    # ======================================================================
    # 1. INGESTION
    # ======================================================================
    transactions_df = build_transactions(
        raw_path=raw_transactions_path,
        output_path=None,  # persistence handled outside pipeline
    )
    results["transactions_df"] = transactions_df

    # ======================================================================
    # 2. VALIDATION
    # ======================================================================
    validation_summary = validate_transactions(transactions_df)
    results["validation_summary"] = validation_summary

    # ======================================================================
    # 3. SNAPSHOT RESOLUTION (ONCE)
    # ======================================================================
    snapshot = get_snapshot_date(transactions_df, snapshot_date)

    # ======================================================================
    # 4. FEATURE ENGINEERING
    # ======================================================================
    rfm_df = compute_rfm_features(
        transactions_df,
        snapshot_date=str(snapshot.date()),
        window_days=90,
    )

    behavioral_df = compute_behavioral_trends(
        transactions_df,
        snapshot_date=str(snapshot.date()),
        window_days=90,
    )

    features_df = (
        rfm_df
        .merge(behavioral_df, on="customer_id", how="left")
        .sort_values("customer_id")
        .reset_index(drop=True)
    )
    results["features_df"] = features_df

    # ======================================================================
    # 5. SEGMENTATION
    # ======================================================================
    segments_df = assign_customer_segments(features_df)
    results["segments_df"] = segments_df

    # ======================================================================
    # 6. RISK ENGINE
    # ======================================================================
    signals_input = features_df[
        ["customer_id", "recency_days", "spend_trend", "frequency_trend"]
    ]

    signals_df = compute_risk_signals(signals_input)
    risk_df = compute_risk_scores(signals_df)
    results["risk_df"] = risk_df

    # ======================================================================
    # 7. DECISION ENGINE
    # ======================================================================
    decision_base = (
        segments_df
        .merge(risk_df, on="customer_id", how="left")
        .merge(features_df[["customer_id", "lifetime_value"]], on="customer_id", how="left")
    )

    actions_df = assign_actions(decision_base)
    results["actions_df"] = actions_df

    roi_df = estimate_action_roi(
        actions_df.merge(
            decision_base[["customer_id", "lifetime_value", "risk_level"]],
            on="customer_id",
            how="left",
        )
    )
    results["roi_df"] = roi_df

    explanations_df = generate_decision_explanations(
        decision_base
        .merge(actions_df, on="customer_id", how="left")
        .merge(signals_df, on="customer_id", how="left")
    )
    results["explanations_df"] = explanations_df

    return results
