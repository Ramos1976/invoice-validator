import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    invoice_number TEXT,
    tester_name TEXT,
    status TEXT NOT NULL,
    issues TEXT,
    matched_sheet_row TEXT
);
"""

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn

def log_run(conn, invoice_number, tester_name, status, issues: list[str], matched_row: str):
    conn.execute(
        "INSERT INTO audit_log (timestamp, invoice_number, tester_name, status, issues, matched_sheet_row) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), invoice_number, tester_name, status, "; ".join(issues), matched_row),
    )
    conn.commit()