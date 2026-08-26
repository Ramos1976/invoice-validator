from extraction.pdf_reader import read_pdf_text
from extraction.parsers import tester_1_parser, tester_2_parser

text1 = read_pdf_text("sample_tester1.pdf")
fields1 = tester_1_parser.parse(text1)
print("Tester_1 name extracted:", fields1["tester_name"])

text2 = read_pdf_text("sample_tester2.pdf")
fields2 = tester_2_parser.parse(text2)
print("Tester_2 name extracted:", fields2["tester_name"])