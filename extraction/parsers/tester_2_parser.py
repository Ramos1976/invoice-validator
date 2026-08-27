import re

def parse(text: str) -> dict:
    invoice_number = re.search(r"INVOICE\s+(\S+)\s*\n", text)
    invoice_date = re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", text)
    due_date = re.search(
        r"Supplier\s+Job\s+Due\s+[Dd]ate\s*\n.*?(\d{1,2}[-/]\d{1,2}[-/]\d{4})", text
    )
    addressee = re.search(
        r"To\s+(?:c/o\s+)?(?:To\s+)?(.*?)\n(.*?)\nSupplier\s+Job\s+Due\s+[Dd]ate",
        text, re.DOTALL,
    )

    tester_name = re.search(
        r"Supplier\s+Job\s+Due Date\s*\n(.*?)\s+(?:Test accounts|Personal|Latvia|Lithuania)",
        text,
    )

    # Description block sits between the header row and "VAT" or "Total"
    desc_block = re.search(
        r"Qty\s+Description\s+Unit Price\s+Line\s*\n(.*?)\n\s*VAT",
        text, re.DOTALL,
    )
    total = re.search(r"Total\s*\n?\s*([\d.,]+)\s*EUR", text) or re.search(
        r"([\d.,]+)\s*EUR\s*\n\s*Total", text
    )
    iban = re.search(
        r"IBAN:?\s*\n?\s*([A-Z0-9][A-Z0-9 ]*?)(?=\s*(?:BIC|SWIFT|\n|$))", text
    )
    bic = re.search(r"(?:BIC|SWIFT)\s*(?:/\s*Swift)?:?\s*\n?\s*([A-Z0-9]{3,11})", text)
    return {
        "template": "tester_2",
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "invoice_date": invoice_date.group(1) if invoice_date else None,
        "due_date": due_date.group(1) if due_date else None,
        "approver_name": addressee.group(1).strip() if addressee else None,
        "company_block": addressee.group(2).strip() if addressee else None,
        "tester_name": tester_name.group(1).strip() if tester_name else None,
        "description_block": desc_block.group(1).strip() if desc_block else None,
        "total": total.group(1) if total else None,
        "bank_details": {
            "iban": iban.group(1) if iban else None,
            "bic": bic.group(1) if bic else None,
        },
    }