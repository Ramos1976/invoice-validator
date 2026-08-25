from sheets_local.loader import parse_tester_month_records

records = parse_tester_month_records("data/check_salaries_export.csv")
print(f"Total tester-month records: {len(records)}")

# Show Abimael's January record specifically, to compare against the real sheet
for r in records:
    if "Abimael" in r["tester_name"] and r["month"] == "Jan":
        print(r)