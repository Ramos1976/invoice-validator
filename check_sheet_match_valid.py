from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser
from validation import rules, normalizers as norm
from validation.decision import decide
from sheets_local.loader import parse_tester_month_records
from sheets_local.matcher import find_record, check_against_sheet

# Typed invoice using Abimael's real, known-correct January numbers
invoice_text = """INVOICE
Date: 20/01/2026
INVOICE No. 45
To Nir Aravot
Trustly Group AB
Rådmansgatan 40
113 57 Stockholm, Sweden
Supplier Job Due Date
Abimael Secco Peixoto United Kingdom Personal 06/02/2026
1 Maintenance- Jan - TestBank 999 EUR 999 EUR
17 Total 999.00EUR
IBAN: XX2222222222
BIC/SwiftCode: XXXXXXX
"""

template = detect_template(invoice_text)
print(f"Detected template: {template}")

fields = tester_1_parser.parse(invoice_text) if template == "tester_1" else None

if fields:
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

    for item in fields["line_items"]:
        issues.append(rules.check_description_pattern(item["description"]))

    issues.append(rules.check_line_items_sum_to_total(fields["line_items"], fields["total"]))
    issues.append(rules.check_bank_details_present(fields["bank_details"]))

    # --- Spreadsheet check, using the real tester name and month from this invoice ---
    sheet_records = parse_tester_month_records("data/check_salaries_export.csv")
    tester_name = "Abimael Secco Peixoto"  # matches "Name on Invoice/Salary" in the sheet
    month = "Jan"  # from the line item description
    record = find_record(sheet_records, tester_name, month)
    sheet_issues = check_against_sheet(record, fields["invoice_number"], fields["line_items"][0]["amount"])
    issues.extend(sheet_issues)

    issues = [i for i in issues if i is not None]
    status, final_issues = decide(issues)

    print("\n--- Validation result ---")
    print("Status:", status)
    print("Issues:", final_issues if final_issues else "None")