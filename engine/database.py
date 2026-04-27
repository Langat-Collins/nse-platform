"""
DATABASE LAYER: SQLite CRUD operations
Single file database, no server needed.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                       "data", "nse_platform.db")


def get_connection():
    """Get database connection. Creates file and tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            ticker TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            sector TEXT NOT NULL,
            company_type TEXT NOT NULL CHECK(company_type IN ('Bank', 'Non-Bank')),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS global_constants (
            constant_name TEXT PRIMARY KEY,
            value REAL NOT NULL,
            source TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS financial_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            revenue REAL,
            cost_of_goods_sold REAL,
            operating_expenses REAL,
            depreciation_amortization REAL,
            interest_expense REAL DEFAULT 0,
            other_income REAL DEFAULT 0,
            tax_expense REAL DEFAULT 0,
            net_interest_income REAL,
            non_interest_income REAL,
            loan_loss_provisions REAL,
            bank_operating_expenses REAL,
            net_interest_margin REAL,
            cash_equivalents REAL,
            trade_receivables REAL DEFAULT 0,
            inventory REAL DEFAULT 0,
            other_current_assets REAL DEFAULT 0,
            ppe_net REAL DEFAULT 0,
            goodwill_intangibles REAL DEFAULT 0,
            other_non_current_assets REAL DEFAULT 0,
            trade_payables REAL DEFAULT 0,
            short_term_debt REAL DEFAULT 0,
            other_current_liabilities REAL DEFAULT 0,
            long_term_debt REAL DEFAULT 0,
            other_non_current_liabilities REAL DEFAULT 0,
            gross_loan_book REAL,
            loan_loss_reserve REAL,
            non_performing_loans REAL,
            customer_deposits REAL,
            risk_weighted_assets REAL,
            capital_adequacy_ratio REAL,
            operating_cash_flow REAL DEFAULT 0,
            capital_expenditure REAL DEFAULT 0,
            investing_cash_flow REAL DEFAULT 0,
            financing_cash_flow REAL DEFAULT 0,
            shares_outstanding REAL DEFAULT 0,
            dividends_per_share REAL DEFAULT 0,
            FOREIGN KEY (ticker) REFERENCES companies(ticker),
            UNIQUE(ticker, fiscal_year)
        );
        
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date DATE NOT NULL,
            close_price REAL,
            volume INTEGER,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            beta_5y REAL,
            sector_pe_median REAL,
            FOREIGN KEY (ticker) REFERENCES companies(ticker),
            UNIQUE(ticker, date)
        );
    """)
    
    conn.commit()
    conn.close()


def seed_sample_data():
    """Seed database with realistic NSE data if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Insert companies
    companies = [
        ("SCOM", "Safaricom PLC", "Telecoms", "Non-Bank"),
        ("EQTY", "Equity Group Holdings", "Banking", "Bank"),
        ("KCB", "KCB Group PLC", "Banking", "Bank"),
        ("EABL", "East African Breweries", "Consumer Goods", "Non-Bank"),
    ]
    cursor.executemany(
        "INSERT INTO companies (ticker, company_name, sector, company_type) VALUES (?, ?, ?, ?)",
        companies
    )
    
    # Insert Safaricom FY2024 data
    cursor.execute("""
        INSERT INTO financial_statements (
            ticker, fiscal_year, revenue, cost_of_goods_sold, operating_expenses,
            depreciation_amortization, interest_expense, other_income, tax_expense,
            cash_equivalents, trade_receivables, inventory, other_current_assets,
            ppe_net, goodwill_intangibles, other_non_current_assets,
            trade_payables, short_term_debt, other_current_liabilities,
            long_term_debt, other_non_current_liabilities,
            operating_cash_flow, capital_expenditure, investing_cash_flow,
            financing_cash_flow, shares_outstanding, dividends_per_share
        ) VALUES (
            'SCOM', 2024, 356800, 160000, 65000,
            39000, 7000, 1200, 29000,
            60000, 33000, 6100, 58900,
            228000, 70000, 42000,
            38000, 28000, 42000,
            87000, 43000,
            119000, 54000, -61000,
            -46000, 40065, 0.90
        )
    """)
    
    conn.commit()
    conn.close()
    print("Sample data seeded successfully!")


def get_company(ticker):
    """Fetch a single company's metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE ticker = ?", (ticker,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_companies(active_only=True):
    """Fetch all companies."""
    conn = get_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute("SELECT * FROM companies WHERE is_active = 1 ORDER BY ticker")
    else:
        cursor.execute("SELECT * FROM companies ORDER BY ticker")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_financial_statement(ticker, fiscal_year):
    """Fetch financial statement for a specific company and year."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM financial_statements WHERE ticker = ? AND fiscal_year = ?",
        (ticker, fiscal_year)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# Initialize database on import
initialize_database()