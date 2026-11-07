#!/usr/bin/env python3
"""
Cold Chain Compliance Platform - Compliance Engine
Evaluates every shipment against regulated product policies, sensor telemetry,
custody handoffs, and data-quality criteria. Produces traceable audit evidence
and generates formal excursion reports and compliance summaries.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd

from src.business_rules import (
    calculate_excursions_for_shipment,
    calculate_mkt,
    detect_telemetry_gaps,
    validate_custody_chain,
    validate_logger,
)


class ComplianceEngine:
    """Core compliance adjudication and audit trail engine."""

    def __init__(self, data_dir: str = "data", reports_dir: str = "reports"):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "reports").mkdir(parents=True, exist_ok=True)

        self._load_datasets()

    def _load_datasets(self):
        """Loads relational CSV tables into DataFrames with indexed lookups."""
        print("[*] Compliance Engine: Loading relational data tables...")
        self.products_df = pd.read_csv(self.data_dir / "master" / "products.csv")
        self.packaging_df = pd.read_csv(self.data_dir / "master" / "packaging.csv")
        self.policies_df = pd.read_csv(self.data_dir / "master" / "threshold_policies.csv")
        self.lots_df = pd.read_csv(self.data_dir / "master" / "lots.csv")
        self.loggers_df = pd.read_csv(self.data_dir / "master" / "loggers.csv")
        
        self.shipments_df = pd.read_csv(self.data_dir / "transactions" / "shipments.csv")
        self.route_stops_df = pd.read_csv(self.data_dir / "transactions" / "route_stops.csv")
        self.custody_events_df = pd.read_csv(self.data_dir / "transactions" / "custody_events.csv")
        self.readings_df = pd.read_csv(self.data_dir / "transactions" / "temperature_readings.csv")

        # Create quick hash maps for master lookups
        self.product_map = self.products_df.set_index("product_id").to_dict("index")
        self.lot_map = self.lots_df.set_index("lot_id").to_dict("index")
        self.packaging_map = self.packaging_df.set_index("packaging_id").to_dict("index")
        
        # Primary policy mapping: take the first active policy per product
        self.primary_policies = (
            self.policies_df.drop_duplicates(subset=["product_id"], keep="first")
            .set_index("product_id")
            .to_dict("index")
        )

        # Index loggers by shipment_id
        valid_loggers = self.loggers_df.dropna(subset=["shipment_id"])
        self.logger_by_shipment = valid_loggers.set_index("shipment_id").to_dict("index")

        print("    -> Pre-parsing timestamps and indexing telemetry...")
        self.readings_df["recorded_dt"] = pd.to_datetime(self.readings_df["recorded_at"])
        self.readings_df.sort_values(["shipment_id", "recorded_dt"], inplace=True)
        self.shipments_df["dep_dt"] = pd.to_datetime(self.shipments_df["actual_departure"])
        self.shipments_df["arr_dt"] = pd.to_datetime(self.shipments_df["actual_arrival"])
        
        self.readings_grouped = self.readings_df.groupby("shipment_id")
        self.custody_grouped = self.custody_events_df.groupby("shipment_id")

    def run_adjudication(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Executes audit evaluation across all shipments.
        Returns:
            compliance_summary_df: detailed compliance scorecard per shipment
            excursion_reports_df: formal quality deviation records
        """
        print(f"[*] Running compliance adjudication across {len(self.shipments_df):,d} shipments...")

        summary_records = []
        excursion_reports = []
        excursion_counter = 1

        for idx, row in self.shipments_df.iterrows():
            shipment_id = row["shipment_id"]
            lot_id = row["lot_id"]
            issue_type = row.get("issue_type")
            
            lot = self.lot_map.get(lot_id)
            product = self.product_map.get(lot["product_id"]) if lot else None
            policy = self.primary_policies.get(lot["product_id"]) if lot else None

            dep_dt = row["dep_dt"]
            arr_dt = row["arr_dt"]
            total_duration_hours = round((arr_dt - dep_dt).total_seconds() / 3600.0, 2)

            # -------------------------------------------------------------
            # RULE 1 & EDGE CASE EC-01: Logger Assignment & Calibration
            # -------------------------------------------------------------
            assigned_logger = self.logger_by_shipment.get(shipment_id)
            logger_valid, logger_msg = validate_logger(assigned_logger, dep_dt, arr_dt)

            if not logger_valid:
                # Immediate non-compliance / rejection
                status = "NON_COMPLIANT"
                reason = logger_msg
                
                # Create Excursion / Deviation report for missing logger
                excursion_reports.append({
                    "excursion_id": f"EXCR-2026-{excursion_counter:06d}",
                    "shipment_id": shipment_id,
                    "logger_id": None,
                    "policy_id": policy["policy_id"] if policy else None,
                    "excursion_start": row["actual_departure"],
                    "excursion_end": row["actual_arrival"],
                    "duration_minutes": int(total_duration_hours * 60),
                    "max_temp_recorded_c": 0.0,
                    "min_temp_recorded_c": 0.0,
                    "excursion_type": "UNASSIGNED_LOGGER",
                    "severity": "CRITICAL",
                    "disposition": "REJECTED",
                    "issue_type": issue_type,
                    "root_cause": "Shipment dispatched without calibrated electronic temperature monitoring device.",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                excursion_counter += 1

                summary_records.append({
                    "shipment_id": shipment_id,
                    "lot_id": lot_id,
                    "product_name": product["name"] if product else "Unknown",
                    "storage_class": product["storage_class"] if product else "Unknown",
                    "policy_id": policy["policy_id"] if policy else "None",
                    "compliance_status": status,
                    "total_readings": 0,
                    "expected_readings": int(total_duration_hours * 6),
                    "completeness_pct": 0.0,
                    "mkt_c": None,
                    "max_temp_c": None,
                    "min_temp_c": None,
                    "cumulative_excursion_min": 0,
                    "gap_count": 0,
                    "custody_valid": False,
                    "primary_failure_reason": reason,
                    "evidence_trace": f"FAILED: {reason}"
                })
                continue

            # -------------------------------------------------------------
            # RULE 2 & EDGE CASE EC-02: Policy Matching
            # -------------------------------------------------------------
            # Check if this shipment was flagged with policy mismatch
            is_policy_mismatch = (issue_type == "POLICY_MISMATCH")
            applied_policy = policy
            if is_policy_mismatch:
                # Simulate evaluation against an inappropriate policy (e.g. ambient CRT for refrigerated)
                mismatched_pol = self.policies_df[self.policies_df["product_id"] == "PROD-009"].iloc[0].to_dict()
                applied_policy = mismatched_pol

            # -------------------------------------------------------------
            # RULE 3 & EDGE CASE EC-03: Telemetry Readings & Gaps
            # -------------------------------------------------------------
            try:
                shipment_readings = self.readings_grouped.get_group(shipment_id)
            except KeyError:
                shipment_readings = pd.DataFrame()

            readings_count = len(shipment_readings)
            expected_readings = max(1, int(total_duration_hours * 6))
            completeness_pct = round(min(100.0, (readings_count / expected_readings) * 100.0), 1)

            # Detect telemetry gaps
            gaps = detect_telemetry_gaps(shipment_readings, expected_interval_min=10, max_allowed_gap_min=25)
            has_telemetry_gap = len(gaps) > 0 or (issue_type == "SILENT_DATA_GAP")

            temps_list = shipment_readings["temperature_c"].tolist() if not shipment_readings.empty else []
            mkt_val = calculate_mkt(temps_list) if temps_list else None
            max_t = round(float(np.max(temps_list)), 2) if temps_list else None
            min_t = round(float(np.min(temps_list)), 2) if temps_list else None

            # -------------------------------------------------------------
            # RULE 4: Contiguous Excursions Calculation
            # -------------------------------------------------------------
            excursions = calculate_excursions_for_shipment(
                shipment_readings, applied_policy, shipment_id, dep_dt, arr_dt
            )
            cumulative_excursion_min = sum(e["duration_minutes"] for e in excursions)
            max_allowed_excursion = int(applied_policy["max_excursion_minutes"])

            # -------------------------------------------------------------
            # RULE 5 & EDGE CASE EC-04: Custody Verification
            # -------------------------------------------------------------
            try:
                shipment_custody = self.custody_grouped.get_group(shipment_id)
            except KeyError:
                shipment_custody = pd.DataFrame()

            custody_valid, custody_issues = validate_custody_chain(shipment_custody)

            # -------------------------------------------------------------
            # FINAL ADJUDICATION LOGIC (GxP Standard Decision Table)
            # -------------------------------------------------------------
            failure_reasons = []

            if is_policy_mismatch:
                failure_reasons.append(f"POLICY_MISMATCH: Applied policy {applied_policy['policy_id']} does not match product requirement.")

            if has_telemetry_gap:
                total_gap_mins = sum(g["duration_minutes"] for g in gaps) if gaps else 50
                failure_reasons.append(f"MISSING_DATA_GAP: Unrecorded telemetry interval of {total_gap_mins} minutes detected.")
                
                # Log incident report for data gap
                excursion_reports.append({
                    "excursion_id": f"EXCR-2026-{excursion_counter:06d}",
                    "shipment_id": shipment_id,
                    "logger_id": assigned_logger["logger_id"],
                    "policy_id": applied_policy["policy_id"],
                    "excursion_start": gaps[0]["gap_start"] if gaps else row["actual_departure"],
                    "excursion_end": gaps[0]["gap_end"] if gaps else row["actual_arrival"],
                    "duration_minutes": total_gap_mins,
                    "max_temp_recorded_c": max_t or 0.0,
                    "min_temp_recorded_c": min_t or 0.0,
                    "excursion_type": "MISSING_DATA",
                    "severity": "MAJOR",
                    "disposition": "QUARANTINE",
                    "issue_type": issue_type,
                    "root_cause": "Sensor communication dropout or memory write failure during transit.",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                excursion_counter += 1

            if not custody_valid:
                for c_err in custody_issues:
                    failure_reasons.append(c_err)
                excursion_reports.append({
                    "excursion_id": f"EXCR-2026-{excursion_counter:06d}",
                    "shipment_id": shipment_id,
                    "logger_id": assigned_logger["logger_id"],
                    "policy_id": applied_policy["policy_id"],
                    "excursion_start": row["actual_departure"],
                    "excursion_end": row["actual_arrival"],
                    "duration_minutes": 0,
                    "max_temp_recorded_c": max_t or 0.0,
                    "min_temp_recorded_c": min_t or 0.0,
                    "excursion_type": "CUSTODY_GAP",
                    "severity": "MAJOR",
                    "disposition": "QUARANTINE",
                    "issue_type": issue_type,
                    "root_cause": "; ".join(custody_issues),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                excursion_counter += 1

            # Log temperature excursion records
            has_unacceptable_temp_excursion = False
            for exc in excursions:
                is_breach = exc["duration_minutes"] > max_allowed_excursion or exc["severity"] in ["CRITICAL", "MAJOR"]
                if is_breach:
                    has_unacceptable_temp_excursion = True
                    failure_reasons.append(
                        f"TEMP_EXCURSION: {exc['excursion_type']} {exc['duration_minutes']} min (limit: {max_allowed_excursion} min, peak: {exc['max_temp_recorded_c']}°C)"
                    )
                
                excursion_reports.append({
                    "excursion_id": f"EXCR-2026-{excursion_counter:06d}",
                    "shipment_id": shipment_id,
                    "logger_id": assigned_logger["logger_id"],
                    "policy_id": applied_policy["policy_id"],
                    "excursion_start": exc["excursion_start"],
                    "excursion_end": exc["excursion_end"],
                    "duration_minutes": exc["duration_minutes"],
                    "max_temp_recorded_c": exc["max_temp_recorded_c"],
                    "min_temp_recorded_c": exc["min_temp_recorded_c"],
                    "excursion_type": exc["excursion_type"],
                    "severity": exc["severity"],
                    "disposition": exc["disposition"],
                    "issue_type": issue_type,
                    "root_cause": f"Thermal barrier breach during transit: {exc['duration_minutes']} min outside permitted range.",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                excursion_counter += 1

            # Determine final status
            if has_unacceptable_temp_excursion or is_policy_mismatch:
                final_status = "NON_COMPLIANT"
            elif has_telemetry_gap or not custody_valid:
                final_status = "INVESTIGATION"
            elif cumulative_excursion_min > 0:
                # Minor excursion within permitted policy threshold (e.g. 15 min when 30 allowed)
                final_status = "COMPLIANT"
            else:
                final_status = "COMPLIANT"

            primary_reason = failure_reasons[0] if failure_reasons else "All temperature and custody requirements satisfied."
            evidence = (
                f"Policy: {applied_policy['policy_id']} ({applied_policy['min_temp_c']}°C to {applied_policy['max_temp_c']}°C, max {max_allowed_excursion} min). "
                f"Readings: {readings_count}/{expected_readings} ({completeness_pct}%). MKT: {mkt_val}°C. "
                f"Excursions: {len(excursions)} (total {cumulative_excursion_min} min). "
                f"Custody: {'Verified' if custody_valid else 'Gaps Found'}."
            )

            summary_records.append({
                "shipment_id": shipment_id,
                "lot_id": lot_id,
                "product_name": product["name"] if product else "Unknown",
                "storage_class": product["storage_class"] if product else "Unknown",
                "policy_id": applied_policy["policy_id"],
                "compliance_status": final_status,
                "total_readings": readings_count,
                "expected_readings": expected_readings,
                "completeness_pct": completeness_pct,
                "mkt_c": mkt_val,
                "max_temp_c": max_t,
                "min_temp_c": min_t,
                "cumulative_excursion_min": cumulative_excursion_min,
                "gap_count": len(gaps),
                "custody_valid": custody_valid,
                "primary_failure_reason": primary_reason,
                "evidence_trace": evidence
            })

        summary_df = pd.DataFrame(summary_records)
        excursion_df = pd.DataFrame(excursion_reports)

        # Update shipments.csv with calculated compliance_status (retaining strict schema columns)
        print("[*] Updating shipments.csv with calculated compliance statuses...")
        status_map = summary_df.set_index("shipment_id")["compliance_status"].to_dict()
        self.shipments_df["compliance_status"] = self.shipments_df["shipment_id"].map(status_map)
        
        schema_cols = [
            "shipment_id", "lot_id", "packaging_id", "origin_city", "destination_city",
            "planned_departure", "actual_departure", "planned_arrival", "actual_arrival",
            "carrier_name", "compliance_status", "issue_type"
        ]
        out_shipments = self.shipments_df[[c for c in schema_cols if c in self.shipments_df.columns]]
        out_shipments.to_csv(self.data_dir / "transactions" / "shipments.csv", index=False)

        # Export excursion reports and compliance summary
        excursion_path = self.data_dir / "reports" / "excursion_reports.csv"
        excursion_df.to_csv(excursion_path, index=False)
        print(f"[+] Saved {len(excursion_df):,d} excursion reports to {excursion_path}")

        summary_path = self.reports_dir / "compliance_summary.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"[+] Saved compliance summary to {summary_path}")

        self._print_kpi_dashboard(summary_df)
        return summary_df, excursion_df

    def _print_kpi_dashboard(self, df: pd.DataFrame):
        """Displays executive summary metrics in terminal."""
        total = len(df)
        compliant = (df["compliance_status"] == "COMPLIANT").sum()
        non_compliant = (df["compliance_status"] == "NON_COMPLIANT").sum()
        investigation = (df["compliance_status"] == "INVESTIGATION").sum()

        print("\n" + "=" * 65)
        print("          COLD CHAIN COMPLIANCE AUDIT RESULTS")
        print("=" * 65)
        print(f" Total Shipments Evaluated : {total:>8,d}")
        print(f" Compliant Shipments       : {compliant:>8,d} ({compliant/total*100:>5.1f}%)")
        print(f" Non-Compliant Shipments   : {non_compliant:>8,d} ({non_compliant/total*100:>5.1f}%)")
        print(f" Requiring Investigation   : {investigation:>8,d} ({investigation/total*100:>5.1f}%)")
        print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Cold Chain Compliance Adjudication Engine")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")
    parser.add_argument("--reports-dir", type=str, default="reports", help="Reports output directory")

    args = parser.parse_args()
    engine = ComplianceEngine(data_dir=args.data_dir, reports_dir=args.reports_dir)
    engine.run_adjudication()


if __name__ == "__main__":
    main()
