# Customer Lifecycle Intelligence Platform
---

## Overview

This repository contains an end-to-end **customer analytics and decision-support system** built using rule-based, deterministic logic.

The system processes raw transactional data and produces:

* Customer-level features
* Lifecycle and value segments
* Risk scores
* Recommended business actions
* ROI estimates
* Plain-English decision explanations

The focus of this project is **analytics engineering, explainability, and production-ready structure**, not machine learning.

---

## Objectives

* Convert raw transaction data into a canonical analytics schema
* Enforce strict data quality validation
* Generate reproducible, snapshot-based customer features
* Apply transparent, rule-driven segmentation and risk scoring
* Translate analytics outputs into concrete business actions
* Present results through an interactive dashboard

---

## Key Characteristics

* No machine learning models
* No predictions or forecasting
* Fully deterministic and auditable logic
* Snapshot-based computations
* Modular, layered architecture
* Clear separation between backend logic and presentation layer

---

## System Flow

```
Raw Transactions (CSV)
→ Ingestion & Canonical Mapping
→ Data Quality Validation
→ Feature Engineering (RFM, Trends)
→ Segmentation (Lifecycle, Value)
→ Risk Engine (Signals, Scores)
→ Decision Engine (Actions, ROI, Explanations)
→ Streamlit Dashboard
```

Each stage operates independently and fails fast on invalid inputs.

---

## Module Breakdown

### Ingestion

* Maps raw transaction data to a canonical schema
* Applies basic filtering (invalid prices, quantities, cancellations)
* Outputs standardized transaction records

### Validation

* Ensures required columns are present
* Enforces non-null and positivity constraints
* Prevents invalid data from entering downstream stages

### Feature Engineering

* RFM metrics (recency, frequency, monetary value)
* Lifetime value calculation
* Behavioral trends using rolling time windows

### Segmentation

* Lifecycle stages based on recency
* Value segments based on monetary percentiles
* Rule-based classification only

### Risk Engine

* Normalized risk signals (0–1)
* Weighted aggregation into 0–100 risk scores
* Threshold-based risk level assignment

### Decision Engine

* Action assignment using explicit rules
* Cost and benefit estimation
* ROI calculation
* Deterministic, text-based explanations

### Dashboard

* Built with Streamlit and Plotly
* Read-only presentation layer
* Filtering, drill-downs, and customer lookup
* No business logic in UI code

---

## How to Run

### 1. Environment Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

The Streamlit dashboard will be available at:

```
http://localhost:8501
```

### 3. Load Data

Use a CSV file matching the Online Retail II schema:

```
Invoice, StockCode, Description, Quantity,
InvoiceDate, Price, CustomerID, Country
```

---

## Testing

Unit tests validate:

* Feature computations
* Segmentation rules
* Risk scoring logic

Run tests using:

```bash
pytest
```

---

## Project Structure (High Level)

```
src/
  ingestion/
  validation/
  features/
  segmentation/
  risk_engine/
  decision_engine/
  services/

dashboards/
tests/
docs/
configs/
scripts/
run.py
app.py
```

---

## Documentation

Additional documentation is available in the `docs/` directory:

* `architecture.md` – system design
* `data_dictionary.md` – schema definitions
* `decision_logic.md` – segmentation and action rules
* `assumptions.md` – business and analytical assumptions

---

## Requirements

See `requirements.txt`.

---

## Notes

* This project is designed as a **single-user analytics system**
* No FastAPI or backend service is required unless multi-user or external integration is needed
* Configuration files (YAML) are included for future extensibility

---


