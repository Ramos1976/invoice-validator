import pdfplumber

def read_pdf_text(pdf_path: str) -> str:
    """Extracts all text from a PDF file, page by page, joined together."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)