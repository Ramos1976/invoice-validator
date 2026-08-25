from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser
from validation import rules, normalizers as norm
from validation.decision import decide

invoice_text = """INVOICE
Date: 28/07/2026
INVOICE 59
To c/o Teo Rantanen
Trustly Group AB
Rådmansgatan 40
113 57 Stockholm, Sweden
Supplier Job Due Date
Tester_2 Test accounts 10/08/2026
Qty Description Unit Price Line
14 August/26
-UK monthly comission – Barclays, Bank Of Scotland, Starling,
Halifax, Tsb Bank, Monzo, Nationwide, Lloyds, Metro,
Santander, Revolut, Cashplus, Wise
-SE monthly commission - Swedbank
40 EUR 560 EUR
VAT
0
Total 560.00 EUR
IBAN XXXXXXXXX BIC XXX
"""

template = detect_template(invoice_text)
print(f"Detected template: {template}")

if template == "tester_1":
    fields = tester_1_parser.parse(invoice_text)
elif template == "tester_2":
    fields = tester_2_parser.parse(invoice_text)
else:
    print("Unknown template — would be flagged REVIEW_REQUIRED here, stopping.")
    fields = None

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
        issues.append(f"Could not parse dates for due-date check: {e}")

    issues.append(rules.check_bank_details_present(fields["bank_details"]))

    issues = [i for i in issues if i is not None]
    status, final_issues = decide(issues)

    print("\n--- Validation result ---")
    print("Status:", status)
    print("Issues:", final_issues if final_issues else "None")