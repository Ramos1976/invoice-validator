import re

def parse(text: str) -> dict:
    invoice_number = re.search(r"Invoice\s+(\d+)", text)
    invoice_date = re.search(r"Invoice Date:\s*([\d]{1,2}-\w{3}-\d{4})", text)
    due_date = re.search(r"Due Date:\s*([\d]{1,2}-\w{3}-\d{4})", text)

    approver = re.search(
        r"TRUSTLY GROUP AB\s*\n\s*(.*?)\n", text
    )

    description = re.search(
    r"\n([A-Za-z][^\n]+?)\s+(\d+)\s+(\d+\.\d{2})\s+(\d+\.\d{2})\s*\n", text
    )

    total = re.search(r"Total\s*€?\s*([\d.,]+)", text)

    tester_name = re.search(r"\n([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+)\s+Payment Details", text)
        
    iban = re.search(r"IBAN:\s*(\S+)", text)
    swift = re.search(r"SWIFT:\s*(\S+)", text)

    return {
        "template": "tester_3",
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "invoice_date": invoice_date.group(1) if invoice_date else None,
        "due_date": due_date.group(1) if due_date else None,
        "approver_name": approver.group(1).strip() if approver else None,
        "tester_name": tester_name.group(1).strip() if tester_name else None,
        "description": description.group(1).strip() if description else None,
        "quantity": description.group(2) if description else None,
        "unit_price": description.group(3) if description else None,
        "total": total.group(1) if total else None,
        "bank_details": {
            "iban": iban.group(1) if iban else None,
            "bic": swift.group(1) if swift else None,
        },
    }