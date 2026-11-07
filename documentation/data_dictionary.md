# Cold Chain Compliance Platform — Data Dictionary & Entity Specifications

## 1. Architectural Overview & Entity Relationships

The data model captures end-to-end pharmaceutical and perishable cold-chain logistics. It models the physical hierarchy (Products & Lots), containment (Packaging), monitoring instrumentation (Loggers), transport journeys (Shipments, RouteStops, CustodyEvents), continuous telemetry (TemperatureReadings), regulatory governance (ThresholdPolicies), and quality deviations (ExcursionReports).

```
   ┌──────────────┐          ┌──────────────────────┐
   │   Product    │1        N│   ThresholdPolicy    │
   │  (Master)    ├──────────┤      (Master)        │
   └──────┬───────┘          └──────────┬───────────┘
          │1                            │
          │N                            │
   ┌──────┴───────┐                     │
   │     Lot      │1                    │
   │  (Master)    │                     │
   └──────┬───────┘                     │
          │1                            │
          │N                            │
   ┌──────┴───────┐N        1┌──────────┴───────────┐
   │   Shipment   ├──────────┤      Packaging       │
   │(Transaction) │          │      (Master)        │
   └──┬───┬───┬───┘          └──────────────────────┘
      │1  │1  │1
      │   │   │
      │N  │N  │N
      │   │   └──────────────────────┐
      │   └──────────────┐           │
      ▼                  ▼           ▼
┌─────────────┐   ┌────────────┐ ┌───────────────┐
│  RouteStop  │1 N│  Custody   │ │Temperature    │
│   (Event)   ├───┤   Event    │ │Reading        │
└─────────────┘   └────────────┘ │  (Telemetry)  │
                                 └───────▲───────┘
                                         │N
                                         │1
                                 ┌───────┴───────┐
                                 │    Logger     │
                                 │(Instrumentation)
                                 └───────▲───────┘
                                         │
   ┌──────────────────────┐              │
   │   ExcursionReport    ├──────────────┘
   │   (Quality/Audit)    │ (Generated from Telemetry + Policy)
   └──────────────────────┘
```

---

## 2. Granular Entity Dictionaries

### 2.1 Table: `products`
- **Description**: Master catalog of pharmaceutical and biologic products requiring temperature control.
- **Cardinality**: 1 Product to N Lots; 1 Product to N ThresholdPolicies.
- **Storage Profile**: Static Master.

| Field Name | Type | Nullable | Primary / Foreign Key | Units / Format | Allowed Values / Enum | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | VARCHAR(32) | NO | PK | `PROD-###` | Alpha-numeric ID | Unique identifier for product (e.g. `PROD-001`). Immutable. |
| `name` | VARCHAR(128) | NO | None | Text | Non-empty string | Commercial or generic name (e.g. `COVID-19 mRNA Vaccine`). |
| `category` | VARCHAR(64) | NO | None | Categorical | `VACCINE`, `BIOLOGIC`, `PHARMA`, `PERISHABLE_FOOD` | Regulated category governing inspection strictness. |
| `storage_class` | VARCHAR(64) | NO | None | Categorical | `ULTRA_LOW` (-80°C to -60°C), `FROZEN` (-25°C to -15°C), `REFRIGERATED` (2°C to 8°C), `CONTROLLED_ROOM_TEMP` (15°C to 25°C) | Standard temperature band according to USP / WHO guidelines. |
| `manufacturer` | VARCHAR(128) | NO | None | Text | Non-empty string | Licensed pharmaceutical manufacturing organization. |
| `created_at` | TIMESTAMP | NO | None | ISO-8601 | YYYY-MM-DD HH:MM:SS | Record audit timestamp. |

---

### 2.2 Table: `packaging`
- **Description**: Thermal packaging systems, passive shippers, and refrigerated containers used to preserve stability.
- **Cardinality**: 1 Packaging Profile to N Shipments.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `packaging_id` | VARCHAR(32) | NO | PK | `PKG-###` | E.g., `PKG-001` | Unique packaging container identifier. |
| `name` | VARCHAR(128) | NO | None | Text | Non-empty | Commercial model (e.g. `Credo Cube Series 4`). |
| `thermal_rating_hours` | NUMERIC(6,2) | NO | None | Hours | > 0 (typically 24.0 to 120.0) | Qualified duration within external ambient profile. |
| `min_temp_c` | NUMERIC(5,2) | NO | None | °Celsius | Real number | Minimum internal temperature rating. |
| `max_temp_c` | NUMERIC(5,2) | NO | None | °Celsius | Real number >= `min_temp_c` | Maximum internal temperature rating. |
| `max_payload_kg` | NUMERIC(6,2) | NO | None | Kilograms | > 0 | Maximum payload mass capacity. |
| `material` | VARCHAR(128) | NO | None | Text | E.g. `VIP + Phase Change Material` | Thermal insulation material specifications. |

---

### 2.3 Table: `threshold_policies`
- **Description**: Quality-approved temperature limits, maximum allowable cumulative excursion duration, and MKT parameters.
- **Cardinality**: 1 Product to N Policies (versioned over effective dates).

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `policy_id` | VARCHAR(32) | NO | PK | `POL-###` | E.g., `POL-001` | Unique regulatory policy identifier. |
| `product_id` | VARCHAR(32) | NO | FK -> `products` | `PROD-###` | Valid `products.product_id` | Foreign key referencing regulated product. |
| `min_temp_c` | NUMERIC(5,2) | NO | None | °Celsius | Real number | Lower specification limit (LSL). E.g., 2.0°C. |
| `max_temp_c` | NUMERIC(5,2) | NO | None | °Celsius | Real number >= `min_temp_c` | Upper specification limit (USL). E.g., 8.0°C. |
| `max_excursion_minutes`| INTEGER | NO | None | Minutes | >= 0 (e.g. 30, 60, 120) | Max cumulative out-of-range duration permitted. |
| `calibration_uncertainty_c` | NUMERIC(4,2) | NO | None | ± °Celsius | Default 0.50 | Logger calibration uncertainty buffer. |
| `mkt_limit_c` | NUMERIC(5,2) | YES | None | °Celsius | Optional | Mean Kinetic Temperature upper threshold limit. |
| `effective_date` | DATE | NO | None | YYYY-MM-DD | Valid date | Start date for quality approval. |
| `expiry_date` | DATE | YES | None | YYYY-MM-DD | Nullable or > effective_date | Expiration of policy version. |

---

### 2.4 Table: `lots`
- **Description**: Specific manufactured batches of products.
- **Cardinality**: 1 Lot to N Shipments; N Lots to 1 Product.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `lot_id` | VARCHAR(32) | NO | PK | `LOT-YYYY-######`| Padded format (e.g. `LOT-2026-000001`)| Unique batch/lot identifier. |
| `product_id` | VARCHAR(32) | NO | FK -> `products` | `PROD-###` | Valid `products.product_id` | Parent product reference. |
| `manufacture_date`| DATE | NO | None | YYYY-MM-DD | Past/present date | Batch release manufacture date. |
| `expiry_date` | DATE | NO | None | YYYY-MM-DD | Must be > `manufacture_date` | Product expiration date. |
| `quantity_units` | INTEGER | NO | None | Units | Integer > 0 | Total manufactured batch quantity. |
| `status` | VARCHAR(32) | NO | None | Categorical | `ACTIVE`, `EXPIRED`, `QUARANTINED`, `RELEASED` | Regulatory lot disposition. |

---

### 2.5 Table: `shipments`
- **Description**: Transport missions transferring products from origin to destination.
- **Cardinality**: 1 Shipment to N TemperatureReadings, N RouteStops, N CustodyEvents, 1 Logger (normally).

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `shipment_id` | VARCHAR(32) | NO | PK | `SHP-YYYY-######`| Padded format (e.g. `SHP-2026-000001`)| Unique shipment identifier. |
| `lot_id` | VARCHAR(32) | NO | FK -> `lots` | `LOT-YYYY-######`| Valid `lots.lot_id` | Child relationship to batch being moved. |
| `packaging_id` | VARCHAR(32) | NO | FK -> `packaging`| `PKG-###` | Valid `packaging.packaging_id` | Packaging container used for shipment. |
| `origin_city` | VARCHAR(64) | NO | None | Text | E.g. `Ahmedabad` | Source departure city. |
| `destination_city` | VARCHAR(64) | NO | None | Text | E.g. `Mumbai` | Destination city. |
| `planned_departure`| TIMESTAMP | NO | None | ISO-8601 | Valid timestamp | Scheduled start. |
| `actual_departure` | TIMESTAMP | NO | None | ISO-8601 | Valid timestamp | Actual dispatch time. |
| `planned_arrival` | TIMESTAMP | NO | None | ISO-8601 | Valid timestamp | Scheduled destination arrival. |
| `actual_arrival` | TIMESTAMP | NO | None | ISO-8601 | >= `actual_departure` | Actual destination delivery time. |
| `carrier_name` | VARCHAR(128) | NO | None | Text | E.g. `BlueDart ColdChain` | Logistics service provider. |
| `compliance_status`| VARCHAR(32) | NO | None | Categorical | `COMPLIANT`, `NON_COMPLIANT`, `INVESTIGATION`, `PENDING` | System determination based on rules. |
| `issue_type` | VARCHAR(64) | YES | None | Text / Tag | Nullable or anomaly label | Ground truth injection flag (for test verification). |

---

### 2.6 Table: `loggers`
- **Description**: Calibrated electronic data logging instrumentation.
- **Cardinality**: 1 Logger to 1 Shipment (active), 1 Logger to N Readings.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `logger_id` | VARCHAR(64) | NO | PK | `LOG-<shipment-id>-01`| E.g. `LOG-SHP-2026-000001-01`| Unique serial identifier. |
| `shipment_id` | VARCHAR(32) | YES | FK -> `shipments`| `SHP-YYYY-######`| Nullable or valid `shipment_id` | Shipment link (NULL = Unassigned Edge Case). |
| `model` | VARCHAR(64) | NO | None | Text | E.g. `ELPRO Libero`, `Sensitech TempTale`| Device hardware model. |
| `calibration_date`| DATE | NO | None | YYYY-MM-DD | Valid date | Date of certified calibration. |
| `calibration_expiry`| DATE | NO | None | YYYY-MM-DD | Must be > `calibration_date` | Calibration certificate validity limit. |
| `reading_interval_min`| INTEGER| NO | None | Minutes | Default 10 | Sampling period between temperature pings. |
| `accuracy_c` | NUMERIC(4,2)| NO | None | ± °Celsius | Default 0.50 | Certified sensor measurement tolerance. |
| `is_active` | BOOLEAN | NO | None | Boolean | 1 / 0 (TRUE/FALSE) | Operational status. |

---

### 2.7 Table: `route_stops`
- **Description**: Origin, intermediate transit hubs, cross-dock facilities, and final destinations.
- **Cardinality**: 1 Shipment to N RouteStops.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `stop_id` | VARCHAR(64) | NO | PK | `STOP-<shipment-id>-##`| Unique stop ID | Sequential waypoint ID. |
| `shipment_id` | VARCHAR(32) | NO | FK -> `shipments` | `SHP-YYYY-######`| Valid `shipment_id` | Associated shipment. |
| `stop_sequence` | INTEGER | NO | None | Sequence index | 1, 2, 3... | Stop sequence order along route. |
| `location_name` | VARCHAR(128)| NO | None | Text | E.g. `Vadodara Transshipment Hub` | Facility or hub title. |
| `city` | VARCHAR(64) | NO | None | Text | E.g. `Vadodara` | Hub city. |
| `planned_arrival` | TIMESTAMP | NO | None | ISO-8601 | Valid timestamp | Scheduled arrival. |
| `actual_arrival` | TIMESTAMP | YES | None | ISO-8601 | Valid timestamp | Recorded gate entry. |
| `planned_departure`| TIMESTAMP | NO | None | ISO-8601 | Valid timestamp | Scheduled departure. |
| `actual_departure` | TIMESTAMP | YES | None | ISO-8601 | Valid timestamp | Recorded dispatch. |
| `dwell_hours` | NUMERIC(5,2)| YES | None | Hours | >= 0 | Dwell time at hub (`actual_departure - actual_arrival`). |
| `stop_type` | VARCHAR(32) | NO | None | Categorical | `ORIGIN`, `WAYPOINT`, `DESTINATION` | Transit stop classification. |

---

### 2.8 Table: `custody_events`
- **Description**: Legal chain-of-custody handovers across operators, drivers, and warehouse staff.
- **Cardinality**: 1 Shipment to N CustodyEvents.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `custody_id` | VARCHAR(64) | NO | PK | `CUST-<shipment-id>-##`| Unique custody ID | Traceable handover event ID. |
| `shipment_id` | VARCHAR(32) | NO | FK -> `shipments` | `SHP-YYYY-######`| Valid `shipment_id` | Associated journey. |
| `stop_id` | VARCHAR(64) | YES | FK -> `route_stops`| `STOP-...` | Nullable or valid `stop_id` | Physical location where transfer took place. |
| `handover_time` | TIMESTAMP | NO | None | ISO-8601 | Valid timestamp | Exact handover clock time. |
| `from_party` | VARCHAR(128)| NO | None | Text | Individual / Entity name | Releasing operator or driver. |
| `to_party` | VARCHAR(128)| NO | None | Text | Individual / Entity name | Receiving operator or driver. |
| `from_party_role` | VARCHAR(64) | NO | None | Categorical | `SUPPLIER`, `CARRIER`, `WAREHOUSE`, `RECIPIENT` | Releasing organization role. |
| `to_party_role` | VARCHAR(64) | NO | None | Categorical | `SUPPLIER`, `CARRIER`, `WAREHOUSE`, `RECIPIENT` | Receiving organization role. |
| `signature_obtained`| BOOLEAN | NO | None | Boolean | 1 / 0 | Electronic signature capture flag. |
| `notes` | TEXT | YES | None | Text | Additional remarks | Condition notes, seal number verification. |
| `gap_flag` | BOOLEAN | NO | None | Boolean | 0 (Normal), 1 (Anomaly) | Indicates an unaccounted custody interval. |

---

### 2.9 Table: `temperature_readings`
- **Description**: Time-series telemetry readings from IoT loggers.
- **Cardinality**: 1 Shipment & 1 Logger to N Readings.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `reading_id` | VARCHAR(96) | NO | PK | `TEMP-<logger-id>-<timestamp>`| E.g. `TEMP-LOG-...-202610221000` | Deterministic telemetry point ID. |
| `logger_id` | VARCHAR(64) | NO | FK -> `loggers` | `LOG-...` | Valid `loggers.logger_id` | Sensing device identifier. |
| `shipment_id` | VARCHAR(32) | NO | FK -> `shipments`| `SHP-...` | Valid `shipments.shipment_id`| Transport journey identifier. |
| `recorded_at` | TIMESTAMP | NO | None | ISO-8601 | 10-minute cadence | Observation timestamp. |
| `temperature_c` | NUMERIC(5,2)| NO | None | °Celsius | Numeric (-90.00 to 50.00) | Physical temperature measurement. |
| `is_excursion` | BOOLEAN | NO | None | Boolean | 1 if out of threshold, else 0 | Single-point threshold breach flag. |
| `is_gap_filled` | BOOLEAN | NO | None | Boolean | 1 if synthetically imputed, else 0 | Data provenance flag. |
| `quality_flag` | VARCHAR(32) | NO | None | Categorical | `NORMAL`, `MISSING`, `SUSPECT`, `GAP` | Quality & calibration tolerance status. |

---

### 2.10 Table: `excursion_reports`
- **Description**: Quality deviation incident reports created when excursions or anomalies occur.
- **Cardinality**: 1 Shipment to N Reports; 1 Report to 1 Shipment.

| Field Name | Type | Nullable | Key | Units / Format | Allowed Values | Description & Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `excursion_id` | VARCHAR(32) | NO | PK | `EXCR-YYYY-######`| E.g. `EXCR-2026-000001` | Unique deviation record number. |
| `shipment_id` | VARCHAR(32) | NO | FK -> `shipments` | `SHP-...` | Valid `shipment_id` | Associated shipment under investigation. |
| `logger_id` | VARCHAR(64) | YES | FK -> `loggers` | `LOG-...` | Nullable or valid logger | Device producing evidence. |
| `policy_id` | VARCHAR(32) | YES | FK -> `threshold_policies`| `POL-...` | Nullable or valid policy | Benchmark criteria applied. |
| `excursion_start` | TIMESTAMP | NO | None | ISO-8601 | Start of breach | Initial deviation timestamp. |
| `excursion_end` | TIMESTAMP | NO | None | ISO-8601 | End of breach | Final deviation timestamp. |
| `duration_minutes`| INTEGER | NO | None | Minutes | Integer >= 0 | Cumulative duration out of range. |
| `max_temp_recorded_c`| NUMERIC(5,2)| NO | None | °Celsius | Observed max | Peak temperature during event. |
| `min_temp_recorded_c`| NUMERIC(5,2)| NO | None | °Celsius | Observed min | Lowest temperature during event. |
| `excursion_type` | VARCHAR(32) | NO | None | Categorical | `HIGH_TEMP`, `LOW_TEMP`, `MISSING_DATA`, `CUSTODY_GAP`, `POLICY_MISMATCH`, `UNASSIGNED_LOGGER` | Nature of quality deviation. |
| `severity` | VARCHAR(32) | NO | None | Categorical | `MINOR`, `MAJOR`, `CRITICAL` | Risk severity based on duration & delta. |
| `disposition` | VARCHAR(32) | NO | None | Categorical | `PENDING`, `ACCEPTED`, `REJECTED`, `QUARANTINE` | Quality assurance sign-off status. |
| `issue_type` | VARCHAR(64) | YES | None | Text | Ground truth tag | Used for benchmark evaluation. |
| `root_cause` | TEXT | YES | None | Free text | Investigation narrative | Detailed diagnostic explanation. |
| `created_at` | TIMESTAMP | NO | None | ISO-8601 | Record timestamp | Creation date/time. |
