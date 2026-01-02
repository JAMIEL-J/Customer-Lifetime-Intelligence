"""
Customer Lifecycle Intelligence Platform - Streamlit App.

Application entry point. Responsible ONLY for:
- Loading pipeline data
- Managing session state
- Routing to page modules
"""

import streamlit as st
from typing import Dict, Any

from src.services.orchestrator import run_full_system

from dashboards.streamlit_app.Home import render_home
from dashboards.streamlit_app.Segments import render_segments
from dashboards.streamlit_app.Risk import render_risk
from dashboards.streamlit_app.Decisions import render_decisions
from dashboards.streamlit_app.Drilldown import render_drilldown


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Customer Lifecycle Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# DATA LOADING
# =============================================================================

CACHE_VERSION = "v2"  # Increment to force cache invalidation

@st.cache_data(show_spinner="Running lifecycle intelligence pipeline...")
def load_pipeline(raw_path: str, snapshot_date: str | None, _version: str = CACHE_VERSION) -> Dict[str, Any]:
    return run_full_system(
        raw_transactions_path=raw_path,
        snapshot_date=snapshot_date,
    )


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.title("📊 Customer Lifecycle")

    raw_path = st.text_input(
        "Transactions CSV Path",
        value="data/raw/online_retail_II.csv",
    )

    snapshot_date = st.text_input(
        "Snapshot Date (optional)",
        placeholder="YYYY-MM-DD",
    )

    page = st.radio(
        "Navigate",
        options=[
            "Overview",
            "Segments",
            "Risk",
            "Decisions",
            "Customer Drilldown",
        ],
    )

    load = st.button("Load Data", type="primary")
    
    if st.button("Clear Cache"):
        st.cache_data.clear()
        if "pipeline" in st.session_state:
            del st.session_state["pipeline"]
        st.rerun()


# =============================================================================
# LOAD DATA
# =============================================================================

if load or "pipeline" not in st.session_state:
    try:
        pipeline_result = load_pipeline(
            raw_path,
            snapshot_date or None,
        )
        st.session_state["pipeline"] = pipeline_result
        st.success(f"Pipeline loaded: {len(pipeline_result.get('features_df', [])):,} customers")
    except Exception as e:
        st.error("Pipeline execution failed")
        st.exception(e)
        st.stop()


pipeline = st.session_state["pipeline"]


# =============================================================================
# ROUTING
# =============================================================================

if page == "Overview":
    render_home(pipeline)
elif page == "Segments":
    render_segments(pipeline)
elif page == "Risk":
    render_risk(pipeline)
elif page == "Decisions":
    render_decisions(pipeline)
elif page == "Customer Drilldown":
    render_drilldown(pipeline)
