from dataclasses import dataclass

@dataclass
class EmailDraft:
    to: str
    cc: str
    subject: str
    body: str
    attachment_filename: str

def build_draft(invoice_number: str, tester_name: str, months: str, year: str, pdf_filename: str, to: str, cc: str) -> EmailDraft:
    subject = f"Invoice {invoice_number} {tester_name} {months} {year}"
    body = (
        "Please find attached the validated invoice.\n\n"
        f"Invoice: {invoice_number}\nTester: {tester_name}\nPeriod: {months} {year}\n"
    )
    return EmailDraft(to=to, cc=cc, subject=subject, body=body, attachment_filename=pdf_filename)