import pandas as pd

from src.segmentation.assign_segments import assign_customer_segments


def test_segmentation_rules_applied_correctly():
    features = pd.DataFrame({
        "customer_id": ["A", "B", "C"],
        "recency_days": [10, 60, 200],
        "monetary": [1000, 300, 0],
    })

    segmented = assign_customer_segments(features)

    a = segmented[segmented["customer_id"] == "A"].iloc[0]
    b = segmented[segmented["customer_id"] == "B"].iloc[0]
    c = segmented[segmented["customer_id"] == "C"].iloc[0]

    # Lifecycle stages
    assert a["lifecycle_stage"] == "Active"
    assert b["lifecycle_stage"] == "At-Risk"
    assert c["lifecycle_stage"] == "Churned"

    # Value segments
    assert a["value_segment"] == "High Value"
    assert b["value_segment"] in {"Medium Value", "Low Value"}
    assert c["value_segment"] == "Low Value"

    # Combined label exists
    assert " " in a["segment_label"]
