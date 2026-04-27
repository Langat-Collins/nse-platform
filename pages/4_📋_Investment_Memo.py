"""
Investment Memo - Auto-generated professional investment memorandum
"""

import streamlit as st
from engine.database import get_all_companies, get_company, get_financial_statement, get_connection
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

# Default prices by ticker
DEFAULT_PRICES = {"SCOM": 29.90, "EQTY": 75.50, "KCB": 68.75, "EABL": 245.00}

# Sidebar inputs
with st.sidebar:
    st.subheader("Memo Settings")
    
    default_price = DEFAULT_PRICES.get(selected_ticker, 50.00)
    share_price = st.number_input("Current Price (KES)", value=float(default_price), step=0.50)
    beta = st.number_input("Beta", value=0.86, step=0.01)
    analyst_name = st.text_input("Analyst Name", value="Institutional Research")
    
    investor_type = st.radio(
        "Tax Residency",
        ["🇰🇪 Resident", "🌍 Non-Resident"],
        index=0
    )
    wht_rate = 0.05 if "Resident" in investor_type else 0.15
    
    fy_data = dict(fy_data)
    fy_data["share_price"] = share_price
    fy_data["beta_5y"] = beta

analytics = calculate_all_analytics(fy_data, company["company_type"])
dcf = full_dcf_analysis(fy_data, analytics)

# Get current risk-free rate
from utils.constants import RISK_FREE_RATE, GDP_GROWTH
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM global_constants WHERE constant_name = 'RISK_FREE_RATE' ORDER BY last_updated DESC LIMIT 1")
    row = cursor.fetchone()
    current_rf = (row["value"] * 100) if row else (RISK_FREE_RATE * 100)
    conn.close()
except:
    current_rf = RISK_FREE_RATE * 100

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

### 1. EXECUTIVE SUMMARY

{company['company_name']} ({selected_ticker}) is a leading {company['sector']} company listed on the Nairobi Securities Exchange. Based on FY2024 financial data, the company generated revenue of **KES {fy_data.get('revenue', 0):,.0f} million** with a net margin of **{analytics['profitability']['net_margin']:.1%}**.

At the current market price of **KES {share_price:,.2f}**, our Discounted Cash Flow (DCF) analysis estimates an intrinsic value of approximately **KES {dcf['intrinsic_value_per_share']:,.2f}** per share, implying a **{dcf['upside_percent']:.1%}** upside potential and a margin of safety of **{dcf['margin_of_safety']:.1%}**.

**Investment Verdict: {dcf['verdict']}**

> ⚠️ **Important:** The DCF model uses FY2024 as a single base year. Intrinsic value estimates are highly sensitive to assumptions regarding revenue growth, WACC, and terminal growth rate. Refer to the Sensitivity Matrix in the Company Analysis page for a range of possible outcomes under different scenarios.

---

### 2. VALUATION SUMMARY

| Metric | Value | Notes |
|--------|-------|-------|
| Current Share Price | KES {share_price:,.2f} | As of {date.today().strftime('%B %d, %Y')} |
| Intrinsic Value (DCF) | KES {dcf['intrinsic_value_per_share']:,.2f} | Base case |
| Upside / Downside | {dcf['upside_percent']:.1%} | vs current price |
| Margin of Safety | {dcf['margin_of_safety']:.1%} | (IV - Price) / IV |
| WACC | {dcf['wacc_components']['wacc']:.1%} | CAPM-based |
| Terminal Growth | 5.0% | Gordon Growth Model |
| Market-Implied Growth | {dcf['implied_growth']:.2%} | Reverse DCF |

**WACC Components:**
- Risk-Free Rate (91-Day T-Bill): {current_rf:.1f}%
- Cost of Equity (CAPM): {dcf['wacc_components']['cost_of_equity']:.1%}
- Cost of Debt (After-Tax): {dcf['wacc_components']['after_tax_cost_of_debt']:.1%}

---

### 3. FINANCIAL HEALTH ANALYSIS

**Profitability (FY2024)**

| Metric | Value |
|--------|-------|
| Revenue | KES {fy_data.get('revenue', 0):,.0f} Million |
| Gross Margin | {analytics['profitability']['gross_margin']:.1%} |
| EBITDA Margin | {analytics['profitability']['ebitda_margin']:.1%} |
| Net Margin | {analytics['profitability']['net_margin']:.1%} |
| ROE | {analytics['profitability']['roe']:.1%} |
| ROIC | {analytics['profitability']['roic']:.1%} |
| Free Cash Flow | KES {analytics['derived_balance']['free_cash_flow']:,.0f} Million |
| FCF Margin | {analytics['profitability']['fcf_margin']:.1%} |

**Financial Stability**

| Metric | Value | Assessment |
|--------|-------|------------|
| Altman Z-Score | {analytics['z_score']['z_score']:.2f} | {analytics['z_score']['verdict']} |
| Current Ratio | {analytics['liquidity']['current_ratio']:.2f}x | |
| Debt-to-Equity | {analytics['liquidity']['debt_to_equity']:.2f}x | |
| Interest Coverage | {analytics['liquidity']['interest_coverage']:.1f}x | |
| DuPont Consistency | {analytics['dupont'].get('variance', 0):.4%} | {'✓ Consistent' if analytics['dupont'].get('is_consistent', False) else '⚠ Review Required'} |

**DuPont Decomposition:**
- Net Margin (Profitability Driver): {analytics['dupont'].get('net_margin_dupont', 0):.1%}
- Asset Turnover (Efficiency Driver): {analytics['dupont'].get('asset_turnover', 0):.2f}x
- Equity Multiplier (Leverage Driver): {analytics['dupont'].get('equity_multiplier', 0):.2f}x

---

### 4. DIVIDEND ANALYSIS

| Metric | Value |
|--------|-------|
| Dividends Per Share (Gross) | KES {fy_data.get('dividends_per_share', 0) or 0:.2f} |
| Withholding Tax Rate | {wht_rate:.0%} ({investor_type}) |
| Net DPS After Tax | KES {(fy_data.get('dividends_per_share', 0) or 0) * (1 - wht_rate):.2f} |
| Dividend Yield (Net) | {(((fy_data.get('dividends_per_share', 0) or 0) * (1 - wht_rate)) / share_price):.2%} |

---

### 5. KEY RISK FACTORS

1. **Macroeconomic Risk:** Kenya's 91-day T-Bill rate of {current_rf:.1f}% indicates a tight monetary environment. High interest rates may pressure corporate earnings and consumer spending.

2. **Currency Risk:** The Kenya Shilling (KES) remains vulnerable to depreciation against major currencies (USD, EUR, GBP), potentially increasing the cost of imported inputs and foreign-denominated debt service.

3. **Regulatory Risk:** Changes in sector-specific regulations, tax policy, or excise duties could materially impact the company's operating margins and profitability.

4. **Model Risk:** The DCF valuation relies on assumptions about future growth, WACC, and terminal value. A 1% change in WACC or terminal growth rate can significantly alter the intrinsic value estimate. Refer to the Sensitivity Matrix for a range of outcomes.

5. **Market Risk:** Equity markets are subject to volatility from both domestic factors (political cycles, election periods) and external shocks (global commodity prices, geopolitical events).

---

### 6. DISCLAIMER

*This memorandum is prepared for informational and educational purposes only. It does not constitute investment advice, a recommendation, or a solicitation to buy or sell any security. All estimates and projections are based on publicly available financial data and standard valuation models. Past performance is not indicative of future results. The intrinsic value calculations involve significant assumptions and inherent uncertainties. Readers should conduct their own due diligence and consult a qualified financial advisor before making any investment decisions.*

*Data Sources: Nairobi Securities Exchange (NSE), Central Bank of Kenya (CBK), Kenya National Bureau of Statistics (KNBS), International Monetary Fund (IMF), Damodaran Online.*

---
**© {date.today().year} NSE Institutional Investment Platform | Confidential | For Institutional Use Only**
"""

st.markdown(memo)

# Download
col1, col2 = st.columns(2)
with col1:
    memo_bytes = memo.encode('utf-8')
    st.download_button(
        label="📥 Download Memo (Text)",
        data=memo_bytes,
        file_name=f"{selected_ticker}_Investment_Memo_{date.today().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )
with col2:
    st.caption("🖨️ Use Ctrl+P to print directly from your browser")

st.divider()
st.caption("📋 This memo is auto-generated based on FY2024 financial data and standard valuation models. Review all assumptions before use.")