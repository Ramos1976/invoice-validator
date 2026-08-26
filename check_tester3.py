from extraction.template_detector import detect_template
from extraction.parsers import tester_3_parser

invoice_text = """Invoice 220153
Invoice Date: 23-Aug-2026
Due Date: 24-Sep-2026
BILL TO
TRUSTLY GROUP AB
Nir Aravot
Radmansgatan 40
11357 Stockholm Sweden
ID Number: 556 745 86 55
VAT: SE 556 745 865 501

DESCRIPTION QTY UNIT PRICE SUBTOTAL VAT
Computerized informational tests Ireland 3 90.00 90.00

SUBTOTAL €90.00 VAT
Total €90.00

Jevgenij Rykov

177 Whitestown Avenue,
D15HD6F,
Dublin,
Ireland
PRSI: 4161352S
Phone: +353833348798
Payment Details

Bank: REVOLUT

Bank address:
Konstitucijos Pr. 21B
LT-08130, Vilnius, Lithuania

Account details:
IBAN: IE34REVO99036057214992
SWIFT: REVOIE23
"""

template = detect_template(invoice_text)
print(f"Detected template: {template}")

fields = tester_3_parser.parse(invoice_text)
print("\n--- Extracted fields ---")
for key, value in fields.items():
    print(f"{key}: {value}")