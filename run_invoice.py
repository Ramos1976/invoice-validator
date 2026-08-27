import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from extraction.pdf_reader import read_pdf_text
from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser, tester_3_parser
from validation import rules, normalizers as norm
from validation.decision import decide, Status
from sheets_local.loader import parse_tester_month_records
from sheets_local.matcher import find_record, check_against_sheet, check_duplicate
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

def extract_months(description: str) -> list[str]:
    """Returns every month mentioned in the description, in the order they
    appear. A description like 'July-August' or 'Jul-Aug' returns both,
    without duplicating a month matched by more than one keyword (e.g.
    'jul' and 'july' both matching the same word)."""
    text = description.lower()
    seen_canonicals = set()
    found = []
    for key, canonical in MONTH_MAP.items():
        if key in text and canonical not in seen_canonicals:
            pos = text.find(key)
            found.append((pos, canonical))
            seen_canonicals.add(canonical)
    found.sort()
    return [canonical for _, canonical in found]

def process_invoice(pdf_path: str, tester_name_override: str | None = None) -> dict:
    """Runs the full pipeline and returns a result dict instead of printing.
    tester_name_override lets a caller (like the UI) supply a name when
    automatic extraction fails, instead of relying on input()."""
    result = {
        "pdf_path": pdf_path,
        "template": None,
        "fields": None,
        "tester_name": None,
        "tester_name_needs_input": False,
        "status": None,
        "issues": [],
        "email_draft": None,
    }

    invoice_text = read_pdf_text(pdf_path)
    template = detect_template(invoice_text)
    result["template"] = template

    conn = get_connection(AUDIT_DB_PATH)

    if template == "unknown":
        status, final_issues = decide(["Unrecognized invoice template — manual review required"])
        result["status"] = status
        result["issues"] = final_issues
        log_run(conn, None, None, status.value, final_issues, "N/A")
        return result

    if template == "tester_1":
        fields = tester_1_parser.parse(invoice_text)
    elif template == "tester_2":
        fields = tester_2_parser.parse(invoice_text)
    elif template == "tester_3":
        fields = tester_3_parser.parse(invoice_text)
    result["fields"] = fields

    issues = []
    issues.append(rules.check_invoice_number_format(fields["invoice_number"]))
    issues.append(rules.check_addressee(fields["approver_name"]))

    invoice_date = None
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

    tester_name = tester_name_override or fields.get("tester_name")
    if not tester_name:
        result["tester_name_needs_input"] = True
        result["issues"] = ["Tester name could not be extracted — manual input required"]
        result["status"] = Status.REVIEW_REQUIRED
        return result

    result["tester_name"] = tester_name
    sheet_records = parse_tester_month_records(SHEET_CSV_PATH)

    if template == "tester_1":
        grouped: dict[tuple, float] = {}
        for item in fields["line_items"]:
            months = extract_months(item["description"])
            if not months:
                issues.append(f"Could not determine month for line item: {item['description']}")
                continue
            try:
                amount = norm.normalize_amount(item["amount"])
            except (ValueError, TypeError):
                issues.append(f"Could not parse amount for line item: {item['description']}")
                continue
            key = tuple(months)
            grouped[key] = grouped.get(key, 0) + amount

        for months, summed_amount in grouped.items():
            if len(months) > 1:
                issues.append(f"Invoice covers {len(months)} months ({'-'.join(months)})")
                target_month = None
                for m in months:
                    rec = find_record(sheet_records, tester_name, m)
                    if rec and rec["invoice_number"].strip() == fields["invoice_number"].strip():
                        target_month = m
                        break
                month = target_month or months[-1]
            else:
                month = months[0]

            record = find_record(sheet_records, tester_name, month)
            issues.extend(check_against_sheet(record, fields["invoice_number"], str(summed_amount)))
            dup = check_duplicate(record, fields["invoice_number"])
            if dup:
                issues.append(dup)
    elif template == "tester_2":
        month = extract_month(fields.get("description_block", "")) or "Jan"
        record = find_record(sheet_records, tester_name, month)
        issues.extend(check_against_sheet(record, fields["invoice_number"], fields["total"]))
        dup = check_duplicate(record, fields["invoice_number"])
        if dup:
            issues.append(dup)
    elif template == "tester_3":
        month = invoice_date.strftime("%b") if invoice_date else "Jan"
        record = find_record(sheet_records, tester_name, month)
        issues.extend(check_against_sheet(record, fields["invoice_number"], fields["total"]))
        dup = check_duplicate(record, fields["invoice_number"])
        if dup:
            issues.append(dup)

    issues = [i for i in issues if i is not None]
    issues = list(dict.fromkeys(issues))
    status, final_issues = decide(issues)
    result["status"] = status
    result["issues"] = final_issues

    if status == Status.VALID and invoice_date:
        draft = build_draft(
            invoice_number=fields["invoice_number"],
            tester_name=tester_name,
            months="see line items",
            year=str(invoice_date.year),
            pdf_filename=pdf_path,
            to=EMAIL_TO,
            cc=EMAIL_CC,
        )
        result["email_draft"] = draft

    log_run(conn, fields["invoice_number"], tester_name, status.value, final_issues, tester_name)
    return result


def run_from_terminal(pdf_path: str):
    """Terminal-friendly wrapper: calls process_invoice and prints the result,
    handling the manual tester-name prompt if needed."""
    result = process_invoice(pdf_path)

    if result["tester_name_needs_input"]:
        manual_name = input("\nCould not extract tester name automatically. Please enter it manually: ").strip()
        result = process_invoice(pdf_path, tester_name_override=manual_name)

    print(f"=== Processing {pdf_path} ===")
    print(f"Detected template: {result['template']}")
    if result["fields"]:
        print("\n--- Extracted fields ---")
        for key, value in result["fields"].items():
            print(f"{key}: {value}")
    print("\n--- Validation result ---")
    print("Status:", result["status"])
    print("Issues:", result["issues"] if result["issues"] else "None")
    if result["email_draft"]:
        d = result["email_draft"]
        print("\n--- Email draft (NOT sent) ---")
        print("To:", d.to, "| CC:", d.cc)
        print("Subject:", d.subject)
        print("Body:", d.body)
        print("Attachment:", d.attachment_filename)
    else:
        print("\nNo email drafted.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 run_invoice.py <path_to_invoice.pdf>")
        sys.exit(1)
    run_from_terminal(sys.argv[1])