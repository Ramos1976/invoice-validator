from sheets_local.loader import parse_tester_month_records
from sheets_local.matcher import find_record, check_against_sheet

records = parse_tester_month_records("data/check_salaries_export.csv")

# Case 1: matches exactly what's on file
record = find_record(records, "Abimael Secco Peixoto", "Jan")
issues = check_against_sheet(record, invoice_number="45", invoice_amount="240.00")
print("Case 1 (should match cleanly):", issues)

# Case 2: wrong amount
issues = check_against_sheet(record, invoice_number="45", invoice_amount="999.00")
print("Case 2 (wrong amount):", issues)

# Case 3: tester not found
missing_record = find_record(records, "Nonexistent Tester", "Jan")
issues = check_against_sheet(missing_record, invoice_number="1", invoice_amount="1")
print("Case 3 (no matching record):", issues)