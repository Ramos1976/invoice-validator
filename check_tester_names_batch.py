from extraction.pdf_reader import read_pdf_text
from extraction.parsers.tester_1_parser import extract_tester_name

files = [
    "Invoice 062026 Duarte Lorvāo June 2026.pdf",
    "Invoice 20260626 - Sylvain Sanchis - April May June 2026.pdf",
    "Invoice 202608 Ilja Laurs Jul-Aug 2026.pdf",
    "Invoice 52 Nnamdi Sieber June 2026.pdf",
    "Invoice 52026  Veka Rounevaara  Jan to July 2026.pdf",
    "Invoice 61 Christian Hansen June 2026.pdf",
]

for f in files:
    text = read_pdf_text(f)
    name = extract_tester_name(text)
    print(f"{f}: {name}")