import re

def parse(text: str) -> dict:
    invoice_number = re.search(r"INVOICE No\.?\s*(\S+)", text)
    invoice_date = re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", text)
    due_date = re.search(r"Supplier\s+Job\s+Due Date\s*\n.*?(\d{2}/\d{2}/\d{4})", text)
    addressee = re.search(r"To\s+(.*?)\n(.*?)\nSupplier\s+Job\s+Due Date", text, re.DOTALL)

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
        "line_items": line_items,
        "total": total.group(1) if total else None,
        "bank_details": {
            "iban": iban.group(1) if iban else None,
            "bic": bic.group(1) if bic else None,
        },
    }