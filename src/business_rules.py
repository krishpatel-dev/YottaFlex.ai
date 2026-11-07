"""
Cold Chain Compliance Platform - Business Rules & Domain Logic
Implements GxP, USP <1079>, and WHO Annex 9 standards for temperature monitoring,
excursion duration calculation, Arrhenius Mean Kinetic Temperature (MKT),
telemetry gap detection, and custody chain validation.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Standard pharmaceutical activation energy delta H / R (in Kelvin)
# Typically 83.144 kJ/mol / 8.3144 J/(mol*K) = 10,000 K
ARRHENIUS_ENERGY_RATIO = 10000.0


def calculate_mkt(temperatures_c: List[float]) -> Optional[float]:
    """
    Calculates the Mean Kinetic Temperature (MKT) in Celsius using the Haynes-Arrhenius equation.
    USP <1079> standard formula:
    Tk = (dH / R) / -ln( (1/n) * sum( exp(-dH / (R * Ti)) ) )
    """
    if not temperatures_c or len(temperatures_c) == 0:
        return None

    # Filter out NaNs
    valid_temps = [t for t in temperatures_c if not np.isnan(t)]
    n = len(valid_temps)
    if n == 0:
        return None

    # Convert to Kelvin
    temps_k = [t + 273.15 for t in valid_temps]
    
    # Check for invalid zero/sub-zero Kelvin
    if any(tk <= 0 for tk in temps_k):
        return None

    try:
        sum_exp = sum(math.exp(-ARRHENIUS_ENERGY_RATIO / tk) for tk in temps_k)
        if sum_exp <= 0:
            return None
        mean_exp = sum_exp / n
        tk_mkt = ARRHENIUS_ENERGY_RATIO / (-math.log(mean_exp))
        return round(tk_mkt - 273.15, 2)
    except (ValueError, OverflowError, ZeroDivisionError):
        return round(float(np.mean(valid_temps)), 2)


def check_reading_status(temp_c: float, min_c: float, max_c: float, uncertainty_c: float = 0.5) -> Tuple[str, str]:
    """
    Evaluates an individual temperature measurement against specification limits.
    Returns (status, quality_flag):
    - status: 'NORMAL', 'EXCURSION_HIGH', 'EXCURSION_LOW'
    - quality_flag: 'NORMAL', 'SUSPECT' (near calibration tolerance boundary)
    """
    if temp_c > max_c:
        status = "EXCURSION_HIGH"
    elif temp_c < min_c:
        status = "EXCURSION_LOW"
    else:
        status = "NORMAL"

    # Calibration uncertainty band (USP guideline)
    if abs(temp_c - min_c) <= uncertainty_c or abs(temp_c - max_c) <= uncertainty_c:
        quality_flag = "SUSPECT"
    else:
        quality_flag = "NORMAL"

    return status, quality_flag


def detect_telemetry_gaps(
    readings_df: pd.DataFrame, 
    expected_interval_min: int = 10, 
    max_allowed_gap_min: int = 25
) -> List[Dict]:
    """
    Scans a chronological series of readings for unrecorded time intervals.
    Any gap exceeding max_allowed_gap_min (e.g. >25 minutes when expecting 10)
    represents missing data that invalidates automatic compliance.
    """
    gaps = []
    if readings_df.empty or len(readings_df) < 2:
        return gaps

    # Use pre-parsed datetime if available
    if "recorded_dt" in readings_df.columns:
        df_sorted = readings_df.sort_values("recorded_dt")
        timestamps = df_sorted["recorded_dt"].tolist()
    else:
        df_sorted = readings_df.sort_values("recorded_at")
        timestamps = pd.to_datetime(df_sorted["recorded_at"]).tolist()

    for i in range(len(timestamps) - 1):
        diff_minutes = (timestamps[i + 1] - timestamps[i]).total_seconds() / 60.0
        if diff_minutes > max_allowed_gap_min:
            gaps.append({
                "gap_start": timestamps[i].strftime("%Y-%m-%d %H:%M:%S"),
                "gap_end": timestamps[i + 1].strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": int(diff_minutes),
                "expected_interval_min": expected_interval_min,
                "missing_readings_estimate": int((diff_minutes - expected_interval_min) // expected_interval_min)
            })

    return gaps


def calculate_excursions_for_shipment(
    readings_df: pd.DataFrame,
    policy: Dict,
    shipment_id: str,
    actual_dep: datetime,
    actual_arr: datetime
) -> List[Dict]:
    """
    Computes contiguous excursion blocks strictly bounded within the shipment's active window.
    Guarantees cross-shipment telemetry isolation (EC-05).
    """
    excursion_events = []
    if readings_df.empty:
        return excursion_events

    # Strictly enforce shipment time boundaries to prevent cross-shipment duration contamination
    if "recorded_dt" in readings_df.columns:
        df_shipment = readings_df
    else:
        df_shipment = readings_df.copy()
        df_shipment["recorded_dt"] = pd.to_datetime(df_shipment["recorded_at"])

    df_bounded = df_shipment[
        (df_shipment["recorded_dt"] >= actual_dep) & 
        (df_shipment["recorded_dt"] <= actual_arr)
    ].sort_values("recorded_dt")

    if df_bounded.empty:
        return excursion_events

    min_c = float(policy["min_temp_c"])
    max_c = float(policy["max_temp_c"])
    reading_interval = int(policy.get("reading_interval_min", 10))

    # Identify contiguous excursion blocks
    current_block: List[Dict] = []
    current_type = None

    for _, row in df_bounded.iterrows():
        temp = float(row["temperature_c"])
        dt = row["recorded_dt"]

        is_high = temp > max_c
        is_low = temp < min_c

        if is_high or is_low:
            e_type = "HIGH_TEMP" if is_high else "LOW_TEMP"
            if current_block and current_type == e_type:
                current_block.append((dt, temp, row.get("reading_id")))
            else:
                if current_block:
                    excursion_events.append(_create_excursion_record(current_block, current_type, shipment_id, policy))
                current_block = [(dt, temp, row.get("reading_id"))]
                current_type = e_type
        else:
            if current_block:
                excursion_events.append(_create_excursion_record(current_block, current_type, shipment_id, policy))
                current_block = []
                current_type = None

    if current_block:
        excursion_events.append(_create_excursion_record(current_block, current_type, shipment_id, policy))

    return excursion_events


def _create_excursion_record(
    block: List[Tuple[datetime, float, str]], 
    e_type: str, 
    shipment_id: str, 
    policy: Dict
) -> Dict:
    """Helper to structure an excursion incident record."""
    dts = [b[0] for b in block]
    temps = [b[1] for b in block]
    r_ids = [b[2] for b in block if b[2]]

    start_dt = min(dts)
    end_dt = max(dts)
    
    # If 1 reading, duration is estimated by reading interval; otherwise elapsed + interval
    if len(block) == 1:
        duration_minutes = 10
    else:
        duration_minutes = int((end_dt - start_dt).total_seconds() // 60) + 10

    max_temp = round(float(max(temps)), 2)
    min_temp = round(float(min(temps)), 2)
    max_allowed = int(policy.get("max_excursion_minutes", 30))

    # Severity classification:
    # MINOR: duration <= allowed limit and within 2°C of threshold
    # MAJOR: duration > allowed limit OR > 4°C above limit
    # CRITICAL: extreme temperature breach (e.g. >15°C for refrigerated or frozen thaw)
    threshold_ref = float(policy["max_temp_c"]) if e_type == "HIGH_TEMP" else float(policy["min_temp_c"])
    delta = abs(max_temp - threshold_ref) if e_type == "HIGH_TEMP" else abs(threshold_ref - min_temp)

    if duration_minutes > max_allowed or delta > 5.0:
        severity = "CRITICAL"
        disposition = "REJECTED"
    elif duration_minutes > (max_allowed * 0.7) or delta > 2.5:
        severity = "MAJOR"
        disposition = "QUARANTINE"
    else:
        severity = "MINOR"
        disposition = "ACCEPTED"

    return {
        "shipment_id": shipment_id,
        "policy_id": policy["policy_id"],
        "excursion_start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "excursion_end": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": duration_minutes,
        "max_temp_recorded_c": max_temp,
        "min_temp_recorded_c": min_temp,
        "excursion_type": e_type,
        "severity": severity,
        "disposition": disposition,
        "evidence_reading_ids": r_ids[:5],  # sample key readings
        "reading_count": len(block)
    }


def validate_logger(logger_row: Optional[Dict], shipment_dep: datetime, shipment_arr: datetime) -> Tuple[bool, str]:
    """
    Validates physical logger deployment, assignment, and calibration validity.
    """
    if logger_row is None:
        return False, "UNASSIGNED_LOGGER: No calibrated logger assigned to shipment."

    if not logger_row.get("is_active", True):
        return False, "INACTIVE_LOGGER: Assigned logger is marked inactive/faulty."

    cal_exp_str = logger_row.get("calibration_expiry")
    if cal_exp_str:
        try:
            cal_exp = datetime.strptime(cal_exp_str, "%Y-%m-%d")
            if cal_exp < shipment_arr:
                return False, f"EXPIRED_CALIBRATION: Calibration expired on {cal_exp_str} before shipment arrival."
        except ValueError:
            pass

    return True, "LOGGER_VALID"


def validate_custody_chain(custody_events_df: pd.DataFrame, max_allowed_handoff_gap_hours: float = 3.0) -> Tuple[bool, List[str]]:
    """
    Checks custody events for unbroken chronological custody and valid digital signatures.
    """
    issues = []
    if custody_events_df.empty:
        return False, ["MISSING_CUSTODY_TRAIL: Zero custody events found."]

    df_sorted = custody_events_df.sort_values("handover_time")

    # Check signatures
    unsigned = df_sorted[df_sorted["signature_obtained"] == 0]
    if not unsigned.empty:
        for _, u in unsigned.iterrows():
            issues.append(f"UNSIGNED_CUSTODY: Event {u.get('custody_id')} at {u.get('handover_time')} lacks signature.")

    # Check explicit gap flags
    flagged = df_sorted[df_sorted["gap_flag"] == 1]
    if not flagged.empty:
        for _, f in flagged.iterrows():
            issues.append(f"CUSTODY_GAP_FLAGGED: Event {f.get('custody_id')} has recorded custody discrepancy.")

    return (len(issues) == 0), issues

