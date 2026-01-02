"""
Segments Page – Customer Segmentation Analysis.

Read-only dashboard page showing segment distributions and breakdowns.
No business logic. No data mutation. Filtering only.
"""

import streamlit as st
import plotly.graph_objects as go
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

def render_segments(pipeline: dict) -> None:
    """Render segments analysis page."""

    st.header("🎯 Customer Segments")
    st.markdown("---")

    segments_df = pipeline.get("segments_df")

    if segments_df is None or segments_df.empty:
        st.warning("No segment data available. Please load data from the main app.")
        return

    # -------------------------------------------------------------------------
    # FILTERS
    # -------------------------------------------------------------------------
    st.subheader("🔍 Filters")

    col1, col2 = st.columns(2)

    lifecycle_options = ["All"] + sorted(segments_df["lifecycle_stage"].unique().tolist())
    value_options = ["All"] + sorted(segments_df["value_segment"].unique().tolist())

    selected_lifecycle = col1.selectbox("Lifecycle Stage", lifecycle_options)
    selected_value = col2.selectbox("Value Segment", value_options)

    # Apply filters (no mutation)
    filtered_df = segments_df.copy()
    if selected_lifecycle != "All":
        filtered_df = filtered_df[filtered_df["lifecycle_stage"] == selected_lifecycle]
    if selected_value != "All":
        filtered_df = filtered_df[filtered_df["value_segment"] == selected_value]

    st.caption(f"Showing {len(filtered_df):,} of {len(segments_df):,} customers")
    st.markdown("---")

    # -------------------------------------------------------------------------
    # CHARTS
    # -------------------------------------------------------------------------
    left, right = st.columns(2)

    with left:
        st.subheader("📊 Lifecycle Stage Distribution")

        if not filtered_df.empty:
            lifecycle_counts = filtered_df["lifecycle_stage"].value_counts()
            labels = lifecycle_counts.index.tolist()
            values = [int(v) for v in lifecycle_counts.values]
            
            colors = ["#e74c3c", "#2ecc71", "#f39c12", "#95a5a6"]
            
            fig = create_bar_chart(labels, values, colors=colors[:len(labels)])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data matches the selected filters.")

    with right:
        st.subheader("💎 Value Segment Distribution")

        if not filtered_df.empty:
            value_counts = filtered_df["value_segment"].value_counts()
            labels = value_counts.index.tolist()
            values = [int(v) for v in value_counts.values]
            
            color_map = {"High Value": "#9b59b6", "Medium Value": "#3498db", "Low Value": "#95a5a6"}
            colors = [color_map.get(label, "#3498db") for label in labels]
            
            fig = create_bar_chart(labels, values, colors=colors)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data matches the selected filters.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SEGMENT LABEL BREAKDOWN
    # -------------------------------------------------------------------------
    st.subheader("📋 Segment Label Breakdown")

    if not filtered_df.empty:
        label_counts = filtered_df["segment_label"].value_counts()
        label_table = pd.DataFrame({
            "Segment Label": label_counts.index.tolist(),
            "Count": [int(v) for v in label_counts.values]
        })
        st.dataframe(label_table, use_container_width=True, hide_index=True)
    else:
        st.info("No data matches the selected filters.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SAMPLE DATA PREVIEW
    # -------------------------------------------------------------------------
    with st.expander("📄 Sample Segment Records (First 100 Rows)"):
        st.dataframe(
            filtered_df.head(100),
            use_container_width=True,
            hide_index=True,
        )
