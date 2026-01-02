# Decision Logic

This document explains how customer decisions are derived from data.

The system uses **rule-based logic only**, ensuring transparency and auditability.

---

## Segmentation Logic

### Lifecycle Staging

- Based solely on `recency_days`
- Thresholds applied in order:
  - **Active**: ≤ 30 days
  - **At-Risk**: 31–90 days
  - **Dormant**: 91–180 days
  - **Churned**: > 180 days

### Value Segmentation

- Based on monetary percentile ranking
- Percentiles computed within cohort
- Segments:
  - **High Value**: top 20%
  - **Medium Value**: middle 40%
  - **Low Value**: bottom 40%

---

## Risk Logic

### Risk Signals

Each customer receives normalized signals (0–1):

- **Recency Signal**: Older inactivity → higher risk
- **Spend Drop Signal**: Declining spend → higher risk
- **Frequency Drop Signal**: Reduced engagement → higher risk

### Risk Scoring

Weighted aggregation:

```
risk_score = (recency_signal × 0.40) +
             (frequency_drop_signal × 0.25) +
             (spend_drop_signal × 0.35)

risk_score_scaled = risk_score × 100
```

### Risk Levels

- **Low**: 0–30
- **Medium**: 31–60
- **High**: 61–100

---

## Action Assignment

Actions are selected using deterministic rules based on:

- Risk level
- Customer value segment

Examples:

- High Risk + High Value → Personal retention outreach
- High Risk + Low Value → Automated reactivation
- Low Risk + High Value → Upsell opportunities

Rules are evaluated top-down; first match wins.

---

## ROI Estimation

ROI is estimated heuristically:

```
expected_benefit = lifetime_value × recovery_rate
estimated_roi = expected_benefit − action_cost
```

These are **decision-support estimates**, not predictions.
