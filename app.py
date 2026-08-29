"""
Dash2BI AI — Main Streamlit Application Entrypoint.
Reconstructs Power BI Reports and Power BI Projects (PBIP/PBIR/TMDL) from Excel/CSV Datasets and HTML Dashboard Designs.
"""

import os
import tempfile
import json
import streamlit as st
import pandas as pd

from src.utils.logging import log_event
from src.utils.file_validation import validate_dataset_file, validate_html_file
from src.utils.errors import Dash2BIError
from src.data.dataset_loader import inspect_excel_sheets
from src.data.dataset_profiler import profile_dataset, DatasetProfile
from src.html.html_loader import load_html_dashboard
from src.html.visual_detector import analyze_html_dashboard
from src.ai.semantic_mapper import run_ai_semantic_mapping
from src.ai.anthropic_provider import AnthropicProvider
from src.mapping.visual_mapper import map_all_visuals
from src.mapping.mapping_validator import compute_reconstruction_score
from src.dax.measure_generator import generate_dax_for_mapped_visuals
from src.powerbi.model_generator import build_semantic_model_spec
from src.powerbi.pbip_generator import create_pbip_project_folder
from src.powerbi.validation import validate_project_before_export
from src.powerbi.export_manager import package_pbip_as_zip, generate_analysis_report_markdown

from src.preview.mapping_view import render_mapping_review_table
from src.preview.dashboard_preview import render_reconstruction_wireframe
from src.preview.validation_view import render_validation_summary

# Streamlit Page Config
st.set_page_config(
    page_title="Dash2BI AI — Dashboard to Power BI Converter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
        .main-header {
            font-size: 2.3rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #475569;
            margin-bottom: 25px;
        }
        .status-badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge-ready { background-color: #DCFCE7; color: #166534; }
        .badge-review { background-color: #FEF3C7; color: #92400E; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "step" not in st.session_state:
    st.session_state.step = 1
if "dataset_file" not in st.session_state:
    st.session_state.dataset_file = None
if "html_file" not in st.session_state:
    st.session_state.html_file = None
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None
if "dataset_profile" not in st.session_state:
    st.session_state.dataset_profile = None
if "html_visuals" not in st.session_state:
    st.session_state.html_visuals = None
if "mapped_visuals" not in st.session_state:
    st.session_state.mapped_visuals = None
if "ai_enabled" not in st.session_state:
    st.session_state.ai_enabled = False

# Sidebar
st.sidebar.title("📊 Dash2BI AI")
st.sidebar.markdown("**Workflow Navigation**")
nav_step = st.sidebar.radio(
    "Steps:",
    ["STEP 1 — Upload", "STEP 2 — Analyze", "STEP 3 — Preview & Map", "STEP 4 — Convert & Download"],
    index=st.session_state.step - 1
)

# Update step if clicked
if nav_step.startswith("STEP 1"):
    st.session_state.step = 1
elif nav_step.startswith("STEP 2"):
    st.session_state.step = 2
elif nav_step.startswith("STEP 3"):
    st.session_state.step = 3
elif nav_step.startswith("STEP 4"):
    st.session_state.step = 4

# Header
st.markdown('<div class="main-header">📊 Dash2BI AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Transform your existing dashboard into a Power BI-ready report using your dataset and HTML design.</div>', unsafe_allow_html=True)

# AI Provider Banner
provider = AnthropicProvider()
if provider.is_available():
    st.sidebar.success("✓ AI-assisted mapping enabled (Claude 3.5 Sonnet)")
    st.session_state.ai_enabled = True
else:
    st.sidebar.info("ℹ AI provider not configured — running on deterministic heuristic matching.")
    st.session_state.ai_enabled = False

# ============================================================
# STEP 1 — UPLOAD PAGE
# ============================================================
if st.session_state.step == 1:
    st.header("STEP 1 — UPLOAD DATASET & HTML DASHBOARD")
    st.caption("Upload your raw data source (.csv, .xlsx) and your HTML dashboard design (.html).")

    col_data, col_html = st.columns(2)

    with col_data:
        st.subheader("1. DATASET FILE")
        ds_upload = st.file_uploader("Upload Excel/CSV Dataset", type=["csv", "xlsx", "xls"], key="ds_uploader")
        
        if ds_upload:
            file_bytes = ds_upload.getvalue()
            valid, err_msg, meta = validate_dataset_file(ds_upload.name, file_bytes)
            if not valid:
                st.error(f"❌ Dataset Upload Error: {err_msg}")
                st.session_state.dataset_file = None
            else:
                st.success(f"✓ Dataset Uploaded: **{ds_upload.name}** ({meta['size_formatted']})")
                st.session_state.dataset_file = {
                    "name": ds_upload.name,
                    "bytes": file_bytes,
                    "meta": meta
                }
                
                # Excel Sheet Selection if multi-sheet
                if meta["extension"] in [".xlsx", ".xls"]:
                    sheets = inspect_excel_sheets(file_bytes)
                    if len(sheets) > 1:
                        sheet_choice = st.selectbox("Select Excel Sheet to Analyze:", sheets)
                        st.session_state.selected_sheet = sheet_choice
                    else:
                        st.session_state.selected_sheet = sheets[0]

    with col_html:
        st.subheader("2. HTML DASHBOARD DESIGN")
        html_upload = st.file_uploader("Upload HTML Dashboard", type=["html", "htm"], key="html_uploader")
        
        if html_upload:
            html_bytes = html_upload.getvalue()
            valid, err_msg, meta = validate_html_file(html_upload.name, html_bytes)
            if not valid:
                st.error(f"❌ HTML Upload Error: {err_msg}")
                st.session_state.html_file = None
            else:
                st.success(f"✓ HTML Dashboard Uploaded: **{html_upload.name}** ({meta['size_formatted']})")
                st.session_state.html_file = {
                    "name": html_upload.name,
                    "bytes": html_bytes,
                    "meta": meta
                }

    st.markdown("---")
    ready_to_analyze = bool(st.session_state.dataset_file and st.session_state.html_file)
    
    if st.button("Analyze Dashboard 🚀", disabled=not ready_to_analyze, type="primary"):
        st.session_state.step = 2
        st.rerun()

# ============================================================
# STEP 2 — ANALYZE PAGE
# ============================================================
elif st.session_state.step == 2:
    st.header("STEP 2 — ANALYZE DATASET & HTML DASHBOARD")

    if not st.session_state.dataset_file or not st.session_state.html_file:
        st.warning("Please upload both Dataset and HTML Dashboard files in Step 1 first.")
        if st.button("Return to Step 1"):
            st.session_state.step = 1
            st.rerun()
    else:
        progress_bar = st.progress(0, text="Starting Analysis...")

        try:
            # 1/6 Loading dataset
            progress_bar.progress(15, text="1/6 Loading dataset...")
            ds = st.session_state.dataset_file
            profile = profile_dataset(ds["name"], ds["bytes"], st.session_state.selected_sheet)
            st.session_state.dataset_profile = profile

            # 3/6 Parsing HTML
            progress_bar.progress(50, text="3/6 Parsing HTML DOM and CSS...")
            html_obj = st.session_state.html_file
            html_str = load_html_dashboard(html_obj["bytes"])

            # 4/6 Detecting visuals
            progress_bar.progress(70, text="4/6 Detecting visual components & KPIs...")
            visuals = analyze_html_dashboard(html_str)
            st.session_state.html_visuals = visuals

            # 5/6 Mapping fields
            progress_bar.progress(85, text="5/6 Running hybrid semantic field mapping...")
            ai_used, ai_results = run_ai_semantic_mapping(profile.to_dict(), visuals)
            mapped = map_all_visuals(visuals, profile.columns_info, ai_results)
            st.session_state.mapped_visuals = mapped

            # 6/6 Complete
            progress_bar.progress(100, text="6/6 Analysis complete!")
            st.success("✓ Dataset and HTML Analysis Completed Successfully!")

        except Dash2BIError as e:
            st.error(e.format_user_message())
        except Exception as e:
            st.error(f"Unexpected Analysis Error: {str(e)}")

        # Render Summary Cards
        if st.session_state.dataset_profile and st.session_state.html_visuals:
            p = st.session_state.dataset_profile
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Dataset Rows", f"{p.row_count:,}")
            c2.metric("Dataset Columns", p.col_count)
            c3.metric("Detected KPIs", sum(1 for v in st.session_state.html_visuals if v["visual_type"] in ["kpi_card", "metric_card"]))
            c4.metric("Detected Visuals", len(st.session_state.html_visuals))

            st.markdown("### 📋 Data Quality Summary")
            st.json(p.quality_summary)

            st.markdown("---")
            if st.button("Proceed to Preview & Map ➡️", type="primary"):
                st.session_state.step = 3
                st.rerun()

# ============================================================
# STEP 3 — PREVIEW & MAP PAGE
# ============================================================
elif st.session_state.step == 3:
    st.header("STEP 3 — PREVIEW & MAP COMPONENTS")

    if not st.session_state.mapped_visuals or not st.session_state.dataset_profile:
        st.warning("Please complete Step 2 (Analyze) first.")
        if st.button("Go to Step 2"):
            st.session_state.step = 2
            st.rerun()
    else:
        # Compute Reconstruction Score
        score_data = compute_reconstruction_score(st.session_state.mapped_visuals)
        
        # Display Reconstruction Score Metrics
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Overall Reconstruction Score", f"{score_data['overall_score']}/100")
        sc2.metric("Field Mapping Score", f"{score_data['field_mapping_pct']}%")
        sc3.metric("Layout Accuracy", f"{score_data['layout_matching_pct']}%")
        sc4.metric("DAX Calculation Accuracy", f"{score_data['calculation_matching_pct']}%")

        if score_data.get("warnings"):
            for w in score_data["warnings"]:
                st.warning(f"⚠ {w}")

        st.markdown("---")

        # Tabbed interface for Mapping Editor and 2D Wireframe Preview
        tab_map, tab_wireframe = st.tabs(["🧩 Field & Visual Mapping Editor", "🖥️ Power BI Canvas Wireframe"])

        with tab_map:
            updated_visuals = render_mapping_review_table(
                st.session_state.mapped_visuals,
                st.session_state.dataset_profile.columns_info
            )
            st.session_state.mapped_visuals = updated_visuals

        with tab_wireframe:
            render_reconstruction_wireframe(st.session_state.mapped_visuals, score_data)

        st.markdown("---")
        if st.button("Confirm Mappings & Proceed to Conversion ⚡", type="primary"):
            st.session_state.step = 4
            st.rerun()

# ============================================================
# STEP 4 — CONVERT & DOWNLOAD PAGE
# ============================================================
elif st.session_state.step == 4:
    st.header("STEP 4 — CONVERT & DOWNLOAD POWER BI PROJECT")

    if not st.session_state.mapped_visuals or not st.session_state.dataset_profile:
        st.warning("Please complete Steps 1 through 3 first.")
        if st.button("Go to Step 1"):
            st.session_state.step = 1
            st.rerun()
    else:
        p = st.session_state.dataset_profile
        mapped = st.session_state.mapped_visuals

        # Generate DAX measures
        measures = generate_dax_for_mapped_visuals(p.table_name, mapped, p.columns_info)

        # Run Pre-flight Validation
        is_ready, val_summary = validate_project_before_export(p.columns_info, mapped, measures)
        render_validation_summary(val_summary)

        st.markdown("---")
        st.subheader("⚡ Power BI Project Export Center")

        # Generate PBIP Project in Temp Directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = create_pbip_project_folder(
                project_name="Dash2BI_Reconstructed_Report",
                table_name=p.table_name,
                dataset_cols=p.columns_info,
                mapped_visuals=mapped,
                measures=measures,
                output_dir=temp_dir
            )

            zip_bytes = package_pbip_as_zip(project_dir)
            report_md = generate_analysis_report_markdown(p.to_dict(), st.session_state.html_visuals, mapped, compute_reconstruction_score(mapped))

            st.download_button(
                label="📦 Download Power BI Project (.pbip ZIP Archive)",
                data=zip_bytes,
                file_name="Dash2BI_PowerBI_Project.zip",
                mime="application/zip",
                type="primary"
            )

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📄 Download Analysis Report (.md)",
                    data=report_md,
                    file_name="Dashboard_Analysis_Report.md",
                    mime="text/markdown"
                )
            with d_col2:
                st.download_button(
                    label="📊 Download Field Mappings (.json)",
                    data=json.dumps(mapped, indent=2),
                    file_name="field_mappings.json",
                    mime="application/json"
                )

        # STRICT PBIX WORKFLOW BANNER
        st.markdown("""
            ---
            ### 📌 Power BI Desktop Opening Instructions
            
            > [!IMPORTANT]
            > **Generated Format:** **Power BI Project (.pbip)**
            > 
            > Pure server environment deployments cannot directly serialize closed proprietary `.pbix` binary report packages. 
            > Dash2BI AI generates fully compliant **Microsoft Power BI Project (.pbip)** artifacts containing complete **PBIR** report definitions and **TMDL** semantic models.
            
            **How to open and save as PBIX:**
            1. Click **Download Power BI Project (.pbip ZIP Archive)** above.
            2. Extract the downloaded `Dash2BI_PowerBI_Project.zip` folder.
            3. Double-click `Dash2BI_Reconstructed_Report.pbip` to open directly in **Power BI Desktop**.
            4. Inside Power BI Desktop, click **File → Save As** and select **Power BI Report (*.pbix)**.
        """)
