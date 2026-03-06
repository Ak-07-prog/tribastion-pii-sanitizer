import streamlit as st
from datetime import datetime
import json
import os


def display_audit_panel():
    st.subheader("📋 Audit Log")

    log_path = "storage/audit_logs/audit.json"

    if not os.path.exists(log_path):
        st.info("No audit logs yet. Upload a file to generate logs.")
        return

    logs = []
    with open(log_path, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                pass

    if not logs:
        st.info("No audit logs yet.")
        return

    # filters
    col1, col2 = st.columns(2)
    with col1:
        action_filter = st.selectbox(
            "Filter by Action",
            ["All", "FILE_UPLOAD", "FILE_DOWNLOAD",
             "LOGIN", "LOGOUT", "PII_DETECTED"]
        )
    with col2:
        user_filter = st.text_input("Filter by User")

    # apply filters
    filtered = logs
    if action_filter != "All":
        filtered = [l for l in filtered if l.get("action") == action_filter]
    if user_filter:
        filtered = [l for l in filtered
                    if user_filter.lower() in l.get("user", "").lower()]

    # display logs
    st.write(f"Showing {len(filtered)} of {len(logs)} events")

    for log in reversed(filtered[-50:]):
        risk = log.get("risk_score", 0)
        if risk >= 80:
            color = "🔴"
        elif risk >= 60:
            color = "🟠"
        elif risk >= 40:
            color = "🟡"
        else:
            color = "🟢"

        with st.expander(
            f"{color} {log.get('action', 'UNKNOWN')} — "
            f"{log.get('user', 'unknown')} — "
            f"{log.get('timestamp', '')[:19]}"
        ):
            st.json(log)

    # anomaly alerts
    st.subheader("⚠️ Anomaly Alerts")
    download_counts = {}
    for log in logs:
        if log.get("action") == "FILE_DOWNLOAD":
            user = log.get("user", "unknown")
            download_counts[user] = download_counts.get(user, 0) + 1

    anomaly_found = False
    for user, count in download_counts.items():
        if count > 10:
            st.error(f"🚨 {user} downloaded {count} files — unusual activity")
            anomaly_found = True

    if not anomaly_found:
        st.success("✅ No anomalies detected")
