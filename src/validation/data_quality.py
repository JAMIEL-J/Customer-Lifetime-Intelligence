"""
Transaction Data Quality Validation.

This module validates canonical transaction data AFTER ingestion and BEFORE
feature engineering. It uses helper functions from checks.py and references
schema definitions from ingestion/schema.py.

Purpose:
    - Validate column presence and types
    - Ensure data integrity for downstream processing
    - Provide validation summary for monitoring

Constraints:
    - No cleaning or transformation
    - No file I/O
    - Validation only - raises on hard failures

Usage:
    from src.validation.data_quality import validate_transactions

    summary = validate_transactions(transactions_df)
"""

from typing import Dict, Any

import pandas as pd

from src.ingestion.schema import (
    TRANSACTIONS_SCHEMA,
    REQUIRED_TRANSACTION_COLUMNS,
)
from src.validation.checks import (
    check_required_columns,
    check_no_nulls,
    check_positive_values,
    check_datetime_column,
)


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

_CRITICAL_NO_NULL_COLUMNS = [
    "transaction_id",
    "customer_id",
    "transaction_date",
    "amount",
]
"""Columns that must never contain null values."""

_POSITIVE_VALUE_COLUMNS = [
    "amount",
]
"""Columns that must contain strictly positive values."""

_DATETIME_COLUMNS = [
    "transaction_date",
]
"""Columns that must be datetime64 dtype."""


# =============================================================================
# PUBLIC API
# =============================================================================

def validate_transactions(transactions_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate canonical transactions DataFrame.

    Performs the following validations:
        1. Required columns exist (from TRANSACTIONS_SCHEMA)
        2. Critical columns have no null values
        3. Amount values are strictly positive
        4. transaction_date is valid datetime dtype

    Args:
        transactions_df: Canonical transactions DataFrame to validate.

    Returns:
        dict: Validation summary with the following keys:
            - row_count: Total number of rows
            - column_count: Total number of columns
            - columns_validated: List of columns checked
            - validations_passed: List of validation names that passed

    Raises:
        ValueError: If any validation check fails.
    """
    validations_passed = []

    # -------------------------------------------------------------------------
    # 1. Check required columns exist
    # -------------------------------------------------------------------------
    schema_columns = list(TRANSACTIONS_SCHEMA.keys())
    check_required_columns(transactions_df, REQUIRED_TRANSACTION_COLUMNS)
    validations_passed.append("required_columns")

    # -------------------------------------------------------------------------
    # 2. Check no nulls in critical columns
    # -------------------------------------------------------------------------
    check_no_nulls(transactions_df, _CRITICAL_NO_NULL_COLUMNS)
    validations_passed.append("no_nulls_critical")

    # -------------------------------------------------------------------------
    # 3. Check positive values in amount column
    # -------------------------------------------------------------------------
    check_positive_values(transactions_df, _POSITIVE_VALUE_COLUMNS)
    validations_passed.append("positive_values")

    # -------------------------------------------------------------------------
    # 4. Check datetime column type
    # -------------------------------------------------------------------------
    for column in _DATETIME_COLUMNS:
        check_datetime_column(transactions_df, column)
    validations_passed.append("datetime_valid")

    # -------------------------------------------------------------------------
    # Build validation summary
    # -------------------------------------------------------------------------
    validated_columns = (
        REQUIRED_TRANSACTION_COLUMNS
        + _CRITICAL_NO_NULL_COLUMNS
        + _POSITIVE_VALUE_COLUMNS
        + _DATETIME_COLUMNS
    )
    validated_columns = sorted(set(validated_columns))
    summary: Dict[str, Any] = {
        "row_count": len(transactions_df),
        "column_count": len(transactions_df.columns),
        "columns_validated": validated_columns,
        "validations_passed": validations_passed,
    }

    return summary
