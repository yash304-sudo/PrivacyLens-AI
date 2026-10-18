import re
from collections import Counter
import streamlit as st
import pandas as pd

st.set_page_config(page_title="PrivacyLens AI", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.main {background: #f7f9fc;}
.block-container {padding-top: 2rem; max-width: 1200px;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#176b87); color: white;}
.hero h1 {color:white; margin-bottom:.25rem;}
.metric-card {padding: 1rem; border: 1px solid #dce5ee; border-radius: 14px; background: white;}
.small-muted {color:#526477; font-size:.92rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🛡️ PrivacyLens AI</h1>
  <div>Privacy risk scanner for safer AI prompts and enterprise text workflows</div>
  <p>Detect • Mask • Review — before sensitive text is shared with an AI tool.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.info("Prototype notice: detection uses pattern matching, not a trained AI model. It can miss sensitive data or flag ordinary text. Do not paste real passwords, financial details, or confidential records.")

SAMPLE = """Hi support team,
Please contact Yash at yash.resham@example.com or 9876543210.
Customer reference: CUST-482913.
We need help with the account issue."""
with st.sidebar:
    st.header("Scan settings")
    detect_email = st.checkbox("Email addresses", value=True)
    detect_phone = st.checkbox("Phone-like numbers", value=True)
    detect_id = st.checkbox("Reference / ID-like values", value=True)
    st.caption("The scanner runs locally in this app session. This demo does not intentionally save submitted text.")

st.subheader("1. Paste text to scan")
text_in = st.text_area("Text / AI prompt", value=SAMPLE, height=190, placeholder="Paste a sample prompt here…")
scan = st.button("Scan and mask sensitive data", type="primary", use_container_width=True)


def scan_text(source, email_on, phone_on, id_on):
    masked = source
    detections = []

    # Detect passwords and usernames using their labels.
    sensitive_patterns = [
        (
            "Password",
            re.compile(
                r'(\b(?:password|passcode|passwd|pwd)\b'
                r'\s*(?:is\s*)?[:=\-]*\s*)([^\s,;]+)',
                re.IGNORECASE
            ),
            "[PASSWORD]"
        ),
        (
            "Username",
            re.compile(
                r'(\b(?:instagram\s*(?:id|username|handle)'
                r'|username|user\s*id)\b'
                r'\s*(?:is\s*)?[:=\-]*\s*)([@]?[A-Za-z0-9._]{3,30})',
                re.IGNORECASE
            ),
            "[USERNAME]"
        ),
    ]

    # Mask credentials first and never display their original values.
    for kind, pattern, replacement in sensitive_patterns:
        matches = list(pattern.finditer(masked))

        for match in matches:
            detections.append({
                "Type": kind,
                "Detected value": "[REDACTED]",
                "Replacement": replacement
            })

        masked = pattern.sub(
            lambda match: match.group(1) + replacement,
            masked
        )

    # Detect other supported patterns.
    patterns = []

    if email_on:
        patterns.append((
            "Email",
            re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            ),
            "[EMAIL]"
        ))

    if phone_on:
        patterns.append((
            "Phone",
            re.compile(r'(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)'),
            "[PHONE]"
        ))

    if id_on:
        patterns.append((
            "Reference ID",
            re.compile(r'\b(?:CUST|ACC|ID|REF)[-_]?[A-Z0-9]{4,}\b',
                       re.IGNORECASE),
            "[REFERENCE_ID]"
        ))

    for kind, pattern, replacement in patterns:
        matches = list(pattern.finditer(masked))

        for match in matches:
            detections.append({
                "Type": kind,
                "Detected value": "[REDACTED]",
                "Replacement": replacement
            })

        masked = pattern.sub(replacement, masked)

    counts = Counter(item["Type"] for item in detections)

    weights = {
        "Password": 50,
        "Username": 15,
        "Email": 25,
        "Phone": 25,
        "Reference ID": 20
    }

    score = min(
        100,
        sum(weights.get(item["Type"], 10) for item in detections)
    )

    if score >= 50:
        level = "High"
    elif score >= 20:
        level = "Medium"
    else:
        level = "Low"

    return masked, detections, counts, score, level


if scan:
    if not text_in.strip():
        st.warning("Enter some sample text first.")
    else:
        masked_text, detections, counts, score, level = scan_text(text_in, detect_email, detect_phone, detect_id)
        st.subheader("2. Privacy scan results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Items detected", len(detections))
        c2.metric("Risk score", f"{score}/100")
        c3.metric("Risk level", level)
        c4.metric("Detection types", len(counts))

        st.progress(score / 100)
        st.caption("Risk score is a transparent demo heuristic, not a probability or security certification.")

        left, right = st.columns(2)
        with left:
            st.markdown("**Original text**")
            st.text_area("Original input (review only)", value=text_in, height=180, disabled=True, key="original_result")
        with right:
            st.markdown("**Masked output**")
            st.text_area("Safer text to copy", value=masked_text, height=180, key="masked_result")
            st.download_button("Download masked text", data=masked_text, file_name="masked_text.txt", mime="text/plain", use_container_width=True)

        st.markdown("**Detection breakdown**")
        if detections:
            st.dataframe(pd.DataFrame(detections), use_container_width=True, hide_index=True)
            st.bar_chart(pd.DataFrame([{"Type": k, "Count": v} for k, v in counts.items()]).set_index("Type"))
        else:
            st.success("No supported patterns detected. This does not guarantee that the text contains no sensitive information.")

        st.markdown("**Recommended next step**")
        if level == "High":
            st.error("Review the text carefully and use the masked version only after checking it.")
        elif level == "Medium":
            st.warning("Review detected values and check for sensitive details the scanner may not recognize.")
        else:
            st.success("No supported patterns or only a low number of matches were detected. Review before sharing.")

st.divider()
st.subheader("How it works")
st.write("Text input → pattern-based detector → masking layer → risk heuristic → user review / download.")
st.caption("Future work: named-entity recognition, configurable enterprise policies, audit events without raw text, role-based access, and deployment testing on IBM LinuxONE.")
