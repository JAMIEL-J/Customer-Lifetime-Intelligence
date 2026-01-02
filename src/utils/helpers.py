"""
Generic Helper Utilities.

Small, reusable helper functions that are safe to use across
all layers of the system.
"""

from typing import Iterable, List, Any
import pandas as pd


# =============================================================================
# SAFE UTILITIES
# =============================================================================

def ensure_list(value: Any) -> List[Any]:
    """
    Ensure input is returned as a list.

    Args:
        value: Single value or iterable.

    Returns:
        List version of input.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return list(value)
    return [value]


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert value to string.

    Args:
        value: Any input value.
        default: Value returned if input is null.

    Returns:
        String representation.
    """
    if pd.isna(value):
        return default
    return str(value)


def assert_columns_exist(df: pd.DataFrame, columns: List[str]) -> None:
    """
    Assert that required columns exist in a DataFrame.

    Args:
        df: DataFrame to validate.
        columns: Required column names.

    Raises:
        KeyError: If any column is missing.
    """
    missing = set(columns) - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")
