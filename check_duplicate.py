from sheets_local.loader import parse_tester_month_records
from sheets_local.matcher import find_record, check_duplicate

records = parse_tester_month_records("data/check_salaries_export.csv")
record = find_record(records, "Abimael Secco Peixoto", "Jan")

# Case 1: same invoice number as already on file (45) -> should flag duplicate
print("Case 1 (same number, #45):", check_duplicate(record, "45"))

# Case 2: a different, new invoice number -> should NOT flag duplicate
print("Case 2 (different number, #999):", check_duplicate(record, "999"))