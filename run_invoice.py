import sys
from extraction.pdf_reader import read_pdf_text
from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser
from validation import rules, normalizers as norm
from validation.decision import decide, Status
from sheets_local.loader import parse_tester_month_records
from sheets_local.matcher import find_record, check_against_sheet
from mailer.draft_builder import build_draft
from audit.db import get_connection, log_run

SHEET_CSV_PATH = "data/check_salaries_export.csv"
AUDIT_DB_PATH = "data/audit.db"
EMAIL_TO = "invoice@trustly.com"
EMAIL_CC = "expansion@trustly.com"

MONTH_MAP = {
    "jan": "Jan", "feb": "Feb", "mar": "Mar", "apr": "Apr", "may": "May", "jun": "Jun",
    "jul": "Jul", "july": "Jul", "aug": "Aug", "sep": "Sep", "oct": "Oct", "nov": "Nov", "dec": "Dec",
}

def extract_month(description: str) -> str | None:
    text = description.lower()
    for key, canonical in MONTH_MAP.items():
        if key in text:
            return canonical
    return None

def run(pdf_path: str):
    print(f"=== Processing {pdf_path} ===")
    invoice_text = read_pdf_text(pdf_path)
    template = detect_template(invoice_text)
    print(f"Detected template: {template}")

    conn = get_connection(AUDIT_DB_PATH)

    if template == "unknown":
        status, final_issues = decide(["Unrecognized invoice template — manual review required"])
        print("\n--- Result ---")
        print("Status:", status, "| Issues:", final_issues)
        log_run(conn, None, None, status.value, final_issues, "N/A")
        return

    fields = tester_1_parser.parse(invoice_text) if template == "tester_1" else tester_2_parser.parse(invoice_text)

    print("\n--- Extracted fields ---")
    for key, value in fields.items():
        print(f"{key}: {value}")

    issues = []
    issues.append(rules.check_invoice_number_format(fields["invoice_number"]))
    issues.append(rules.check_addressee(fields["approver_name"]))

    try:
        invoice_date = norm.normalize_date(fields["invoice_date"])
        due_date = norm.normalize_date(fields["due_date"])
        issues.append(rules.check_due_date(invoice_date, due_date))
    except ValueError as e:
        issues.append(f"Could not parse dates: {e}")

    issues.append(rules.check_bank_details_present(fields["bank_details"]))

    if template == "tester_1":
        for item in fields["line_items"]:
            issues.append(rules.check_description_pattern(item["description"]))
        issues.append(rules.check_line_items_sum_to_total(fields["line_items"], fields["total"]))

    # --- Spreadsheet check ---
    tester_name = input("\nEnter tester name as it appears in the sheet (Name on Invoice/Salary): ").strip()
    sheet_records = parse_tester_month_records(SHEET_CSV_PATH)

    if template == "tester_1":
        for item in fields["line_items"]:
            month = extract_month(item["description"])
            if month is None:
                issues.append(f"Could not determine month for line item: {item['description']}")
                continue
            record = find_record(sheet_records, tester_name, month)
            issues.extend(check_against_sheet(record, fields["invoice_number"], item["amount"]))
    else:
        month = extract_month(fields.get("description_block", "")) or "Jan"
        record = find_record(sheet_records, tester_name, month)
        issues.extend(check_against_sheet(record, fields["invoice_number"], fields["total"]))

    issues = [i for i in issues if i is not None]
    issues = list(dict.fromkeys(issues))  # removes exact duplicates, keeps order
    issues = [i for i in issues if i is not None]
    status, final_issues = decide(issues)

    print("\n--- Validation result ---")
    print("Status:", status)
    print("Issues:", final_issues if final_issues else "None")

    if status == Status.VALID:
        draft = build_draft(
            invoice_number=fields["invoice_number"],
            tester_name=tester_name,
            months="see line items",
            year=str(invoice_date.year),
            pdf_filename=pdf_path,
            to=EMAIL_TO,
            cc=EMAIL_CC,
        )
        print("\n--- Email draft (NOT sent) ---")
        print("To:", draft.to, "| CC:", draft.cc)
        print("Subject:", draft.subject)
        print("Body:", draft.body)
        print("Attachment:", draft.attachment_filename)
    else:
        print("\nNo email drafted — flagged for manual review, nothing sent.")

    log_run(conn, fields["invoice_number"], tester_name, status.value, final_issues, tester_name)
    print("\nLogged to audit database.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 run_invoice.py <path_to_invoice.pdf>")
        sys.exit(1)
    run(sys.argv[1])
