import re

def detect_template(text: str) -> str:
    has_maintenance_lines = "Maintenance" in text or "Opening" in text
    has_numbered_eur_lines = bool(re.search(r"^\d+\s+.+?\d+\s*EUR\s+\d+\s*EUR", text, re.MULTILINE))
    has_qty_description = "Qty" in text and "Description" in text

    if "INVOICE No" in text and has_maintenance_lines:
        return "tester_1"
    if has_maintenance_lines and has_qty_description:
        return "tester_1"
    if has_numbered_eur_lines and has_qty_description:
        return "tester_1"
    if "BILL TO" in text and "Payment Details" in text:
        return "tester_3"
    if has_qty_description:
        return "tester_2"
    return "unknown"