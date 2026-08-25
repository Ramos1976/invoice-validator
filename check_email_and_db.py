from mailer.draft_builder import build_draft
from audit.db import get_connection, log_run

# --- Test the email draft builder ---
draft = build_draft(
    invoice_number="2301",
    tester_name="John Doe",
    months="March",
    year="2026",
    pdf_filename="invoice_2301.pdf",
    to="invoice@trustly.com",
    cc="expansion@trustly.com",
)
print("--- Email draft ---")
print("To:", draft.to)
print("CC:", draft.cc)
print("Subject:", draft.subject)
print("Body:", draft.body)
print("Attachment:", draft.attachment_filename)

# --- Test the audit log ---
conn = get_connection("data/audit.db")
log_run(
    conn,
    invoice_number="2301",
    tester_name="John Doe",
    status="VALID",
    issues=[],
    matched_row="row_42",
)
print("\n--- Audit log ---")
rows = conn.execute("SELECT * FROM audit_log").fetchall()
for row in rows:
    print(row)