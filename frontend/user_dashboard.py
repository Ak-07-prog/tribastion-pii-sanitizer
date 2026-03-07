import streamlit as st
import os


def user_dashboard():
    st.markdown("## 👤 Standard User Dashboard")

    tab1, tab2 = st.tabs(["📁 Sanitized Files", "📤 Send Document to Admin"])

    with tab1:
        st.info("You can only view and download sanitized files.")
        sanitized_dir = "storage/sanitized"

        if not os.path.exists(sanitized_dir):
            st.warning("No sanitized files available yet.")
            return

        files = [f for f in os.listdir(sanitized_dir)]

        if not files:
            st.warning("No sanitized files available yet.")
            return

        st.subheader("📁 Available Sanitized Files")
        search = st.text_input("🔍 Search files")
        if search:
            files = [f for f in files if search.lower() in f.lower()]

        for filename in files:
            filepath = os.path.join(sanitized_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {filename}")
                with col2:
                    st.download_button(
                        "⬇️ Download",
                        content,
                        file_name=filename,
                        mime="text/plain",
                        key=filename
                    )
            except Exception as e:
                st.error(f"Could not read {filename}: {e}")

    with tab2:
        st.subheader("📤 Send Document to Admin for Sanitization")
        st.info("Upload a document and it will be sent to admin for PII sanitization.")

        uploaded = st.file_uploader(
            "Upload document",
            type=["txt", "pdf", "docx", "csv", "json", "sql", "xml"]
        )
        note = st.text_area("Add a note for admin (optional)")

        if uploaded and st.button("📤 Send to Admin"):
            os.makedirs("storage/user_submissions", exist_ok=True)
            save_path = f"storage/user_submissions/{st.session_state.get('user', 'user')}_{uploaded.name}"
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())

            # log the submission
            try:
                from file_handlers.audit_logger import log
                log({
                    "action": "USER_SUBMISSION",
                    "user": st.session_state.get("user", "unknown"),
                    "filename": uploaded.name,
                    "note": note
                })
            except:
                pass

            st.success(f"✅ {uploaded.name} sent to admin successfully!")
