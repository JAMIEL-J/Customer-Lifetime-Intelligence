"""
Risk Score Threshold Definitions.

This module defines centralized thresholds for categorizing customer risk levels.
These constants are used by downstream scoring logic to assign risk categories.

Purpose:
    - Centralize risk categorization boundaries
    - Provide clear, documented thresholds
    - Enable consistent risk labeling across the platform

Constraints:
    - No pandas or data manipulation
    - No ML or prediction
    - Constants only - no executable logic

Usage:
    from src.risk_engine.thresholds import (
        RISK_SCORE_THRESHOLDS,
        THRESHOLD_METADATA,
    )
"""

from typing import Dict, List, Any, Final


# =============================================================================
# RISK SCORE THRESHOLDS
# =============================================================================
# Risk scores are assumed to be on a 0-100 scale.
# Categories are evaluated in order; first matching range wins.
#
# Philosophy:
# - Low risk: Healthy customers with minimal intervention needed
# - Medium risk: Customers showing early warning signs, monitor closely
# - High risk: Customers requiring immediate attention/intervention
# =============================================================================

RISK_SCORE_THRESHOLDS: Final[List[Dict[str, Any]]] = [
    {
        "category": "Low",
        "score_min": 0,
        "score_max": 30,
        "description": "Healthy customers with stable engagement patterns",
        "recommended_action": "Maintain relationship, upsell opportunities",
    },
    {
        "category": "Medium",
        "score_min": 31,
        "score_max": 60,
        "description": "Customers showing early warning signs of disengagement",
        "recommended_action": "Proactive outreach, engagement campaigns",
    },
    {
        "category": "High",
        "score_min": 61,
        "score_max": 100,
        "description": "Customers at significant risk of churn",
        "recommended_action": "Immediate intervention, retention offers",
    },
]
"""
Risk score categories with score ranges and recommended actions.

Each threshold contains:
    - category: Risk level label (Low/Medium/High)
    - score_min: Minimum score for this category (inclusive)
    - score_max: Maximum score for this category (inclusive)
    - description: What this risk level indicates
    - recommended_action: Suggested business response

Scores are expected to be on a 0-100 scale.
"""


# =============================================================================
# THRESHOLD METADATA
# =============================================================================
# Version and documentation for threshold governance and auditability.
# =============================================================================

THRESHOLD_METADATA: Final[Dict[str, str]] = {
    "version": "1.0.0",
    "description": (
        "Risk thresholds designed for e-commerce/retail customer base. "
        "Low threshold (0-30) captures ~50% of healthy customers. "
        "Medium threshold (31-60) identifies early warning signals. "
        "High threshold (61-100) flags customers needing urgent attention. "
        "Thresholds should be recalibrated quarterly based on actual churn rates."
    ),
    "score_scale": "0-100",
    "author": "Analytics Engineering",
    "last_updated": "2026-01-01",
}
"""
Metadata for risk threshold governance.

Contains:
    - version: Semantic version of threshold definitions
    - description: Philosophy and calibration notes
    - score_scale: Expected input score range
    - author: Responsible team or owner
    - last_updated: Date of last threshold revision
"""
