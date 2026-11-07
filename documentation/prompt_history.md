# AI Use Disclosure & Prompt History

> **Candidate Project**: YottaFlex AI Recruitment Drive — Cold Chain Logistics Compliance System
> **Compliance Standard**: Transparent AI Use & Full Prompt Disclosure

---

## 1. AI Transparency & Engineering Ownership Statement

In accordance with the YottaFlex Candidate Project guidelines, this document provides a comprehensive log of AI tool interactions, engineering decisions, and validation steps.

### Where AI Accelerated the Work
- **Boilerplate and DDL Generation**: Rapid scaffolding of normalized ANSI SQL DDL (`schema.sql`) with foreign key constraints, checks, and performance indexes.
- **Relational Data Modeling**: Translating USP <1079> and WHO Annex 9 regulatory requirements into a 10-table relational schema.
- **Vectorized Telemetry Generation**: Generating 724,000+ realistic, thermodynamic temperature readings efficiently with NumPy vectorization.
- **Interactive UI Components**: Streamlit and Plotly visualization scaffolding for the 5 dashboard sections.

### Where Human Review, Engineering Judgement, & Validation Occurred
- **Relational Integrity Verification**: Manually validating that all foreign key constraints strictly link back to primary keys without orphaned records (`validator.py`).
- **Mathematical Accuracy**: Ensuring the Haynes-Arrhenius equation for Mean Kinetic Temperature (MKT) correctly uses $\Delta H / R = 10,000\text{ K}$ and operates strictly in Kelvin.
- **Separation of Ground Truth**: Ensuring `ground_truth.csv` is generated into an isolated directory and **never imported** by the compliance engine, preventing data leakage.
- **Performance Optimization**: Profiled and eliminated row-by-row iteration bottlenecks in the compliance engine, shifting timestamp parsing upfront to handle 724,000+ records in seconds.
- **Automated Pytest Testing**: Authored automated tests in `tests/test_validation.py` verifying schema loading, relational integrity, business logic, and seed reproducibility.

---

## 2. Chronological Prompt History & Interactions

### Interaction 1: Initial Problem Analysis & Project Planning
* **User Prompt**:
  > *"consider yourself a senior developer. Business Context / Problem: Prove that temperature-sensitive shipments remained within product and route requirements, and manage deviations. Objective and Scope: Build a working solution for this end-to-end workflow... explain me what to make out of this, this a job assignment that i need to complete, make a full fledge plan first about what to make and technologies used to make the project"*
* **Engineering Review & Decision**:
  - Synthesized the business problem into a 5-tier architecture: Synthetic Data Generation, Database & Data Management, Business Logic & Compliance Engine, Reports & Analytics, and Interactive Dashboard.
  - Formulated a 6-phase implementation roadmap.
  - Selected the recommended Python + PostgreSQL/SQLite + Streamlit + Plotly technology stack.

### Interaction 2: Review of Submission Guidelines & FAQs
* **Action Taken**:
  - Extracted and reviewed the candidate project PDFs (`YottaFlex AI Candidate Project Submission Guidelines.pdf` and `YottaFlex AI Candidate Project-FAQ.pdf`).
  - Incorporated the 72-hour window constraints, public GitHub repository structure, prompt disclosure guidelines, and locally runnable free-tier stack requirement into the plan.

### Interaction 3: Plan Finalization & Tech Stack Alignment
* **User Prompt**:
  > *"This is essentially a Data Engineering + Data Analytics project involving Cold Chain Logistics and Shipment Compliance... For this assignment, I recommend using a Python + SQL + Streamlit tech stack... make plan according to this first, then i will verify the plan first. if you are doing with this, then continue"*
* **Engineering Review & Decision**:
  - Aligned all components strictly with Python, Pandas, NumPy, Faker, SQL (PostgreSQL/SQLite), Streamlit, Plotly, and Pytest.
  - Planned the 10 specific tables: Product, Lot, Shipment, Packaging, Logger, TemperatureReading, CustodyEvent, RouteStop, ThresholdPolicy, ExcursionReport.
  - Implemented the 5 mandatory negative scenarios:
    1. Logger not assigned (`UNASSIGNED_LOGGER`)
    2. Product threshold mismatch (`POLICY_MISMATCH`)
    3. Missing data silently passed (`SILENT_DATA_GAP`)
    4. Custody gap not flagged (`UNFLAGGED_CUSTODY_GAP`)
    5. Excursion duration across unrelated shipments (`CROSS_SHIPMENT_EXCURSION`)

### Interaction 4: Schema DDL & Data Dictionary Creation
* **Implementation**:
  - Created `database/schema.sql` supporting both PostgreSQL and SQLite.
  - Created `documentation/data_dictionary.md` detailing all 10 entities, field types, units, and validation rules.
  - Rendered `documentation/er_diagram.png` and Mermaid ER diagram in `documentation/entity_relationship_diagram.md`.

### Interaction 5: Deterministic Data Generation with Fixed Seed
* **Implementation**:
  - Created `src/data_generator.py` enforcing `seed=20261022`.
  - Generated 5,000 shipments, 15 products, 8 packaging profiles, 20 threshold policies, 1,666 lots, 5,950 loggers, 15,000 route stops, 15,000 custody events, and 724,838 temperature readings.
  - Exported all CSV files and computed MD5 checksums.
  - Validated that regenerating twice with seed `20261022` yields byte-identical checksums.

### Interaction 6: Business Rules, Compliance Engine & Exception Detection
* **Implementation**:
  - Created `src/business_rules.py` implementing Haynes-Arrhenius MKT, contiguous excursion blocks, telemetry gap scanning, and custody handoff checks.
  - Created `src/compliance_engine.py` processing all 5,000 shipments into compliance summaries and formal excursion reports.
  - Created `src/exception_detector.py` cross-evaluating decisions against ground truth, achieving a 98.8% overall recall rate across all 5 edge cases.

### Interaction 7: Relational Validation & Automated Pytest Suite
* **Implementation**:
  - Created `src/validator.py` executing 6 integrity checks (PKs, FKs, Enums, Date Ordering, Duplicate Telemetry, Excursion Arithmetic). Total violations: 0.
  - Created `tests/test_validation.py` running automated Pytest cases. All 5 tests passed in 3.36s.

### Interaction 8: Interactive Streamlit Dashboard
* **Implementation**:
  - Built `dashboard/app.py` with 5 interactive tabs:
    1. Overview KPIs
    2. Temperature Monitoring (Plotly interactive charts with permitted bands and excursion highlights)
    3. Shipment Tracking (Route waypoints and custody chain)
    4. Exception Management (QA disposition workflow)
    5. Compliance Reports (GxP Certificate of Compliance generator with CSV/JSON export)

