"""
Transaction Data Loader for Online Retail II Dataset.

This module ingests raw CSV data from the Online Retail II dataset and
transforms it into the canonical transactions format defined in schema.py.

Input Dataset Columns:
    Invoice, Description, StockCode, Quantity,
    InvoiceDate, Price, Customer ID, Country

Output Schema:
    Matches TRANSACTIONS_SCHEMA from schema.py:
    transaction_id, customer_id, transaction_date, amount,
    product_id, category, channel, region

Assumptions:
    - Input file is a valid CSV with expected column names
    - InvoiceDate is parseable as datetime
    - Invoice values starting with "C" represent cancellations
    - Customer ID null values indicate incomplete records
    - Quantity and Price must be positive for valid transactions

Constraints:
    - No aggregation or feature engineering
    - No validation beyond required cleaning
    - No print statements or logging
"""

import pandas as pd

from src.ingestion.schema import TRANSACTIONS_SCHEMA


# =============================================================================
# COLUMN MAPPINGS
# =============================================================================

_RAW_TO_CANONICAL_COLUMNS = {
    "Invoice": "transaction_id",
    "Customer ID": "customer_id",
    "InvoiceDate": "transaction_date",
    "StockCode": "product_id",
    "Description": "category",
    "Country": "region",
}


# =============================================================================
# PUBLIC API
# =============================================================================

def build_transactions(raw_path: str, output_path: str) -> pd.DataFrame:
    """
    Ingest raw Online Retail II CSV and convert it to canonical transactions format.

    Args:
        raw_path: Path to raw Online Retail II CSV file.
        output_path: Path to write canonical transactions dataset
                     (should be under data/processed/).

    Returns:
        pd.DataFrame: Canonical transactions DataFrame.

    Raises:
        FileNotFoundError: If raw_path does not exist.
        KeyError: If expected columns are missing.
    """
    # -------------------------------------------------------------------------
    # 1. Load raw data
    # -------------------------------------------------------------------------
    df = pd.read_csv(raw_path)

    # -------------------------------------------------------------------------
    # 2. Parse datetime - handle various formats including malformed dates
    # -------------------------------------------------------------------------
    # Strip whitespace first
    df["InvoiceDate"] = df["InvoiceDate"].astype(str).str.strip()
    
    # Fix malformed dates like "2009-12-0107:45:00" -> "2009-12-01 07:45:00"
    # Pattern: date ends with day (2 digits), time starts with hour (2 digits)
    df["InvoiceDate"] = df["InvoiceDate"].str.replace(
        r'(\d{4}-\d{2}-\d{2})(\d{2}:\d{2}:\d{2})',
        r'\1 \2',
        regex=True
    )
    
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format='mixed', dayfirst=True)

    # -------------------------------------------------------------------------
    # 3. Drop rows with missing CustomerID
    # -------------------------------------------------------------------------
    df = df[df["Customer ID"].notna()]

    # -------------------------------------------------------------------------
    # 4. Exclude cancellations (Invoice starts with 'C')
    # -------------------------------------------------------------------------
    df = df[~df["Invoice"].astype(str).str.startswith("C")]

    # -------------------------------------------------------------------------
    # 5. Exclude invalid quantities and prices
    # -------------------------------------------------------------------------
    df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

    # -------------------------------------------------------------------------
    # 6. Rename columns to canonical names
    # -------------------------------------------------------------------------
    df = df.rename(columns=_RAW_TO_CANONICAL_COLUMNS)

    # -------------------------------------------------------------------------
    # 7. Fix customer_id correctly (avoid '12345.0' bug)
    # -------------------------------------------------------------------------
    df["customer_id"] = df["customer_id"].astype(int).astype(str)

    # -------------------------------------------------------------------------
    # 8. Derive amount
    # -------------------------------------------------------------------------
    df["amount"] = df["Quantity"] * df["Price"]

    # -------------------------------------------------------------------------
    # 9. Add channel
    # -------------------------------------------------------------------------
    df["channel"] = "online"

    # -------------------------------------------------------------------------
    # 10. Select and order canonical columns
    # -------------------------------------------------------------------------
    canonical_columns = list(TRANSACTIONS_SCHEMA.keys())
    df = df[canonical_columns]

    # -------------------------------------------------------------------------
    # 11. Cast columns according to schema
    # -------------------------------------------------------------------------
    for column, dtype in TRANSACTIONS_SCHEMA.items():
        if column == "customer_id":
            # already handled explicitly
            continue
        if dtype == "string":
            df[column] = df[column].astype(str)
        elif dtype == "float":
            df[column] = df[column].astype(float)
        elif dtype == "datetime64[ns]":
            df[column] = pd.to_datetime(df[column])

    # -------------------------------------------------------------------------
    # 12. Write canonical dataset
    # -------------------------------------------------------------------------
    df.to_csv(output_path, index=False)

    return df
