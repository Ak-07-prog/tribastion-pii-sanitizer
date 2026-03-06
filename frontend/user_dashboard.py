import streamlit as st
import os


def user_dashboard():
    st.markdown("## 👤 Standard User Dashboard")
    st.info("You can only view and download sanitized files.")

    sanitized_dir = "storage/sanitized"

    if not os.path.exists(sanitized_dir):
        st.warning("No sanitized files available yet.")
        return

    files = os.listdir(sanitized_dir)

    if not files:
        st.warning("No sanitized files available yet.")
        return

    st.subheader("📁 Available Sanitized Files")

    search = st.text_input("🔍 Search files")
    if search:
        files = [f for f in files if search.lower() in f.lower()]

    for filename in files:
        filepath = os.path.join(sanitized_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
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
