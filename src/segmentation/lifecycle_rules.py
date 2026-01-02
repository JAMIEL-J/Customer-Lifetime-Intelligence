"""
lifecycle_rules.py
Lifecycle and Value Segmentation Rule Definitions.

This module defines centralized, constant rules for customer lifecycle staging
and value segmentation. These rules are used by downstream segmentation logic
to classify customers into meaningful groups.

Purpose:
    - Centralize segmentation thresholds
    - Provide clear, documented business rules
    - Enable consistent segmentation across the platform

Constraints:
    - No pandas or data manipulation
    - No ML or clustering
    - Constants only - no executable logic
    - Rules are applied elsewhere

Usage:
    from src.segmentation.lifecycle_rules import (
        LIFECYCLE_STAGE_RULES,
        VALUE_SEGMENT_RULES,
        RULE_METADATA,
    )
"""

from typing import Dict, List, Any, Final


# =============================================================================
# LIFECYCLE STAGE RULES
# =============================================================================
# Lifecycle stages are determined by recency_days (days since last transaction).
# Lower recency = more recent activity = healthier customer relationship.
#
# Thresholds are evaluated in order; first matching rule wins.
# =============================================================================

LIFECYCLE_STAGE_RULES: Final[List[Dict[str, Any]]] = [
    {
        "stage": "Active",
        "recency_max": 30,  # Last transaction within 30 days
        "description": "Engaged customers with recent activity",
    },
    {
        "stage": "At-Risk",
        "recency_min": 31,
        "recency_max": 90,  # Last transaction 31-90 days ago
        "description": "Customers showing early signs of disengagement",
    },
    {
        "stage": "Dormant",
        "recency_min": 91,
        "recency_max": 180,  # Last transaction 91-180 days ago
        "description": "Inactive customers requiring reactivation efforts",
    },
    {
        "stage": "Churned",
        "recency_min": 181,  # Last transaction more than 180 days ago
        "description": "Customers considered lost without intervention",
    },
]
"""
Lifecycle stage definitions based on recency_days thresholds.

Each rule contains:
    - stage: Human-readable stage name
    - recency_min: Minimum recency_days (inclusive), optional
    - recency_max: Maximum recency_days (inclusive), optional
    - description: Explanation of stage meaning

Evaluation order matters; apply rules sequentially.
"""


# =============================================================================
# VALUE SEGMENT RULES
# =============================================================================
# Value segments are determined by monetary percentile rankings.
# Customers are classified based on their spend relative to the cohort.
#
# Percentiles are cumulative from bottom (0) to top (100).
# =============================================================================

VALUE_SEGMENT_RULES: Final[List[Dict[str, Any]]] = [
    {
        "segment": "High Value",
        "percentile_min": 80,  # Top 20% of spenders
        "percentile_max": 100,
        "description": "Premium customers driving majority of revenue",
    },
    {
        "segment": "Medium Value",
        "percentile_min": 40,  # Middle 40% of spenders
        "percentile_max": 79,
        "description": "Core customer base with growth potential",
    },
    {
        "segment": "Low Value",
        "percentile_min": 0,  # Bottom 40% of spenders
        "percentile_max": 39,
        "description": "Price-sensitive or infrequent customers",
    },
]
"""
Value segment definitions based on monetary percentile cutoffs.

Each rule contains:
    - segment: Human-readable segment name
    - percentile_min: Minimum percentile (inclusive)
    - percentile_max: Maximum percentile (inclusive)
    - description: Explanation of segment characteristics

Percentiles are computed on the monetary column at runtime.
"""


# =============================================================================
# RULE METADATA
# =============================================================================
# Version and documentation for rule governance and auditability.
# =============================================================================

RULE_METADATA: Final[Dict[str, str]] = {
    "version": "1.0.0",
    "description": (
        "Rule-based customer segmentation using RFM-derived metrics. "
        "Lifecycle stages prioritize recency for engagement health; "
        "value segments use monetary percentiles for revenue contribution. "
        "Thresholds are calibrated for e-commerce/retail contexts."
    ),
    "author": "Analytics Engineering",
    "last_updated": "2026-01-01",
}
"""
Metadata for segmentation rule governance.

Contains:
    - version: Semantic version of the rule set
    - description: Philosophy and rationale behind segmentation approach
    - author: Responsible team or owner
    - last_updated: Date of last rule modification
"""
