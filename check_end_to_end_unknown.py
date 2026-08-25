from extraction.template_detector import detect_template
from extraction.parsers import tester_1_parser, tester_2_parser

invoice_text = """PVM sąskaita faktūra/VAT invoice: AMX
89/26
Sąskaitos išrašymo data:
21.08.2026
04.09.2026
MB AMEXA
Įmonės kodas/Company ID: xxxxx
Date of issue:
Sąskaitą apmokėti iki:
PVM numeris/VAT Number: LT100017888010 Due date:
periodas:
Tel.: xxxxxxxx
E-mail: xxxxxxx@gmail.com Pirkėjas/Customer:
AUGUST
TRUSTLY GROUP AB
Radmansgatan 40
11357 Stockholm
Sweden
Įmonės kodas/Company ID: xxxx
PVM numeris/VAT Number: xxxxx
Služba
Service
Cena
Price
Kiekis
Quantity
Suma
Total
Kompiuteriniai informaciniai testai Lietuva
Computerized informational tests Lithuania
40.00 € 13.0 520.00 €
"""

template = detect_template(invoice_text)
print(f"Detected template: {template}")

if template == "tester_1":
    fields = tester_1_parser.parse(invoice_text)
    print("\nWARNING: this was misclassified as tester_1!")
elif template == "tester_2":
    fields = tester_2_parser.parse(invoice_text)
    print("\nWARNING: this was misclassified as tester_2!")
else:
    print("\nCorrectly unrecognized — this invoice would be flagged REVIEW_REQUIRED")
    print("Reason: 'Unrecognized invoice template — manual review required'")