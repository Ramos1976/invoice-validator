import re

HEADER_CONTINUATION_WORDS = {
    "due", "date", "days", "after", "sent", "payment",
    "terms", "customer", "id",
}


def _rejoin_wrapped_lines(text: str) -> str:
    """Fixes PDF text where a line-item description wraps onto its own line
    without a leading number, followed by a line that starts with the number
    and amounts. Rebuilds them in the correct order: number, description,
    amounts — matching what the main line-item regex expects."""
    lines = text.split("\n")
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            re.match(r"^(Maintenance|Opening)[-\s]", line.strip())
            and i + 1 < len(lines)
        ):
            next_match = re.match(r"^(\d+)\s+(.*)", lines[i + 1].strip())
            if next_match:
                number, amounts = next_match.groups()
                fixed_lines.append(f"{number} {line.strip()} {amounts}")
                i += 2
                continue
        fixed_lines.append(line)
        i += 1
    return "\n".join(fixed_lines)


def find_data_line(text: str) -> str | None:
    """Finds the header line (contains 'Supplier' and 'Job'), then scans
    forward past any header-continuation lines (e.g. 'Due Date', 'days
    after date sent', 'Payment Terms'), returning the first real data line
    — the one with the tester's name, country/job, and due date."""
    lines = text.split("\n")
    header_idx = None
    for i, line in enumerate(lines):
        if "Supplier" in line and "Job" in line:
            header_idx = i
            break
    if header_idx is None:
        return None

    for line in lines[header_idx + 1:]:
        words = line.strip().split()
        if not words:
            continue
        lower_words = {w.lower().strip(":") for w in words}
        if lower_words.issubset(HEADER_CONTINUATION_WORDS):
            continue
        return line.strip()
    return None


def extract_tester_name(text: str) -> str | None:
    line = find_data_line(text)
    if not line:
        return None
    words = line.split()
    name_words = []
    for w in words[:2]:
        if w[0].isupper():
            name_words.append(w)
        else:
            break
    return " ".join(name_words) if name_words else None


def extract_due_date(text: str) -> str | None:
    """The due date is the date-shaped value on the same data line as the
    tester's name — this avoids depending on the exact header wording."""
    line = find_data_line(text)
    if not line:
        return None
    match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})", line)
    return match.group(1) if match else None


def extract_addressee(text: str) -> tuple[str | None, str | None]:
    """Finds the 'To' line and captures everything after it, up to the
    header line, as the approver name and company block."""
    lines = text.split("\n")
    to_idx = None
    approver_name = None
    header_idx = None

    for i, line in enumerate(lines):
        if to_idx is None:
            m = re.match(r"To:?\s+(\S.*)", line.strip())
            if m:
                to_idx = i
                approver_name = m.group(1).strip()
        if "Supplier" in line and "Job" in line:
            header_idx = i
            break

    if to_idx is None:
        return None, None

    end_idx = header_idx if header_idx and header_idx > to_idx else to_idx + 4
    company_lines = [l.strip() for l in lines[to_idx + 1:end_idx] if l.strip()]
    company_block = "\n".join(company_lines) if company_lines else None
    return approver_name, company_block


def parse(text: str) -> dict:
    text = _rejoin_wrapped_lines(text)

    invoice_number = re.search(r"INVOICE\s+No\.?\s*(\S+)", text) or re.search(
        r"INVOICE\s+(\d+)\s*\n", text
    )
    invoice_date = re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", text) or re.search(
        r"Date:\s*([A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?,\s*\d{4})", text
    )

    due_date = extract_due_date(text)
    approver_name, company_block = extract_addressee(text)
    tester_name = extract_tester_name(text)

    line_items = []
    for m in re.finditer(
        r"^\d+\s+(?P<description>(?:Maintenance|Opening)[-\s].*?)\s+"
        r"€?€?\s*(?P<unit_price>[\d.,]+)\s*EUR"
        r"(?:\s+€?€?\s*(?P<amount>[\d.,]+)\s*EUR)?",
        text, re.MULTILINE,
    ):
        unit_price = m.group("unit_price")
        amount = m.group("amount") or unit_price
        line_items.append({
            "description": m.group("description").strip(),
            "unit_price": unit_price,
            "amount": amount,
        })

    total = re.search(r"Total\s+([\d.,]+)\s*EUR", text)
    iban = re.search(r"IBAN:?\s*(\S+)", text)
    bic = re.search(r"BIC\s*/?\s*Swift\s*(?:Code)?:?\s*(\S+)", text, re.IGNORECASE)

    return {
        "template": "tester_1",
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "invoice_date": invoice_date.group(1) if invoice_date else None,
        "due_date": due_date,
        "approver_name": approver_name,
        "company_block": company_block,
        "tester_name": tester_name,
        "line_items": line_items,
        "total": total.group(1) if total else None,
        "bank_details": {
            "iban": iban.group(1) if iban else None,
            "bic": bic.group(1) if bic else None,
        },
    }