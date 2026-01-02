"""
Canonical Schema Specifications for Ingested Datasets.

This module defines schema constants for transaction datasets used throughout
the analytics pipeline. It provides type specifications, required columns,
and optional columns as immutable constants.

Purpose:
    - Centralized schema definitions for data validation
    - Type specifications for downstream processing
    - Column categorization (required vs optional)

Constraints:
    - No data loading or I/O operations
    - No business logic or transformations
    - Constants only - no executable code
    - No pandas or external dependencies

"""

from typing import Dict, List, Final


# =============================================================================
# TRANSACTIONS SCHEMA
# =============================================================================

TRANSACTIONS_SCHEMA: Final[Dict[str, str]] = {
    "transaction_id": "string",
    "customer_id": "string",
    "transaction_date": "datetime64[ns]",
    "amount": "float",
    "product_id": "string",
    "category": "string",
    "channel": "string",
    "region": "string",
}
"""
Schema specification for transaction datasets.

Keys represent column names, values represent expected data types.
Types are specified as strings compatible with pandas/numpy dtype casting.
"""


# =============================================================================
# COLUMN CLASSIFICATIONS
# =============================================================================

REQUIRED_TRANSACTION_COLUMNS: Final[List[str]] = [
    "transaction_id",
    "customer_id",
    "transaction_date",
    "amount",
]
"""
Mandatory columns that must be present in all transaction datasets.

These columns are essential for core transaction processing and analytics.
Datasets missing any of these columns should fail validation.
"""


OPTIONAL_TRANSACTION_COLUMNS: Final[List[str]] = [
    "product_id",
    "category",
    "channel",
    "region",
]
"""
Optional columns that may be present in transaction datasets.

These columns provide supplementary context for enhanced analytics
but are not required for basic transaction processing.
"""
