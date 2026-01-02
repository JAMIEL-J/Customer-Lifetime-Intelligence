# Data Dictionary

This document defines the canonical data structures used throughout the
Customer Lifecycle Intelligence Platform.

---

## Canonical Transactions Table

### `transactions`

| Column Name        | Type              | Description |
|--------------------|-------------------|-------------|
| transaction_id     | string            | Unique transaction identifier |
| customer_id        | string            | Unique customer identifier |
| transaction_date   | datetime64[ns]    | Date of transaction |
| amount             | float             | Transaction value (Quantity × Price) |
| product_id         | string            | Product identifier |
| category           | string            | Product description/category |
| channel            | string            | Sales channel (e.g., "online") |
| region             | string            | Customer country/region |

---

## Feature Table

### `features_df`

| Column Name        | Type   | Description |
|--------------------|--------|-------------|
| customer_id        | string | Unique customer identifier |
| recency_days       | int    | Days since last transaction |
| frequency          | int    | Number of transaction rows in window |
| monetary           | float  | Total spend in rolling window |
| lifetime_value     | float  | Total historical spend |
| spend_trend        | float  | % change in spend vs prior window |
| frequency_trend    | float  | % change in frequency vs prior window |

---

## Segmentation Table

### `segments_df`

| Column Name        | Type   | Description |
|--------------------|--------|-------------|
| customer_id        | string | Unique customer identifier |
| lifecycle_stage    | string | Active / At-Risk / Dormant / Churned |
| value_segment      | string | High / Medium / Low Value |
| segment_label      | string | Combined segment label |
| segment_version    | string | Rule version identifier |

---

## Risk Table

### `risk_df`

| Column Name | Type   | Description |
|-------------|--------|-------------|
| customer_id | string | Unique customer identifier |
| risk_score  | float  | Aggregated risk score (0–100) |
| risk_level  | string | Low / Medium / High |

---

## Decision Tables

### `actions_df`

| Column Name         | Type   | Description |
|---------------------|--------|-------------|
| customer_id         | string | Unique customer identifier |
| recommended_action  | string | Business action |
| action_priority     | string | High / Medium / Low |

### `roi_df`

| Column Name        | Type   | Description |
|--------------------|--------|-------------|
| customer_id        | string | Unique customer identifier |
| action_cost        | float  | Estimated cost of action |
| expected_benefit   | float  | Estimated recoverable value |
| estimated_roi      | float  | Benefit minus cost |

### `explanations_df`

| Column Name            | Type   | Description |
|------------------------|--------|-------------|
| customer_id            | string | Unique customer identifier |
| decision_explanation   | string | Human-readable rationale |
