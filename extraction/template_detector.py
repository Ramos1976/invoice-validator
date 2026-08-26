def detect_template(text: str) -> str:
    if "INVOICE No" in text and "Maintenance" in text:
        return "tester_1"
    if "INVOICE" in text and "Qty" in text and "Description" in text:
        return "tester_2"
    if "BILL TO" in text and "Payment Details" in text:
        return "tester_3"
    return "unknown"