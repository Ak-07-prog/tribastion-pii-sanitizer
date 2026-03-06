import streamlit as st
from frontend.login import login_page
from frontend.admin_dashboard import admin_dashboard
from frontend.user_dashboard import user_dashboard

st.set_page_config(
    page_title="PII Sanitizer",
    page_icon="🛡️",
    layout="wide"
)


def main():
    if "logged_in" not in st.session_state:
        login_page()
    else:
        role = st.session_state["role"]

        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state['user']}")
            st.markdown(f"**Role:** {role}")
            st.markdown("---")

            # navigation based on role
            if role in ["Super Admin", "Admin"]:
                page = st.radio(
                    "Navigate",
                    ["📂 Upload & Scan", "📋 Audit Log"]
                )
                st.session_state["page"] = page

            st.markdown("---")
            if st.button("🚪 Logout"):
                try:
                    from file_handlers.audit_logger import log_logout
                    log_logout(st.session_state.get("user", "unknown"))
                except:
                    pass
                st.session_state.clear()
                st.rerun()

        if role in ["Super Admin", "Admin"]:
            page = st.session_state.get("page", "📂 Upload & Scan")
            if page == "📂 Upload & Scan":
                admin_dashboard()
            elif page == "📋 Audit Log":
                from frontend.audit_panel import display_audit_panel
                display_audit_panel()

        elif role == "Analyst":
            st.title("🔍 Analyst Dashboard")
            st.info("Coming soon...")

        else:
            user_dashboard()


if __name__ == "__main__":
    main()
