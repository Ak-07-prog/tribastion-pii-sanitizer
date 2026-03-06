import streamlit as st
from frontend.login import login_page
from frontend.admin_dashboard import admin_dashboard

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
            if st.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()

        if role in ["Super Admin", "Admin"]:
            admin_dashboard()
        elif role == "Analyst":
            st.title("🔍 Analyst Dashboard")
            st.info("Coming soon...")
        else:
            st.title("👤 Standard User Dashboard")
            st.info("Coming soon...")


if __name__ == "__main__":
    main()
