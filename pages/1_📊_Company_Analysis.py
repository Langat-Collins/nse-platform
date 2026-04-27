"""
Company Analysis Page - Full DCF, DuPont, Z-Score analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from engine.database import get_all_companies, get_company, get_financial_statement
from engine.analytics import calculate_all_analytics
from engine.valuation import full_dcf_analysis
from engine.monte_carlo import run_monte_carlo
from utils.constants import *

st.set_page_config(page_title="Company Analysis", page_icon="📊", layout="wide")

st.title("📊 Company Analysis")

# --- Company Selector ---
companies = get_all_companies()
ticker_options = [f"{c['ticker']} - {c['company_name']}" for c in companies]
selected = st.selectbox("Select Company", ticker_options)
selected_ticker = selected.split(" - ")[0]
company = get_company(selected_ticker)

if not company:
    st.error("Company not found in database.")
    st.stop()

# --- Fetch Financial Data ---
fy_data = get_financial_statement(selected_ticker, 2024)
if not fy_data:
    st.warning("No FY2024 data found. Please add data in Data Management page.")
    st.stop()

# Add share price if not present
if "share_price" not in fy_data:
    fy_data["share_price"] = 0
if "beta_5y" not in fy_data:
    fy_data["beta_5y"] = 0.86

# Sidebar for share price input
with st.sidebar:
    st.subheader("📈 Market Data")
    
    # Try to fetch live price (with fallback)
    live_price = None
    try:
        from engine.market_data import get_single_price
        live = get_single_price(selected_ticker)
        live_price = live.get("price") if live else None
    except:
        pass
    
    if live_price:
        st.success(f"📡 Live Price: KES {live_price:,.2f}")
        default_price = live_price
    else:
        st.info("💡 Enter price manually (live feed unavailable)")
        default_price = float(fy_data.get("share_price", 0)) or 18.50
    
    share_price = st.number_input("Current Share Price (KES)", value=default_price, step=0.50)
    beta = st.number_input("Beta (5Y)", value=float(fy_data.get("beta_5y", 0.86)), step=0.01)
    fy_data["share_price"] = share_price
    fy_data["beta_5y"] = beta
# --- Run Analytics Engine ---
analytics = calculate_all_analytics(fy_data, company["company_type"])
dcf = full_dcf_analysis(fy_data, analytics)

# --- Display Dashboard ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Valuation", "🔬 Financial Health", "🎲 Monte Carlo", "📋 Raw Data"
])

with tab1:
    st.subheader("DCF Valuation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"KES {dcf['current_price']:,.2f}")
    with col2:
        st.metric("Intrinsic Value", f"KES {dcf['intrinsic_value_per_share']:,.2f}")
    with col3:
        st.metric("Margin of Safety", f"{dcf['margin_of_safety']:.1%}" if dcf['margin_of_safety'] else "N/A")
    with col4:
        st.metric("Upside", f"{dcf['upside_percent']:.1%}" if dcf['upside_percent'] else "N/A")
    
    st.markdown(f"### Verdict: **{dcf['verdict']}**")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("WACC Build-Up")
        wacc_data = dcf["wacc_components"]
        wacc_df = pd.DataFrame({
            "Component": ["Risk-Free Rate", "Equity Risk Premium", "Cost of Equity", 
                         "After-Tax Cost of Debt", "WACC"],
            "Value": [
                f"{RISK_FREE_RATE:.1%}",
                f"{EQUITY_RISK_PREMIUM:.1%}",
                f"{wacc_data['cost_of_equity']:.2%}",
                f"{wacc_data['after_tax_cost_of_debt']:.2%}",
                f"{wacc_data['wacc']:.2%}"
            ]
        })
        st.dataframe(wacc_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("Reverse DCF")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Market-Implied Growth", 
                     f"{dcf['implied_growth']:.2%}" if dcf['implied_growth'] else "N/A")
        with col_b:
            st.metric("Kenya GDP Growth", f"{GDP_GROWTH:.1%}")
    
    st.divider()
    st.subheader("DCF Projections")
    proj_df = pd.DataFrame(dcf["dcf_projections"])
    proj_df["FCF (KES M)"] = proj_df["fcf"].apply(lambda x: f"{x:,.0f}")
    proj_df["PV of FCF (KES M)"] = proj_df["pv_fcf"].apply(lambda x: f"{x:,.0f}")
    st.dataframe(proj_df[["year", "growth_phase", "FCF (KES M)", "PV of FCF (KES M)"]], 
                 hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Profitability Ratios")
    prof = analytics["profitability"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gross Margin", f"{prof['gross_margin']:.1%}")
        st.metric("EBIT Margin", f"{prof['ebit_margin']:.1%}")
        st.metric("Net Margin", f"{prof['net_margin']:.1%}")
    with col2:
        st.metric("ROE", f"{prof['roe']:.1%}")
        st.metric("ROIC", f"{prof['roic']:.1%}")
        st.metric("FCF Margin", f"{prof['fcf_margin']:.1%}")
    with col3:
        st.metric("EBITDA Margin", f"{prof['ebitda_margin']:.1%}")
        st.metric("OCF Quality", f"{prof['ocf_quality']:.1f}x")
    
    st.divider()
    st.subheader("DuPont Decomposition")
    dup = analytics["dupont"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Net Margin", f"{dup['net_margin_dupont']:.1%}")
    with col2:
        st.metric("Asset Turnover", f"{dup['asset_turnover']:.2f}x")
    with col3:
        st.metric("Equity Multiplier", f"{dup['equity_multiplier']:.2f}x")
    
    st.metric("DuPont ROE", f"{dup.get('dupont_roe', 0):.1%}", 
         delta="✓ Consistent" if dup.get("is_consistent", False) else "✗ Data Error")
    
    st.divider()
    st.subheader("Altman Z-Score")
    z = analytics["z_score"]
    if "SAFE" in str(z.get("verdict", "")):
        z_emoji = "🟢"
    elif "GREY" in str(z["verdict"]):
        z_emoji = "🟠"
    else:
        z_emoji = "🔴"
    st.metric("Z-Score", f"{z['z_score']:.2f}", delta=f"{z_emoji} {z['verdict']}")
    
    # Show components
    comp_df = pd.DataFrame([
        {"Component": k, "Value": f"{v:.4f}"} for k, v in z["components"].items()
    ])
    st.dataframe(comp_df, hide_index=True, use_container_width=True)
    
    # Bank-specific metrics
    if company["company_type"] == "Bank" and analytics.get("bank_metrics"):
        st.divider()
        st.subheader("Bank-Specific Metrics")
        bm = analytics["bank_metrics"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("NIM", f"{bm['nim']:.1%}")
        with col2:
            st.metric("Cost/Income", f"{bm['cir']:.1%}")
        with col3:
            st.metric("NPL Ratio", f"{bm['npl_ratio']:.1%}")
        with col4:
            st.metric("CAR", f"{bm['car']:.1%}")

with tab3:
    st.subheader("🎲 Monte Carlo Simulation")
    
    if st.button("Run Monte Carlo (1,000 iterations)", type="primary"):
        with st.spinner("Running 1,000 simulations..."):
            mc_results = run_monte_carlo(
                base_fcf=dcf["dcf_projections"][0]["fcf"],
                wacc_mu=dcf["wacc_components"]["wacc"],
                terminal_growth_mu=0.05,
                growth_1_mu=0.10,
                shares_outstanding=fy_data["shares_outstanding"],
                net_debt=analytics["derived_balance"]["net_debt"],
                iterations=1000
            )
            
            if mc_results:
                st.success(f"Simulation complete: {mc_results['iterations']} iterations")
                
                # Distribution chart
                fig = px.histogram(
                    mc_results["distribution"],
                    nbins=50,
                    title="Intrinsic Value Distribution (KES/share)",
                    labels={"value": "Intrinsic Value (KES)"},
                    color_discrete_sequence=["#1f77b4"]
                )
                fig.add_vline(x=dcf["current_price"], line_dash="dash", 
                             line_color="red", annotation_text="Current Price")
                fig.add_vline(x=mc_results["median"], line_dash="dash",
                             line_color="green", annotation_text="Median IV")
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean IV", f"KES {mc_results['mean']:,.2f}")
                with col2:
                    st.metric("Median IV", f"KES {mc_results['median']:,.2f}")
                with col3:
                    st.metric("P5 (Downside)", f"KES {mc_results['p5']:,.2f}")
                with col4:
                    st.metric("P95 (Upside)", f"KES {mc_results['p95']:,.2f}")

with tab4:
    st.subheader("📋 Raw Financial Data (KES Millions)")
    
    # Clean up the dict for display
    display_data = {}
    for k, v in fy_data.items():
        if k not in ["id", "ticker", "fiscal_year"]:
            if v is not None:
                display_data[k.replace("_", " ").title()] = f"{v:,.2f}" if isinstance(v, (int, float)) else v
    
    raw_df = pd.DataFrame(list(display_data.items()), columns=["Item", "Value"])
    st.dataframe(raw_df, hide_index=True, use_container_width=True, height=600)