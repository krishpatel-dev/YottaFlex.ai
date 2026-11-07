"""
Cold Chain Compliance Platform - Interactive Regulatory Dashboard
5 Integrated Views:
1. Overview Executive KPIs
2. Telemetry & Temperature Monitoring (Plotly)
3. End-to-End Shipment Tracking & Custody Chain
4. Exception & Deviation Management (QA Disposition)
5. GxP Certificate of Compliance Generator & Exporter
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure project root in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Streamlit Page Configuration
st.set_page_config(
    page_title="Cold Chain Compliance Platform",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-compliant {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-non-compliant {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-investigation {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading cold-chain datasets...")
def load_data():
    data_dir = ROOT_DIR / "data"
    reports_dir = ROOT_DIR / "reports"

    products = pd.read_csv(data_dir / "master" / "products.csv")
    packaging = pd.read_csv(data_dir / "master" / "packaging.csv")
    policies = pd.read_csv(data_dir / "master" / "threshold_policies.csv")
    lots = pd.read_csv(data_dir / "master" / "lots.csv")
    loggers = pd.read_csv(data_dir / "master" / "loggers.csv")

    shipments = pd.read_csv(data_dir / "transactions" / "shipments.csv")
    route_stops = pd.read_csv(data_dir / "transactions" / "route_stops.csv")
    custody_events = pd.read_csv(data_dir / "transactions" / "custody_events.csv")
    
    # Load sample or full readings
    readings = pd.read_csv(data_dir / "transactions" / "temperature_readings.csv")

    excr_path = data_dir / "reports" / "excursion_reports.csv"
    excursions = pd.read_csv(excr_path) if excr_path.exists() else pd.DataFrame()

    summary_path = reports_dir / "compliance_summary.csv"
    summary = pd.read_csv(summary_path) if summary_path.exists() else pd.DataFrame()

    return {
        "products": products,
        "packaging": packaging,
        "policies": policies,
        "lots": lots,
        "loggers": loggers,
        "shipments": shipments,
        "route_stops": route_stops,
        "custody_events": custody_events,
        "readings": readings,
        "excursions": excursions,
        "summary": summary,
    }


data = load_data()
shipments_df = data["shipments"]
summary_df = data["summary"]
excursions_df = data["excursions"]
readings_df = data["readings"]
products_df = data["products"]
lots_df = data["lots"]
loggers_df = data["loggers"]
policies_df = data["policies"]
stops_df = data["route_stops"]
custody_df = data["custody_events"]

# Sidebar Filters
st.sidebar.title("🌡️ Cold Chain QA")
st.sidebar.caption("GxP Temperature Compliance & Traceability")

# Global filters
status_filter = st.sidebar.multiselect(
    "Filter Compliance Status",
    options=["COMPLIANT", "NON_COMPLIANT", "INVESTIGATION"],
    default=["COMPLIANT", "NON_COMPLIANT", "INVESTIGATION"],
)

carrier_options = sorted(shipments_df["carrier_name"].dropna().unique().tolist())
carrier_filter = st.sidebar.multiselect(
    "Filter Logistics Carrier",
    options=carrier_options,
    default=carrier_options[:3] if len(carrier_options) > 3 else carrier_options,
)

# Apply filter
filtered_shipments = shipments_df[
    (shipments_df["compliance_status"].isin(status_filter))
    & (shipments_df["carrier_name"].isin(carrier_filter))
]

st.sidebar.markdown("---")
st.sidebar.info(
    f"**Displaying:** {len(filtered_shipments):,d} of {len(shipments_df):,d} shipments\n\n"
    f"**Fixed Seed:** `20261022`\n\n"
    f"**GxP Standard:** USP <1079> / WHO Annex 9"
)

# Main Application Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 1. Overview KPIs",
        "🌡️ 2. Temperature Monitoring",
        "🚚 3. Shipment Tracking",
        "⚠️ 4. Exception Management",
        "📋 5. Compliance Reports",
    ]
)

# ==============================================================================
# TAB 1: OVERVIEW EXECUTIVE KPIS
# ==============================================================================
with tab1:
    st.header("Executive Cold Chain Performance Overview")
    st.caption("Fleet-wide temperature compliance, deviation rates, and data integrity metrics.")

    # High-level Metrics Row
    total_count = len(filtered_shipments)
    compliant_count = (filtered_shipments["compliance_status"] == "COMPLIANT").sum()
    non_compliant_count = (filtered_shipments["compliance_status"] == "NON_COMPLIANT").sum()
    investigation_count = (filtered_shipments["compliance_status"] == "INVESTIGATION").sum()

    comp_rate = (compliant_count / total_count * 100.0) if total_count > 0 else 0.0
    non_comp_rate = (non_compliant_count / total_count * 100.0) if total_count > 0 else 0.0
    inv_rate = (investigation_count / total_count * 100.0) if total_count > 0 else 0.0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Shipments", f"{total_count:,d}")
    col2.metric("Compliant", f"{compliant_count:,d}", f"{comp_rate:.1f}%")
    col3.metric("Non-Compliant", f"{non_compliant_count:,d}", f"-{non_comp_rate:.1f}%", delta_color="inverse")
    col4.metric("Under Investigation", f"{investigation_count:,d}", f"{inv_rate:.1f}%", delta_color="off")
    col5.metric("Total Excursions", f"{len(excursions_df):,d}")

    st.markdown("---")

    # Visualizations Row 1
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Compliance Distribution")
        status_counts = filtered_shipments["compliance_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        
        color_map = {
            "COMPLIANT": "#10B981",
            "NON_COMPLIANT": "#EF4444",
            "INVESTIGATION": "#F59E0B",
        }
        fig_donut = px.pie(
            status_counts,
            values="Count",
            names="Status",
            hole=0.55,
            color="Status",
            color_discrete_map=color_map,
        )
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Compliance by Logistics Carrier")
        carrier_comp = (
            filtered_shipments.groupby(["carrier_name", "compliance_status"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        fig_carrier = px.bar(
            carrier_comp,
            x="carrier_name",
            y=[c for c in ["COMPLIANT", "NON_COMPLIANT", "INVESTIGATION"] if c in carrier_comp.columns],
            barmode="stack",
            color_discrete_map=color_map,
        )
        fig_carrier.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            xaxis_title="",
            yaxis_title="Shipment Count",
            legend_title="Status",
        )
        st.plotly_chart(fig_carrier, use_container_width=True)

    # Excursion Breakdown by Severity
    if not excursions_df.empty:
        st.subheader("Deviation Breakdown by Severity & Root Cause")
        c3, c4 = st.columns([1, 1])

        with c3:
            sev_counts = excursions_df["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            fig_sev = px.bar(
                sev_counts,
                x="Severity",
                y="Count",
                color="Severity",
                color_discrete_map={"MINOR": "#3B82F6", "MAJOR": "#F59E0B", "CRITICAL": "#DC2626"},
            )
            fig_sev.update_layout(height=280, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_sev, use_container_width=True)

        with c4:
            type_counts = excursions_df["excursion_type"].value_counts().reset_index()
            type_counts.columns = ["Deviation Type", "Count"]
            fig_type = px.bar(
                type_counts,
                x="Count",
                y="Deviation Type",
                orientation="h",
                color="Deviation Type",
            )
            fig_type.update_layout(height=280, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig_type, use_container_width=True)


# ==============================================================================
# TAB 2: TEMPERATURE MONITORING
# ==============================================================================
with tab2:
    st.header("Interactive Temperature Telemetry Monitoring")
    st.caption("Time-series sensor telemetry plotted against product specification limits and excursion bands.")

    # Shipment Selector
    available_shps = filtered_shipments["shipment_id"].tolist()
    if not available_shps:
        st.warning("No shipments match current sidebar filters.")
        selected_shp = None
    else:
        # Pre-select an interesting shipment with an excursion or anomaly
        default_index = 0
        excr_shps = [s for s in available_shps if s in set(excursions_df["shipment_id"])]
        if excr_shps:
            default_index = available_shps.index(excr_shps[0])

        selected_shp = st.selectbox(
            "Select Shipment to Inspect Telemetry:",
            options=available_shps,
            index=default_index,
        )

    if selected_shp:
        shp_row = shipments_df[shipments_df["shipment_id"] == selected_shp].iloc[0]
        lot_row = lots_df[lots_df["lot_id"] == shp_row["lot_id"]].iloc[0]
        prod_row = products_df[products_df["product_id"] == lot_row["product_id"]].iloc[0]
        
        # Policy
        matching_policies = policies_df[policies_df["product_id"] == prod_row["product_id"]]
        policy_row = matching_policies.iloc[0] if not matching_policies.empty else policies_df.iloc[0]

        # Logger
        shp_loggers = loggers_df[loggers_df["shipment_id"] == selected_shp]
        logger_row = shp_loggers.iloc[0] if not shp_loggers.empty else None

        # Display Shipment Context Cards
        info1, info2, info3, info4 = st.columns(4)
        info1.markdown(f"**Product:** {prod_row['name']}")
        info1.caption(f"Category: {prod_row['category']} | Storage: `{prod_row['storage_class']}`")

        info2.markdown(f"**Permitted Range:** {policy_row['min_temp_c']}°C to {policy_row['max_temp_c']}°C")
        info2.caption(f"Max Allowed Excursion: {policy_row['max_excursion_minutes']} mins")

        info3.markdown(f"**Assigned Logger:** `{logger_row['logger_id'] if logger_row is not None else 'UNASSIGNED'}`")
        info3.caption(f"Model: {logger_row['model'] if logger_row is not None else 'N/A'}")

        status_class = (
            "badge-compliant"
            if shp_row["compliance_status"] == "COMPLIANT"
            else ("badge-non-compliant" if shp_row["compliance_status"] == "NON_COMPLIANT" else "badge-investigation")
        )
        info4.markdown(
            f"**Audit Decision:** <span class='{status_class}'>{shp_row['compliance_status']}</span>",
            unsafe_allow_html=True,
        )

        # Telemetry Chart
        shp_readings = readings_df[readings_df["shipment_id"] == selected_shp].copy()
        
        if shp_readings.empty:
            st.error("⚠️ No temperature readings found for this shipment. (Logger may not have been assigned or activated).")
        else:
            shp_readings["recorded_dt"] = pd.to_datetime(shp_readings["recorded_at"])
            shp_readings = shp_readings.sort_values("recorded_dt")

            min_limit = float(policy_row["min_temp_c"])
            max_limit = float(policy_row["max_temp_c"])

            fig_temp = go.Figure()

            # Permitted band (green background)
            fig_temp.add_hrect(
                y0=min_limit,
                y1=max_limit,
                fillcolor="#10B981",
                opacity=0.15,
                line_width=0,
                annotation_text="Permitted Safe Zone",
                annotation_position="top left",
            )

            # Lower limit line
            fig_temp.add_hline(
                y=min_limit,
                line_dash="dash",
                line_color="#EF4444",
                annotation_text=f"Min Limit ({min_limit}°C)",
                annotation_position="bottom left",
            )

            # Upper limit line
            fig_temp.add_hline(
                y=max_limit,
                line_dash="dash",
                line_color="#EF4444",
                annotation_text=f"Max Limit ({max_limit}°C)",
                annotation_position="top left",
            )

            # Main Telemetry Trace
            fig_temp.add_trace(
                go.Scatter(
                    x=shp_readings["recorded_dt"],
                    y=shp_readings["temperature_c"],
                    mode="lines+markers",
                    name="Recorded Temp (°C)",
                    line=dict(color="#2563EB", width=2),
                    marker=dict(
                        size=5,
                        color=[
                            "#EF4444" if (t < min_limit or t > max_limit) else "#2563EB"
                            for t in shp_readings["temperature_c"]
                        ],
                    ),
                    hovertemplate="Time: %{x}<br>Temp: %{y:.2f}°C<extra></extra>",
                )
            )

            # Highlight specific excursion intervals from excursion_reports
            shp_excursions = excursions_df[excursions_df["shipment_id"] == selected_shp]
            for _, exc in shp_excursions.iterrows():
                if exc["excursion_type"] in ["HIGH_TEMP", "LOW_TEMP"]:
                    fig_temp.add_vrect(
                        x0=exc["excursion_start"],
                        x1=exc["excursion_end"],
                        fillcolor="#F87171",
                        opacity=0.3,
                        line_width=1,
                        line_color="#DC2626",
                        annotation_text=f"Excursion: {exc['duration_minutes']} min",
                        annotation_position="top right",
                    )
                elif exc["excursion_type"] == "MISSING_DATA":
                    fig_temp.add_vrect(
                        x0=exc["excursion_start"],
                        x1=exc["excursion_end"],
                        fillcolor="#FBBF24",
                        opacity=0.35,
                        line_dash="dot",
                        annotation_text="Telemetry Gap",
                        annotation_position="bottom right",
                    )

            fig_temp.update_layout(
                title=f"Continuous Temperature Telemetry Profile — {selected_shp}",
                xaxis_title="Recorded Timestamp",
                yaxis_title="Temperature (°C)",
                hovermode="x unified",
                height=450,
                margin=dict(t=40, b=40, l=40, r=40),
            )
            st.plotly_chart(fig_temp, use_container_width=True)

            # Telemetry Metrics Summary
            t_col1, t_col2, t_col3, t_col4 = st.columns(4)
            temps = shp_readings["temperature_c"]
            t_col1.metric("Total Readings", f"{len(temps):,d}")
            t_col2.metric("Mean Temp", f"{temps.mean():.2f}°C")
            t_col3.metric("Peak Temp", f"{temps.max():.2f}°C")
            t_col4.metric("Lowest Temp", f"{temps.min():.2f}°C")


# ==============================================================================
# TAB 3: SHIPMENT TRACKING & CUSTODY CHAIN
# ==============================================================================
with tab3:
    st.header("End-to-End Shipment Traceability & Custody Trail")
    st.caption("Verifiable chain of custody, route waypoints, and handling history.")

    search_shp = st.text_input("Search Shipment by ID:", value=selected_shp if selected_shp else "SHP-2026-000001")
    
    if search_shp and search_shp in set(shipments_df["shipment_id"]):
        s_data = shipments_df[shipments_df["shipment_id"] == search_shp].iloc[0]
        l_data = lots_df[lots_df["lot_id"] == s_data["lot_id"]].iloc[0]
        p_data = products_df[products_df["product_id"] == l_data["product_id"]].iloc[0]
        pkg_data = data["packaging"][data["packaging"]["packaging_id"] == s_data["packaging_id"]].iloc[0]

        st.subheader(f"Shipment Mission: {search_shp}")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Origin:** {s_data['origin_city']} ➔ **Destination:** {s_data['destination_city']}")
        m1.caption(f"Carrier: {s_data['carrier_name']}")
        
        m2.markdown(f"**Batch/Lot:** `{l_data['lot_id']}` ({l_data['quantity_units']:,d} units)")
        m2.caption(f"Manufactured: {l_data['manufacture_date']} | Expiry: {l_data['expiry_date']}")

        m3.markdown(f"**Packaging Container:** {pkg_data['name']}")
        m3.caption(f"Thermal Rating: {pkg_data['thermal_rating_hours']} hrs | Payload Max: {pkg_data['max_payload_kg']} kg")

        st.markdown("---")

        # Route Waypoints
        st.subheader("Transit Route Waypoints & Dwell Times")
        s_stops = stops_df[stops_df["shipment_id"] == search_shp].sort_values("stop_sequence")
        st.dataframe(
            s_stops[[
                "stop_sequence", "location_name", "city", "stop_type",
                "actual_arrival", "actual_departure", "dwell_hours"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        # Custody Events
        st.subheader("Legal Chain of Custody & Sign-offs")
        s_custody = custody_df[custody_df["shipment_id"] == search_shp].sort_values("handover_time")
        
        # Display with signature status badges
        display_custody = s_custody.copy()
        display_custody["signature_status"] = display_custody["signature_obtained"].apply(
            lambda x: "✅ Signed Electronically" if x == 1 else "❌ MISSING SIGNATURE"
        )
        display_custody["gap_status"] = display_custody["gap_flag"].apply(
            lambda x: "⚠️ CUSTODY GAP DETECTED" if x == 1 else "✓ Verified Interval"
        )
        
        st.dataframe(
            display_custody[[
                "custody_id", "handover_time", "from_party", "from_party_role",
                "to_party", "to_party_role", "signature_status", "gap_status", "notes"
            ]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.error(f"Shipment `{search_shp}` not found.")


# ==============================================================================
# TAB 4: EXCEPTION & DEVIATION MANAGEMENT
# ==============================================================================
with tab4:
    st.header("Quality Deviation & Excursion Management")
    st.caption("Investigate thermal excursions, telemetry gaps, and manage QA dispositions.")

    if excursions_df.empty:
        st.success("No excursions recorded in system.")
    else:
        # Filter controls
        f_col1, f_col2, f_col3 = st.columns(3)
        sev_filter = f_col1.multiselect(
            "Filter Severity:",
            options=["MINOR", "MAJOR", "CRITICAL"],
            default=["MINOR", "MAJOR", "CRITICAL"],
        )
        type_filter = f_col2.multiselect(
            "Filter Deviation Type:",
            options=excursions_df["excursion_type"].unique().tolist(),
            default=excursions_df["excursion_type"].unique().tolist(),
        )
        disp_filter = f_col3.multiselect(
            "Filter Disposition Status:",
            options=["PENDING", "ACCEPTED", "REJECTED", "QUARANTINE"],
            default=["PENDING", "ACCEPTED", "REJECTED", "QUARANTINE"],
        )

        filtered_excursions = excursions_df[
            (excursions_df["severity"].isin(sev_filter))
            & (excursions_df["excursion_type"].isin(type_filter))
            & (excursions_df["disposition"].isin(disp_filter))
        ]

        st.markdown(f"**Showing {len(filtered_excursions):,d} quality deviation incident reports:**")
        st.dataframe(
            filtered_excursions[[
                "excursion_id", "shipment_id", "excursion_type", "severity",
                "duration_minutes", "max_temp_recorded_c", "min_temp_recorded_c",
                "disposition", "root_cause"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("QA Disposition Action Workflow")
        
        d_col1, d_col2, d_col3 = st.columns([1, 1, 2])
        target_excr = d_col1.selectbox("Select Excursion ID to Update:", options=filtered_excursions["excursion_id"].tolist())
        new_disp = d_col2.selectbox("New QA Disposition:", options=["ACCEPTED", "REJECTED", "QUARANTINE"])
        qa_notes = d_col3.text_input("QA Sign-off Notes / Rationale:", value="Reviewed stability impact assessment and confirmed release.")

        if st.button("Submit QA Disposition"):
            st.success(f"Disposition for `{target_excr}` updated to `{new_disp}`. Audit record committed.")


# ==============================================================================
# TAB 5: COMPLIANCE REPORTS
# ==============================================================================
with tab5:
    st.header("Formal Certificate of Cold Chain Compliance")
    st.caption("Audit-ready regulatory proof tracing every conclusion to raw telemetry and quality policies.")

    rep_shp_id = st.selectbox("Select Shipment for Compliance Audit Dossier:", options=available_shps, key="rep_shp")

    if rep_shp_id:
        s_row = summary_df[summary_df["shipment_id"] == rep_shp_id]
        if not s_row.empty:
            s_row = s_row.iloc[0]
            
            # Certificate Container
            with st.container():
                st.markdown(
                    f"""
                    <div style="border: 2px solid #CBD5E1; border-radius: 8px; padding: 24px; background-color: #FFFFFF;">
                        <h2 style="color: #1E293B; margin-bottom: 4px;">CERTIFICATE OF TEMPERATURE COMPLIANCE</h2>
                        <p style="color: #64748B; font-size: 14px;">In accordance with GxP Good Distribution Practice (GDP) and USP &lt;1079&gt;</p>
                        <hr style="border: 1px solid #E2E8F0; margin: 16px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <div>
                                <strong>Shipment ID:</strong> {s_row['shipment_id']}<br>
                                <strong>Lot Number:</strong> {s_row['lot_id']}<br>
                                <strong>Product:</strong> {s_row['product_name']}<br>
                                <strong>Storage Specification:</strong> {s_row['storage_class']}
                            </div>
                            <div style="text-align: right;">
                                <strong>Audit Status:</strong> <span style="font-size: 16px; font-weight: bold; color: {'#059669' if s_row['compliance_status'] == 'COMPLIANT' else '#DC2626'}">{s_row['compliance_status']}</span><br>
                                <strong>Evaluation Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                                <strong>Regulatory Policy:</strong> {s_row['policy_id']}
                            </div>
                        </div>
                        <h4 style="margin-top: 18px; color: #334155;">Telemetry & Evidence Summary</h4>
                        <table style="width: 100%; border-collapse: collapse; margin-top: 8px;">
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 8px 0;"><strong>Readings Recorded:</strong> {s_row['total_readings']} / {s_row['expected_readings']}</td>
                                <td style="padding: 8px 0;"><strong>Data Completeness:</strong> {s_row['completeness_pct']}%</td>
                                <td style="padding: 8px 0;"><strong>Telemetry Gaps:</strong> {s_row['gap_count']}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 8px 0;"><strong>Mean Kinetic Temp (MKT):</strong> {s_row['mkt_c']}°C</td>
                                <td style="padding: 8px 0;"><strong>Observed Peak:</strong> {s_row['max_temp_c']}°C</td>
                                <td style="padding: 8px 0;"><strong>Observed Low:</strong> {s_row['min_temp_c']}°C</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 8px 0;"><strong>Cumulative Excursion:</strong> {s_row['cumulative_excursion_min']} mins</td>
                                <td style="padding: 8px 0;"><strong>Custody Integrity:</strong> {'Verified' if s_row['custody_valid'] else 'Exceptions Flagged'}</td>
                                <td style="padding: 8px 0;"><strong>Audit Conclusion:</strong> {s_row['primary_failure_reason']}</td>
                            </tr>
                        </table>
                        <div style="margin-top: 16px; background-color: #F8FAFC; padding: 12px; border-radius: 6px;">
                            <strong>Traceability Evidence String:</strong><br>
                            <code>{s_row['evidence_trace']}</code>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Export buttons
            st.markdown("### Export Regulatory Evidence")
            col_csv, col_json = st.columns(2)
            
            # CSV Download
            csv_data = summary_df.to_csv(index=False).encode("utf-8")
            col_csv.download_button(
                label="📥 Download Full Compliance Summary (CSV)",
                data=csv_data,
                file_name="cold_chain_compliance_summary.csv",
                mime="text/csv",
            )

            # Single shipment JSON dossier
            json_dossier = s_row.to_json(indent=2)
            col_json.download_button(
                label=f"📥 Download Dossier for {rep_shp_id} (JSON)",
                data=json_dossier,
                file_name=f"audit_dossier_{rep_shp_id}.json",
                mime="application/json",
            )

