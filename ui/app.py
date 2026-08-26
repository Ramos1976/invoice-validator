import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import tempfile
from run_invoice import process_invoice

st.set_page_config(page_title="Invoice Validator", layout="centered")
st.title("Bank Tester Invoice Validator")

uploaded_file = st.file_uploader("Upload an invoice PDF", type=["pdf"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary path, since process_invoice expects a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.subheader("Processing...")
    result = process_invoice(tmp_path)

    st.write(f"**Detected template:** {result['template']}")

    if result["tester_name_needs_input"]:
        st.warning("Tester name could not be extracted automatically.")
        manual_name = st.text_input("Enter tester name as it appears in the spreadsheet:")
        if manual_name:
            result = process_invoice(tmp_path, tester_name_override=manual_name)
        else:
            st.stop()  # wait for input before continuing

    if result["fields"]:
        st.subheader("Extracted fields")
        st.json(result["fields"])

    st.subheader("Validation result")
    status = result["status"]
    if status is not None and status.value == "VALID":
        st.success(f"Status: {status.value}")
    elif status is not None and status.value == "REVIEW_REQUIRED":
        st.warning(f"Status: {status.value}")
    else:
        st.error(f"Status: {status.value if status else 'UNKNOWN'}")

    if result["issues"]:
        st.write("**Issues found:**")
        for issue in result["issues"]:
            st.write(f"- {issue}")
    else:
        st.write("No issues found.")

    if result["email_draft"]:
        st.subheader("Email draft (not sent)")
        d = result["email_draft"]
        st.write(f"**To:** {d.to}")
        st.write(f"**CC:** {d.cc}")
        st.write(f"**Subject:** {d.subject}")
        st.text_area("Body", d.body, height=120)
        st.write(f"**Attachment:** {d.attachment_filename}")
    else:
        st.info("No email drafted — flagged for manual review, nothing sent automatically.")

    os.unlink(tmp_path)  # clean up the temporary file