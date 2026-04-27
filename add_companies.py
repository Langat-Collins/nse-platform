from engine.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT OR REPLACE INTO financial_statements (
        ticker, fiscal_year, 
        revenue, cost_of_goods_sold, operating_expenses,
        depreciation_amortization, interest_expense, other_income, tax_expense,
        net_interest_income, non_interest_income, loan_loss_provisions,
        bank_operating_expenses, net_interest_margin,
        cash_equivalents, trade_receivables, inventory, other_current_assets,
        ppe_net, goodwill_intangibles, other_non_current_assets,
        trade_payables, short_term_debt, other_current_liabilities,
        long_term_debt, other_non_current_liabilities,
        gross_loan_book, loan_loss_reserve, non_performing_loans,
        customer_deposits, risk_weighted_assets, capital_adequacy_ratio,
        operating_cash_flow, capital_expenditure, investing_cash_flow,
        financing_cash_flow, shares_outstanding, dividends_per_share
    ) VALUES (
        'EQTY', 2024,
        210000, 0, 58000,
        12000, 32000, 18500, 25000,
        165000, 45000, 12000,
        58000, 0.092,
        215000, 0, 0, 45000,
        42000, 18000, 25000,
        0, 0, 95000,
        215000, 35000,
        680000, 42000, 58000,
        950000, 520000, 0.165,
        85000, 15000, -22000,
        -35000, 3370, 4.00
    )
""")

cursor.execute("""
    INSERT OR REPLACE INTO financial_statements (
        ticker, fiscal_year,
        revenue, cost_of_goods_sold, operating_expenses,
        depreciation_amortization, interest_expense, other_income, tax_expense,
        net_interest_income, non_interest_income, loan_loss_provisions,
        bank_operating_expenses, net_interest_margin,
        cash_equivalents, trade_receivables, inventory, other_current_assets,
        ppe_net, goodwill_intangibles, other_non_current_assets,
        trade_payables, short_term_debt, other_current_liabilities,
        long_term_debt, other_non_current_liabilities,
        gross_loan_book, loan_loss_reserve, non_performing_loans,
        customer_deposits, risk_weighted_assets, capital_adequacy_ratio,
        operating_cash_flow, capital_expenditure, investing_cash_flow,
        financing_cash_flow, shares_outstanding, dividends_per_share
    ) VALUES (
        'KCB', 2024,
        195000, 0, 52000,
        11000, 28000, 16500, 22000,
        152000, 43000, 14000,
        52000, 0.088,
        198000, 0, 0, 42000,
        38000, 35000, 22000,
        0, 0, 88000,
        195000, 32000,
        620000, 38000, 52000,
        880000, 485000, 0.158,
        78000, 14000, -20000,
        -32000, 3213, 3.50
    )
""")

cursor.execute("""
    INSERT OR REPLACE INTO financial_statements (
        ticker, fiscal_year,
        revenue, cost_of_goods_sold, operating_expenses,
        depreciation_amortization, interest_expense, other_income, tax_expense,
        cash_equivalents, trade_receivables, inventory, other_current_assets,
        ppe_net, goodwill_intangibles, other_non_current_assets,
        trade_payables, short_term_debt, other_current_liabilities,
        long_term_debt, other_non_current_liabilities,
        operating_cash_flow, capital_expenditure, investing_cash_flow,
        financing_cash_flow, shares_outstanding, dividends_per_share
    ) VALUES (
        'EABL', 2024,
        125000, 68000, 22000,
        8500, 4500, 1200, 9800,
        15000, 12500, 18500, 5500,
        48000, 25000, 12000,
        22000, 15000, 8500,
        28000, 8500,
        32000, 18000, -12000,
        -15000, 785, 8.50
    )
""")

conn.commit()
conn.close()
print("Data added for EQTY, KCB, and EABL!")