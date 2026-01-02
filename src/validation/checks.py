"""
Low-Level Data Validation Helper Functions.

This module provides reusable validation functions for DataFrame quality checks.
Functions are dataset-agnostic and designed for use across the analytics pipeline.

Purpose:
    - Validate column presence
    - Check for null values
    - Verify positive numeric values
    - Validate datetime column types

Constraints:
    - No file I/O
    - No dataset-specific assumptions
    - No DataFrame mutations
    - No logging or printing

Usage:
    from src.validation.checks import (
        check_required_columns,
        check_no_nulls,
        check_positive_values,
        check_datetime_column,
    )
"""

from typing import List

import pandas as pd


def check_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    """
    Verify that all required columns are present in the DataFrame.

    Args:
        df: DataFrame to validate.
        required_columns: List of column names that must be present.

    Raises:
        ValueError: If one or more required columns are missing.
    """
    existing_columns = set(df.columns)
    required_set = set(required_columns)
    missing_columns = required_set - existing_columns

    if missing_columns:
        missing_list = sorted(missing_columns)
        raise ValueError(
            f"Missing required columns: {missing_list}. "
            f"Found columns: {sorted(existing_columns)}"
        )


def check_no_nulls(df: pd.DataFrame, columns: List[str]) -> None:
    """
    Verify that specified columns contain no null values.

    Args:
        df: DataFrame to validate.
        columns: List of column names to check for nulls.

    Raises:
        ValueError: If any specified column contains null values.
    """
    for column in columns:
        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' does not exist in DataFrame. "
                f"Available columns: {sorted(df.columns.tolist())}"
            )

        null_count = df[column].isna().sum()
        if null_count > 0:
            raise ValueError(
                f"Column '{column}' contains {null_count} null value(s). "
                f"Expected zero nulls."
            )


def check_positive_values(df: pd.DataFrame, columns: List[str]) -> None:
    """
    Verify that specified columns contain only positive values (> 0).

    Args:
        df: DataFrame to validate.
        columns: List of numeric column names to check.

    Raises:
        ValueError: If any specified column contains non-positive values.
    """
    for column in columns:
        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' does not exist in DataFrame. "
                f"Available columns: {sorted(df.columns.tolist())}"
            )

        non_positive_count = (df[column] <= 0).sum()
        if non_positive_count > 0:
            raise ValueError(
                f"Column '{column}' contains {non_positive_count} non-positive value(s). "
                f"All values must be > 0."
            )


def check_datetime_column(df: pd.DataFrame, column_name: str) -> None:
    """
    Verify that a column is of datetime64 dtype.

    Args:
        df: DataFrame to validate.
        column_name: Name of the column to check.

    Raises:
        ValueError: If column does not exist or is not datetime64 dtype.
    """
    if column_name not in df.columns:
        raise ValueError(
            f"Column '{column_name}' does not exist in DataFrame. "
            f"Available columns: {sorted(df.columns.tolist())}"
        )

    if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
        actual_dtype = df[column_name].dtype
        raise ValueError(
            f"Column '{column_name}' is not datetime64 dtype. "
            f"Found dtype: {actual_dtype}"
        )
