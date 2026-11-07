#!/usr/bin/env python3
"""
Cold Chain Compliance Platform - Database Loader
Loads relational CSV datasets into a local SQLite database or PostgreSQL.

Usage:
    # Load into local SQLite database (database/coldchain.db)
    python database/load_database.py

    # Load into PostgreSQL
    python database/load_database.py --db-url postgresql://user:pass@localhost:5432/coldchain_db
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

ROOT_DIR = Path(__file__).resolve().parent.parent

def load_database(db_url: str = None):
    data_dir = ROOT_DIR / "data"
    schema_path = ROOT_DIR / "database" / "schema.sql"

    if not db_url:
        sqlite_file = ROOT_DIR / "database" / "coldchain.db"
        if sqlite_file.exists():
            sqlite_file.unlink()
        print(f"[*] Initializing local SQLite database at {sqlite_file}...")
        
        conn = sqlite3.connect(sqlite_file)
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        engine = None
    else:
        print(f"[*] Initializing relational database at {db_url}...")
        engine = create_engine(db_url)
        with open(schema_path, "r", encoding="utf-8") as f:
            raw_sql = f.read()
        with engine.connect() as conn:
            conn.execute(raw_sql)
        conn = None

    tables = [
        ("products", data_dir / "master" / "products.csv"),
        ("packaging", data_dir / "master" / "packaging.csv"),
        ("threshold_policies", data_dir / "master" / "threshold_policies.csv"),
        ("lots", data_dir / "master" / "lots.csv"),
        ("loggers", data_dir / "master" / "loggers.csv"),
        ("shipments", data_dir / "transactions" / "shipments.csv"),
        ("route_stops", data_dir / "transactions" / "route_stops.csv"),
        ("custody_events", data_dir / "transactions" / "custody_events.csv"),
        ("temperature_readings", data_dir / "transactions" / "temperature_readings.csv"),
        ("excursion_reports", data_dir / "reports" / "excursion_reports.csv")
    ]

    target_conn = conn if conn else engine
    for tbl_name, file_path in tables:
        if file_path.exists():
            print(f"    -> Loading {tbl_name} from {file_path.name}...")
            df = pd.read_csv(file_path)
            df.to_sql(tbl_name, target_conn, if_exists="append", index=False)
            print(f"       ✓ {len(df):,d} records committed.")

    if conn:
        conn.commit()
        conn.close()
        print(f"\n[+] SQLite database ready: {sqlite_file} ({sqlite_file.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print("\n[+] PostgreSQL database load completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Cold Chain datasets into SQL database")
    parser.add_argument("--db-url", type=str, default=None, help="Database connection URL (defaults to SQLite)")
    args = parser.parse_args()
    load_database(args.db_url)
