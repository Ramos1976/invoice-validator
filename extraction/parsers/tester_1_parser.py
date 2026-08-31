import re

HEADER_CONTINUATION_WORDS = {
    "due", "date", "days", "after", "sent", "payment",
    "terms", "customer", "id",
}

def _rejoin_wrapped_lines(text: str) -> str:
    """Fixes PDF text where a line-item description wraps onto its own line
    (with no leading number and no amount), followed by a line that starts
    with just the number and the amounts. Works for any description text,
    not just ones starting with 'Maintenance'/'Opening'."""
    lines = text.split("\n")
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            next_match = re.match(r"^(\d+)\s+([\d.,]+\s*EUR.*)$", next_line)
            looks_like_wrapped_description = bool(re.match(r"^[A-Za-z]", line)) and "EUR" not in line
            if next_match and looks_like_wrapped_description:
                number, rest = next_match.groups()
                fixed_lines.append(f"{number} {line} {rest}")
                i += 2
                continue
        fixed_lines.append(lines[i])
        i += 1
    return "\n".join(fixed_lines)

def _parse_single_line_header(text: str) -> dict:
    """Handles headers written entirely on one line with inline colons, e.g.
    'Supplier: Christian Hansen Job: DANISH ACCOUNTS (7) Due Date: 14/09/2026'
    — a different shape than the two-line 'Supplier Job \\n Name Country ...'
    header our other logic expects."""
    m = re.search(
        r"Supplier:\s*(?P<name>.*?)\s+Job:\s*(?P<job>.*?)\s+Due\s*Date:\s*"
        r"(?P<due>\d{1,2}[-/]\d{1,2}[-/]\d{4})",
        text,
    )
    if not m:
        return {}
    return {"tester_name": m.group("name").strip(), "due_date": m.group("due")}


def extract_invoice_date(text: str) -> str | None:
    """Tries labeled 'Date:' formats first (slash, dot, or written-out month).
    The (?<!Due ) lookbehind avoids accidentally matching inside 'Due Date:',
    which literally contains the substring 'Date:'. Falls back to a bare
    date-only line with no label at all, appearing before the 'To' line —
    some invoices state the date with no 'Date:' label whatsoever."""
    m = (
        re.search(r"(?<!Due )Date:\s*(\d{2}/\d{2}/\d{4})", text)
        or re.search(r"(?<!Due )Date:\s*(\d{2}\.\d{2}\.\d{4})", text)
        or re.search(r"(?<!Due )Date:\s*([A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?,?\s*\d{4})", text)
    )
    if m:
        return m.group(1)

    lines = text.split("\n")
    for line in lines:
        if re.match(r"^To:?\s", line.strip()):
            break
        bare = re.match(r"^(\d{1,2}[/.]\d{1,2}[/.]\d{4})$", line.strip())
        if bare:
            return bare.group(1)
    return None


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
    single_line = _parse_single_line_header(text)
    if single_line.get("tester_name"):
        return single_line["tester_name"]

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
    single_line = _parse_single_line_header(text)
    if single_line.get("due_date"):
        return single_line["due_date"]

    line = find_data_line(text)
    if not line:
        return None
    match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})", line)
    return match.group(1) if match else None

def extract_addressee(text: str) -> tuple[str | None, str | None]:
    lines = text.split("\n")
    to_idx = None
    approver_name = None
    header_idx = None

    for i, line in enumerate(lines):
        if to_idx is None:
            m = re.match(r"To:?\s+(\S.*)", line.strip())
            if m:
                to_idx = i
                name = m.group(1).strip()
                name = re.sub(r"^To:?\s+", "", name)  # strip a doubled "To"
                approver_name = name
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
    text = text.replace("●", "").replace("•", "")

    invoice_number = re.search(r"INVOICE\s+No\.?\s*(\S+)", text) or re.search(
        r"INVOICE\s+(\d+)\s*\n", text
    )
    invoice_date = extract_invoice_date(text)
    due_date = extract_due_date(text)
    approver_name, company_block = extract_addressee(text)
    tester_name = extract_tester_name(text)

    line_items = []
    for m in re.finditer(
        r"^\d+\s+(?P<description>[A-Za-z].*?)\s+"
        r"€?€?\s*(?P<unit_price>[\d.,]+)\s*EUR"
        r"(?:\s+€?€?\s*(?P<amount>[\d.,]+)\s*EUR)?",
        text, re.MULTILINE,
    ):
        description = m.group("description").strip()
        if description.lower() == "total":
            continue
        unit_price = m.group("unit_price")
        amount = m.group("amount") or unit_price
        line_items.append({
            "description": description,
            "unit_price": unit_price,
            "amount": amount,
        })

    total = re.search(r"Total\s+EUR\s+([\d.,]+)", text) or re.search(
        r"Total\s+([\d.,]+)\s*EUR", text
    )
    iban = re.search(
        r"IBAN:?\s*\n?\s*([A-Z0-9][A-Z0-9 ]*?)(?=\s*(?:BIC|SWIFT|/|\n|$))", text
    )
    bic = re.search(
        r"(?:BIC|SWIFT)(?:\s*/?\s*Swift)?(?:\s*Code)?:?\s*\n?\s*([A-Z0-9]{3,11})",
        text, re.IGNORECASE,
    )

    return {
        "template": "tester_1",
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "invoice_date": invoice_date,
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