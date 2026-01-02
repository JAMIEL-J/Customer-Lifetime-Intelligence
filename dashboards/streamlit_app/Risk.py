"""
Risk Page – Risk Analysis Dashboard.

Read-only dashboard page showing risk score distributions and high-risk customers.
No business logic. No data mutation. Sorting and filtering only.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# =============================================================================
# CHART HELPERS
# =============================================================================

def create_bar_chart(labels, values, colors=None):
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
        showlegend=False,
        height=400,
    )
    
    return fig


# =============================================================================
# PUBLIC API
# =============================================================================

def render_risk(pipeline: dict) -> None:
    """Render risk analysis page."""

    st.header("⚠️ Risk Analysis")
    st.markdown("---")

    risk_df = pipeline.get("risk_df")

    if risk_df is None or risk_df.empty:
        st.warning("No risk data available. Please load data from the main app.")
        return

    # -------------------------------------------------------------------------
    # KPI METRICS
    # -------------------------------------------------------------------------
    st.subheader("📊 Risk Summary")

    risk_counts = risk_df["risk_level"].value_counts()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", f"{len(risk_df):,}")
    col2.metric("High Risk", f"{int(risk_counts.get('High', 0)):,}")
    col3.metric("Medium Risk", f"{int(risk_counts.get('Medium', 0)):,}")
    col4.metric("Low Risk", f"{int(risk_counts.get('Low', 0)):,}")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # RISK SCORE DISTRIBUTION
    # -------------------------------------------------------------------------
    st.subheader("📈 Risk Score Distribution")

    # Use graph_objects histogram for reliability
    fig_hist = go.Figure(data=[
        go.Histogram(
            x=risk_df["risk_score"].tolist(),
            nbinsx=20,
            marker_color="#3498db",
        )
    ])
    fig_hist.update_layout(
        xaxis_title="Risk Score (0–100)",
        yaxis_title="Number of Customers",
        bargap=0.1,
        height=400,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # HIGH RISK CUSTOMERS
    # -------------------------------------------------------------------------
    st.subheader("🚨 High Risk Customers")

    top_n = st.slider("Show Top N Customers", 10, 100, 25, step=5)

    high_risk_df = (
        risk_df[risk_df["risk_level"] == "High"]
        .sort_values("risk_score", ascending=False)
        .head(top_n)
    )

    if high_risk_df.empty:
        st.info("No high-risk customers found.")
    else:
        st.dataframe(high_risk_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # AVERAGE RISK SCORE BY LEVEL
    # -------------------------------------------------------------------------
    st.subheader("📊 Average Risk Score by Risk Level")

    avg_scores = risk_df.groupby("risk_level")["risk_score"].mean()
    labels = avg_scores.index.tolist()
    values = [round(float(v), 2) for v in avg_scores.values]
    
    color_map = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c", "Unknown": "#95a5a6"}
    colors = [color_map.get(label, "#3498db") for label in labels]

    fig_avg = create_bar_chart(labels, values, colors=colors)
    fig_avg.update_layout(
        xaxis_title="Risk Level",
        yaxis_title="Average Risk Score",
    )
    st.plotly_chart(fig_avg, use_container_width=True)

    # -------------------------------------------------------------------------
    # SAMPLE DATA PREVIEW
    # -------------------------------------------------------------------------
    with st.expander("📄 Sample Risk Records (First 100 Rows)"):
        filter_level = st.multiselect(
            "Filter by Risk Level",
            options=["Low", "Medium", "High", "Unknown"],
            default=["Low", "Medium", "High"],
        )

        filtered = risk_df[risk_df["risk_level"].isin(filter_level)]
        st.caption(f"Showing {len(filtered):,} customers")
        st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)
