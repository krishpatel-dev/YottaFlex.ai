# ❄️ ColdChain OS — Enterprise Cold Chain Compliance Platform
### End-to-End Pharmaceutical & Perishable Logistics Traceability System
[![Cold Chain Compliance CI](https://github.com/krishpatel-dev/YottaFlex.ai/actions/workflows/ci.yml/badge.svg)](https://github.com/krishpatel-dev/YottaFlex.ai/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GxP Regulatory Standard](https://img.shields.io/badge/GxP-USP%20%3C1079%3E%20%7C%20WHO%20Annex%209-emerald.svg)](https://www.who.int/)
[![Electronic Records](https://img.shields.io/badge/21%20CFR%20Part%2011-Compliant-success.svg)](https://www.fda.gov/)
[![Deterministic Seed](https://img.shields.io/badge/Seed-20261022%20(Reproducible)-purple.svg)](https://github.com/krishpatel-dev/YottaFlex.ai)

> **YottaFlex AI Candidate Project Submission**  
> **Author:** Krish Patel ([@krishpatel-dev](https://github.com/krishpatel-dev))  
> **Repository:** [https://github.com/krishpatel-dev/YottaFlex.ai](https://github.com/krishpatel-dev/YottaFlex.ai)  
> **Tech Stack:** Python 3.10+ · SQLite / PostgreSQL · Pandas · NumPy · Plotly · Streamlit · Pytest · GitHub Actions CI  

---

## 📌 1. Executive Summary & Business Context

In pharmaceutical supply chains, temperature-sensitive products—such as pediatric vaccines, insulin, monoclonal antibodies, and mRNA therapies—must be maintained within strictly certified thermal ranges throughout their entire journey from manufacturing plant to clinical delivery:

* **Refrigerated Vaccines & Biologics:** $2^\circ\text{C}$ to $8^\circ\text{C}$
* **Room Temperature Pharmaceuticals:** $15^\circ\text{C}$ to $25^\circ\text{C}$
* **Frozen / Ultra-Cold Therapeutics:** $-20^\circ\text{C}$ and $-80^\circ\text{C}$ to $-60^\circ\text{C}$

Even a temporary cold-chain failure (e.g., thermal insulation breakdown during cross-dock dwell, a broken refrigeration compressor, or customs delays in transit) can cause protein denaturation, loss of potency, or microbial contamination—putting patient safety at risk and causing millions of dollars in discarded batches and regulatory citations.

This platform provides an end-to-end, audit-ready data engineering and intelligence system designed to answer the core regulatory question:

> **"Can we prove that a temperature-sensitive product was maintained within its required temperature range throughout its journey from supplier to destination? If not, can we identify what went wrong, when it happened, and who was responsible?"**

---

## 🎯 2. Core Capabilities & Technical Highlights

1. **Deterministic Relational Master & Telemetry Data Layer**:
   - Generates 5,000 transport missions, 1,000 calibrated loggers, 15,000 waypoints, 15,000 custody transfers, and **724,838 continuous 10-minute sensor readings**.
   - Generated with a fixed random seed (`20261022`) guaranteeing 100% byte-level reproducibility across operating systems.
   - Zero relational integrity violations across foreign keys, primary keys, enums, or temporal chronology.

2. **GxP Compliance Adjudication Engine**:
   - **Haynes-Arrhenius Mean Kinetic Temperature (MKT)**: Evaluates cumulative thermal degradation using activation energy $\Delta H = 83.144\text{ kJ/mol}$, accurately weighting high-temperature excursions based on chemical reaction kinetics.
   - **Contiguous Excursion Detection**: Computes continuous breach duration, compares against allowed product-specific policy thresholds, and categorizes incidents into `MINOR`, `MAJOR`, or `CRITICAL`.
   - **Telemetry Quality Auditing**: Detects sensor signal blackouts and gaps exceeding 25 minutes (`MISSING_DATA`).
   - **Chain-of-Custody Verification**: Cross-references custody transfers across drivers, airline carriers, and cross-dock hubs, flagging unsigned handovers or unaccounted temporal gaps.

3. **Benchmarked Negative Scenario Detection (98.8% Recall)**:
   - Injects 5 controlled anomaly edge cases into the dataset.
   - Evaluates automated detection against an isolated ground truth benchmark without data leakage.

4. **Enterprise SaaS Dashboard (`ColdChain OS`)**:
   - Dark-themed executive control tower built in Streamlit & Plotly.
   - 5 integrated views: Control Tower Overview, Temperature Telemetry, Shipment Traceability, Deviation Management, and Compliance Dossiers.
   - Sub-second view navigation powered by indexed SQLite telemetry lazy loading (`idx_tr_shipment`).
   - Official printable GxP Certificates with strict contrast typography and SHA-256 digital sign-off.

---

## 🏗️ 3. Architecture & Data Flow

```mermaid
flowchart TD
    subgraph MasterData ["Master Data Layer"]
        PRD["Products (15)"]
        PKG["Packaging Systems (8)"]
        POL["Threshold Policies (20)"]
        LOT["Manufactured Lots (50)"]
        LOG["Calibrated Loggers (1,000)"]
    end

    subgraph Generator ["Synthetic Data Engine (Seed: 20261022)"]
        GEN["Deterministic Generator<br/>(NumPy / Pandas)"]
        GT["Isolated Ground Truth<br/>(160 Controlled Anomalies)"]
    end

    subgraph Transactions ["Operational Transaction Tables"]
        SHP["Shipments (5,000)"]
        RTE["Route Stops (15,000)"]
        CUS["Custody Events (15,000)"]
        TEL["Temperature Readings (724,838)<br/>10-minute telemetry pings"]
    end

    subgraph ComplianceEngine ["GxP Compliance & Deviation Engine"]
        MKT["Haynes-Arrhenius MKT Engine<br/>(ΔH = 83.144 kJ/mol)"]
        EXC["Contiguous Excursion Calculator<br/>(Duration vs Allowed Tolerance)"]
        GAP["Telemetry Gap Detector (>25 min)"]
        CH["Custody Chain Verifier (Signatures & Gaps)"]
    end

    subgraph DatabaseLayer ["Relational Storage Layer"]
        SQL[("coldchain.db<br/>(SQLite / PostgreSQL)")<br/>ANSI SQL DDL with PK/FK/Indexes]
    end

    subgraph UI ["ColdChain OS — SaaS Control Tower"]
        V1["📊 Executive Overview (KPIs & Charts)"]
        V2["🌡️ Temperature Telemetry & Excursions"]
        V3["🚚 Shipment Traceability & Custody"]
        V4["⚠️ Deviation Management & QA Disposition"]
        V5["📋 GxP Regulatory Compliance Dossier"]
    end

    MasterData --> GEN
    GEN --> Transactions
    GEN --> GT
    Transactions --> DatabaseLayer
    Transactions --> ComplianceEngine
    ComplianceEngine --> DatabaseLayer
    DatabaseLayer --> UI
```

---

## 📊 4. Database Schema & Data Dictionary

The relational model consists of **10 normalized tables** categorized into Master, Transactional, and Reporting entities.

| # | Entity Name | Table Type | Primary Key | Foreign Keys / Relationships | Record Count |
| :---: | :--- | :---: | :--- | :--- | :---: |
| 1 | `products` | Master | `product_id` | Master catalog of pharmaceutical vaccines & biologics | 15 |
| 2 | `packaging` | Master | `packaging_id` | Certified thermal shippers with rated insulation durations | 8 |
| 3 | `threshold_policies` | Master | `policy_id` | References `products.product_id` (1:N) | 20 |
| 4 | `lots` | Master | `lot_id` | References `products.product_id` (N:1) | 50 |
| 5 | `loggers` | Master | `logger_id` | Digital NIST-calibrated dataloggers | 1,000 |
| 6 | `shipments` | Transaction | `shipment_id` | References `lots.lot_id`, `packaging.packaging_id`, `loggers.logger_id` | 5,000 |
| 7 | `route_stops` | Transaction | `stop_id` | References `shipments.shipment_id` (N:1) | 15,000 |
| 8 | `custody_events` | Transaction | `custody_id` | References `shipments.shipment_id` (N:1) | 15,000 |
| 9 | `temperature_readings` | Transaction | `reading_id` | References `loggers.logger_id`, `shipments.shipment_id` | 724,838 |
| 10 | `excursion_reports` | Report | `excursion_id` | References `shipments.shipment_id`, `loggers.logger_id` | 825 |

### Comprehensive Schema Artifacts
* **Markdown Data Dictionary:** [`documentation/data_dictionary.md`](documentation/data_dictionary.md)
* **Formatted Excel Spreadsheet:** [`documentation/data_dictionary.xlsx`](documentation/data_dictionary.xlsx)
* **Entity-Relationship Specification:** [`documentation/entity_relationship_diagram.md`](documentation/entity_relationship_diagram.md)
* **High-Resolution ERD Image:** [`documentation/er_diagram.png`](documentation/er_diagram.png)

---

## 🧪 5. Controlled Anomaly Scenarios & Detection Benchmark

To validate the compliance engine against ground truth, 5 realistic cold-chain failure modes were injected into the data generator:

1. **EC-01: Unassigned / Unactivated Logger (`UNASSIGNED_LOGGER`)**:
   - Shipment dispatched without an active datalogger. Generates zero telemetry pings.
   - *Detection Rule:* Total readings $= 0$. Flagged as `INVESTIGATION`.
2. **EC-02: Sustained High Temperature Excursion (`HIGH_TEMP`)**:
   - Product exceeds upper threshold ($T > 8^\circ\text{C}$) for longer than allowed tolerance (e.g. 45 min vs 30 min allowed).
   - *Detection Rule:* Contiguous duration calculation exceeding policy limit. Flagged as `NON_COMPLIANT`.
3. **EC-03: Cumulative Low Temperature / Freezing Breaches (`LOW_TEMP`)**:
   - Temperature drops below lower bound ($T < 2^\circ\text{C}$ or freezing $T \le 0^\circ\text{C}$).
   - *Detection Rule:* Immediate critical violation for freeze-sensitive vaccines. Flagged as `NON_COMPLIANT`.
4. **EC-04: Sensor Blackout / Silent Telemetry Gaps (`MISSING_DATA`)**:
   - Physical logger failure or battery loss causing intervals $> 25\text{ minutes}$ between expected 10-minute pings.
   - *Detection Rule:* Consecutive reading timestamp delta $\Delta t > 25\text{ min}$. Flagged as `INVESTIGATION`.
5. **EC-05: Unsigned or Unverified Custody Handoff (`CUSTODY_GAP`)**:
   - Carrier handover occurred without an authorized recipient signature or with unexplained transit delay.
   - *Detection Rule:* `signature_obtained == 0` or handover interval $> 60\text{ min}$. Flagged as `INVESTIGATION`.

### Benchmark Results (Evaluated Against Isolated Ground Truth)

| Scenario Code | Failure Description | Injected Count | Detected Count | Recall Rate | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`UNASSIGNED_LOGGER`** | Dispatched without datalogger | 50 | 50 | **100.0%** | PASSED |
| **`HIGH_TEMP` / `POLICY_MISMATCH`** | Thermal excursion exceeding policy tolerance | 30 | 30 | **100.0%** | PASSED |
| **`MISSING_DATA`** | Sensor blackout gap (>25 min) | 40 | 38 | **95.0%** | PASSED |
| **`CUSTODY_GAP`** | Missing legal transfer signature | 25 | 25 | **100.0%** | PASSED |
| **`CROSS_SHIPMENT_EXCURSION`** | Telemetry isolation & boundary check | 15 | 15 | **100.0%** | PASSED |
| **OVERALL BENCHMARK** | **Total Injected Controlled Anomalies** | **160** | **158** | **98.8%** | **EXCELLENT** |

---

## 📐 6. Mathematical Foundations: Mean Kinetic Temperature (MKT)

In life sciences, arithmetic average temperature is scientifically invalid because degradation reactions follow an exponential Arrhenius relationship. The platform derives MKT using the **Haynes-Arrhenius equation** recommended by USP \<1079\> and WHO:

$$T_K = \frac{\frac{\Delta H}{R}}{-\ln\left(\frac{1}{n}\sum_{i=1}^{n} e^{-\frac{\Delta H}{R \cdot T_i}}\right)}$$

$$MKT (^\circ\text{C}) = T_K - 273.15$$

Where:
* $\Delta H = 83.144\text{ kJ/mol}$ (Standard activation energy for biopharmaceutical stability)
* $R = 8.314472\text{ J/(mol}\cdot\text{K)}$ (Universal gas constant)
* $T_i$ is the recorded absolute temperature in Kelvin ($T_i = t_i + 273.15$)
* $n$ is the total count of timestamped readings

This non-linear formulation correctly penalizes even brief spikes at high temperatures, providing defensible evidence during GxP regulatory audits.

---

## 🖥️ 7. ColdChain OS Dashboard Tour

The platform includes an enterprise dark-theme control tower accessible via any web browser:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ ❄️ ColdChain OS | GxP Control Tower                                               │
├────────────────────┬─────────────────────────────────────────────────────────────┤
│ 📋 MAIN NAVIGATION │ 1. 📊 Executive Control Tower Overview                      │
│ • Control Tower    │    - Active Fleet KPIs (Total, Compliant, Deviations)       │
│ • Telemetry        │    - Carrier Compliance Bar Chart & Fleet Donut Breakdown   │
│ • Traceability     │    - Deviation Severity Breakdown (Minor, Major, Critical)  │
│ • Exceptions       ├─────────────────────────────────────────────────────────────┤
│ • Reports          │ 2. 🌡️ Temperature Telemetry & Excursions                     │
│                    │    - Interactive Plotly Time-Series with Permitted Zones    │
│ 🔍 GLOBAL SEARCH   │    - Contiguous Excursion Shading & Telemetry Gap Bands     │
│ [SHP-2026-000004]  │    - MKT, Min, Max, Arithmetic Mean Summary Metrics         │
│                    ├─────────────────────────────────────────────────────────────┤
│ ⚙️ FILTERS SCOPE   │ 3. 🚚 Shipment Traceability & Custody Chain                 │
│ [x] Compliant      │    - Visual 3-Stage Shipment Stepper (Origin -> Cross-Dock) │
│ [x] Investigation  │    - Transit Waypoint Dwell Logs & Handover Signature Table │
│                    ├─────────────────────────────────────────────────────────────┤
│ ℹ️ QUALITY MANIFEST│ 4. ⚠️ Deviation Management & QA Disposition                  │
│ Total: 5,000       │    - Filterable Incident Dossiers (Severity, Root Cause)    │
│ Pings: 724,838     │    - Electronic Sign-off: ACCEPT, REJECT, or QUARANTINE     │
│ Status: 0 Violat.  ├─────────────────────────────────────────────────────────────┤
│                    │ 5. 📋 GxP Regulatory Compliance Dossier                     │
│                    │    - Official Printable Certificate of Compliance           │
│                    │    - High-contrast white parchment card with SHA256 Hash   │
│                    │    - One-click CSV & JSON Dossier Exports                   │
└────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 🚀 8. Quick Start & Execution Guide

### 1. Prerequisites & Environment Setup
Clone the repository and ensure Python 3.10+ is installed:
```powershell
git clone https://github.com/krishpatel-dev/YottaFlex.ai.git
cd YottaFlex.ai
pip install -r requirements.txt
```

### 2. Generate the Deterministic Dataset
Generate the entire 10-table relational dataset using fixed seed `20261022`:
```powershell
python src/data_generator.py --seed 20261022 --shipments 5000 --checksums
```
*(Executes in ~12 seconds. Outputs all CSVs into `data/master/` and `data/transactions/`).*

### 3. Run the Compliance Adjudication Engine
Compute MKT, detect contiguous excursions, assess gaps, and produce compliance summaries:
```powershell
python src/compliance_engine.py
```
*(Produces `reports/compliance_summary.csv` and `data/reports/excursion_reports.csv`).*

### 4. Benchmark Negative Scenarios
Evaluate detection precision and recall against the isolated ground truth:
```powershell
python src/exception_detector.py
```

### 5. Run Relational Integrity Validator
Audit primary keys, foreign keys, categorical enums, dates, and telemetry counts:
```powershell
python src/validator.py
```
*(Verifies 0 relational or chronological violations across all tables).*

### 6. Run Automated Pytest Suite
```powershell
python -m pytest tests/test_validation.py -v
```
*(Runs 5 unit and regression tests confirming DDL, MKT, integrity, and negative scenarios).*

### 7. Initialize Database (SQLite / PostgreSQL)
Load the normalized tables into local SQLite (`database/coldchain.db`) or PostgreSQL:
```powershell
# Local SQLite (zero-setup)
python database/load_database.py

# Or PostgreSQL
python database/load_database.py --db-url postgresql://postgres:password@localhost:5432/coldchain_db
```

### 8. Launch the Streamlit Control Tower
```powershell
python -m streamlit run dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 9. Exploratory Data Analysis Notebook
To explore data distributions, MKT sensitivity curves, and carrier comparisons interactively:
```powershell
jupyter notebook notebooks/cold_chain_analysis.ipynb
```

---

## 📂 9. Project Directory Tree

```
YottaFlex.ai/
│
├── .github/
│   └── workflows/
│       └── ci.yml                       # Automated GitHub Actions CI workflow
│
├── data/
│   ├── master/                          # Master Catalog Tables
│   │   ├── products.csv                 # 15 regulated pharmaceutical products
│   │   ├── packaging.csv                # 8 certified thermal shipper specifications
│   │   ├── threshold_policies.csv       # 20 product-specific temperature policies
│   │   ├── lots.csv                     # 50 manufactured pharmaceutical batches
│   │   └── loggers.csv                  # 1,000 calibrated digital dataloggers
│   ├── transactions/                    # Operational Transaction Tables
│   │   ├── shipments.csv                # 5,000 shipment dispatch and arrival missions
│   │   ├── route_stops.csv              # 15,000 origin, cross-dock, and destination waypoints
│   │   ├── custody_events.csv           # 15,000 legal custody transfers with digital signatures
│   │   └── temperature_readings.csv     # 724,838 10-minute continuous telemetry readings
│   ├── reports/
│   │   └── excursion_reports.csv        # 825 logged quality deviation dossiers
│   └── ground_truth/
│       └── ground_truth.csv             # Isolated benchmark controls (160 injected anomalies)
│
├── database/
│   ├── schema.sql                       # ANSI SQL DDL (PostgreSQL & SQLite compatible)
│   ├── seed.sql                         # Database seed records for master tables
│   ├── load_database.py                 # Automated relational loader (SQLite & PostgreSQL)
│   └── create_seed_sql.py               # Seed creation utility
│
├── src/
│   ├── data_generator.py                # Deterministic synthetic data generator (Seed: 20261022)
│   ├── business_rules.py                # Haynes-Arrhenius MKT, contiguous excursions, gap logic
│   ├── compliance_engine.py             # Full fleet adjudication engine producing scorecards
│   ├── exception_detector.py            # Benchmark detector evaluating against ground truth
│   └── validator.py                     # Relational integrity auditor (PK/FK/Enum/Chronology)
│
├── dashboard/
│   └── app.py                           # Enterprise SaaS Control Tower Dashboard (Streamlit & Plotly)
│
├── reports/
│   ├── compliance_summary.csv           # 5,000-shipment compliance audit scorecard
│   └── validation_summary.json          # Anomaly detection recall and precision benchmark
│
├── tests/
│   └── test_validation.py               # Automated Pytest suite (DDL, MKT, rules, edge cases)
│
├── notebooks/
│   └── cold_chain_analysis.ipynb        # Exploratory Data Analysis & visual analytics
│
├── documentation/
│   ├── data_dictionary.md               # Markdown schema documentation for all 10 entities
│   ├── data_dictionary.xlsx             # Formatted multi-tab Excel data dictionary spreadsheet
│   ├── entity_relationship_diagram.md   # Mermaid ER diagram & cardinality documentation
│   ├── er_diagram.png                   # High-resolution architectural ER diagram image
│   ├── project_documentation.md         # Comprehensive system & domain documentation
│   └── prompt_history.md                # Full transparent AI prompt disclosure log (Entries 1.1-3.11)
│
├── requirements.txt                     # Pinned project dependencies
└── README.md                            # Main project documentation & guide
```

---

## 🔒 10. Verification of Deterministic Reproducibility

Generating the dataset with `--seed 20261022` yields identical row counts and byte-matching MD5 checksums:

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

## 📜 11. Regulatory Compliance Standards & AI Disclosure

* **USP \<1079\>**: Good Storage and Distribution Practices for Drug Products.
* **WHO Technical Report Series, No. 961, Annex 9**: Model guidance for the storage and transport of time- and temperature-sensitive pharmaceutical products.
* **FDA 21 CFR Part 11**: Electronic Records and Signatures audit trail integrity.
* **Transparent AI Disclosure**: Per project submission requirements, every prompt provided by the candidate, along with actions taken and architectural decisions made, is transparently documented in [`documentation/prompt_history.md`](documentation/prompt_history.md).

---

## 👤 Author & Support
* **Candidate:** Krish Patel
* **GitHub Profile:** [@krishpatel-dev](https://github.com/krishpatel-dev)
* **Project Repository:** [https://github.com/krishpatel-dev/YottaFlex.ai](https://github.com/krishpatel-dev/YottaFlex.ai)
