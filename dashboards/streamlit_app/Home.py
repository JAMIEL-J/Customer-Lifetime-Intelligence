"""
Home Page – Executive Overview.

Read-only dashboard page showing high-level system outputs.
No business logic. No data mutation.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =============================================================================
# CHART HELPERS
# =============================================================================

def create_bar_chart(labels, values, title="", colors=None):
    """Create a bar chart using plotly graph_objects."""
    if colors is None:
        colors = ["#3498db"] * len(labels)
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(labels),
            y=list(values),
            text=list(values),
            textposition="outside",
            marker_color=colors,
        )
    ])
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=400,
    )
    
    return fig


# =============================================================================
# PUBLIC API
# =============================================================================

def render_home(pipeline: dict) -> None:
    """Render executive overview page."""

    st.header("🏠 Executive Overview")
    st.markdown("---")

    # -------------------------------------------------------------------------
    # Required inputs
    # -------------------------------------------------------------------------
    features_df = pipeline.get("features_df")
    segments_df = pipeline.get("segments_df")
    risk_df = pipeline.get("risk_df")
    actions_df = pipeline.get("actions_df")

    if features_df is None or features_df.empty:
        st.warning("No data available. Please load data from the main app.")
        return

    # -------------------------------------------------------------------------
    # KPI METRICS
    # -------------------------------------------------------------------------
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Customers", f"{len(features_df):,}")

    with col2:
        if risk_df is not None and not risk_df.empty:
            high_risk_count = int((risk_df["risk_level"] == "High").sum())
            st.metric("High Risk Customers", f"{high_risk_count:,}")
        else:
            st.metric("High Risk Customers", "N/A")

    with col3:
        if "lifetime_value" in features_df.columns:
            total_ltv = float(features_df['lifetime_value'].sum())
            st.metric("Total Lifetime Value", f"${total_ltv:,.0f}")
        else:
            st.metric("Total Lifetime Value", "N/A")

    with col4:
        if actions_df is not None and not actions_df.empty:
            high_priority_count = int((actions_df["action_priority"] == "High").sum())
            st.metric("High Priority Actions", f"{high_priority_count:,}")
        else:
            st.metric("High Priority Actions", "N/A")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # CHARTS
    # -------------------------------------------------------------------------
    col_left, col_right = st.columns(2)

    # Lifecycle distribution
    with col_left:
        st.subheader("🎯 Customers by Lifecycle Stage")

        if segments_df is not None and not segments_df.empty:
            lifecycle_counts = segments_df["lifecycle_stage"].value_counts()
            labels = lifecycle_counts.index.tolist()
            values = [int(v) for v in lifecycle_counts.values]
            
            colors = ["#e74c3c", "#2ecc71", "#f39c12", "#95a5a6"]  # Churned, Active, At-Risk, Dormant
            
            fig = create_bar_chart(labels, values, colors=colors[:len(labels)])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Lifecycle data unavailable.")

    # Risk distribution
    with col_right:
        st.subheader("⚠️ Customers by Risk Level")

        if risk_df is not None and not risk_df.empty:
            risk_counts = risk_df["risk_level"].value_counts()
            labels = risk_counts.index.tolist()
            values = [int(v) for v in risk_counts.values]
            
            color_map = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c", "Unknown": "#95a5a6"}
            colors = [color_map.get(label, "#3498db") for label in labels]
            
            fig = create_bar_chart(labels, values, colors=colors)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Risk data unavailable.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # TOP ACTIONS
    # -------------------------------------------------------------------------
    st.subheader("💡 Top Actions by Volume")

    if actions_df is not None and not actions_df.empty:
        action_counts = actions_df["recommended_action"].value_counts().head(10)
        top_actions = pd.DataFrame({
            "Recommended Action": action_counts.index.tolist(),
            "Customer Count": [int(v) for v in action_counts.values]
        })

        st.dataframe(top_actions, use_container_width=True, hide_index=True)
    else:
        st.info("Action data unavailable.")
