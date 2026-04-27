"""
Data Management Page - Enter and manage financial statement data
"""

import streamlit as st
import pandas as pd
from engine.database import get_all_companies, get_company, get_financial_statement, get_connection

st.set_page_config(page_title="Data Management", page_icon="💾", layout="wide")

st.title("💾 Data Management")

st.markdown("### View & Enter Financial Data")

# Company selector
companies = get_all_companies()
ticker_options = [f"{c['ticker']} - {c['company_name']} ({c['sector']})" for c in companies]
selected = st.selectbox("Select Company", ticker_options)
selected_ticker = selected.split(" - ")[0]
company = get_company(selected_ticker)

if company:
    st.info(f"**Sector:** {company['sector']} | **Type:** {company['company_type']}")
    
    # Show existing data
    fy_data = get_financial_statement(selected_ticker, 2024)
    
    if fy_data:
        st.success("✅ FY2024 data found in database")
        
        st.subheader("Income Statement (KES Millions)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Revenue", f"{fy_data.get('revenue', 0):,.0f}")
            st.metric("COGS", f"{fy_data.get('cost_of_goods_sold', 0):,.0f}")
            st.metric("Operating Expenses", f"{fy_data.get('operating_expenses', 0):,.0f}")
        with col2:
            st.metric("EBITDA Proxy", f"{fy_data.get('depreciation_amortization', 0):,.0f}")
            st.metric("Interest Expense", f"{fy_data.get('interest_expense', 0):,.0f}")
            st.metric("Tax Expense", f"{fy_data.get('tax_expense', 0):,.0f}")
        with col3:
            st.metric("Operating CF", f"{fy_data.get('operating_cash_flow', 0):,.0f}")
            st.metric("CapEx", f"{fy_data.get('capital_expenditure', 0):,.0f}")
            st.metric("Shares Outstanding", f"{fy_data.get('shares_outstanding', 0):,.0f}")
        
        st.subheader("Balance Sheet (KES Millions)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cash", f"{fy_data.get('cash_equivalents', 0):,.0f}")
            st.metric("Receivables", f"{fy_data.get('trade_receivables', 0):,.0f}")
            st.metric("PPE Net", f"{fy_data.get('ppe_net', 0):,.0f}")
            st.metric("Goodwill", f"{fy_data.get('goodwill_intangibles', 0):,.0f}")
        with col2:
            st.metric("Payables", f"{fy_data.get('trade_payables', 0):,.0f}")
            st.metric("Short-Term Debt", f"{fy_data.get('short_term_debt', 0):,.0f}")
            st.metric("Long-Term Debt", f"{fy_data.get('long_term_debt', 0):,.0f}")
    else:
        st.warning("No FY2024 data found for this company")
        
    # Add new data form
    st.divider()
    st.subheader("➕ Add company")
    with st.expander("Add a new company to the database"):
        new_ticker = st.text_input("Ticker", max_chars=4).upper()
        new_name = st.text_input("Company Name")
        new_sector = st.selectbox("Sector", ["Telecoms", "Banking", "Consumer Goods", "Construction", "Insurance"])
        new_type = st.selectbox("Type", ["Non-Bank", "Bank"])
        
        if st.button("Add Company"):
            if new_ticker and new_name:
                conn = get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO companies (ticker, company_name, sector, company_type) VALUES (?, ?, ?, ?)",
                        (new_ticker, new_name, new_sector, new_type)
                    )
                    conn.commit()
                    st.success(f"Added {new_ticker} - {new_name}")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    conn.close()