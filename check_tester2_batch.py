from extraction.pdf_reader import read_pdf_text
from extraction.parsers import tester_2_parser

files = [
    "sample_tester2.pdf",
    "Invoice 52026  Veka Rounevaara  Jan to July 2026.pdf",
    "Invoice 61 Christian Hansen June 2026.pdf",
]

for f in files:
    print(f"=== {f} ===")
    text = read_pdf_text(f)
    fields = tester_2_parser.parse(text)
    print("tester_name:", fields["tester_name"])
    print("description_block:", fields["description_block"])
    print()