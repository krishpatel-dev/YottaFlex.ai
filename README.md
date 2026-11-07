# 🌡️ Cold Chain Compliance Platform
### End-to-End Pharmaceutical & Perishable Logistics Traceability System
[![Cold Chain Compliance CI](https://github.com/krishpatel-dev/YottaFlex.ai/actions/workflows/ci.yml/badge.svg)](https://github.com/krishpatel-dev/YottaFlex.ai/actions/workflows/ci.yml)
> **YottaFlex AI Candidate Project Submission**  
> **Tech Stack:** Python 3.11+ · Pandas · NumPy · Faker · SQL (PostgreSQL / SQLite) · Streamlit · Plotly · Pytest  
> **Fixed Seed:** `20261022` (100% Deterministic Reproducibility)

---

## 📌 Executive Summary

Pharmaceutical vaccines, biologics, and clinical trial reagents require strict temperature control (e.g. 2°C to 8°C for refrigerated vaccines, -80°C to -60°C for mRNA) from manufacturing release through final clinical delivery. This platform answers the core question:

> **"Can we prove that a temperature-sensitive product was maintained within its required temperature range throughout its journey from supplier to destination? If not, can we identify what went wrong, when it happened, and who was responsible?"**

The solution combines:
1. **Relational Master & Telemetry Data Engine**: Generates 5,000 shipments, 10 interconnected normalized tables, and 724,000+ continuous temperature readings.
2. **GxP Compliance Adjudication Engine**: Implements Haynes-Arrhenius Mean Kinetic Temperature (MKT), contiguous excursion duration calculation, telemetry gap detection, and chain-of-custody verification.
3. **Five Mandatory Negative Scenarios**: Controlled injection and automated detection of unassigned loggers, threshold policy mismatches, missing data gaps, unrecorded custody transfers, and cross-shipment telemetry isolation.
4. **Interactive Regulatory Dashboard**: A 5-tab Streamlit & Plotly application providing KPI tracking, telemetry inspection, custody verification, deviation disposition, and audit-ready compliance certificates.

---

## 🏗️ Project Architecture & Component Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Interactive Dashboard (Streamlit)                     │
│   [1. Overview]   [2. Telemetry]   [3. Tracking]   [4. Exceptions]   [5. Dossier]
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    Compliance Adjudication Engine (Python)                  │
│   • Haynes-Arrhenius MKT             • Contiguous Excursion Duration        │
│   • Telemetry Gap Detection          • Custody Chain & Signature Audit      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    Relational Data Layer (PostgreSQL / SQLite)              │
│   10 Tables: Products, Packaging, Policies, Lots, Shipments, Loggers,        │
│   RouteStops, CustodyEvents, TemperatureReadings, ExcursionReports          │
└──────────────────────────────────────▲──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                    Synthetic Data Generator (Seed: 20261022)                │
│   Deterministic NumPy/Pandas Generation · Controlled Anomaly Injection      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
E:\YottaFlex/
├── data/
│   ├── master/
│   │   ├── products.csv                 # 15 regulated pharmaceutical products
│   │   ├── packaging.csv                # 8 certified thermal packaging profiles
│   │   ├── threshold_policies.csv       # 20 quality temperature policies
│   │   ├── lots.csv                     # 1,666 manufactured product batches
│   │   └── loggers.csv                  # 5,950 calibrated dataloggers
│   ├── transactions/
│   │   ├── shipments.csv                # 5,000 transport missions
│   │   ├── route_stops.csv              # 15,000 origin/transit/destination stops
│   │   ├── custody_events.csv           # 15,000 legal handovers with signatures
│   │   └── temperature_readings.csv     # 724,838 10-minute sensor telemetry points
│   ├── reports/
│   │   └── excursion_reports.csv        # 825 formal quality deviation reports
│   └── ground_truth/
│       └── ground_truth.csv             # ISOLATED: Injected edge-case ground truth
│
├── database/
│   ├── schema.sql                       # ANSI SQL DDL (PostgreSQL & SQLite compatible)
│   ├── seed.sql                         # Initial database seed script
│   └── create_seed_sql.py               # Seed generator utility
│
├── src/
│   ├── data_generator.py                # Deterministic synthetic data generator
│   ├── business_rules.py                # Haynes-Arrhenius MKT, excursion & gap logic
│   ├── compliance_engine.py             # Adjudication engine producing audit summaries
│   ├── exception_detector.py            # Benchmark detector evaluating against ground truth
│   └── validator.py                     # Relational integrity validator (PK/FK/Enum/Dates)
│
├── dashboard/
│   └── app.py                           # 5-tab interactive Streamlit dashboard
│
├── reports/
│   ├── compliance_summary.csv           # Full compliance audit scorecard for 5,000 shipments
│   └── validation_summary.json          # Anomaly detection benchmark metrics
│
├── tests/
│   └── test_validation.py               # Automated Pytest suite (DDL, integrity, MKT, edge cases)
│
├── documentation/
│   ├── data_dictionary.md               # Complete schema specifications for all 10 entities
│   ├── entity_relationship_diagram.md   # Mermaid ER diagram & relational cardinalities
│   ├── er_diagram.png                   # High-resolution architectural ER diagram image
│   ├── project_documentation.md         # Comprehensive system & domain documentation
│   └── prompt_history.md                # Full transparent AI prompt disclosure log
│
├── requirements.txt                     # Pinned project dependencies
└── README.md                            # Main project guide
```

---

## ⚡ Quick Start & Execution Guide

### 1. Prerequisites & Environment Setup
Python 3.10+ is required. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Generate the Dataset (Seed: 20261022)
To generate the full 5,000 shipments dataset with fixed random seed:
```bash
python src/data_generator.py --seed 20261022 --shipments 5000 --checksums
```
*(Takes ~12 seconds. Generates 724,000+ readings across all 10 relational tables).*

### 3. Run the Compliance Adjudication Engine
To evaluate all shipments against product policies, calculate MKT, identify excursions, and update compliance statuses:
```bash
python src/compliance_engine.py
```
Outputs:
- `data/reports/excursion_reports.csv`
- `reports/compliance_summary.csv`
- Updates `data/transactions/shipments.csv`

### 4. Evaluate Mandatory Negative Scenarios
Benchmark the system's detection recall against the isolated ground truth:
```bash
python src/exception_detector.py
```

### 5. Run Relational Integrity Validator
Verify primary keys, foreign keys, enums, temporal dates, and arithmetic reconciliation:
```bash
python src/validator.py
```

### 6. Run the Automated Pytest Suite
```bash
python -m pytest tests/test_validation.py -v
```

### 7. Launch the Interactive Dashboard
```bash
python -m streamlit run dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📊 Negative Scenario Detection Benchmark

The compliance engine was evaluated against `data/ground_truth/ground_truth.csv` (which was never used as an input feature during adjudication):

| Scenario Code | Description | Injected Count | Correctly Detected | Detection Recall |
| :--- | :--- | :---: | :---: | :---: |
| **`UNASSIGNED_LOGGER`** | Shipment dispatched without calibrated logger | 50 | 50 | **100.0%** |
| **`POLICY_MISMATCH`** | Wrong thermal policy applied to product | 30 | 30 | **100.0%** |
| **`SILENT_DATA_GAP`** | Unrecorded sensor blackout (>25 min gap) | 40 | 38 | **95.0%** |
| **`UNFLAGGED_CUSTODY_GAP`** | Unsigned or unrecorded custody transfer | 25 | 25 | **100.0%** |
| **`CROSS_SHIPMENT_EXCURSION`**| Telemetry boundary containment | 15 | 15 | **100.0%** |
| **OVERALL BENCHMARK** | **All Controlled Anomaly Scenarios** | **160** | **158** | **98.8%** |

---

## 🔒 Relational Integrity & Reproducibility Verification

1. **Relational Integrity Audit**:
   - Primary Key Uniqueness: **100% Unique** across all 10 tables.
   - Foreign Key Integrity: **0 orphaned records**.
   - Allowed Enums: **100% valid**.
   - Chronological Ordering: **100% compliant** (`manufacture_date < expiry_date`, `departure <= arrival`).
   - Telemetry Duplicates: **0 duplicates** per logger/timestamp.
   - Total Detected Violations: **0**.

2. **Byte-Level Reproducibility Proof (Seed: 20261022)**:
   Generating twice with seed `20261022` produces identical row counts and matching MD5 hashes:
   ```
   products.csv             1fb2e28bfb16a0b1095c0cd89528d799
   packaging.csv            b49e6ce6b33c66200de3fadfd2ceb788
   threshold_policies.csv   c4945b8a882b70ff2fb578fcdbb04113
   lots.csv                 00f05efd1612d4c6221f12fdeabc74cf
   loggers.csv              1ce2903e716e6b7422d8e41e66f17cd3
   shipments.csv            c854f1162d2228161c12d83e1d409b12
   route_stops.csv          18739670f595b6b0a95c34b8e504705a
   custody_events.csv       af2443249858733ecb68e4dcdc3e188d
   temperature_readings.csv a75b89eae12a2616c6ba509f3b248e0e
   ground_truth.csv         5d7a1f0981c18505d16e03b8d6b6c6ec
   ```

---

## 🌐 Database Loading (PostgreSQL / SQLite)

The schema in `database/schema.sql` is compatible with PostgreSQL 14+ and SQLite 3.35+:

- **SQLite (Zero Setup Local DB)**:
  ```bash
  sqlite3 coldchain.db < database/schema.sql
  sqlite3 coldchain.db < database/seed.sql
  ```
- **PostgreSQL**:
  ```bash
  psql -U postgres -d coldchain_db -f database/schema.sql
  psql -U postgres -d coldchain_db -f database/seed.sql
  ```

---

## 🤖 Transparent AI Use & Prompt Disclosure

In accordance with candidate project submission requirements:
- Full prompt history and human validation log are documented in [`documentation/prompt_history.md`](documentation/prompt_history.md).
- Relational schema, MKT calculations, and GxP decision rules were verified against USP <1079> and WHO Annex 9 specifications.

