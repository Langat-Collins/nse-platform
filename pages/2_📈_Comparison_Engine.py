"""
Comparison Engine - Side-by-side ranking of NSE stocks
"""

import streamlit as st
import pandas as pd
from engine.database import get_all_companies, get_financial_statement
from engine.analytics import calculate_all_analytics

st.set_page_config(page_title="Comparison Engine", page_icon="📈", layout="wide")

st.title("📈 Comparison Engine")

companies = get_all_companies()

# Collect data for all companies
all_data = []
for company in companies:
    fy = get_financial_statement(company["ticker"], 2024)
    if fy:
        fy["share_price"] = 0  # default
        fy["beta_5y"] = 0.86
        analytics = calculate_all_analytics(fy, company["company_type"])
        
        all_data.append({
            "Ticker": company["ticker"],
            "Company": company["company_name"],
            "Sector": company["sector"],
            "Revenue (KES M)": f"{fy.get('revenue', 0):,.0f}",
            "Net Margin": f"{analytics['profitability']['net_margin']:.1%}",
            "ROE": f"{analytics['profitability']['roe']:.1%}",
            "ROIC": f"{analytics['profitability']['roic']:.1%}",
            "Z-Score": f"{analytics['z_score']['z_score']:.2f}",
            "Z-Verdict": analytics["z_score"]["verdict"],
        })

if all_data:
    df = pd.DataFrame(all_data)
    
    st.subheader(f"Peer Comparison — FY2024 ({len(all_data)} companies)")
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.divider()
    st.subheader("📊 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Companies", len(all_data))
    with col2:
        z_scores = [float(d["Z-Score"]) for d in all_data]
        st.metric("Avg Z-Score", f"{sum(z_scores)/len(z_scores):.2f}")
    with col3:
        safe_count = sum(1 for d in all_data if "SAFE" in d["Z-Verdict"])
        st.metric("Safe Zone", safe_count)
    with col4:
        banks = sum(1 for c in companies if c["company_type"] == "Bank")
        st.metric("Banks", banks)
else:
    st.warning("No financial data found. Add data in Data Management page.")