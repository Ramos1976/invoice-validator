from validation.rules import check_invoice_number_format
from validation.decision import decide

result = check_invoice_number_format("INV-2301")
print("Issue found:", result)

status, issues = decide([result] if result else [])
print("Status:", status)