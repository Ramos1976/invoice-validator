def detect_template(text: str) -> str:
    """Returns 'tester_1', 'tester_2', or 'unknown'."""
    if "INVOICE No" in text and "Maintenance" in text:
        return "tester_1"
    if "INVOICE" in text and "Qty" in text and "Description" in text:
        return "tester_2"
    return "unknown"