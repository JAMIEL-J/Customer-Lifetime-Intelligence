"""
Global System Constants.

Defines non-business, cross-cutting constants used across the platform.
No domain rules, thresholds, or business assumptions belong here.
"""

from typing import Final


# =============================================================================
# DATE & TIME
# =============================================================================

DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d"
UTC_TIMEZONE: Final[str] = "UTC"


# =============================================================================
# DATA WINDOW DEFAULTS
# =============================================================================

DEFAULT_WINDOW_DAYS: Final[int] = 90
DEFAULT_RECENCY_CAP_DAYS: Final[int] = 365


# =============================================================================
# COMMON COLUMN NAMES
# =============================================================================

CUSTOMER_ID_COL: Final[str] = "customer_id"
TRANSACTION_DATE_COL: Final[str] = "transaction_date"
AMOUNT_COL: Final[str] = "amount"


# =============================================================================
# SYSTEM BEHAVIOR
# =============================================================================

UNKNOWN_LABEL: Final[str] = "Unknown"
