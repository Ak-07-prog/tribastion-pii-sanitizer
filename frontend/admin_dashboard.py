from frontend.masking_preview import show_masking_preview
from frontend.risk_panel import display_risk_panel
from pipeline import process_file
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def admin_dashboard():
    st.markdown("""
        <style>
        .stButton>button {
            background-color: #e91e8c;
            color: white;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 📂 Upload Document")

    mode = st.radio(
        "Processing Mode",
        ["⚡ Auto (Instant output)", "🔍 Manual Review"],
        horizontal=True
    )
    st.session_state["mode"] = mode

    strategy = st.selectbox(
        "Select Masking Strategy",
        ["redact", "partial", "pseudonymize",
         "tokenize", "synthetic", "format_preserving"],
        help="Choose how PII will be hidden in the output"
    )

    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload",
        type=["txt", "pdf", "docx", "csv", "json",
              "sql", "xml", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        if "result" in st.session_state:
            show_masking_preview(st.session_state["result"]["pii_found"])

        if st.button("🔍 Process File"):
            os.makedirs("temp", exist_ok=True)
            temp_path = f"temp/{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("🔄 Scanning for PII..."):
                result = process_file(temp_path, strategy)

            try:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    st.session_state["original_text"] = f.read()
            except:
                st.session_state["original_text"] = "Binary file — text extracted for scanning"

            st.session_state["result"] = result
            st.session_state["filename"] = uploaded_file.name
            st.session_state["original_filepath"] = temp_path
            st.rerun()

    if "result" in st.session_state:
        display_results()


def display_results():
    result = st.session_state["result"]

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    tab1, tab2, tab3 = st.tabs([
        "📄 Document View",
        "📊 Risk Analysis",
        "🔍 PII Details"
    ])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📄 Original Document")
            st.text_area(
                "",
                st.session_state.get("original_text", ""),
                height=400
            )
        with col2:
            st.subheader("✅ Sanitized Document")
            st.text_area(
                "",
                result["sanitized_text"],
                height=400
            )

        # show sanitized image if available
        if result.get("sanitized_image"):
            st.subheader("🖼️ Sanitized Image")
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.write("**Original:**")
                original_path = st.session_state.get("original_filepath", "")
                if original_path and os.path.exists(original_path):
                    st.image(original_path)
            with img_col2:
                st.write("**Sanitized:**")
                st.image(result["sanitized_image"])

        if st.download_button(
            "⬇️ Download Sanitized File",
            result["sanitized_text"],
            file_name=f"sanitized_{st.session_state.get('filename', 'output.txt')}",
            mime="text/plain"
        ):
            try:
                from file_handlers.audit_logger import log_download
                log_download(
                    st.session_state.get("user", "unknown"),
                    st.session_state.get("filename", "unknown")
                )
            except:
                pass

        # executive summary export
        st.markdown("---")
        if st.button("📊 Generate Executive Summary PDF"):
            try:
                from frontend.export import generate_executive_summary
                pdf_path = generate_executive_summary(
                    result,
                    st.session_state.get("filename", "document"),
                    st.session_state.get("user", "admin")
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Executive Summary",
                        f.read(),
                        file_name="executive_summary.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
                st.success("✅ Executive Summary generated!")
            except Exception as e:
                st.error(f"Export error: {e}")

    with tab2:
        display_risk_panel(result)

    with tab3:
        st.subheader("🔍 All PII Found")
        if result["pii_found"]:
            for pii in result["pii_found"]:
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.warning(f"**{pii['type']}**")
                with col2:
                    st.code(pii['value'])
                with col3:
                    st.write(f"{int(pii['confidence']*100)}%")
        else:
            st.success("✅ No PII detected in this document")
