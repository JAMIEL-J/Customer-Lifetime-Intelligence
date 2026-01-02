import pandas as pd

from src.risk_engine.signals import compute_risk_signals
from src.risk_engine.scoring import compute_risk_scores


def test_risk_signal_normalization():
    features = pd.DataFrame({
        "customer_id": ["A"],
        "recency_days": [200],
        "spend_trend": [-50],
        "frequency_trend": [-20],
    })

    signals = compute_risk_signals(features)
    row = signals.iloc[0]

    assert 0 <= row["recency_signal"] <= 1
    assert 0 <= row["spend_drop_signal"] <= 1
    assert 0 <= row["frequency_drop_signal"] <= 1


def test_risk_score_and_level_assignment():
    signals = pd.DataFrame({
        "customer_id": ["A"],
        "recency_signal": [1.0],
        "spend_drop_signal": [1.0],
        "frequency_drop_signal": [1.0],
    })

    scores = compute_risk_scores(signals)
    row = scores.iloc[0]

    assert row["risk_score"] == 100.0
    assert row["risk_level"] == "High"
