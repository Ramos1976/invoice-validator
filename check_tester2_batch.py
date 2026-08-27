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
    print("due_date:", fields["due_date"])
    print("approver_name:", fields["approver_name"])
    print("total:", fields["total"])
    print("bank_details:", fields["bank_details"])
    print()