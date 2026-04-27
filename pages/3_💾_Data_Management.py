"""
Data Management Page - Enter financial data, update CBK rates, manage companies
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from engine.database import get_all_companies, get_company, get_financial_statement, get_connection

st.set_page_config(page_title="Data Management", page_icon="💾", layout="wide")

st.title("💾 Data Management")

tab1, tab2, tab3 = st.tabs(["📊 View Data", "🏦 Update CBK Rates", "➕ Add Company"])

# ==================== TAB 1: VIEW DATA ====================
with tab1:
    st.subheader("View Financial Data")
    
    companies = get_all_companies()
    ticker_options = [f"{c['ticker']} - {c['company_name']} ({c['sector']})" for c in companies]
    selected = st.selectbox("Select Company", ticker_options)
    selected_ticker = selected.split(" - ")[0]
    company = get_company(selected_ticker)
    
    if company:
        st.info(f"**Sector:** {company['sector']} | **Type:** {company['company_type']}")
        
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
                st.metric("D&A", f"{fy_data.get('depreciation_amortization', 0):,.0f}")
                st.metric("Interest Expense", f"{fy_data.get('interest_expense', 0):,.0f}")
                st.metric("Tax Expense", f"{fy_data.get('tax_expense', 0):,.0f}")
            with col3:
                st.metric("Operating CF", f"{fy_data.get('operating_cash_flow', 0):,.0f}")
                st.metric("CapEx", f"{fy_data.get('capital_expenditure', 0):,.0f}")
                st.metric("Shares (M)", f"{fy_data.get('shares_outstanding', 0):,.0f}")
            
            st.subheader("Balance Sheet (KES Millions)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cash", f"{fy_data.get('cash_equivalents', 0):,.0f}")
                st.metric("Receivables", f"{fy_data.get('trade_receivables', 0):,.0f}")
                st.metric("PPE Net", f"{fy_data.get('ppe_net', 0):,.0f}")
            with col2:
                st.metric("Payables", f"{fy_data.get('trade_payables', 0):,.0f}")
                st.metric("Short-Term Debt", f"{fy_data.get('short_term_debt', 0):,.0f}")
                st.metric("Long-Term Debt", f"{fy_data.get('long_term_debt', 0):,.0f}")
        else:
            st.warning("No FY2024 data found")

# ==================== TAB 2: UPDATE CBK RATES ====================
with tab2:
    st.subheader("🏦 Update CBK Treasury Bill Rates")
    st.caption("Enter the latest rates from centralbank.go.ke — updates flow to all valuations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_rf_rate = st.number_input(
            "91-Day T-Bill Rate (%)",
            min_value=5.0,
            max_value=20.0,
            value=13.5,
            step=0.1,
            help="Get this from https://www.centralbank.go.ke/treasury-bills/"
        )
        
        new_erp = st.number_input(
            "Kenya Equity Risk Premium (%)",
            min_value=3.0,
            max_value=15.0,
            value=6.5,
            step=0.1,
            help="Update annually from Damodaran"
        )
    
    with col2:
        new_gdp = st.number_input(
            "GDP Growth Rate (%)",
            min_value=1.0,
            max_value=10.0,
            value=5.3,
            step=0.1,
            help="IMF World Economic Outlook"
        )
        
        new_inflation = st.number_input(
            "CPI Inflation (%)",
            min_value=2.0,
            max_value=15.0,
            value=6.2,
            step=0.1,
            help="KNBS Consumer Price Index"
        )
    
    if st.button("💾 Save Rates to Constants", type="primary", use_container_width=True):
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = [
            ("RISK_FREE_RATE", new_rf_rate / 100, "CBK 91-Day T-Bill"),
            ("EQUITY_RISK_PREMIUM", new_erp / 100, "Damodaran"),
            ("GDP_GROWTH", new_gdp / 100, "IMF WEO"),
            ("CPI_INFLATION", new_inflation / 100, "KNBS"),
        ]
        
        for name, value, source in updates:
            cursor.execute("""
                INSERT OR REPLACE INTO global_constants (constant_name, value, source, last_updated)
                VALUES (?, ?, ?, ?)
            """, (name, value, source, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        conn.close()
        
        st.success("✅ Rates updated successfully!")
        st.info(f"""
        **New Values Saved:**
        - Risk-Free Rate: {new_rf_rate:.1f}%
        - Equity Risk Premium: {new_erp:.1f}%
        - GDP Growth: {new_gdp:.1f}%
        - CPI Inflation: {new_inflation:.1f}%
        """)
    
    st.divider()
    st.subheader("📋 Current Rate History")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM global_constants ORDER BY last_updated DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        history_df = pd.DataFrame([
            {
                "Constant": r["constant_name"],
                "Value": f"{r['value']*100:.1f}%",
                "Source": r["source"],
                "Last Updated": r["last_updated"]
            }
            for r in rows
        ])
        st.dataframe(history_df, hide_index=True, use_container_width=True)
    else:
        st.caption("No rate history yet. Default values from constants.py are in use.")

# ==================== TAB 3: ADD COMPANY ====================
with tab3:
    st.subheader("➕ Add New Company")
    
    new_ticker = st.text_input("Ticker Symbol", max_chars=4, placeholder="e.g. COOP").upper()
    new_name = st.text_input("Company Name", placeholder="e.g. Co-operative Bank of Kenya")
    new_sector = st.selectbox("Sector", ["Banking", "Telecoms", "Consumer Goods", "Construction", "Insurance", "Energy", "Other"])
    new_type = st.selectbox("Type", ["Non-Bank", "Bank"])
    
    if st.button("➕ Add Company to Database", use_container_width=True):
        if new_ticker and new_name:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO companies (ticker, company_name, sector, company_type) VALUES (?, ?, ?, ?)",
                    (new_ticker, new_name, new_sector, new_type)
                )
                conn.commit()
                st.success(f"✅ Added {new_ticker} — {new_name}")
                st.info("Add financial data using the add_companies.py script pattern.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                conn.close()
        else:
            st.warning("Please fill in both Ticker and Company Name.")