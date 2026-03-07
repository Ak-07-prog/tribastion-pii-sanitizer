import streamlit as st
import os
from frontend.login import login_page
from frontend.admin_dashboard import admin_dashboard
from frontend.user_dashboard import user_dashboard

st.set_page_config(page_title="PII Sanitizer", page_icon="🛡️", layout="wide")


def main():
    if "logged_in" not in st.session_state:
        login_page()
    else:
        role = st.session_state["role"]
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state['user']}")
            st.markdown(f"**Role:** {role}")
            st.markdown("---")
            if role in ["Super Admin", "Admin"]:
                page = st.radio(
                    "Navigate", ["📂 Upload & Scan", "📋 Audit Log", "📁 Past Reports", "📥 User Submissions"])
                st.session_state["page"] = page
            st.markdown("---")
            submissions_dir = "storage/user_submissions"
            if os.path.exists(submissions_dir):
                pending = len(os.listdir(submissions_dir))
                if pending > 0:
                    st.sidebar.warning(
                        f"📥 {pending} pending user submission(s)")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh"):
                    keys_to_clear = ["result", "original_text", "original_filepath",
                                     "filename", "manual_mode", "pending_text",
                                     "pending_detections", "pending_filepath"]
                    for key in keys_to_clear:
                        st.session_state.pop(key, None)
                    st.rerun()
            with col2:
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
            elif page == "📁 Past Reports":
                show_past_reports()
            elif page == "📥 User Submissions":
                show_user_submissions()
        elif role == "Analyst":
            analyst_dashboard()
        else:
            user_dashboard()


def show_past_reports():
    st.title("📁 Past Reports")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(base_dir, "storage", "sanitized")
    if not os.path.exists(report_dir):
        st.info("No reports yet.")
        return
    files = [f for f in os.listdir(report_dir) if not f.startswith('.')]
    if not files:
        st.info("No reports yet.")
        return
    for filename in sorted(files, reverse=True):
        filepath = os.path.join(report_dir, filename)
        is_pdf = filename.endswith('.pdf')
        is_image = filename.lower().endswith(('.png', '.jpg', '.jpeg'))
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            col1, col2 = st.columns([3, 1])
            with col1:
                if is_image:
                    st.write(f"🖼️ {filename}")
                elif is_pdf:
                    st.write(f"📊 {filename}")
                else:
                    st.write(f"📄 {filename}")
            with col2:
                if is_image:
                    mime = "image/jpeg" if filename.lower().endswith(('.jpg', '.jpeg')) else "image/png"
                elif is_pdf:
                    mime = "application/pdf"
                else:
                    mime = "text/plain"
                st.download_button(
                    "⬇️ Download",
                    content,
                    file_name=filename,
                    mime=mime,
                    key=filename
                )
        except Exception as e:
            st.error(f"Could not read {filename}: {e}")


def analyst_dashboard():
    st.title("🔍 Analyst Dashboard")
    st.info("You can view sanitized files and audit logs.")
    from frontend.audit_panel import display_audit_panel
    tab1, tab2 = st.tabs(["📁 Sanitized Files", "📋 Audit Log"])
    with tab1:
        sanitized_dir = "storage/sanitized"
        files = [f for f in os.listdir(sanitized_dir) if f.endswith(
            '.txt')] if os.path.exists(sanitized_dir) else []
        for filename in files:
            filepath = os.path.join(sanitized_dir, filename)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {filename}")
            with col2:
                st.download_button("⬇️ Download", content,
                                   file_name=filename, mime="text/plain", key=filename)
    with tab2:
        display_audit_panel()


def show_user_submissions():
    st.title("📥 User Submissions")
    submissions_dir = "storage/user_submissions"
    if not os.path.exists(submissions_dir) or not os.listdir(submissions_dir):
        st.info("No pending submissions from users.")
        return

    files = os.listdir(submissions_dir)
    st.success(f"{len(files)} submission(s) received")

    for filename in files:
        filepath = os.path.join(submissions_dir, filename)
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"📄 {filename}")
        with col2:
            if st.button("⚙️ Process", key=f"process_{filename}"):
                from pipeline import process_file
                result = process_file(filepath, "redact")
                st.session_state["result"] = result
                st.session_state["original_filepath"] = filepath
                st.session_state["filename"] = filename
                st.session_state[
                    "original_text"] = f"Submitted by user: {filename.split('_')[0]}"
                st.session_state["page"] = "📂 Upload & Scan"
                st.rerun()
        with col3:
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Download", f.read(),
                                   file_name=filename, key=f"dl_{filename}")


if __name__ == "__main__":
    main()
