"""
NSE Institutional Investment Platform
Main entry point - redirects to Company Analysis by default.
"""

import streamlit as st

st.set_page_config(
    page_title="NSE Institutional Platform",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🇰🇪 NSE Institutional Investment Platform")
st.caption("Professional-grade financial analysis for the Nairobi Securities Exchange")

st.markdown("""
### Welcome to the NSE Institutional Platform

This application replicates the functionality of an institutional-grade Excel workbook 
for Kenyan equity analysis, converted into a live, interactive web platform.

**Navigation:** Use the sidebar to explore different modules:
- **Company Analysis** — Deep-dive DCF valuation, DuPont analysis, Z-Score, and financial health
- **Comparison Engine** — Side-by-side ranking of up to 8 NSE stocks
- **Investment Memo** — Auto-generated professional investment memorandum
- **Data Management** — Enter and manage financial statement data
""")

# Sidebar summary
with st.sidebar:
    st.header("📊 Quick Overview")
    from engine.database import get_all_companies
    companies = get_all_companies()
    st.metric("Companies Tracked", len(companies))
    st.metric("Latest Data", "FY2024")
    st.divider()
    st.caption("Data sources: CBK, NSE, Damodaran, IMF WEO")