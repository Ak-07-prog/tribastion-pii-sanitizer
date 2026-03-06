import streamlit as st

USERS = {
    "superadmin@company.com": {"password": "super123", "role": "Super Admin"},
    "admin@company.com": {"password": "admin123", "role": "Admin"},
    "analyst@company.com": {"password": "analyst123", "role": "Analyst"},
    "user@company.com": {"password": "user123", "role": "Standard User"}
}


def login_page():
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #e91e8c;
            color: white;
            width: 100%;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#e91e8c'>🛡️ PII Sanitizer</h1>",
                    unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center; color:gray'>Powered by Tribastion</h4>",
                    unsafe_allow_html=True)
        st.markdown("---")

        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")

        if st.button("Login"):
            if email in USERS and USERS[email]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["user"] = email
                st.session_state["role"] = USERS[email]["role"]
                # log login event
                try:
                    from file_handlers.audit_logger import log_login
                    log_login(email, USERS[email]["role"])
                except:
                    pass
                st.success(f"Welcome {USERS[email]['role']}!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

        st.markdown("---")
        st.markdown("""
        <p style='text-align:center; color:gray; font-size:12px'>
        Demo accounts:<br>
        admin@company.com / admin123<br>
        user@company.com / user123
        </p>
        """, unsafe_allow_html=True)
