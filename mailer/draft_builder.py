from dataclasses import dataclass

@dataclass
class EmailDraft:
    to: str
    cc: str
    subject: str
    body: str
    attachment_filename: str

def build_draft(invoice_number: str, tester_name: str, months: str, year: str, pdf_filename: str, to: str, cc: str) -> EmailDraft:
    """VALID invoices: subject only, no body — matches the Confluence
    convention of forwarding the invoice with just the filename-style
    subject line and the PDF attached."""
    subject = f"Invoice {invoice_number} {tester_name} {months} {year}"
    return EmailDraft(to=to, cc=cc, subject=subject, body="", attachment_filename=pdf_filename)


def build_review_notification(invoice_number: str, tester_name: str, template: str, issues: list[str], pdf_filename: str, to: str) -> EmailDraft:
    """REVIEW_REQUIRED / INVALID invoices: detailed body listing the
    specific issues found, sent to the team rather than invoice@trustly.com."""
    subject = f"Review needed: Invoice {invoice_number} — {tester_name}"
    issues_text = "\n".join(f"- {issue}" for issue in issues)
    body = (
        "Hello,\n\n"
        "The following invoice requires manual review before it can be sent or approved.\n\n"
        f"Invoice: {invoice_number}\n"
        f"Tester: {tester_name}\n"
        f"Template detected: {template}\n\n"
        "Issues found:\n"
        f"{issues_text}\n\n"
        "This invoice was NOT sent automatically. Please review manually.\n\n"
        f"Attachment: {pdf_filename} (please attach manually before sending, if forwarding)\n\n"
        "Regards,\nInvoice Validation System"
    )
    return EmailDraft(to=to, cc="", subject=subject, body=body, attachment_filename=pdf_filename)