from validation import normalizers as norm

def find_record(records: list[dict], tester_name: str, month: str) -> dict | None:
    """Finds the one record for a given tester and month."""
    for r in records:
        if norm.normalize_text(r["tester_name"]) == norm.normalize_text(tester_name) and r["month"] == month:
            return r
    return None

def check_against_sheet(record: dict | None, invoice_number: str, invoice_amount: str) -> list[str]:
    """Compares an extracted invoice against its matching sheet record.
    Returns a list of issues (empty list = no problems)."""
    issues = []

    if record is None:
        issues.append("No matching tester/month record found in the spreadsheet")
        return issues  # nothing further to compare without a record

    sheet_invoice_number = record["invoice_number"].strip()
    if sheet_invoice_number and sheet_invoice_number != invoice_number.strip():
        issues.append(
            f"Invoice number mismatch: invoice shows '{invoice_number}', "
            f"sheet already has '{sheet_invoice_number}' on file for this tester/month"
        )

    try:
        expected = norm.normalize_amount(record["expected_amount"])
        actual = norm.normalize_amount(invoice_amount)
        if abs(expected - actual) > 0.01:
            issues.append(f"Amount mismatch: invoice shows {actual}, sheet expects {expected}")
    except (ValueError, TypeError):
        issues.append("Could not compare amounts against sheet")

    return issues

def find_record(records: list[dict], tester_name: str, month: str) -> dict | None:
    normalized_input = norm.normalize_text(tester_name)

    # Exact match first
    for r in records:
        if norm.normalize_text(r["tester_name"]) == normalized_input and r["month"] == month:
            return r

    # Fallback: partial match (all words in the typed name appear in the sheet name)
    input_words = set(normalized_input.split())
    for r in records:
        sheet_words = set(norm.normalize_text(r["tester_name"]).split())
        if input_words.issubset(sheet_words) and r["month"] == month:
            return r

    return None