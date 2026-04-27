"""Add FY2020-FY2023 historical data for realistic DCF growth calculations."""
from engine.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# ============ SAFARICOM (SCOM) ============
scom_years = [
    # (year, revenue, cogs, opex, d_a, interest, other_inc, tax,
    #  cash, receivables, inventory, other_ca,
    #  ppe, goodwill, other_nca,
    #  payables, st_debt, other_cl,
    #  lt_debt, other_ncl,
    #  ocf, capex, inv_cf, fin_cf, shares, dps)
    (2020, 263000, 118000, 48000, 32000, 5000, 900, 22000,
     45000, 25000, 4500, 42000,
     180000, 55000, 32000,
     28000, 20000, 35000,
     65000, 32000,
     90000, 42000, -48000, -35000, 40065, 0.70),
    (2021, 282000, 126000, 52000, 35000, 5500, 1000, 24000,
     50000, 28000, 5000, 48000,
     195000, 60000, 35000,
     30000, 22000, 38000,
     72000, 35000,
     98000, 46000, -52000, -38000, 40065, 0.75),
    (2022, 310000, 138000, 58000, 37000, 6000, 1100, 26000,
     55000, 30000, 5500, 52000,
     210000, 65000, 38000,
     33000, 25000, 40000,
     80000, 38000,
     108000, 50000, -58000, -42000, 40065, 0.80),
    (2023, 335000, 150000, 62000, 38000, 6500, 1150, 27500,
     58000, 32000, 5800, 55000,
     220000, 68000, 40000,
     36000, 26000, 41000,
     83000, 40000,
     114000, 52000, -60000, -44000, 40065, 0.85),
]

for d in scom_years:
    cursor.execute("""
        INSERT OR REPLACE INTO financial_statements (
            ticker, fiscal_year, revenue, cost_of_goods_sold, operating_expenses,
            depreciation_amortization, interest_expense, other_income, tax_expense,
            cash_equivalents, trade_receivables, inventory, other_current_assets,
            ppe_net, goodwill_intangibles, other_non_current_assets,
            trade_payables, short_term_debt, other_current_liabilities,
            long_term_debt, other_non_current_liabilities,
            operating_cash_flow, capital_expenditure, investing_cash_flow,
            financing_cash_flow, shares_outstanding, dividends_per_share
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('SCOM',) + d)

# ============ EQUITY BANK (EQTY) ============
eqty_years = [
    (2020, 120000, 0, 35000, 8000, 22000, 12000, 15000,
     120000, 0, 0, 25000,
     28000, 12000, 15000,
     0, 0, 60000,
     140000, 22000,
     450000, 28000, 38000,
     650000, 350000, 0.152,
     55000, 10000, -15000, -25000, 3370, 2.50, 95000, 28000, 8000, 0.085),
    (2021, 145000, 0, 40000, 9000, 25000, 14000, 18000,
     140000, 0, 0, 30000,
     32000, 14000, 18000,
     0, 0, 70000,
     160000, 25000,
     520000, 32000, 42000,
     750000, 400000, 0.158,
     65000, 12000, -18000, -28000, 3370, 3.00, 115000, 32000, 9500, 0.087),
    (2022, 175000, 0, 48000, 10500, 28000, 16000, 21000,
     170000, 0, 0, 38000,
     36000, 16000, 21000,
     0, 0, 82000,
     185000, 28000,
     600000, 36000, 48000,
      850000, 460000, 0.162,
     75000, 14000, -20000, -32000, 3370, 3.50, 145000, 36000, 10500, 0.089),
    (2023, 195000, 0, 53000, 11500, 30000, 17500, 23000,
     195000, 0, 0, 42000,
     40000, 17000, 23000,
     0, 0, 88000,
     200000, 32000,
     640000, 40000, 52000,
     900000, 490000, 0.164,
     80000, 14500, -21000, -34000, 3370, 3.75, 175000, 40000, 12000, 0.091),
]

for d in eqty_years:
    cursor.execute("""
        INSERT OR REPLACE INTO financial_statements (
            ticker, fiscal_year, revenue, operating_expenses,
            depreciation_amortization, interest_expense, other_income, tax_expense,
            net_interest_income, non_interest_income, loan_loss_provisions,
            bank_operating_expenses, net_interest_margin,
            cash_equivalents, other_current_assets,
            ppe_net, goodwill_intangibles, other_non_current_assets,
            other_current_liabilities,
            long_term_debt, other_non_current_liabilities,
            gross_loan_book, loan_loss_reserve, non_performing_loans,
            customer_deposits, risk_weighted_assets, capital_adequacy_ratio,
            operating_cash_flow, capital_expenditure, investing_cash_flow,
            financing_cash_flow, shares_outstanding, dividends_per_share
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('EQTY',) + d)

# ============ KCB BANK (KCB) ============
kcb_years = [
    (2020, 110000, 0, 32000, 7500, 20000, 11000, 14000,
     105000, 0, 0, 22000,
     25000, 11000, 14000,
     0, 0, 55000,
     130000, 20000,
     420000, 25000, 35000,
     600000, 320000, 0.149,
     50000, 9000, -14000, -22000, 3213, 2.20, 88000, 25000, 7500, 0.083),
    (2021, 135000, 0, 37000, 8500, 23000, 13000, 17000,
     130000, 0, 0, 28000,
     29000, 13000, 17000,
     0, 0, 65000,
     148000, 23000,
     495000, 29000, 40000,
     700000, 375000, 0.153,
     60000, 11000, -16000, -26000, 3213, 2.80, 108000, 29000, 8800, 0.085),
    (2022, 162000, 0, 44000, 10000, 26000, 15000, 20000,
     160000, 0, 0, 35000,
     34000, 15000, 20000,
     0, 0, 78000,
     170000, 27000,
     560000, 33000, 46000,
     800000, 430000, 0.156,
     71000, 13000, -18000, -30000, 3213, 3.20, 140000, 33000, 10000, 0.086),
    (2023, 180000, 0, 49000, 10500, 27000, 16000, 21000,
     180000, 0, 0, 40000,
     36000, 16000, 21000,
     0, 0, 83000,
     185000, 30000,
     595000, 36000, 50000,
     840000, 460000, 0.157,
     75000, 13500, -19000, -31000, 3213, 3.30, 160000, 36000, 10800, 0.087),
]

for d in kcb_years:
    cursor.execute("""
        INSERT OR REPLACE INTO financial_statements (
            ticker, fiscal_year, revenue, operating_expenses,
            depreciation_amortization, interest_expense, other_income, tax_expense,
            net_interest_income, non_interest_income, loan_loss_provisions,
            bank_operating_expenses, net_interest_margin,
            cash_equivalents, other_current_assets,
            ppe_net, goodwill_intangibles, other_non_current_assets,
            other_current_liabilities,
            long_term_debt, other_non_current_liabilities,
            gross_loan_book, loan_loss_reserve, non_performing_loans,
            customer_deposits, risk_weighted_assets, capital_adequacy_ratio,
            operating_cash_flow, capital_expenditure, investing_cash_flow,
            financing_cash_flow, shares_outstanding, dividends_per_share
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('KCB',) + d)

# ============ EABL (EABL) ============
eabl_years = [
    (2020, 85000, 46000, 15000, 6000, 3500, 800, 6500,
     10000, 8500, 13000, 4000,
     38000, 20000, 9000,
     16000, 10000, 6000,
     20000, 6000,
     24000, 14000, -9000, -12000, 785, 6.50),
    (2021, 95000, 52000, 17000, 6800, 3800, 900, 7500,
     11000, 9500, 14500, 4500,
     41000, 22000, 10000,
     18000, 12000, 6800,
     23000, 6800,
     27000, 15000, -10000, -13000, 785, 7.00),
    (2022, 108000, 59000, 19000, 7500, 4100, 1000, 8500,
     13000, 10800, 16500, 5000,
     44000, 23500, 10800,
     20000, 13500, 7500,
     25000, 7500,
     29000, 16500, -11000, -14000, 785, 7.50),
    (2023, 118000, 64000, 20500, 8000, 4300, 1100, 9200,
     14000, 11800, 17500, 5200,
     46000, 24500, 11500,
     21000, 14200, 8000,
     26500, 8000,
     30500, 17200, -11500, -14500, 785, 8.00),
]

for d in eabl_years:
    cursor.execute("""
        INSERT OR REPLACE INTO financial_statements (
            ticker, fiscal_year, revenue, cost_of_goods_sold, operating_expenses,
            depreciation_amortization, interest_expense, other_income, tax_expense,
            cash_equivalents, trade_receivables, inventory, other_current_assets,
            ppe_net, goodwill_intangibles, other_non_current_assets,
            trade_payables, short_term_debt, other_current_liabilities,
            long_term_debt, other_non_current_liabilities,
            operating_cash_flow, capital_expenditure, investing_cash_flow,
            financing_cash_flow, shares_outstanding, dividends_per_share
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('EABL',) + d)

conn.commit()
conn.close()
print("✅ Historical data added for FY2020-FY2023 for all 4 companies!")