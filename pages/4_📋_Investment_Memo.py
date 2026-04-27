"""
Investment Memo - Auto-generated professional investment memorandum
"""

import streamlit as st
from engine.database import get_all_companies, get_company, get_financial_statement
from engine.analytics import calculate_all_analytics
from engine.valuation import full_dcf_analysis
from datetime import date

st.set_page_config(page_title="Investment Memo", page_icon="📋", layout="wide")

st.title("📋 Investment Memo Generator")

companies = get_all_companies()
ticker_options = [f"{c['ticker']} - {c['company_name']}" for c in companies]
selected = st.selectbox("Select Company for Memo", ticker_options)
selected_ticker = selected.split(" - ")[0]
company = get_company(selected_ticker)

if not company:
    st.stop()

fy_data = get_financial_statement(selected_ticker, 2024)
if not fy_data:
    st.warning("No FY2024 data found.")
    st.stop()

# Sidebar inputs
with st.sidebar:
    st.subheader("Memo Settings")
    share_price = st.number_input("Current Price (KES)", value=18.50, step=0.50)
    beta = st.number_input("Beta", value=0.86, step=0.01)
    analyst_name = st.text_input("Analyst Name", value="Institutional Research")
    fy_data["share_price"] = share_price
    fy_data["beta_5y"] = beta

analytics = calculate_all_analytics(fy_data, company["company_type"])
dcf = full_dcf_analysis(fy_data, analytics)

# Generate Memo
st.divider()
st.subheader(f"📄 Investment Memorandum: {company['company_name']} ({selected_ticker})")

memo = f"""
---
### CONFIDENTIAL — FOR INSTITUTIONAL USE ONLY
**Date:** {date.today().strftime('%B %d, %Y')}  
**Analyst:** {analyst_name}  
**Ticker:** {selected_ticker} | **Sector:** {company['sector']}  

---

### 1. INVESTMENT THESIS

{company['company_name']} currently trades at **KES {share_price:,.2f}** per share. Our DCF analysis suggests an intrinsic value of **KES {dcf['intrinsic_value_per_share']:,.2f}**, representing a **{dcf['margin_of_safety']:.1%}** margin of safety.

**Verdict: {dcf['verdict']}**

---

### 2. VALUATION SUMMARY

| Metric | Value |
|--------|-------|
| Current Price | KES {share_price:,.2f} |
| Intrinsic Value (DCF) | KES {dcf['intrinsic_value_per_share']:,.2f} |
| Upside / Downside | {dcf['upside_percent']:.1%} |
| WACC | {dcf['wacc_components']['wacc']:.1%} |
| Terminal Growth | 5.0% |

---

### 3. FINANCIAL HEALTH

| Metric | Value |
|--------|-------|
| Revenue (FY2024) | KES {fy_data.get('revenue', 0):,.0f} M |
| Net Margin | {analytics['profitability']['net_margin']:.1%} |
| ROE | {analytics['profitability']['roe']:.1%} |
| ROIC | {analytics['profitability']['roic']:.1%} |
| Z-Score | {analytics['z_score']['z_score']:.2f} ({analytics['z_score']['verdict']}) |
| DuPont Variance | {analytics['dupont']['variance']:.4%} {'✓ Consistent' if analytics['dupont']['is_consistent'] else '⚠ Review Data'} |

---

### 4. KEY RISKS

- Kenya macroeconomic environment ({13.5:.0%} risk-free rate indicates tight monetary conditions)
- Currency depreciation risk on foreign-denominated debt
- Sector-specific regulatory changes
- Execution risk on growth strategy assumptions

---

### 5. DISCLAIMER

This memorandum is for informational purposes only and does not constitute investment advice. 
All estimates are based on publicly available data and standard financial models. Past performance 
is not indicative of future results. Consult a qualified financial advisor before making investment decisions.

---
**© {date.today().year} NSE Institutional Platform**
"""

st.markdown(memo)

col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Download as Text", use_container_width=True):
        st.download_button(
            label="Download Memo",
            data=memo,
            file_name=f"{selected_ticker}_Investment_Memo_{date.today()}.txt",
            mime="text/plain"
        )
with col2:
    st.button("🖨️ Print Memo", use_container_width=True, 
             help="Use your browser's print function (Ctrl+P)")