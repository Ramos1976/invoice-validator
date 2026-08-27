from extraction.pdf_reader import read_pdf_text
from extraction.template_detector import detect_template

files = [
    "sample_tester1.pdf",
    "sample_tester2.pdf",
    "sample_tester3.pdf",
    "sample_unknown.pdf",
    "sample_unknown_1.pdf",
    "Invoice 062026 Duarte Lorvāo June 2026.pdf",
    "Invoice 20260626 - Sylvain Sanchis - April May June 2026.pdf",
    "Invoice 202608 Ilja Laurs Jul-Aug 2026.pdf",
    "Invoice 52 Nnamdi Sieber June 2026.pdf",
    "Invoice 52026  Veka Rounevaara  Jan to July 2026.pdf",
    "Invoice 61 Christian Hansen June 2026.pdf",
    "Invoice 8526 Ales Bakirov June 2026.pdf",
]

for f in files:
    text = read_pdf_text(f)
    template = detect_template(text)
    print(f"{f}: {template}")