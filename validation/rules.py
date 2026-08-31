import re as _re
from datetime import timedelta
from . import normalizers as norm

REQUIRED_ADDRESSEE_NAME_OPTIONS = ["luana momm"]  # extend with other approvers
REQUIRED_COMPANY_LINE = "trustly group ab"

def check_invoice_number_format(invoice_number_raw: str) -> str | None:
    if not norm.invoice_number_is_valid(invoice_number_raw):
        return f"Invoice number '{invoice_number_raw}' must contain only digits (no #, brackets, spaces, or symbols)"
    return None

def check_invoice_number_sequence(current_number: str, previous_number: str) -> str | None:
    """Soft check: flags for review if the new number isn't greater than the
    last one on file for this tester — doesn't hard-fail, since testers can
    have legitimate gaps or resets."""
    try:
        if int(current_number) <= int(previous_number):
            return f"Invoice number {current_number} is not greater than previous number {previous_number} on file"
    except (TypeError, ValueError):
        return "Could not compare invoice number sequence (missing or non-numeric previous number)"
    return None

def check_duplicate(current_number: str, vendor: str, existing_records: list[dict]) -> str | None:
    """Rule: same invoice number + same vendor = duplicate. Same number across
    different vendors is fine."""
    for rec in existing_records:
        if rec["invoice_number"] == current_number and norm.normalize_text(rec["vendor"]) == norm.normalize_text(vendor):
            return f"Duplicate: invoice {current_number} already recorded for vendor {vendor}"
    return None

def check_due_date(invoice_date, due_date, min_days: int = 15) -> str | None:
    if due_date < invoice_date + timedelta(days=min_days):
        return f"Due date {due_date} is less than {min_days} days after invoice date {invoice_date}"
    return None

CURRENT_APPROVED_RECIPIENT = "Nir Aravot"

def check_addressee(approver_name_raw: str) -> str | None:
    if approver_name_raw is None or approver_name_raw.strip() == "":
        return "Approver name could not be extracted from the invoice"
    if norm.normalize_text(approver_name_raw) != norm.normalize_text(CURRENT_APPROVED_RECIPIENT):
        return f"Invoice addressed to '{approver_name_raw}', expected '{CURRENT_APPROVED_RECIPIENT}' — needs manual correction"
    return None

def check_description_pattern(description_raw: str) -> str | None:
    """Loosened deliberately: real invoices use many different phrasings
    ('Maintenance', 'Opening', 'Monthly Commission', etc.), so we only check
    that the description looks like real text, not specific keywords. The
    spreadsheet amount comparison is the real safety net for correctness."""
    text = norm.normalize_text(description_raw)
    if not text or not text[0].isalpha():
        return f"Description '{description_raw}' does not look like a valid service description"
    return None

def check_amount(invoice_amount_raw: str, expected_amount: float, tolerance_abs: float = 0.01) -> str | None:
    try:
        invoice_amount = norm.normalize_amount(invoice_amount_raw)
    except (ValueError, TypeError):
        return f"Could not parse invoice amount '{invoice_amount_raw}'"
    if abs(invoice_amount - expected_amount) > tolerance_abs:
        return f"Amount mismatch: invoice shows {invoice_amount}, expected {expected_amount}"
    return None

def check_bank_details_present(bank_details: dict) -> str | None:
    missing = [field for field in ("iban", "bic") if not bank_details.get(field)]
    if missing:
        return f"Missing bank details: {', '.join(missing)}"
    return None

def check_line_items_sum_to_total(line_items: list[dict], total_raw: str, tolerance_abs: float = 0.01) -> str | None:
    try:
        line_sum = sum(norm.normalize_amount(item["amount"]) for item in line_items)
        total = norm.normalize_amount(total_raw)
    except (ValueError, TypeError, KeyError) as e:
        return f"Could not verify line items against total: {e}"
    if abs(line_sum - total) > tolerance_abs:
        return f"Line items sum to {line_sum}, but total states {total}"
    return None