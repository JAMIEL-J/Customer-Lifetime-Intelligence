"""
Decisions Page – Actions and ROI Dashboard.

Read-only dashboard page showing recommended actions and ROI estimates.
No business logic. No data mutation. Display-only.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


# =============================================================================
# CHART HELPERS
# =============================================================================

def create_bar_chart(labels, values, colors=None, orientation="v"):
    """Create a bar chart using plotly graph_objects."""
    if colors is None:
        colors = ["#3498db"] * len(labels)
    
    if orientation == "h":
        fig = go.Figure(data=[
            go.Bar(
                x=list(values),
                y=list(labels),
                orientation="h",
                text=list(values),
                textposition="outside",
                marker_color=colors,
            )
        ])
    else:
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

def render_decisions(pipeline: dict) -> None:
    """Render decisions and ROI page."""

    st.header("💡 Recommended Decisions")
    st.markdown("---")

    actions_df = pipeline.get("actions_df")
    roi_df = pipeline.get("roi_df")

    if actions_df is None or actions_df.empty:
        st.warning("No action data available. Please load data from the main app.")
        return

    # -------------------------------------------------------------------------
    # KPI METRICS
    # -------------------------------------------------------------------------
    st.subheader("📊 Actions Summary")

    priority_counts = actions_df["action_priority"].value_counts()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Actions", f"{len(actions_df):,}")
    col2.metric("High Priority", f"{int(priority_counts.get('High', 0)):,}")
    col3.metric("Medium Priority", f"{int(priority_counts.get('Medium', 0)):,}")
    col4.metric(
        "ROI Positive",
        f"{int((roi_df['estimated_roi'] > 0).sum()):,}" if roi_df is not None and not roi_df.empty else "N/A",
    )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # ACTIONS BY PRIORITY
    # -------------------------------------------------------------------------
    st.subheader("📊 Actions by Priority")

    # Sort by priority order
    priority_order = ["High", "Medium", "Low"]
    labels = []
    values = []
    for p in priority_order:
        if p in priority_counts.index:
            labels.append(p)
            values.append(int(priority_counts[p]))
    
    color_map = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}
    colors = [color_map.get(label, "#3498db") for label in labels]

    fig_priority = create_bar_chart(labels, values, colors=colors)
    fig_priority.update_layout(yaxis_title="Number of Actions")
    st.plotly_chart(fig_priority, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # ACTIONS BY TYPE
    # -------------------------------------------------------------------------
    st.subheader("📋 Actions by Type")

    action_counts = actions_df["recommended_action"].value_counts()
    labels = action_counts.index.tolist()
    values = [int(v) for v in action_counts.values]

    fig_actions = create_bar_chart(labels, values, orientation="h")
    fig_actions.update_layout(
        xaxis_title="Number of Customers",
        height=max(400, len(labels) * 40),
    )
    st.plotly_chart(fig_actions, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # ROI TABLE
    # -------------------------------------------------------------------------
    st.subheader("💰 ROI Estimates")

    if roi_df is not None and not roi_df.empty:
        display_df = actions_df.merge(roi_df, on="customer_id", how="left")

        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=["High", "Medium", "Low"],
                default=["High", "Medium", "Low"],
            )

        with col_filter2:
            roi_filter = st.selectbox(
                "ROI Filter",
                ["All", "Positive ROI Only", "Negative ROI Only"],
            )

        filtered_df = display_df[display_df["action_priority"].isin(priority_filter)]

        if roi_filter == "Positive ROI Only":
            filtered_df = filtered_df[filtered_df["estimated_roi"] > 0]
        elif roi_filter == "Negative ROI Only":
            filtered_df = filtered_df[filtered_df["estimated_roi"] <= 0]

        st.caption(f"Showing {len(filtered_df):,} actions")

        display_subset = filtered_df[
            [
                "customer_id",
                "recommended_action",
                "action_priority",
                "action_cost",
                "expected_benefit",
                "estimated_roi",
            ]
        ].head(100)

        st.dataframe(display_subset, use_container_width=True, hide_index=True)

    else:
        st.info("ROI data not available.")

    # -------------------------------------------------------------------------
    # RAW ACTIONS SAMPLE
    # -------------------------------------------------------------------------
    with st.expander("📄 Sample Actions (First 100 Rows)"):
        st.dataframe(
            actions_df.head(100),
            use_container_width=True,
            hide_index=True,
        )
