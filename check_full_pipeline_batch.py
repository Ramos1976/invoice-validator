from run_invoice import process_invoice

files = [
    "Invoice 062026 Duarte Lorvāo June 2026.pdf",
    "Invoice 20260626 - Sylvain Sanchis - April May June 2026.pdf",
    "Invoice 202608 Ilja Laurs Jul-Aug 2026.pdf",
    "Invoice 52 Nnamdi Sieber June 2026.pdf",
    "Invoice 52026  Veka Rounevaara  Jan to July 2026.pdf",
    "Invoice 61 Christian Hansen June 2026.pdf",
    "Invoice 8526 Ales Bakirov June 2026.pdf",
]

for f in files:
    print(f"\n=== {f} ===")
    result = process_invoice(f)
    print("Template:", result["template"])
    print("Tester name:", result["tester_name"])
    print("Status:", result["status"])
    print("Issues:", result["issues"] if result["issues"] else "None")
    if result["email_draft"]:
        print("Email would be drafted to:", result["email_draft"].to)
    else:
        print("No email drafted.")