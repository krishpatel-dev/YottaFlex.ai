-- ============================================================================
-- Cold Chain Compliance Platform: Initial Seed Data
-- Master Catalog, Packaging, Threshold Policies, and Sample Transactions
-- ============================================================================

-- 1. Products Master
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-001', 'COVID-19 mRNA Vaccine', 'VACCINE', 'ULTRA_LOW', 'BioTech Global Corp', '2025-01-15 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-002', 'Rotavirus Oral Vaccine', 'VACCINE', 'REFRIGERATED', 'Serum Institute Bio', '2025-01-25 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-003', 'Hepatitis B Recombinant Vaccine', 'VACCINE', 'REFRIGERATED', 'Bharat Pharma Innovations', '2025-02-04 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-004', 'Human Recombinant Insulin 100IU', 'BIOLOGIC', 'REFRIGERATED', 'Novo Health Sciences', '2025-02-14 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-005', 'Monoclonal Antibody (Oncology)', 'BIOLOGIC', 'REFRIGERATED', 'Roche Bio Therapeutics', '2025-02-24 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-006', 'Immune Globulin Intravenous (IGIV)', 'BIOLOGIC', 'REFRIGERATED', 'Baxalta Life Sciences', '2025-03-06 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-007', 'Varicella Zoster Live Vaccine', 'VACCINE', 'FROZEN', 'Merck Bio Vaccine', '2025-03-16 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-008', 'MMR Triple Antigen Vaccine', 'VACCINE', 'REFRIGERATED', 'Sanofi Pasteur Med', '2025-03-26 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-009', 'Lyophilized Plasma Protein', 'BIOLOGIC', 'CONTROLLED_ROOM_TEMP', 'CSL Bio Formulations', '2025-04-05 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-010', 'Oxytocin Injection 10IU/ml', 'PHARMA', 'REFRIGERATED', 'Novartis Healthcare', '2025-04-15 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-011', 'Enoxaparin Sodium Pre-filled', 'PHARMA', 'CONTROLLED_ROOM_TEMP', 'Aventis Generics', '2025-04-25 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-012', 'Probiotic Bio-Culture Sachets', 'PERISHABLE_FOOD', 'REFRIGERATED', 'Yakult Bio Nutrients', '2025-05-05 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-013', 'Enzyme Replacement Therapy Infusion', 'BIOLOGIC', 'REFRIGERATED', 'Genzyme Therapeutics', '2025-05-15 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-014', 'Dengue Tetravalent Vaccine', 'VACCINE', 'REFRIGERATED', 'Takeda Pharma India', '2025-05-25 08:00:00');
INSERT INTO products (product_id, name, category, storage_class, manufacturer, created_at) VALUES ('PROD-015', 'Fresh Frozen Medical Diagnostic Reagent', 'BIOLOGIC', 'FROZEN', 'Abbott Diagnostics', '2025-06-04 08:00:00');

-- 2. Packaging Master
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-001', 'Credo Cube VIP Shipper 12L', 72.0, 2.0, 8.0, 15.0, 'Vacuum Insulated Panels + TIC PCM');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-002', 'Credo Cube Deep Frozen 28L', 96.0, -25.0, -15.0, 22.0, 'VIP + Dry Ice System');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-003', 'AcuTemp Ultra-Cold Shipper 50L', 120.0, -85.0, -60.0, 35.0, 'VIP Vacuum Core + Liquid N2 Vapor');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-004', 'BioTherm Insulated Box 10L', 48.0, 2.0, 8.0, 10.0, 'Expanded Polystyrene + Water Gel Packs');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-005', 'PharmaTrans Active CRT Container 100L', 96.0, 15.0, 25.0, 80.0, 'Active Thermo-Electric Peltier Shell');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-006', 'BioCourier Heavy Cargo 250L', 72.0, 2.0, 8.0, 180.0, 'Polyurethane Foam + Gel Panels');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-007', 'AeroChill Express Frozen 15L', 48.0, -25.0, -15.0, 12.0, 'VIP + Phase 22 Frozen PCM');
INSERT INTO packaging (packaging_id, name, thermal_rating_hours, min_temp_c, max_temp_c, max_payload_kg, material) VALUES ('PKG-008', 'TempStable Ambient Shield 30L', 60.0, 15.0, 25.0, 25.0, 'Reflective Multi-foil Air Gel');

-- 3. Threshold Policies
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-001', 'PROD-001', -80.0, -60.0, 15, 0.5, -65.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-002', 'PROD-002', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-003', 'PROD-003', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-004', 'PROD-004', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-005', 'PROD-005', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-006', 'PROD-006', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-007', 'PROD-007', -25.0, -15.0, 30, 0.5, -18.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-008', 'PROD-008', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-009', 'PROD-009', 15.0, 25.0, 60, 0.5, 20.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-010', 'PROD-010', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-011', 'PROD-011', 15.0, 25.0, 60, 0.5, 20.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-012', 'PROD-012', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-013', 'PROD-013', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-014', 'PROD-014', 2.0, 8.0, 30, 0.5, 5.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-015', 'PROD-015', -25.0, -15.0, 30, 0.5, -18.0, '2025-01-01', '2027-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-016', 'PROD-001', -85.0, -65.0, 10, 0.3, -70.0, '2026-01-01', '2028-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-017', 'PROD-002', 2.0, 6.0, 20, 0.2, 4.0, '2026-01-01', '2028-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-018', 'PROD-004', 2.0, 8.0, 15, 0.3, 4.5, '2026-01-01', '2028-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-019', 'PROD-005', 2.0, 8.0, 20, 0.25, 4.8, '2026-01-01', '2028-12-31');
INSERT INTO threshold_policies (policy_id, product_id, min_temp_c, max_temp_c, max_excursion_minutes, calibration_uncertainty_c, mkt_limit_c, effective_date, expiry_date) VALUES ('POL-020', 'PROD-007', -25.0, -18.0, 20, 0.3, -20.0, '2026-01-01', '2028-12-31');
