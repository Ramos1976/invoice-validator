from extraction.pdf_reader import read_pdf_text
from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser

for filename in ["sample_unknown.pdf", "sample_unknown_1.pdf"]:
    invoice_text = read_pdf_text(filename)
    template = detect_template(invoice_text)
    print(f"{filename}: detected template = {template}")