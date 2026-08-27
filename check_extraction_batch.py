from extraction.pdf_reader import read_pdf_text
from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser, tester_3_parser

files = [
    "Invoice 52026  Veka Rounevaara  Jan to July 2026.pdf",
    "Invoice 61 Christian Hansen June 2026.pdf",
]

parsers = {
    "tester_1": tester_1_parser,
    "tester_2": tester_2_parser,
    "tester_3": tester_3_parser,
}

for f in files:
    print(f"=== {f} ===")
    text = read_pdf_text(f)
    template = detect_template(text)
    print(f"Detected template: {template}")
    fields = parsers[template].parse(text)
    for key, value in fields.items():
        print(f"{key}: {value}")
    print()