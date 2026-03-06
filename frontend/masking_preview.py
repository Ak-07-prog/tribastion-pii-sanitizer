import streamlit as st


def show_masking_preview(pii_found):
    if not pii_found:
        return

    st.markdown("---")
    st.subheader("👁️ Masking Preview")
    st.write("See how each strategy will look before applying:")

    for pii in pii_found[:3]:
        st.markdown(f"**{pii['type']}** — Original: `{pii['value']}`")

        cols = st.columns(3)
        strategies = ["redact", "partial", "pseudonymize"]
        for i, col in enumerate(cols):
            with col:
                preview = get_preview(pii["value"], pii["type"], strategies[i])
                st.markdown(f"""
                <div style='background:#1e1e2e; padding:10px; 
                border-radius:8px; margin:5px 0'>
                    <small style='color:#e91e8c'>{strategies[i]}</small><br>
                    <code style='color:white'>{preview}</code>
                </div>
                """, unsafe_allow_html=True)

        cols2 = st.columns(3)
        strategies2 = ["tokenize", "synthetic", "format_preserving"]
        for i, col in enumerate(cols2):
            with col:
                preview = get_preview(
                    pii["value"], pii["type"], strategies2[i])
                st.markdown(f"""
                <div style='background:#1e1e2e; padding:10px;
                border-radius:8px; margin:5px 0'>
                    <small style='color:#e91e8c'>{strategies2[i]}</small><br>
                    <code style='color:white'>{preview}</code>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")


def get_preview(value, pii_type, strategy):
    if strategy == "redact":
        return "[REDACTED]"
    elif strategy == "partial":
        if pii_type == "EMAIL" and "@" in value:
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        elif pii_type == "AADHAAR":
            return "XXXX XXXX " + value[-4:]
        elif pii_type == "PAN":
            return "XXXXX" + value[-4:]
        else:
            return value[:2] + "***"
    elif strategy == "pseudonymize":
        previews = {
            "NAME": "Arjun Mehta",
            "EMAIL": "arjun.mehta@example.com",
            "PHONE": "+91 8123456789",
            "ADDRESS": "42 MG Road, Mumbai"
        }
        return previews.get(pii_type, "[PSEUDONYM]")
    elif strategy == "tokenize":
        return f"TKN-{pii_type[0]}-A1B2C3D4"
    elif strategy == "synthetic":
        synthetics = {
            "AADHAAR": "7823 4521 9034",
            "PAN": "XKRPQ7734M",
            "EMAIL": "fake.user@example.com",
            "PHONE": "+91 7012345678"
        }
        return synthetics.get(pii_type, "[SYNTHETIC]")
    elif strategy == "format_preserving":
        if pii_type == "AADHAAR":
            return "XXXX XXXX " + value[-4:]
        elif pii_type == "EMAIL" and "@" in value:
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        else:
            return "[MASKED]"
    return "[REDACTED]"
