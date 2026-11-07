#!/usr/bin/env python3
"""
Generates database/seed.sql containing SQL INSERT statements for master and seed data.
"""

from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

def generate_seed_sql():
    data_dir = ROOT_DIR / "data"
    out_path = ROOT_DIR / "database" / "seed.sql"

    products = pd.read_csv(data_dir / "master" / "products.csv")
    packaging = pd.read_csv(data_dir / "master" / "packaging.csv")
    policies = pd.read_csv(data_dir / "master" / "threshold_policies.csv")
    lots = pd.read_csv(data_dir / "master" / "lots.csv").head(100)
    shipments = pd.read_csv(data_dir / "transactions" / "shipments.csv").head(100)
    loggers = pd.read_csv(data_dir / "master" / "loggers.csv").head(100)

    lines = [
        "-- ============================================================================",
        "-- Cold Chain Compliance Platform: Initial Seed Data",
        "-- Master Catalog, Packaging, Threshold Policies, and Sample Transactions",
        "-- ============================================================================\n"
    ]

    # Products
    lines.append("-- 1. Products Master")
    for _, r in products.iterrows():
        p_name = str(r['name']).replace("'", "''")
        mfr = str(r['manufacturer']).replace("'", "''")
        lines.append(
            f"INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) "
            f"VALUES ('{r['product_id']}', '{p_name}', '{r['category']}', '{r['storage_class']}', '{mfr}', '{r['created_at']}');"
        )
    lines.append("")

    # Packaging
    lines.append("-- 2. Packaging Master")
    for _, r in packaging.iterrows():
        pkg_name = str(r['name']).replace("'", "''")
        mat = str(r['material']).replace("'", "''")
        lines.append(
            f"INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) "
            f"VALUES ('{r['packaging_id']}', '{pkg_name}', {r['thermal_rating_hours']}, {r['min_temp_c']}, {r['max_temp_c']}, {r['max_payload_kg']}, '{mat}');"
        )
    lines.append("")

    # Policies
    lines.append("-- 3. Threshold Policies")
    for _, r in policies.iterrows():
        exp = f"'{r['expiry_date']}'" if pd.notna(r['expiry_date']) else "NULL"
        mkt = r['mkt_limit_c'] if pd.notna(r['mkt_limit_c']) else "NULL"
        lines.append(
            f"INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) "
            f"VALUES ('{r['policy_id']}', '{r['product_id']}', {r['min_temp_c']}, {r['max_temp_c']}, {r['max_excursion_minutes']}, {r['calibration_uncertainty_c']}, {mkt}, '{r['effective_date']}', {exp});"
        )
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[+] Successfully generated {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    generate_seed_sql()
