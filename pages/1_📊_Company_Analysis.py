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


@st.cache_data(ttl=300)
def get_cached_analytics(ticker, company_type, share_price, beta):
    """Cache analytics results for 5 minutes."""
    fy_data = get_financial_statement(ticker, 2024)
    if not fy_data:
        return None, None
    fy_data = dict(fy_data)
    fy_data["share_price"] = share_price
    fy_data["beta_5y"] = beta
    analytics = calculate_all_analytics(fy_data, company_type)
    return fy_data, analytics


@st.cache_data(ttl=300)
def get_cached_dcf(fy_data, analytics):
    """Cache DCF results for 5 minutes."""
    return full_dcf_analysis(fy_data, analytics)


@st.cache_data(ttl=300)
def get_cached_prices():
    """Cache live prices for 5 minutes."""
    try:
        from engine.market_data import fetch_our_prices
        return fetch_our_prices()
    except:
        return {}


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

# --- Investor Type (for withholding tax) ---
with st.sidebar:
    st.subheader("👤 Investor Profile")
    investor_type = st.radio(
        "Tax Residency",
        ["🇰🇪 Resident (5% WHT)", "🌍 Non-Resident (15% WHT)"],
        index=0
    )
    wht_rate = 0.05 if "Resident" in investor_type else 0.15
    st.caption(f"Withholding Tax: {wht_rate:.0%} on dividends")
    
    st.divider()
    st.subheader("📈 Market Data")
    
    # Try live prices
    live_prices = get_cached_prices()
    live_data = live_prices.get(selected_ticker, {}) if "error" not in live_prices else {}
    live_price = live_data.get("price") if live_data else None
    live_volume = live_data.get("volume") if live_data else None
    
    if live_price:
        st.success(f"📡 Live Price: KES {live_price:,.2f}")
        if live_volume:
            st.caption(f"Volume: {live_volume:,}")
        default_price = live_price
    else:
        st.info("💡 Live feed unavailable — enter manually")
        default_price = 18.50
    
    share_price = st.number_input("Current Share Price (KES)", 
                                   value=float(default_price), step=0.50)
    beta = st.number_input("Beta (5Y)", 
                           value=0.86, 
                           step=0.01,
                           help="5-year beta vs NASI index")

# --- Fetch & Cache Data ---
fy_data, analytics = get_cached_analytics(
    selected_ticker, company["company_type"], share_price, beta
)

if not fy_data:
    st.warning(f"No FY2024 data found for {selected_ticker}. Please add data in Data Management page.")
    st.stop()

dcf = get_cached_dcf(fy_data, analytics)

# --- Display Dashboard ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Valuation", "🔬 Financial Health", "🎲 Monte Carlo", 
    "🏦 Bank Metrics", "📋 Raw Data"
])

# ==================== TAB 1: VALUATION ====================
with tab1:
    st.subheader("DCF Valuation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"KES {dcf['current_price']:,.2f}")
    with col2:
        st.metric("Intrinsic Value", f"KES {dcf['intrinsic_value_per_share']:,.2f}")
    with col3:
        mos = dcf.get('margin_of_safety')
        st.metric("Margin of Safety", f"{mos:.1%}" if mos is not None else "N/A")
    with col4:
        upside = dcf.get('upside_percent')
        st.metric("Upside", f"{upside:.1%}" if upside is not None else "N/A")
    
    # Verdict with color
    verdict = dcf.get('verdict', 'N/A')
    if "BUY" in verdict:
        st.success(f"### Verdict: {verdict}")
    elif "HOLD" in verdict:
        st.warning(f"### Verdict: {verdict}")
    else:
        st.error(f"### Verdict: {verdict}")
    
    st.divider()
    
    # WACC and Reverse DCF side by side
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("WACC Build-Up")
        wacc_data = dcf["wacc_components"]
        wacc_df = pd.DataFrame({
            "Component": [
                "Risk-Free Rate (91-Day T-Bill)",
                "Equity Risk Premium",
                "Beta",
                "Cost of Equity (CAPM)",
                "After-Tax Cost of Debt",
                "Equity Weight",
                "Debt Weight",
                "**WACC**"
            ],
            "Value": [
                f"{RISK_FREE_RATE:.1%}",
                f"{EQUITY_RISK_PREMIUM:.1%}",
                f"{beta:.2f}",
                f"{wacc_data['cost_of_equity']:.2%}",
                f"{wacc_data['after_tax_cost_of_debt']:.2%}",
                f"{wacc_data['equity_weight']:.1%}",
                f"{wacc_data['debt_weight']:.1%}",
                f"**{wacc_data['wacc']:.2%}**"
            ]
        })
        st.dataframe(wacc_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("Reverse DCF Analysis")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            implied = dcf.get('implied_growth')
            st.metric("Market-Implied Growth", 
                     f"{implied:.2%}" if implied is not None else "N/A")
        with col_b:
            st.metric("Kenya GDP Growth", f"{GDP_GROWTH:.1%}")
        with col_c:
            implied_vs_gdp = dcf.get('implied_growth_vs_gdp')
            if implied_vs_gdp is not None:
                st.metric("Growth Premium", f"{implied_vs_gdp:.1%}",
                         delta="Above GDP" if implied_vs_gdp > 0 else "Below GDP",
                         delta_color="inverse" if implied_vs_gdp < 0 else "normal")
        
        st.caption("Market-implied growth > GDP = market expects above-average growth")
    
    st.divider()
    
    # DCF Projections Table
    st.subheader("10-Year DCF Projections")
    proj_df = pd.DataFrame(dcf["dcf_projections"])
    display_df = pd.DataFrame({
        "Year": proj_df["year"],
        "Phase": proj_df["growth_phase"],
        "FCF (KES Millions)": proj_df["fcf"].apply(lambda x: f"{x:,.0f}"),
        "Discount Factor": proj_df["discount_factor"].apply(lambda x: f"{x:.4f}"),
        "PV of FCF (KES Millions)": proj_df["pv_fcf"].apply(lambda x: f"{x:,.0f}")
    })
    st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("PV of Cash Flows", f"KES {dcf['pv_fcfs_sum']:,.0f}")
    with col2:
        st.metric("Terminal Value", f"KES {dcf['terminal_value']:,.0f}")
    with col3:
        st.metric("TV % of EV", f"{dcf['tv_percentage']:.1%}",
                 help="Terminal Value as % of Enterprise Value. 60-80% is typical for mature companies.")
    
    st.divider()
    
    # Sensitivity Matrix Heatmap
    st.subheader("📊 Sensitivity Analysis: IV/Share vs WACC & Terminal Growth")
    st.caption("Hover over cells to see Intrinsic Value per Share")
    
    matrix = dcf.get("sensitivity_matrix", [])
    if matrix:
        # Convert to DataFrame for heatmap
        rows = []
        for row in matrix:
            wacc_val = row["wacc"]
            for key, value in row.items():
                if key != "wacc":
                    tg_val = key.replace("g=", "")
                    rows.append({
                        "WACC": wacc_val,
                        "Terminal Growth": tg_val,
                        "IV/Share": value if value else 0
                    })
        
        heatmap_df = pd.DataFrame(rows)
        pivot = heatmap_df.pivot(index="Terminal Growth", columns="WACC", values="IV/Share")
        
        fig = px.imshow(
            pivot,
            text_auto=".0f",
            color_continuous_scale="RdYlGn",
            title="Intrinsic Value / Share (KES)",
            aspect="auto"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: FINANCIAL HEALTH ====================
with tab2:
    st.subheader("Profitability Ratios")
    prof = analytics["profitability"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gross Margin", f"{prof['gross_margin']:.1%}")
        st.metric("EBITDA Margin", f"{prof['ebitda_margin']:.1%}")
        st.metric("Net Margin", f"{prof['net_margin']:.1%}")
    with col2:
        st.metric("ROE", f"{prof['roe']:.1%}")
        st.metric("ROA", f"{prof['roa']:.1%}")
        st.metric("ROIC", f"{prof['roic']:.1%}")
    with col3:
        st.metric("FCF Margin", f"{prof['fcf_margin']:.1%}")
        st.metric("OCF Quality", f"{prof['ocf_quality']:.1f}x")
        st.metric("Capex Intensity", f"{prof.get('capex_intensity', 0):.1%}")
    
    st.divider()
    
    # DuPont Decomposition
    st.subheader("🔍 DuPont 3-Factor Decomposition")
    st.caption("ROE = Net Margin × Asset Turnover × Equity Multiplier")
    
    dup = analytics.get("dupont", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Net Margin (Profitability)", f"{dup.get('net_margin_dupont', 0):.1%}")
    with col2:
        st.metric("Asset Turnover (Efficiency)", f"{dup.get('asset_turnover', 0):.2f}x")
    with col3:
        st.metric("Equity Multiplier (Leverage)", f"{dup.get('equity_multiplier', 0):.2f}x")
    
    st.metric("DuPont ROE", f"{dup.get('dupont_roe', 0):.1%}", 
             delta="✓ Consistent" if dup.get("is_consistent", False) else "⚠ Review Data")
    
    st.divider()
    
    # Altman Z-Score
    st.subheader("🏦 Altman Z-Score")
    
    z = analytics.get("z_score", {})
    z_val = z.get("z_score", 0)
    z_verdict = z.get("verdict", "N/A")
    
    if "SAFE" in str(z_verdict):
        st.success(f"**Z-Score: {z_val:.2f}** — {z_verdict}")
    elif "GREY" in str(z_verdict):
        st.warning(f"**Z-Score: {z_val:.2f}** — {z_verdict}")
    else:
        st.error(f"**Z-Score: {z_val:.2f}** — {z_verdict}")
    
    # Z-Score components
    comp = z.get("components", {})
    if comp:
        comp_df = pd.DataFrame([
            {"Component": k, "Value": f"{v:.4f}", "Weight": w}
            for k, v, w in [
                ("X1: Working Capital / Assets", comp.get("X1", 0), "6.56"),
                ("X2: Retained Earnings / Assets", comp.get("X2", 0), "3.26"),
                ("X3: EBIT / Assets", comp.get("X3", 0), "6.72"),
                ("X4: Equity / Liabilities", comp.get("X4", 0), "1.05"),
            ] + ([("X5: Revenue / Assets", comp.get("X5", 0), "6.72")] if "X5" in comp else [])
        ])
        st.dataframe(comp_df, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # Liquidity & Solvency
    st.subheader("💧 Liquidity & Solvency")
    liq = analytics.get("liquidity", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Ratio", f"{liq.get('current_ratio', 0):.2f}x")
        st.metric("Quick Ratio", f"{liq.get('quick_ratio', 0):.2f}x")
    with col2:
        st.metric("Debt / Equity", f"{liq.get('debt_to_equity', 0):.2f}x")
        st.metric("Debt / Assets", f"{liq.get('debt_to_assets', 0):.2%}")
    with col3:
        st.metric("Interest Coverage", f"{liq.get('interest_coverage', 0):.1f}x")
        st.metric("Net Debt / EBITDA", f"{liq.get('net_debt_ebitda', 0):.1f}x")
    
    st.divider()
    
    # Efficiency
    st.subheader("⚡ Operational Efficiency")
    eff = analytics.get("efficiency", {})
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("DSO (Days)", f"{eff.get('dso', 0):.0f}")
    with col2:
        st.metric("DIO (Days)", f"{eff.get('dio', 0):.0f}")
    with col3:
        st.metric("DPO (Days)", f"{eff.get('dpo', 0):.0f}")
    with col4:
        st.metric("Cash Cycle", f"{eff.get('ccc', 0):.0f} days")
    
    # Dividend section with WHT
    st.divider()
    st.subheader("💵 Dividend Analysis")
    dps = fy_data.get("dividends_per_share", 0) or 0
    div_yield = (dps / share_price) if share_price else 0
    div_after_tax = dps * (1 - wht_rate)
    net_yield = (div_after_tax / share_price) if share_price else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("DPS (Gross)", f"KES {dps:.2f}")
    with col2:
        st.metric(f"After WHT ({wht_rate:.0%})", f"KES {div_after_tax:.2f}")
    with col3:
        st.metric("Net Dividend Yield", f"{net_yield:.2%}")

# ==================== TAB 3: MONTE CARLO ====================
with tab3:
    st.subheader("🎲 Monte Carlo Simulation")
    st.caption("1,000 iterations using Log-Normal distribution (no negative prices)")
    
    if st.button("🚀 Run Monte Carlo Simulation", type="primary", use_container_width=True):
        with st.spinner("Running 1,000 simulations with Log-Normal distribution..."):
            mc_results = run_monte_carlo(
                base_fcf=dcf["dcf_projections"][0]["fcf"],
                wacc_mu=dcf["wacc_components"]["wacc"],
                terminal_growth_mu=0.05,
                growth_1_mu=0.10,
                shares_outstanding=fy_data["shares_outstanding"],
                net_debt=analytics["derived_balance"]["net_debt"],
                iterations=1000,
                current_price=share_price
            )
            
            if mc_results:
                st.success(f"✅ {mc_results['iterations']} iterations complete")
                
                # Distribution chart
                fig = px.histogram(
                    mc_results["distribution"],
                    nbins=50,
                    title="Intrinsic Value Distribution (KES/share)",
                    labels={"value": "Intrinsic Value (KES)"},
                    color_discrete_sequence=["#1f77b4"]
                )
                fig.add_vline(x=share_price, line_dash="dash", 
                             line_color="red", line_width=2,
                             annotation_text=f"Current: {share_price:.0f}")
                fig.add_vline(x=mc_results["median"], line_dash="dash",
                             line_color="green", line_width=2,
                             annotation_text=f"Median IV: {mc_results['median']:.0f}")
                fig.update_layout(height=450, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                st.subheader("Distribution Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean IV", f"KES {mc_results['mean']:,.2f}")
                    st.metric("Min IV", f"KES {mc_results['min']:,.2f}")
                with col2:
                    st.metric("Median IV", f"KES {mc_results['median']:,.2f}")
                    st.metric("Max IV", f"KES {mc_results['max']:,.2f}")
                with col3:
                    st.metric("P5 (Downside)", f"KES {mc_results['p5']:,.2f}")
                    st.metric("Std Dev", f"KES {mc_results['std_dev']:,.2f}")
                with col4:
                    st.metric("P95 (Upside)", f"KES {mc_results['p95']:,.2f}")
                    prob_above = sum(1 for x in mc_results["distribution"] if x > share_price) / mc_results["iterations"]
                    st.metric("Prob. IV > Price", f"{prob_above:.1%}")
                
                # Threshold analysis
                st.subheader("Probability Thresholds")
                thresholds = [
                    share_price * 1.5,
                    share_price * 2,
                    share_price * 3,
                    mc_results["median"],
                    mc_results["p75"]
                ]
                from engine.monte_carlo import monte_carlo_probability_analysis
                probs = monte_carlo_probability_analysis(mc_results, thresholds, share_price)
                if probs:
                    prob_df = pd.DataFrame([
                        {
                            "Threshold (KES)": f"KES {p['threshold']:,.0f}",
                            "Probability Above": f"{p['p_above']:.1%}",
                            "Interpretation": p["interpretation"]
                        }
                        for p in probs
                    ])
                    st.dataframe(prob_df, hide_index=True, use_container_width=True)
    else:
        st.info("👆 Click the button above to run the simulation")

# ==================== TAB 4: BANK METRICS ====================
with tab4:
    if company["company_type"] == "Bank" and analytics.get("bank_metrics"):
        st.subheader("🏦 CAMELS-Style Bank Analysis")
        
        bm = analytics["bank_metrics"]
        
        # Capital Adequacy
        st.markdown("### C — Capital Adequacy")
        col1, col2, col3 = st.columns(3)
        with col1:
            car = bm.get("car", 0)
            st.metric("CAR", f"{car:.1%}", 
                     delta=f"Buffer: {bm.get('car_buffer', 0):.1%}",
                     delta_color="normal" if car >= MIN_CAR_REQUIREMENT else "inverse")
        with col2:
            st.metric("Min Required", f"{MIN_CAR_REQUIREMENT:.1%}")
        with col3:
            status = "✅ Compliant" if car >= MIN_CAR_REQUIREMENT else "❌ Below Requirement"
            st.metric("Status", status)
        
        # Asset Quality
        st.markdown("### A — Asset Quality")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("NPL Ratio", f"{bm.get('npl_ratio', 0):.1%}",
                     help="Non-Performing Loans / Gross Loans")
        with col2:
            st.metric("NPL Coverage", f"{bm.get('npl_coverage', 0):.1%}",
                     help="Loan Loss Reserves / NPLs")
        with col3:
            st.metric("Credit Loss Rate", f"{bm.get('credit_loss_rate', 0):.1%}",
                     help="Loan Loss Provisions / Gross Loans (Cost of Risk)")
        
        # Management Quality (Efficiency)
        st.markdown("### M — Management Quality (Efficiency)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cost-to-Income Ratio", f"{bm.get('cir', 0):.1%}",
                     delta=f"Industry Avg: {COST_TO_INCOME_AVG:.1%}",
                     delta_color="inverse" if bm.get('cir', 0) > COST_TO_INCOME_AVG else "normal")
        with col2:
            st.metric("Net Interest Margin", f"{bm.get('nim', 0):.2%}")
        
        # Earnings & Liquidity
        st.markdown("### E & L — Earnings & Liquidity")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Loan-to-Deposit Ratio", f"{bm.get('ldr', 0):.1%}")
        with col2:
            st.metric("NPL vs Industry", f"{bm.get('npl_ratio', 0):.1%}",
                     delta=f"Industry: {NPL_INDUSTRY_AVG:.1%}",
                     delta_color="inverse" if bm.get('npl_ratio', 0) > NPL_INDUSTRY_AVG else "normal")
        
    else:
        st.info(f"🏦 Bank-specific metrics are only available for banking institutions. {company['company_name']} is classified as '{company['company_type']}'.")

# ==================== TAB 5: RAW DATA ====================
with tab5:
    st.subheader("📋 Raw Financial Data (KES Millions)")
    st.caption("FY2024 data from database")
    
    # Clean up the dict for display
    display_data = {}
    for k, v in fy_data.items():
        if k not in ["id", "ticker", "fiscal_year"] and v is not None:
            display_data[k.replace("_", " ").title()] = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
    
    raw_df = pd.DataFrame(list(display_data.items()), columns=["Item", "Value (KES Millions)"])
    st.dataframe(raw_df, hide_index=True, use_container_width=True, height=600)
    
    # Download button
    csv = raw_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{selected_ticker}_FY2024_data.csv",
        mime="text/csv"
    )


# --- Sidebar Footer ---
with st.sidebar:
    st.divider()
    st.caption(f"Data sources: CBK, NSE, Damodaran, IMF WEO")
    st.caption(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")