import pandas as pd

from src.features.rfm import compute_rfm_features
from src.features.behavioral import compute_behavioral_trends


def _sample_transactions():
    return pd.DataFrame({
        "customer_id": ["A", "A", "B", "B"],
        "transaction_date": pd.to_datetime([
            "2024-01-01",
            "2024-01-10",
            "2023-12-01",
            "2024-01-05",
        ]),
        "amount": [100, 200, 50, 50],
    })


def test_rfm_basic_computation():
    df = _sample_transactions()

    rfm = compute_rfm_features(
        df,
        snapshot_date="2024-01-10",
        window_days=30,
    )

    row_a = rfm[rfm["customer_id"] == "A"].iloc[0]
    row_b = rfm[rfm["customer_id"] == "B"].iloc[0]

    # Customer A: monetary is window-based (excludes snapshot date 2024-01-10)
    # Only the 2024-01-01 transaction ($100) is in [2023-12-11, 2024-01-09]
    assert row_a["recency_days"] == 0
    assert row_a["frequency"] == 1
    assert row_a["monetary"] == 100  # Window spend only
    assert row_a["lifetime_value"] == 300  # All-time spend

    # Customer B: both transactions are in window
    # 2023-12-01 ($50) and 2024-01-05 ($50) are both in [2023-12-11, 2024-01-09]
    # Actually only 2024-01-05 since 2023-12-01 < 2023-12-11
    assert row_b["recency_days"] == 5
    assert row_b["frequency"] == 1  # Only 2024-01-05 is in window
    assert row_b["monetary"] == 50  # Window spend only
    assert row_b["lifetime_value"] == 100  # All-time spend


def test_behavioral_trends_direction():
    df = _sample_transactions()

    trends = compute_behavioral_trends(
        df,
        snapshot_date="2024-01-10",
        window_days=5,
    )

    row_a = trends[trends["customer_id"] == "A"].iloc[0]

    # Customer A had spend only in recent window → positive trend
    assert row_a["spend_trend"] >= 0
    assert row_a["frequency_trend"] >= 0
