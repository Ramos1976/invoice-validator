import re
from datetime import datetime

def normalize_invoice_number(raw: str) -> str:
    """Per the bank-tester rules: digits only, no #, brackets, spaces, ?, +, _"""
    if raw is None:
        return ""
    cleaned = re.sub(r"[^\d]", "", raw)
    return cleaned

def invoice_number_is_valid(raw: str) -> bool:
    """Rule: invoice number must contain only digits after normalization
    matches the original, uninterrupted. A raw value like 'INV-2301' would
    normalize to '2301' but that's a format violation, not a clean number —
    so we check the raw string directly against a digits-only pattern."""
    if raw is None:
        return False
    return bool(re.fullmatch(r"\d+", raw.strip()))

def normalize_amount(raw: str) -> float:
    """Strip currency symbols, spaces, unify decimal separator."""
    if raw is None:
        return None
    cleaned = re.sub(r"[^\d,.\-]", "", raw)
    # Handle European (1.234,56) vs US (1,234.56) formats
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # Ambiguous: could be thousands sep or decimal sep.
        # Heuristic: if exactly 2 digits after last comma, treat as decimal.
        parts = cleaned.split(",")
        cleaned = cleaned.replace(",", ".") if len(parts[-1]) == 2 else cleaned.replace(",", "")
    return float(cleaned)

def normalize_date(raw: str) -> datetime.date:
    """Try common formats; raise ValueError if none match — an unparseable
    date should surface as REVIEW_REQUIRED, never be silently guessed."""
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%d.%m.%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {raw!r}")

def normalize_text(raw: str) -> str:
    """Trim, collapse whitespace, lowercase — for fuzzy text comparison only.
    Never used for numeric or invoice-number fields."""
    if raw is None:
        return ""
    return re.sub(r"\s+", " ", raw.strip()).lower()