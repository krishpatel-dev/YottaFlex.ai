-- ============================================================================
-- Cold Chain Compliance Platform: Relational Database Schema (DDL)
-- Compliant with PostgreSQL 14+ and SQLite 3.35+
-- ============================================================================

-- Drop tables in reverse-dependency order if existing
DROP TABLE IF EXISTS excursion_reports;
DROP TABLE IF EXISTS temperature_readings;
DROP TABLE IF EXISTS custody_events;
DROP TABLE IF EXISTS route_stops;
DROP TABLE IF EXISTS loggers;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS lots;
DROP TABLE IF EXISTS threshold_policies;
DROP TABLE IF EXISTS packaging;
DROP TABLE IF EXISTS products;

-- 1. Master: Products
CREATE TABLE products (
    product_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL CHECK (category IN ('VACCINE', 'BIOLOGIC', 'PHARMA', 'PERISHABLE_FOOD')),
    storage_class VARCHAR(64) NOT NULL CHECK (storage_class IN ('ULTRA_LOW', 'FROZEN', 'REFRIGERATED', 'CONTROLLED_ROOM_TEMP')),
    manufacturer VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- 2. Master: Packaging Profiles
CREATE TABLE packaging (
    packaging_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    thermal_rating_hours NUMERIC(6,2) NOT NULL CHECK (thermal_rating_hours > 0),
    min_temp_c NUMERIC(5,2) NOT NULL,
    max_temp_c NUMERIC(5,2) NOT NULL CHECK (max_temp_c >= min_temp_c),
    max_payload_kg NUMERIC(6,2) NOT NULL CHECK (max_payload_kg > 0),
    material VARCHAR(128) NOT NULL
);

-- 3. Master: Threshold Policies (linked to Product)
CREATE TABLE threshold_policies (
    policy_id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    min_temp_c NUMERIC(5,2) NOT NULL,
    max_temp_c NUMERIC(5,2) NOT NULL CHECK (max_temp_c >= min_temp_c),
    max_excursion_minutes INTEGER NOT NULL CHECK (max_excursion_minutes >= 0),
    calibration_uncertainty_c NUMERIC(4,2) NOT NULL DEFAULT 0.50,
    mkt_limit_c NUMERIC(5,2),
    effective_date DATE NOT NULL,
    expiry_date DATE
);

-- 4. Master: Product Lots
CREATE TABLE lots (
    lot_id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    manufacture_date DATE NOT NULL,
    expiry_date DATE NOT NULL CHECK (expiry_date > manufacture_date),
    quantity_units INTEGER NOT NULL CHECK (quantity_units > 0),
    status VARCHAR(32) NOT NULL CHECK (status IN ('ACTIVE', 'EXPIRED', 'QUARANTINED', 'RELEASED'))
);

-- 5. Transactions: Shipments
CREATE TABLE shipments (
    shipment_id VARCHAR(32) PRIMARY KEY,
    lot_id VARCHAR(32) NOT NULL REFERENCES lots(lot_id),
    packaging_id VARCHAR(32) NOT NULL REFERENCES packaging(packaging_id),
    origin_city VARCHAR(64) NOT NULL,
    destination_city VARCHAR(64) NOT NULL,
    planned_departure TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP NOT NULL,
    planned_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP NOT NULL CHECK (actual_arrival >= actual_departure),
    carrier_name VARCHAR(128) NOT NULL,
    compliance_status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (compliance_status IN ('COMPLIANT', 'NON_COMPLIANT', 'INVESTIGATION', 'PENDING')),
    issue_type VARCHAR(64)
);

-- 6. Master / Assigned: Loggers
CREATE TABLE loggers (
    logger_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(32) REFERENCES shipments(shipment_id),
    model VARCHAR(64) NOT NULL,
    calibration_date DATE NOT NULL,
    calibration_expiry DATE NOT NULL CHECK (calibration_expiry > calibration_date),
    reading_interval_min INTEGER NOT NULL DEFAULT 10 CHECK (reading_interval_min > 0),
    accuracy_c NUMERIC(4,2) NOT NULL DEFAULT 0.50,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- 7. Events: Route Stops
CREATE TABLE route_stops (
    stop_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(32) NOT NULL REFERENCES shipments(shipment_id),
    stop_sequence INTEGER NOT NULL CHECK (stop_sequence >= 1),
    location_name VARCHAR(128) NOT NULL,
    city VARCHAR(64) NOT NULL,
    planned_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP,
    planned_departure TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    dwell_hours NUMERIC(5,2) DEFAULT 0.0,
    stop_type VARCHAR(32) NOT NULL CHECK (stop_type IN ('ORIGIN', 'WAYPOINT', 'DESTINATION')),
    CONSTRAINT uq_shipment_stop_seq UNIQUE (shipment_id, stop_sequence)
);

-- 8. Events: Custody Events
CREATE TABLE custody_events (
    custody_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(32) NOT NULL REFERENCES shipments(shipment_id),
    stop_id VARCHAR(64) REFERENCES route_stops(stop_id),
    handover_time TIMESTAMP NOT NULL,
    from_party VARCHAR(128) NOT NULL,
    to_party VARCHAR(128) NOT NULL,
    from_party_role VARCHAR(64) NOT NULL CHECK (from_party_role IN ('SUPPLIER', 'CARRIER', 'WAREHOUSE', 'RECIPIENT')),
    to_party_role VARCHAR(64) NOT NULL CHECK (to_party_role IN ('SUPPLIER', 'CARRIER', 'WAREHOUSE', 'RECIPIENT')),
    signature_obtained BOOLEAN NOT NULL DEFAULT 1,
    notes TEXT,
    gap_flag BOOLEAN NOT NULL DEFAULT 0
);

-- 9. Events: Temperature Readings
CREATE TABLE temperature_readings (
    reading_id VARCHAR(96) PRIMARY KEY,
    logger_id VARCHAR(64) NOT NULL REFERENCES loggers(logger_id),
    shipment_id VARCHAR(32) NOT NULL REFERENCES shipments(shipment_id),
    recorded_at TIMESTAMP NOT NULL,
    temperature_c NUMERIC(5,2) NOT NULL,
    is_excursion BOOLEAN NOT NULL DEFAULT 0,
    is_gap_filled BOOLEAN NOT NULL DEFAULT 0,
    quality_flag VARCHAR(32) NOT NULL DEFAULT 'NORMAL' CHECK (quality_flag IN ('NORMAL', 'MISSING', 'SUSPECT', 'GAP'))
);

-- 10. Reports: Excursion Reports & Deviations
CREATE TABLE excursion_reports (
    excursion_id VARCHAR(32) PRIMARY KEY,
    shipment_id VARCHAR(32) NOT NULL REFERENCES shipments(shipment_id),
    logger_id VARCHAR(64) REFERENCES loggers(logger_id),
    policy_id VARCHAR(32) REFERENCES threshold_policies(policy_id),
    excursion_start TIMESTAMP NOT NULL,
    excursion_end TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes >= 0),
    max_temp_recorded_c NUMERIC(5,2) NOT NULL,
    min_temp_recorded_c NUMERIC(5,2) NOT NULL,
    excursion_type VARCHAR(32) NOT NULL CHECK (excursion_type IN ('HIGH_TEMP', 'LOW_TEMP', 'MISSING_DATA', 'CUSTODY_GAP', 'POLICY_MISMATCH', 'UNASSIGNED_LOGGER')),
    severity VARCHAR(32) NOT NULL CHECK (severity IN ('MINOR', 'MAJOR', 'CRITICAL')),
    disposition VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (disposition IN ('PENDING', 'ACCEPTED', 'REJECTED', 'QUARANTINE')),
    issue_type VARCHAR(64),
    root_cause TEXT,
    created_at TIMESTAMP NOT NULL
);

-- Performance Indexes
CREATE INDEX idx_shipments_lot ON shipments(lot_id);
CREATE INDEX idx_shipments_compliance ON shipments(compliance_status);
CREATE INDEX idx_loggers_shipment ON loggers(shipment_id);
CREATE INDEX idx_route_stops_shipment ON route_stops(shipment_id);
CREATE INDEX idx_custody_events_shipment ON custody_events(shipment_id);
CREATE INDEX idx_temp_readings_shipment_time ON temperature_readings(shipment_id, recorded_at);
CREATE INDEX idx_temp_readings_logger_time ON temperature_readings(logger_id, recorded_at);
CREATE INDEX idx_excursion_reports_shipment ON excursion_reports(shipment_id);
