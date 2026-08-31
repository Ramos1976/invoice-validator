# Invoice Validator

## Setup
1. Clone the repo
2. `python3 -m venv venv`
3. `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. Copy `config/.env.example` to `.env` and fill in real values
6. Place the spreadsheet export at `data/check_salaries_export.csv` (ask Fabio for this — not included in git, contains real financial data)

## Running the app
- Web UI: `streamlit run ui/app.py`
- Terminal (single invoice): `python3 run_invoice.py path/to/invoice.pdf`

## What it does
Extracts data from bank tester invoices (PDF), validates against the spreadsheet, and flags issues for manual review. Supports 3 invoice templates so far; anything else is routed to manual review automatically.