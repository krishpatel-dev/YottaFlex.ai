#!/usr/bin/env python3
"""
Cold Chain Compliance Platform - Synthetic Data Generation Engine
Generates deterministic, relational master data, shipments, telemetry, and edge cases.
Enforces fixed random seed (default: 20261022) for exact byte-level reproducibility.
"""

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from faker import Faker

# Default configuration constants
DEFAULT_SEED = 20261022
DEFAULT_SHIPMENTS = 5000
READING_INTERVAL_MINUTES = 10

# Indian pharmaceutical manufacturing & distribution hubs
INDIAN_HUBS = [
    ("Ahmedabad", "Gujarat", "Pharma SEZ Hub"),
    ("Mumbai", "Maharashtra", "Central Air Cargo Logistics"),
    ("Hyderabad", "Telangana", "Genome Valley Dist Center"),
    ("Pune", "Maharashtra", "BioPharma Logistics Park"),
    ("Bengaluru", "Karnataka", "Life Sciences Cold Storage"),
    ("Delhi-NCR", "Delhi", "Northern Gateway Transshipment"),
    ("Vadodara", "Gujarat", "Bulk Active Transit Hub"),
    ("Baddi", "Himachal Pradesh", "Formulations Logistics Point"),
    ("Goa", "Goa", "Coastal Port Pharma Terminal"),
    ("Chennai", "Tamil Nadu", "South Gateway Cold Facility"),
    ("Indore", "Madhya Pradesh", "Central Hub Cross-dock"),
    ("Kolkata", "West Bengal", "Eastern Regional Warehouse")
]

CARRIERS = [
    "ColdEx Logistics",
    "Blue Dart Cold Chain Express",
    "Snowman Logistics",
    "TCI Cold Chain",
    "DHL Medical Express",
    "FedEx Temp-Assure",
    "Kuehne+Nagel PharmaChain"
]


class ColdChainDataGenerator:
    """Master generator for relational cold-chain dataset with controlled anomalies."""

    def __init__(self, seed: int = DEFAULT_SEED, num_shipments: int = DEFAULT_SHIPMENTS, output_dir: str = "data"):
        self.seed = seed
        self.num_shipments = num_shipments
        self.output_dir = Path(output_dir)
        self.fake = Faker("en_IN")
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)

        # Output folder hierarchy
        self.master_dir = self.output_dir / "master"
        self.trans_dir = self.output_dir / "transactions"
        self.reports_dir = self.output_dir / "reports"
        self.gt_dir = self.output_dir / "ground_truth"

        for d in [self.master_dir, self.trans_dir, self.reports_dir, self.gt_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # In-memory storage of generated entity records
        self.products: List[Dict] = []
        self.packaging: List[Dict] = []
        self.policies: List[Dict] = []
        self.lots: List[Dict] = []
        self.shipments: List[Dict] = []
        self.loggers: List[Dict] = []
        self.route_stops: List[Dict] = []
        self.custody_events: List[Dict] = []
        self.readings: List[Dict] = []
        self.ground_truth: List[Dict] = []

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """Executes full generation sequence following strict dependency hierarchy."""
        print(f"[*] Starting synthetic data generation with seed={self.seed}, target_shipments={self.num_shipments}...")

        self._generate_products()
        self._generate_packaging()
        self._generate_threshold_policies()
        self._generate_lots()
        self._generate_shipments_and_routes()
        self._generate_loggers_and_readings()

        dfs = self._export_to_csv()
        print("[+] Synthetic data generation completed successfully.")
        return dfs

    def _generate_products(self):
        """Generates 15 regulated pharmaceutical, biologic, and cold food products."""
        product_definitions = [
            ("PROD-001", "COVID-19 mRNA Vaccine", "VACCINE", "ULTRA_LOW", "BioTech Global Corp"),
            ("PROD-002", "Rotavirus Oral Vaccine", "VACCINE", "REFRIGERATED", "Serum Institute Bio"),
            ("PROD-003", "Hepatitis B Recombinant Vaccine", "VACCINE", "REFRIGERATED", "Bharat Pharma Innovations"),
            ("PROD-004", "Human Recombinant Insulin 100IU", "BIOLOGIC", "REFRIGERATED", "Novo Health Sciences"),
            ("PROD-005", "Monoclonal Antibody (Oncology)", "BIOLOGIC", "REFRIGERATED", "Roche Bio Therapeutics"),
            ("PROD-006", "Immune Globulin Intravenous (IGIV)", "BIOLOGIC", "REFRIGERATED", "Baxalta Life Sciences"),
            ("PROD-007", "Varicella Zoster Live Vaccine", "VACCINE", "FROZEN", "Merck Bio Vaccine"),
            ("PROD-008", "MMR Triple Antigen Vaccine", "VACCINE", "REFRIGERATED", "Sanofi Pasteur Med"),
            ("PROD-009", "Lyophilized Plasma Protein", "BIOLOGIC", "CONTROLLED_ROOM_TEMP", "CSL Bio Formulations"),
            ("PROD-010", "Oxytocin Injection 10IU/ml", "PHARMA", "REFRIGERATED", "Novartis Healthcare"),
            ("PROD-011", "Enoxaparin Sodium Pre-filled", "PHARMA", "CONTROLLED_ROOM_TEMP", "Aventis Generics"),
            ("PROD-012", "Probiotic Bio-Culture Sachets", "PERISHABLE_FOOD", "REFRIGERATED", "Yakult Bio Nutrients"),
            ("PROD-013", "Enzyme Replacement Therapy Infusion", "BIOLOGIC", "REFRIGERATED", "Genzyme Therapeutics"),
            ("PROD-014", "Dengue Tetravalent Vaccine", "VACCINE", "REFRIGERATED", "Takeda Pharma India"),
            ("PROD-015", "Fresh Frozen Medical Diagnostic Reagent", "BIOLOGIC", "FROZEN", "Abbott Diagnostics")
        ]

        base_date = datetime(2025, 1, 15, 8, 0, 0)
        for idx, (p_id, name, cat, s_class, mfr) in enumerate(product_definitions):
            self.products.append({
                "product_id": p_id,
                "name": name,
                "category": cat,
                "storage_class": s_class,
                "manufacturer": mfr,
                "created_at": (base_date + timedelta(days=idx * 10)).strftime("%Y-%m-%d %H:%M:%S")
            })

    def _generate_packaging(self):
        """Generates 8 standardized certified thermal packaging solutions."""
        packaging_profiles = [
            ("PKG-001", "Credo Cube VIP Shipper 12L", 72.0, 2.0, 8.0, 15.0, "Vacuum Insulated Panels + TIC PCM"),
            ("PKG-002", "Credo Cube Deep Frozen 28L", 96.0, -25.0, -15.0, 22.0, "VIP + Dry Ice System"),
            ("PKG-003", "AcuTemp Ultra-Cold Shipper 50L", 120.0, -85.0, -60.0, 35.0, "VIP Vacuum Core + Liquid N2 Vapor"),
            ("PKG-004", "BioTherm Insulated Box 10L", 48.0, 2.0, 8.0, 10.0, "Expanded Polystyrene + Water Gel Packs"),
            ("PKG-005", "PharmaTrans Active CRT Container 100L", 96.0, 15.0, 25.0, 80.0, "Active Thermo-Electric Peltier Shell"),
            ("PKG-006", "BioCourier Heavy Cargo 250L", 72.0, 2.0, 8.0, 180.0, "Polyurethane Foam + Gel Panels"),
            ("PKG-007", "AeroChill Express Frozen 15L", 48.0, -25.0, -15.0, 12.0, "VIP + Phase 22 Frozen PCM"),
            ("PKG-008", "TempStable Ambient Shield 30L", 60.0, 15.0, 25.0, 25.0, "Reflective Multi-foil Air Gel")
        ]

        for p_id, name, rating, min_t, max_t, payload, material in packaging_profiles:
            self.packaging.append({
                "packaging_id": p_id,
                "name": name,
                "thermal_rating_hours": rating,
                "min_temp_c": min_t,
                "max_temp_c": max_t,
                "max_payload_kg": payload,
                "material": material
            })

    def _generate_threshold_policies(self):
        """Generates regulatory threshold policies corresponding to products."""
        policy_rules = {
            "ULTRA_LOW": (-80.0, -60.0, 15, 0.5, -65.0),
            "FROZEN": (-25.0, -15.0, 30, 0.5, -18.0),
            "REFRIGERATED": (2.0, 8.0, 30, 0.5, 5.0),
            "CONTROLLED_ROOM_TEMP": (15.0, 25.0, 60, 0.5, 20.0)
        }

        for idx, prod in enumerate(self.products, start=1):
            s_class = prod["storage_class"]
            min_t, max_t, max_excursion, uncert, mkt = policy_rules[s_class]
            
            # Create primary policy
            self.policies.append({
                "policy_id": f"POL-{idx:03d}",
                "product_id": prod["product_id"],
                "min_temp_c": min_t,
                "max_temp_c": max_t,
                "max_excursion_minutes": max_excursion,
                "calibration_uncertainty_c": uncert,
                "mkt_limit_c": mkt,
                "effective_date": "2025-01-01",
                "expiry_date": "2027-12-31"
            })

        # Add 5 specialized alternative / stricter revision policies (for total 20 policies)
        revisions = [
            ("POL-016", "PROD-001", -85.0, -65.0, 10, 0.3, -70.0),
            ("POL-017", "PROD-002", 2.0, 6.0, 20, 0.2, 4.0),
            ("POL-018", "PROD-004", 2.0, 8.0, 15, 0.3, 4.5),
            ("POL-019", "PROD-005", 2.0, 8.0, 20, 0.25, 4.8),
            ("POL-020", "PROD-007", -25.0, -18.0, 20, 0.3, -20.0)
        ]
        for p_id, prod_id, min_t, max_t, max_exc, uncert, mkt in revisions:
            self.policies.append({
                "policy_id": p_id,
                "product_id": prod_id,
                "min_temp_c": min_t,
                "max_temp_c": max_t,
                "max_excursion_minutes": max_exc,
                "calibration_uncertainty_c": uncert,
                "mkt_limit_c": mkt,
                "effective_date": "2026-01-01",
                "expiry_date": "2028-12-31"
            })

    def _generate_lots(self):
        """Generates ~1,500 batches/lots across the 15 products."""
        num_lots = max(1500, self.num_shipments // 3)
        base_date = date(2025, 6, 1)

        for lot_idx in range(1, num_lots + 1):
            lot_id = f"LOT-2026-{lot_idx:06d}"
            product = self.products[(lot_idx - 1) % len(self.products)]
            
            # Manufacture date between June 2025 and Dec 2025
            mfg_offset = (lot_idx * 3) % 180
            mfg_date = base_date + timedelta(days=mfg_offset)
            
            # Expiry date 1 to 2 years after manufacture
            expiry_date = mfg_date + timedelta(days=random.choice([365, 540, 730]))
            quantity = random.randint(500, 25000)
            status = "ACTIVE" if lot_idx % 100 != 0 else "QUARANTINED"

            self.lots.append({
                "lot_id": lot_id,
                "product_id": product["product_id"],
                "manufacture_date": mfg_date.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "quantity_units": quantity,
                "status": status
            })

    def _generate_shipments_and_routes(self):
        """Generates shipments, route waypoints, and custody events with designated anomaly candidates."""
        start_time_base = datetime(2026, 1, 10, 6, 0, 0)
        
        # Determine anomaly allocations
        # Required negative scenarios:
        # EC-01: Logger not assigned (50)
        # EC-02: Product threshold mismatch (30)
        # EC-03: Missing data silently passed (40)
        # EC-04: Custody gap not flagged (25)
        # EC-05: Cross-shipment excursion boundary (15)
        # Real-world excursions: ~400 shipments have natural high/low excursions
        
        all_indices = list(range(1, self.num_shipments + 1))
        random.shuffle(all_indices)

        ec1_indices = set(all_indices[0:50])
        ec2_indices = set(all_indices[50:80])
        ec3_indices = set(all_indices[80:120])
        ec4_indices = set(all_indices[120:145])
        ec5_indices = set(all_indices[145:160])
        natural_excursion_indices = set(all_indices[160:560])

        lot_lookup = {l["lot_id"]: l for l in self.lots}
        packaging_by_class = {
            "ULTRA_LOW": ["PKG-003"],
            "FROZEN": ["PKG-002", "PKG-007"],
            "REFRIGERATED": ["PKG-001", "PKG-004", "PKG-006"],
            "CONTROLLED_ROOM_TEMP": ["PKG-005", "PKG-008"]
        }

        prod_lookup = {p["product_id"]: p for p in self.products}

        for idx in range(1, self.num_shipments + 1):
            shipment_id = f"SHP-2026-{idx:06d}"
            
            # Select lot and product
            lot = self.lots[(idx - 1) % len(self.lots)]
            product = prod_lookup[lot["product_id"]]
            s_class = product["storage_class"]

            # Select suitable packaging
            pkg_choices = packaging_by_class.get(s_class, ["PKG-001"])
            pkg_id = random.choice(pkg_choices)

            # Route cities
            origin = INDIAN_HUBS[(idx % len(INDIAN_HUBS))]
            dest_offset = (idx + (idx // len(INDIAN_HUBS)) + 1) % len(INDIAN_HUBS)
            destination = INDIAN_HUBS[dest_offset]
            if origin[0] == destination[0]:
                dest_offset = (dest_offset + 1) % len(INDIAN_HUBS)
                destination = INDIAN_HUBS[dest_offset]

            # Trip duration: 12 to 36 hours (avg 20 hours -> ~120 readings)
            transit_hours = random.choice([14, 18, 22, 26, 30, 36])
            dep_offset_hours = (idx * 2) % 2000
            planned_dep = start_time_base + timedelta(hours=dep_offset_hours)
            actual_dep = planned_dep + timedelta(minutes=random.choice([0, 15, 30, -10]))
            
            planned_arr = planned_dep + timedelta(hours=transit_hours)
            actual_arr = actual_dep + timedelta(hours=transit_hours, minutes=random.randint(-20, 45))

            carrier = CARRIERS[idx % len(CARRIERS)]

            # Tag edge case
            issue_type = None
            if idx in ec1_indices:
                issue_type = "UNASSIGNED_LOGGER"
            elif idx in ec2_indices:
                issue_type = "POLICY_MISMATCH"
            elif idx in ec3_indices:
                issue_type = "SILENT_DATA_GAP"
            elif idx in ec4_indices:
                issue_type = "UNFLAGGED_CUSTODY_GAP"
            elif idx in ec5_indices:
                issue_type = "CROSS_SHIPMENT_EXCURSION"
            elif idx in natural_excursion_indices:
                issue_type = "NATURAL_EXCURSION"

            self.shipments.append({
                "shipment_id": shipment_id,
                "lot_id": lot["lot_id"],
                "packaging_id": pkg_id,
                "origin_city": origin[0],
                "destination_city": destination[0],
                "planned_departure": planned_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_departure": actual_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "planned_arrival": planned_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_arrival": actual_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "carrier_name": carrier,
                "compliance_status": "PENDING",  # Will be calculated by compliance engine
                "issue_type": issue_type
            })

            # Record in ground truth if edge case or deliberate excursion
            if issue_type:
                expected_outcome = "REJECT" if issue_type in ["UNASSIGNED_LOGGER", "NATURAL_EXCURSION"] else (
                    "INVESTIGATION" if issue_type in ["SILENT_DATA_GAP", "UNFLAGGED_CUSTODY_GAP"] else "FLAG"
                )
                if issue_type == "CROSS_SHIPMENT_EXCURSION":
                    expected_outcome = "NO_FALSE_EXCURSION"

                self.ground_truth.append({
                    "shipment_id": shipment_id,
                    "issue_type": issue_type,
                    "expected_outcome": expected_outcome,
                    "description": f"Controlled injection for scenario: {issue_type}"
                })

            # Route Stops: Origin -> 1 or 2 Waypoints -> Destination
            # Origin stop
            stop1_id = f"STOP-{shipment_id}-01"
            self.route_stops.append({
                "stop_id": stop1_id,
                "shipment_id": shipment_id,
                "stop_sequence": 1,
                "location_name": f"{origin[0]} Plant Facility",
                "city": origin[0],
                "planned_arrival": planned_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_arrival": actual_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "planned_departure": planned_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_departure": actual_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "dwell_hours": 0.0,
                "stop_type": "ORIGIN"
            })

            # Midpoint transit waypoint
            mid_city = INDIAN_HUBS[(idx + 4) % len(INDIAN_HUBS)][0]
            mid_arr = actual_dep + timedelta(hours=transit_hours / 2)
            dwell = round(random.uniform(0.5, 2.5), 2)
            mid_dep = mid_arr + timedelta(hours=dwell)
            stop2_id = f"STOP-{shipment_id}-02"
            self.route_stops.append({
                "stop_id": stop2_id,
                "shipment_id": shipment_id,
                "stop_sequence": 2,
                "location_name": f"{mid_city} Transit Cross-Dock Hub",
                "city": mid_city,
                "planned_arrival": (planned_dep + timedelta(hours=transit_hours / 2)).strftime("%Y-%m-%d %H:%M:%S"),
                "actual_arrival": mid_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "planned_departure": (planned_dep + timedelta(hours=transit_hours / 2 + 1)).strftime("%Y-%m-%d %H:%M:%S"),
                "actual_departure": mid_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "dwell_hours": dwell,
                "stop_type": "WAYPOINT"
            })

            # Destination stop
            stop3_id = f"STOP-{shipment_id}-03"
            self.route_stops.append({
                "stop_id": stop3_id,
                "shipment_id": shipment_id,
                "stop_sequence": 3,
                "location_name": f"{destination[0]} Central Receiving Warehouse",
                "city": destination[0],
                "planned_arrival": planned_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_arrival": actual_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "planned_departure": planned_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_departure": actual_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "dwell_hours": 0.0,
                "stop_type": "DESTINATION"
            })

            # Custody Events: 3 handoffs
            # Handoff 1: Supplier -> Carrier at Origin
            c1_time = actual_dep
            self.custody_events.append({
                "custody_id": f"CUST-{shipment_id}-01",
                "shipment_id": shipment_id,
                "stop_id": stop1_id,
                "handover_time": c1_time.strftime("%Y-%m-%d %H:%M:%S"),
                "from_party": f"{product['manufacturer']} Dispatch Team",
                "to_party": f"{carrier} Primary Driver",
                "from_party_role": "SUPPLIER",
                "to_party_role": "CARRIER",
                "signature_obtained": 1,
                "notes": "Security tamper seals intact and verified.",
                "gap_flag": 0
            })

            # Handoff 2: Midpoint cross-dock handover
            c2_time = mid_arr + timedelta(minutes=15)
            # EC-04 injection: custody gap not signed or missing timestamp gap > 3 hours
            is_ec4 = (idx in ec4_indices)
            self.custody_events.append({
                "custody_id": f"CUST-{shipment_id}-02",
                "shipment_id": shipment_id,
                "stop_id": stop2_id,
                "handover_time": (c2_time + timedelta(hours=4 if is_ec4 else 0)).strftime("%Y-%m-%d %H:%M:%S"),
                "from_party": f"{carrier} Primary Driver",
                "to_party": f"{mid_city} Hub Facility Supervisor",
                "from_party_role": "CARRIER",
                "to_party_role": "WAREHOUSE",
                "signature_obtained": 0 if is_ec4 else 1,
                "notes": "Unrecorded handover delay during shift change." if is_ec4 else "Intermediate custody verification verified.",
                "gap_flag": 1 if is_ec4 else 0
            })

            # Handoff 3: Destination Receiving
            c3_time = actual_arr
            self.custody_events.append({
                "custody_id": f"CUST-{shipment_id}-03",
                "shipment_id": shipment_id,
                "stop_id": stop3_id,
                "handover_time": c3_time.strftime("%Y-%m-%d %H:%M:%S"),
                "from_party": f"{carrier} Delivery Crew",
                "to_party": f"{destination[0]} Inbound QA Officer",
                "from_party_role": "CARRIER",
                "to_party_role": "RECIPIENT",
                "signature_obtained": 1,
                "notes": "Destination receipt signed upon thermal package receipt.",
                "gap_flag": 0
            })

    def _generate_loggers_and_readings(self):
        """Generates 1,000 calibrated loggers and time-series temperature readings."""
        print("    -> Generating loggers and time-series temperature telemetry...")
        
        # 1,000 unique loggers are deployed across the shipments
        num_loggers = 1000
        logger_models = ["ELPRO Libero CL", "Sensitech TempTale Ultra", "TSE SensoSafe 4G", "Berlinger Fridge-tag 2"]

        # Pre-create 1,000 physical logger instruments
        for l_idx in range(1, num_loggers + 1):
            logger_id = f"LOG-PHYSICAL-{l_idx:04d}"
            cal_date = date(2025, 10, 1) + timedelta(days=(l_idx % 60))
            cal_exp = cal_date + timedelta(days=365)
            self.loggers.append({
                "logger_id": logger_id,
                "shipment_id": None,  # Will be mapped below
                "model": logger_models[l_idx % len(logger_models)],
                "calibration_date": cal_date.strftime("%Y-%m-%d"),
                "calibration_expiry": cal_exp.strftime("%Y-%m-%d"),
                "reading_interval_min": READING_INTERVAL_MINUTES,
                "accuracy_c": 0.50,
                "is_active": 1
            })

        # Map shipments to loggers:
        # Note: In cold chain operations, loggers are assigned per shipment.
        # ID convention: LOG-<shipment-id>-01
        # For EC-01: 50 shipments have NO logger (logger_id not created or unassigned).
        # We also associate physical serials.
        
        lot_lookup = {l["lot_id"]: l for l in self.lots}
        prod_lookup = {p["product_id"]: p for p in self.products}
        pol_lookup = {p["product_id"]: p for p in self.policies if p["policy_id"].startswith("POL-0")}

        readings_buffer: List[Dict] = []
        readings_count = 0

        # Target temperature centers by storage class
        temp_centers = {
            "ULTRA_LOW": (-72.0, 1.2),
            "FROZEN": (-20.0, 1.0),
            "REFRIGERATED": (4.8, 0.7),
            "CONTROLLED_ROOM_TEMP": (20.0, 1.0)
        }

        for idx, shp in enumerate(self.shipments, start=1):
            shipment_id = shp["shipment_id"]
            issue_type = shp["issue_type"]
            lot = lot_lookup[shp["lot_id"]]
            prod = prod_lookup[lot["product_id"]]
            s_class = prod["storage_class"]
            policy = pol_lookup.get(prod["product_id"], self.policies[0])

            # EC-01: Logger unassigned scenario
            if issue_type == "UNASSIGNED_LOGGER":
                # Do NOT generate logger or readings for this shipment
                continue

            logger_id = f"LOG-{shipment_id}-01"
            cal_date = date(2025, 11, 15)
            cal_exp = date(2026, 11, 15)

            # Store the logger record
            self.loggers.append({
                "logger_id": logger_id,
                "shipment_id": shipment_id,
                "model": logger_models[idx % len(logger_models)],
                "calibration_date": cal_date.strftime("%Y-%m-%d"),
                "calibration_expiry": cal_exp.strftime("%Y-%m-%d"),
                "reading_interval_min": READING_INTERVAL_MINUTES,
                "accuracy_c": 0.50,
                "is_active": 1
            })

            # Calculate reading intervals
            dep_time = datetime.strptime(shp["actual_departure"], "%Y-%m-%d %H:%M:%S")
            arr_time = datetime.strptime(shp["actual_arrival"], "%Y-%m-%d %H:%M:%S")
            total_duration_minutes = int((arr_time - dep_time).total_seconds() // 60)
            num_points = total_duration_minutes // READING_INTERVAL_MINUTES

            mean_temp, std_temp = temp_centers.get(s_class, (5.0, 0.8))

            # Vectorized baseline temperature generation
            base_temps = np.random.normal(loc=mean_temp, scale=std_temp, size=num_points)

            # Injection handling:
            # 1. EC-03: SILENT_DATA_GAP -> Drop 4 to 8 consecutive readings (40 to 80 minutes missing)
            gap_indices = set()
            if issue_type == "SILENT_DATA_GAP" and num_points > 20:
                gap_start = num_points // 2
                gap_len = random.randint(4, 7)  # 40-70 minutes missing
                gap_indices = set(range(gap_start, gap_start + gap_len))

            # 2. EC-02: POLICY_MISMATCH -> The product is REFRIGERATED (2-8°C) but ambient or wrong range
            # We record realistic readings for the lot, but the system must detect that a mismatched policy was evaluated.

            # 3. Natural or injected excursion:
            # Raise temperature above max_temp_c for a specific duration
            excursion_indices = set()
            if issue_type in ["NATURAL_EXCURSION", "CROSS_SHIPMENT_EXCURSION"] or (idx % 18 == 0):
                # Pick duration: either minor (< max_excursion) or major (> max_excursion)
                is_major = (issue_type == "NATURAL_EXCURSION") or (idx % 36 == 0)
                dur_readings = random.randint(5, 12) if is_major else random.randint(1, 2)
                start_ex = max(5, num_points // 3)
                excursion_indices = set(range(start_ex, min(num_points, start_ex + dur_readings)))
                
                # Excursion spike value
                spike = (policy["max_temp_c"] + random.uniform(2.5, 6.0)) if s_class == "REFRIGERATED" else (policy["max_temp_c"] + 8.0)
                for e_i in excursion_indices:
                    base_temps[e_i] = spike + np.random.normal(0, 0.2)

            for step_i in range(num_points):
                if step_i in gap_indices:
                    # Skip writing this point to create real data gap in the time series
                    continue

                curr_time = dep_time + timedelta(minutes=step_i * READING_INTERVAL_MINUTES)
                val_c = round(float(base_temps[step_i]), 2)
                
                is_excr = (val_c < policy["min_temp_c"] or val_c > policy["max_temp_c"])
                quality = "NORMAL"
                
                # Flag calibration boundary proximity
                if abs(val_c - policy["min_temp_c"]) <= policy["calibration_uncertainty_c"] or \
                   abs(val_c - policy["max_temp_c"]) <= policy["calibration_uncertainty_c"]:
                    quality = "SUSPECT"

                time_str_id = curr_time.strftime("%Y%m%d%H%M")
                reading_id = f"TEMP-{logger_id}-{time_str_id}"

                readings_buffer.append({
                    "reading_id": reading_id,
                    "logger_id": logger_id,
                    "shipment_id": shipment_id,
                    "recorded_at": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "temperature_c": val_c,
                    "is_excursion": 1 if is_excr else 0,
                    "is_gap_filled": 0,
                    "quality_flag": quality
                })

            readings_count += len(readings_buffer)
            # Batch memory release into main collection
            if len(readings_buffer) >= 50000:
                self.readings.extend(readings_buffer)
                readings_buffer = []

        if readings_buffer:
            self.readings.extend(readings_buffer)

        print(f"    -> Total temperature telemetry points generated: {len(self.readings):,}")

    def _export_to_csv(self) -> Dict[str, pd.DataFrame]:
        """Writes all relational entity collections to validated CSV datasets."""
        print("[*] Serializing relational datasets to CSV files...")
        
        tables = {
            # Master data
            self.master_dir / "products.csv": (self.products, ["product_id", "name", "category", "storage_class", "manufacturer", "created_at"]),
            self.master_dir / "packaging.csv": (self.packaging, ["packaging_id", "name", "thermal_rating_hours", "min_temp_c", "max_temp_c", "max_payload_kg", "material"]),
            self.master_dir / "threshold_policies.csv": (self.policies, ["policy_id", "product_id", "min_temp_c", "max_temp_c", "max_excursion_minutes", "calibration_uncertainty_c", "mkt_limit_c", "effective_date", "expiry_date"]),
            self.master_dir / "lots.csv": (self.lots, ["lot_id", "product_id", "manufacture_date", "expiry_date", "quantity_units", "status"]),
            self.master_dir / "loggers.csv": (self.loggers, ["logger_id", "shipment_id", "model", "calibration_date", "calibration_expiry", "reading_interval_min", "accuracy_c", "is_active"]),
            
            # Transactions & Events
            self.trans_dir / "shipments.csv": (self.shipments, ["shipment_id", "lot_id", "packaging_id", "origin_city", "destination_city", "planned_departure", "actual_departure", "planned_arrival", "actual_arrival", "carrier_name", "compliance_status", "issue_type"]),
            self.trans_dir / "route_stops.csv": (self.route_stops, ["stop_id", "shipment_id", "stop_sequence", "location_name", "city", "planned_arrival", "actual_arrival", "planned_departure", "actual_departure", "dwell_hours", "stop_type"]),
            self.trans_dir / "custody_events.csv": (self.custody_events, ["custody_id", "shipment_id", "stop_id", "handover_time", "from_party", "to_party", "from_party_role", "to_party_role", "signature_obtained", "notes", "gap_flag"]),
            self.trans_dir / "temperature_readings.csv": (self.readings, ["reading_id", "logger_id", "shipment_id", "recorded_at", "temperature_c", "is_excursion", "is_gap_filled", "quality_flag"]),
            
            # Ground truth (isolated)
            self.gt_dir / "ground_truth.csv": (self.ground_truth, ["shipment_id", "issue_type", "expected_outcome", "description"])
        }

        dataframes = {}
        for path, (records, columns) in tables.items():
            df = pd.DataFrame(records, columns=columns)
            df.to_csv(path, index=False)
            dataframes[path.stem] = df
            print(f"    Exported {path.name:25s} : {len(df):>10,d} records ({path.stat().st_size / (1024*1024):.2f} MB)")

        return dataframes


def compute_checksums(data_dir: Path) -> Dict[str, str]:
    """Calculates MD5 hash for every generated CSV to guarantee exact reproducibility."""
    checksums = {}
    for csv_file in sorted(data_dir.rglob("*.csv")):
        h = hashlib.md5()
        with open(csv_file, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        checksums[csv_file.name] = h.hexdigest()
    return checksums


def main():
    parser = argparse.ArgumentParser(description="Deterministic Cold Chain Synthetic Data Generator")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"Random seed (default: {DEFAULT_SEED})")
    parser.add_argument("--shipments", type=int, default=DEFAULT_SHIPMENTS, help=f"Number of shipments (default: {DEFAULT_SHIPMENTS})")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory")
    parser.add_argument("--checksums", action="store_true", help="Print MD5 checksums of generated files")

    args = parser.parse_args()
    generator = ColdChainDataGenerator(seed=args.seed, num_shipments=args.shipments, output_dir=args.output_dir)
    generator.generate_all()

    if args.checksums:
        print("\n[*] MD5 Checksums:")
        csums = compute_checksums(Path(args.output_dir))
        for fname, hval in csums.items():
            print(f"    {fname:28s} {hval}")


if __name__ == "__main__":
    main()
