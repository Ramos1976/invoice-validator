import re

def detect_template(text: str) -> str:
    has_maintenance_lines = "Maintenance" in text or "Opening" in text
    double_eur_line_count = len(re.findall(r"^\d+\s+.+?\d+\s*EUR\s+\d+\s*EUR", text, re.MULTILINE))
    single_eur_line_count = len(re.findall(r"^\d+\s+.+?\d+\s*EUR", text, re.MULTILINE))
    has_numbered_eur_lines = double_eur_line_count >= 3 or single_eur_line_count >= 3
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