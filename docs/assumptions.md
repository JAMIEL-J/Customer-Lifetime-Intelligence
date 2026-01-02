# Assumptions and Limitations

This system is built on explicit assumptions to ensure clarity and trust.

---

## Data Assumptions

- Each transaction row represents a valid purchase line
- Cancellations and refunds are excluded in the baseline
- CustomerID uniquely identifies a customer
- Transaction timestamps are reliable

---

## Behavioral Assumptions

- Recent inactivity is the strongest churn indicator
- Declining spend precedes disengagement
- Frequency changes lag spend changes

---

## Modeling Assumptions

- No machine learning models are used
- All decisions are rule-based and deterministic
- Percentile-based value segmentation assumes a reasonably sized cohort

---

## ROI Assumptions

- Action costs are fixed heuristics
- Recovery rates are estimated, not predictive
- ROI is directional, not guaranteed

---

## System Limitations

- Single-user execution model
- In-memory processing (pandas)
- No real-time updates
- No order-level aggregation (line-item based)

---

## Intended Use

This system is designed for:
- Decision support
- Strategic customer analysis
- Explainable lifecycle intelligence

It is **not** intended to:
- Predict churn probabilities
- Replace CRM systems
- Automate actions without human oversight
