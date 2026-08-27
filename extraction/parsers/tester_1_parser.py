import re

def extract_tester_name(text: str) -> str | None:
    """Finds the tester's name by locating the 'Supplier ... Job' header,
    then scanning forward past any header-continuation lines (e.g. 'Due Date',
    'Payment Terms', 'days after date sent') until the first real data line.
    The name is the first 1-2 Title-Case words on that line — this works
    regardless of which country or job title follows, since we never try to
    match those specifically."""
    lines = text.split("\n")
    header_idx = None
    for i, line in enumerate(lines):
        if "Supplier" in line and "Job" in line:
            header_idx = i
            break
    if header_idx is None:
        return None

    header_continuation_words = {
        "due", "date", "days", "after", "sent", "payment",
        "terms", "customer", "id",
    }

    for line in lines[header_idx + 1:]:
        words = line.strip().split()
        if not words:
            continue
        lower_words = {w.lower().strip(":") for w in words}
        if lower_words.issubset(header_continuation_words):
            continue  # just another header-continuation line, skip it

        name_words = []
        for w in words[:2]:
            if w[0].isupper():
                name_words.append(w)
            else:
                break
        return " ".join(name_words) if name_words else None

    return None

def parse(text: str) -> dict:
    invoice_number = re.search(r"INVOICE No\.?\s*(\S+)", text)
    invoice_date = re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", text)
    due_date = re.search(r"Supplier\s+Job\s+Due Date\s*\n.*?(\d{2}/\d{2}/\d{4})", text)
    addressee = re.search(r"To\s+(.*?)\n(.*?)\nSupplier\s+Job\s+Due Date", text, re.DOTALL)

    tester_name = extract_tester_name(text)(
        r"Supplier\s+Job\s+Due Date\s*\n(.*?)\s+(?:Latvia|Lithuania|Sweden|UK|United Kingdom|Bank Consultant|Test accounts|Personal)",
        text,
    )

    line_items = []
    for m in re.finditer(
        r"^\d+\s+(?P<description>(?:Maintenance|Opening)[-\s].*?)\s+"
        r"(?P<unit_price>[\d.,]+)\s*EUR\s+(?P<amount>[\d.,]+)\s*EUR",
        text, re.MULTILINE,
    ):
        line_items.append({
            "description": m.group("description").strip(),
            "unit_price": m.group("unit_price"),
            "amount": m.group("amount"),
        })

    total = re.search(r"Total\s+([\d.,]+)\s*EUR", text)
    iban = re.search(r"IBAN:?\s*(\S+)", text)
    bic = re.search(r"BIC\s*/?\s*Swift\s*Code:?\s*(\S+)", text, re.IGNORECASE)

    return {
        "template": "tester_1",
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "invoice_date": invoice_date.group(1) if invoice_date else None,
        "due_date": due_date.group(1) if due_date else None,
        "approver_name": addressee.group(1).strip() if addressee else None,
        "company_block": addressee.group(2).strip() if addressee else None,
        "tester_name": tester_name,
        "line_items": line_items,
        "total": total.group(1) if total else None,
        "bank_details": {
            "iban": iban.group(1) if iban else None,
            "bic": bic.group(1) if bic else None,
        },
    }