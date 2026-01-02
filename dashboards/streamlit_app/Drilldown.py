"""
Drilldown Page – Individual Customer Analysis.

Read-only dashboard page showing detailed view of a single customer.
No business logic. No data mutation. Display-only.
"""

import streamlit as st


MAX_CUSTOMERS = 1000  # UI safeguard


def render_drilldown(pipeline: dict) -> None:
    """Render customer drilldown page."""

    st.header("🔍 Customer Drilldown")
    st.markdown("---")

    features_df = pipeline.get("features_df")
    segments_df = pipeline.get("segments_df")
    risk_df = pipeline.get("risk_df")
    actions_df = pipeline.get("actions_df")
    explanations_df = pipeline.get("explanations_df")

    if features_df is None or features_df.empty:
        st.warning("No customer data available. Please load data from the main app.")
        return

    # -------------------------------------------------------------------------
    # CUSTOMER SELECTOR
    # -------------------------------------------------------------------------
    customer_ids = sorted(features_df["customer_id"].unique())[:MAX_CUSTOMERS]

    col_search, col_info = st.columns([2, 1])

    with col_search:
        selected_customer = st.selectbox(
            "Select Customer ID",
            options=customer_ids,
            help=f"Showing first {MAX_CUSTOMERS:,} customers for performance",
        )

    with col_info:
        st.metric("Total Customers", f"{features_df['customer_id'].nunique():,}")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # DECISION EXPLANATION
    # -------------------------------------------------------------------------
    st.subheader("💬 Decision Explanation")

    if explanations_df is not None:
        row = explanations_df[explanations_df["customer_id"] == selected_customer]
        if not row.empty:
            st.info(row["decision_explanation"].iloc[0])
        else:
            st.caption("No explanation available.")
    else:
        st.caption("Explanation data not available.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # CUSTOMER SNAPSHOT
    # -------------------------------------------------------------------------
    col_left, col_right = st.columns(2)

    # FEATURES
    with col_left:
        st.subheader("📊 Features")

        row = features_df[features_df["customer_id"] == selected_customer]
        if not row.empty:
            data = row.iloc[0].to_dict()
            for k, v in data.items():
                if k == "customer_id":
                    continue
                label = k.replace("_", " ").title()
                if isinstance(v, (int, float)):
                    st.metric(label, f"{v:,.2f}")
                else:
                    st.write(f"**{label}:** {v}")
        else:
            st.caption("No feature data available.")

    # SEGMENT & RISK
    with col_right:
        st.subheader("🎯 Segment & Risk")

        if segments_df is not None:
            seg = segments_df[segments_df["customer_id"] == selected_customer]
            if not seg.empty:
                s = seg.iloc[0]
                st.metric("Lifecycle Stage", s["lifecycle_stage"])
                st.metric("Value Segment", s["value_segment"])
                st.metric("Segment Label", s["segment_label"])

        if risk_df is not None:
            risk = risk_df[risk_df["customer_id"] == selected_customer]
            if not risk.empty:
                r = risk.iloc[0]
                color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(r["risk_level"], "⚪")
                st.metric("Risk Score", f"{r['risk_score']:.2f}")
                st.metric("Risk Level", f"{color} {r['risk_level']}")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # RECOMMENDED ACTION
    # -------------------------------------------------------------------------
    st.subheader("💡 Recommended Action")

    if actions_df is not None:
        act = actions_df[actions_df["customer_id"] == selected_customer]
        if not act.empty:
            a = act.iloc[0]
            col1, col2 = st.columns(2)
            col1.metric("Action", a["recommended_action"])
            icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(a["action_priority"], "⚪")
            col2.metric("Priority", f"{icon} {a['action_priority']}")
        else:
            st.caption("No action assigned.")
    else:
        st.caption("Action data not available.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # RAW DATA (SAMPLES)
    # -------------------------------------------------------------------------
    with st.expander("📄 View Raw Customer Data (Sample)"):
        tab1, tab2, tab3, tab4 = st.tabs(["Features", "Segment", "Risk", "Action"])

        with tab1:
            st.dataframe(row, use_container_width=True, hide_index=True)

        with tab2:
            if segments_df is not None:
                st.dataframe(seg, use_container_width=True, hide_index=True)

        with tab3:
            if risk_df is not None:
                st.dataframe(risk, use_container_width=True, hide_index=True)

        with tab4:
            if actions_df is not None:
                st.dataframe(act, use_container_width=True, hide_index=True)
