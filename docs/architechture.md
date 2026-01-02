# System Architecture

## Overview

The Customer Lifecycle Intelligence Platform is a deterministic, rule-based analytics system designed to convert raw transaction data into actionable customer decisions.

The architecture prioritizes:

- Explainability over black-box models
- Clear separation of concerns
- Point-in-time correctness
- Incremental extensibility

The system is designed as a **single-process analytical pipeline** orchestrated from a Streamlit interface, without premature microservices or APIs.

---

## High-Level Flow

```
Raw Transactions
       ↓
Canonical Ingestion
       ↓
Data Validation
       ↓
Feature Engineering (RFM + Trends)
       ↓
Segmentation (Lifecycle + Value)
       ↓
Risk Engine (Signals → Scores)
       ↓
Decision Engine (Actions + ROI + Explanations)
       ↓
Dashboard (Read-only Visualization)
```

---

## Layered Design

### 1. Ingestion Layer (`src/ingestion`)

- Converts raw datasets into a canonical schema
- Enforces consistent column naming and types
- Handles exclusions (cancellations, refunds, invalid rows)

### 2. Validation Layer (`src/validation`)

- Ensures data quality before analytics
- Fails fast on missing or invalid critical fields
- Prevents silent data corruption downstream

### 3. Feature Engineering (`src/features`)

- Snapshot-based RFM computation
- Behavioral trend comparison across time windows
- Pure computation (no decisions or thresholds)

### 4. Segmentation (`src/segmentation`)

- Rule-based lifecycle staging using recency
- Value segmentation using monetary percentiles
- Deterministic and explainable logic

### 5. Risk Engine (`src/risk_engine`)

- Converts behavioral features into normalized risk signals
- Aggregates signals using explicit weights
- Assigns categorical risk levels via thresholds

### 6. Decision Engine (`src/decision_engine`)

- Maps risk and value to recommended actions
- Estimates ROI using heuristic assumptions
- Generates human-readable decision explanations

### 7. Presentation Layer (`dashboards/`)

- Streamlit-based UI
- Read-only consumption of pipeline outputs
- No business logic or computation

---

## Design Decisions

- **No ML models**: Rule-based baseline ensures transparency and trust
- **No FastAPI**: Single-user, batch-oriented execution does not require APIs
- **Python-first rules**: Safer and testable; YAML configs reserved for future
- **No notebooks in production path**: All logic is modular and testable

---

## Extensibility

The architecture supports future enhancements:

- Externalized rule configuration via YAML
- FastAPI service layer for multi-user access
- Database-backed persistence
- ML-based risk augmentation (optional, additive)

These are intentionally deferred to avoid premature complexity.
