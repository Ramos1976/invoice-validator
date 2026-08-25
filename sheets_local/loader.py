import csv

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

NAME_ON_INVOICE_COLUMN = 3   # 0-indexed position of "Name on Invoice/Salary"
MONTH_BLOCK_START = 34       # position where the Jan block begins
MONTH_BLOCK_SIZE = 10        # columns per month

def load_raw_rows(csv_path: str) -> list[list[str]]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))

def parse_tester_month_records(csv_path: str) -> list[dict]:
    """Reshapes the wide sheet (one row per tester, 12 months across) into
    a flat list — one dict per tester PER MONTH. Much easier to search."""
    rows = load_raw_rows(csv_path)
    data_rows = rows[2:]  # skip the two header/title rows

    records = []
    for row in data_rows:
        if len(row) <= NAME_ON_INVOICE_COLUMN:
            continue
        tester_name = row[NAME_ON_INVOICE_COLUMN].strip()
        if not tester_name:
            continue

        for month_index, month in enumerate(MONTHS):
            start = MONTH_BLOCK_START + month_index * MONTH_BLOCK_SIZE
            block = row[start:start + MONTH_BLOCK_SIZE]
            if len(block) < MONTH_BLOCK_SIZE:
                continue
            records.append({
                "tester_name": tester_name,
                "month": month,
                "expected_amount": block[2],
                "date_received": block[3],
                "value_paid": block[5],
                "difference": block[6],
                "invoice_number": block[7],
            })
    return records