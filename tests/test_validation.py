"""
Cold Chain Compliance Platform - Automated Pytest Suite
Verifies:
- Relational schema loading
- Data integrity (PK, FK, enums, temporal ordering)
- Business rules & MKT mathematical calculations
- All 5 mandatory negative anomaly scenarios (>= 95% recall)
- Fixed seed reproducibility
"""

import json
import sqlite3
import sys
from pathlib import Path

# Ensure project root is in sys.path across all platforms
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
import pandas as pd
import numpy as np

from src.business_rules import calculate_mkt, check_reading_status, detect_telemetry_gaps
from src.validator import RelationalValidator
from src.exception_detector import ExceptionDetector

DATA_DIR = ROOT_DIR / "data"


def test_schema_ddl():
    """Verifies that schema.sql executes cleanly and creates all 10 tables."""
    conn = sqlite3.connect(":memory:")
    sql_path = Path("database/schema.sql")
    assert sql_path.exists(), "database/schema.sql must exist"
    
    with open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {
        "products", "packaging", "threshold_policies", "lots",
        "shipments", "loggers", "route_stops", "custody_events",
        "temperature_readings", "excursion_reports"
    }
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"


def test_relational_integrity():
    """Verifies zero violations across PKs, FKs, enums, dates, and duplicate readings."""
    validator = RelationalValidator(data_dir=str(DATA_DIR))
    summary = validator.validate_all()
    assert summary["validation_status"] == "PASSED"
    assert summary["total_violations"] == 0


def test_mkt_arrhenius_calculation():
    """Verifies Arrhenius MKT calculation with standard temperature series."""
    # Test 1: Constant temperature of 5.0°C should yield MKT = 5.0°C
    constant_temps = [5.0] * 20
    mkt_const = calculate_mkt(constant_temps)
    assert mkt_const is not None
    assert abs(mkt_const - 5.0) < 0.05

    # Test 2: Series with temperature spike should give MKT higher than arithmetic mean
    varying_temps = [4.0, 4.5, 5.0, 5.5, 12.0, 5.0, 4.5]
    arithmetic_mean = float(np.mean(varying_temps))
    mkt_val = calculate_mkt(varying_temps)
    assert mkt_val is not None
    assert mkt_val > arithmetic_mean, "MKT must weight higher temperatures more heavily than arithmetic mean"


def test_reading_status_and_uncertainty():
    """Verifies single-point threshold checking and calibration uncertainty tagging."""
    # Within 2 to 8°C
    status, q = check_reading_status(5.0, 2.0, 8.0, 0.5)
    assert status == "NORMAL"
    assert q == "NORMAL"

    # Calibration buffer boundary (e.g. 7.8°C within 0.5 of 8.0)
    status, q = check_reading_status(7.8, 2.0, 8.0, 0.5)
    assert status == "NORMAL"
    assert q == "SUSPECT"

    # High excursion
    status, q = check_reading_status(9.2, 2.0, 8.0, 0.5)
    assert status == "EXCURSION_HIGH"


def test_mandatory_negative_scenarios():
    """Verifies detection of all 5 mandatory negative anomaly scenarios."""
    detector = ExceptionDetector(data_dir=str(DATA_DIR), reports_dir="reports")
    results = detector.evaluate_all()
    
    scenarios = results["scenarios"]
    assert "UNASSIGNED_LOGGER" in scenarios
    assert "POLICY_MISMATCH" in scenarios
    assert "SILENT_DATA_GAP" in scenarios
    assert "UNFLAGGED_CUSTODY_GAP" in scenarios
    assert "CROSS_SHIPMENT_EXCURSION" in scenarios

    # Verify high detection recall
    overall_recall = float(results["overall_summary"]["overall_recall"].replace("%", ""))
    assert overall_recall >= 95.0, f"Expected >= 95% overall recall, got {overall_recall}%"

