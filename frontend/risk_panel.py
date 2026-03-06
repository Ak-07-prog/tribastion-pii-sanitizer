import streamlit as st
import plotly.graph_objects as go


def display_risk_panel(result):
    score = result["risk_score"]
    level = result["risk_level"]

    color_map = {
        "LOW": "green",
        "MEDIUM": "orange",
        "HIGH": "red",
        "CRITICAL": "darkred"
    }

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": f"Risk Level: {level}"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color_map.get(level, "gray")},
            "steps": [
                {"range": [0, 40], "color": "#d4edda"},
                {"range": [40, 60], "color": "#fff3cd"},
                {"range": [60, 80], "color": "#ffe5d0"},
                {"range": [80, 100], "color": "#f8d7da"}
            ]
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Before Sanitization",
            value=f"{score}/100",
            delta=f"-{score} after sanitization",
            delta_color="inverse"
        )
    with col2:
        st.metric(
            label="After Sanitization",
            value="0/100",
            delta="SAFE ✅",
            delta_color="normal"
        )

    if result["attack_vectors"]:
        st.subheader("⚔️ Attack Vectors Detected")
        for vector in result["attack_vectors"]:
            st.error(f"🔴 {vector}")

    if result["attack_narrative"]:
        st.subheader("📖 How an attacker would exploit this")
        st.warning(result["attack_narrative"])

    if result["compliance_flags"]:
        st.subheader("⚖️ Compliance Violations")
        for flag in result["compliance_flags"]:
            st.error(f"🚨 {flag}")
