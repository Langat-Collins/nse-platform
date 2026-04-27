"""
ANALYTICS ENGINE: DuPont Decomposition, Altman Z-Score, Financial Ratios
Directly mirrors the ANALYTICS ENGINE sheet formulas.
"""

from utils.constants import (
    CORPORATE_TAX_RATE, Z_SCORE_SAFE, Z_SCORE_GREY,
    Z_BANK_SAFE, Z_BANK_GREY, MIN_CAR_REQUIREMENT
)


def calculate_income_statement_derived(data):
    """
    Mirrors derived income statement items.
    Input: dict with raw financial data
    Output: dict with all derived metrics
    """
    result = {}
    
    # Gross Profit = Revenue - COGS
    result["gross_profit"] = data["revenue"] - data["cost_of_goods_sold"]
    
    # EBIT = Gross Profit - Operating Expenses
    result["ebit"] = result["gross_profit"] - data["operating_expenses"]
    
    # EBITDA = EBIT + Depreciation
    result["ebitda"] = result["ebit"] + data["depreciation_amortization"]
    
    # PBT = EBIT - Interest + Other Income
    result["pbt"] = result["ebit"] - data["interest_expense"] + data["other_income"]
    
    # Net Profit = PBT - Tax
    result["net_profit"] = result["pbt"] - data["tax_expense"]
    
    # NOPAT = EBIT x (1 - Tax Rate)
    result["nopat"] = result["ebit"] * (1 - CORPORATE_TAX_RATE)
    
    # Total Operating Income (for banks)
    if data.get("net_interest_income"):
        result["total_operating_income"] = (
            data["net_interest_income"] + data["non_interest_income"]
        )
    
    return result


def calculate_balance_sheet_derived(data, derived_income):
    """
    Mirrors derived balance sheet items.
    """
    result = {}
    
    # Current Assets
    result["total_current_assets"] = (
        data["cash_equivalents"] +
        data["trade_receivables"] +
        data["inventory"] +
        data["other_current_assets"]
    )
    
    # Non-Current Assets
    result["total_non_current_assets"] = (
        data["ppe_net"] +
        data["goodwill_intangibles"] +
        data["other_non_current_assets"]
    )
    
    # Total Assets
    result["total_assets"] = (
        result["total_current_assets"] + 
        result["total_non_current_assets"]
    )
    
    # Current Liabilities
    result["total_current_liabilities"] = (
        data["trade_payables"] +
        data["short_term_debt"] +
        data["other_current_liabilities"]
    )
    
    # Non-Current Liabilities
    result["total_non_current_liabilities"] = (
        data["long_term_debt"] +
        data["other_non_current_liabilities"]
    )
    
    # Total Liabilities
    result["total_liabilities"] = (
        result["total_current_liabilities"] + 
        result["total_non_current_liabilities"]
    )
    
    # Shareholders' Equity = Total Assets - Total Liabilities
    result["shareholders_equity"] = (
        result["total_assets"] - result["total_liabilities"]
    )
    
    # Total Debt = Short-term + Long-term
    result["total_debt"] = data["short_term_debt"] + data["long_term_debt"]
    
    # Net Debt = Total Debt - Cash
    result["net_debt"] = result["total_debt"] - data["cash_equivalents"]
    
    # Working Capital = Current Assets - Current Liabilities
    result["working_capital"] = (
        result["total_current_assets"] - result["total_current_liabilities"]
    )
    
    # Invested Capital = Equity + Total Debt
    result["invested_capital"] = (
        result["shareholders_equity"] + result["total_debt"]
    )
    
    # Book Value Per Share (KES)
    result["bvps"] = (
        result["shareholders_equity"] / data["shares_outstanding"] * 1000
    ) if data["shares_outstanding"] else 0
    
    # Free Cash Flow = Operating CF - Capex
    result["free_cash_flow"] = (
        data["operating_cash_flow"] - data["capital_expenditure"]
    )
    
    return result


def calculate_profitability_ratios(data, derived_income, derived_balance):
    """
    Profitability ratios section.
    """
    ratios = {}
    
    rev = data["revenue"] if data["revenue"] else 0
    ratios["gross_margin"] = derived_income["gross_profit"] / rev if rev else 0
    ratios["ebit_margin"] = derived_income["ebit"] / rev if rev else 0
    ratios["ebitda_margin"] = derived_income["ebitda"] / rev if rev else 0
    ratios["net_margin"] = derived_income["net_profit"] / rev if rev else 0
    ratios["nopat_margin"] = derived_income["nopat"] / rev if rev else 0
    ratios["fcf_margin"] = derived_balance["free_cash_flow"] / rev if rev else 0
    
    # OCF Quality = Operating CF / Net Profit
    ratios["ocf_quality"] = (
        data["operating_cash_flow"] / derived_income["net_profit"] 
        if derived_income["net_profit"] else 0
    )
    
    # Capex Intensity
    ratios["capex_intensity"] = data["capital_expenditure"] / rev if rev else 0
    
    # ROA, ROE, ROCE, ROIC
    ratios["roa"] = (
        derived_income["net_profit"] / derived_balance["total_assets"]
        if derived_balance["total_assets"] else 0
    )
    ratios["roe"] = (
        derived_income["net_profit"] / derived_balance["shareholders_equity"]
        if derived_balance["shareholders_equity"] else 0
    )
    roce_denom = derived_balance["total_assets"] - derived_balance["total_current_liabilities"]
    ratios["roce"] = derived_income["ebit"] / roce_denom if roce_denom else 0
    ratios["roic"] = (
        derived_income["nopat"] / derived_balance["invested_capital"]
        if derived_balance["invested_capital"] else 0
    )
    
    return ratios


def dupont_decomposition(ratios, derived_balance, data):
    """
    3-Factor DuPont: ROE = Net Margin x Asset Turnover x Equity Multiplier
    """
    total_assets = derived_balance["total_assets"]
    equity = derived_balance["shareholders_equity"]
    revenue = data["revenue"]
    
    if not total_assets or not equity or not revenue:
        return {"net_margin_dupont": 0, "asset_turnover": 0, 
                "equity_multiplier": 0, "dupont_roe": 0, "variance": 1}
    
    net_margin = ratios["net_margin"]
    asset_turnover = revenue / total_assets
    equity_multiplier = total_assets / equity
    
    dupont_roe = net_margin * asset_turnover * equity_multiplier
    actual_roe = ratios["roe"]
    variance = dupont_roe - actual_roe
    
    return {
        "net_margin_dupont": net_margin,
        "asset_turnover": asset_turnover,
        "equity_multiplier": equity_multiplier,
        "dupont_roe": dupont_roe,
        "actual_roe": actual_roe,
        "variance": variance,
        "is_consistent": abs(variance) < 0.0001
    }


def altman_z_score_non_bank(data, derived_income, derived_balance):
    """
    Z'-Score for non-manufacturing companies.
    Z' = 6.56X1 + 3.26X2 + 6.72X3 + 1.05X4 + 6.72X5
    """
    ta = derived_balance["total_assets"]
    if not ta:
        return {"z_score": 0, "verdict": "N/A", "components": {}}
    
    x1 = derived_balance["working_capital"] / ta
    x2 = derived_balance["shareholders_equity"] / ta
    x3 = derived_income["ebit"] / ta
    x4 = (derived_balance["shareholders_equity"] / derived_balance["total_liabilities"] 
          if derived_balance["total_liabilities"] else 0)
    x5 = data["revenue"] / ta
    
    z_score = 6.56*x1 + 3.26*x2 + 6.72*x3 + 1.05*x4 + 6.72*x5
    
    if z_score > Z_SCORE_SAFE:
        verdict = "SAFE ZONE"
    elif z_score > Z_SCORE_GREY:
        verdict = "GREY ZONE"
    else:
        verdict = "DISTRESS ZONE"
    
    return {
        "z_score": z_score,
        "verdict": verdict,
        "components": {"X1": x1, "X2": x2, "X3": x3, "X4": x4, "X5": x5}
    }


def altman_z_score_bank(data, derived_income, derived_balance):
    """
    Z''-Score (4-Factor for Financial Institutions).
    Z'' = 6.56X1 + 3.26X2 + 6.72X3 + 1.05X4
    """
    ta = derived_balance["total_assets"]
    if not ta:
        return {"z_score": 0, "verdict": "N/A", "components": {}}
    
    x1 = derived_balance["working_capital"] / ta
    x2 = derived_balance["shareholders_equity"] / ta
    x3 = derived_income["ebit"] / ta
    x4 = (derived_balance["shareholders_equity"] / derived_balance["total_liabilities"] 
          if derived_balance["total_liabilities"] else 0)
    
    z_score = 6.56*x1 + 3.26*x2 + 6.72*x3 + 1.05*x4
    
    if z_score > Z_BANK_SAFE:
        verdict = "SAFE ZONE"
    elif z_score > Z_BANK_GREY:
        verdict = "GREY ZONE"
    else:
        verdict = "DISTRESS ZONE"
    
    return {
        "z_score": z_score,
        "verdict": verdict,
        "components": {"X1": x1, "X2": x2, "X3": x3, "X4": x4}
    }


def calculate_bank_metrics(data, derived_income, derived_balance):
    """
    Bank-specific metrics: NIM, CIR, NPL Ratio, Coverage, LDR, CAR
    """
    metrics = {}
    
    # Net Interest Margin (NIM)
    metrics["nim"] = data.get("net_interest_margin", 0)
    
    # Cost-to-Income Ratio
    total_income = data.get("net_interest_income", 0) + data.get("non_interest_income", 0)
    opex = data.get("bank_operating_expenses", 0)
    metrics["cir"] = opex / total_income if total_income else 0
    
    # NPL Ratio
    gross_loans = data.get("gross_loan_book", 0)
    npls = data.get("non_performing_loans", 0)
    metrics["npl_ratio"] = npls / gross_loans if gross_loans else 0
    
    # NPL Coverage
    reserve = data.get("loan_loss_reserve", 0)
    metrics["npl_coverage"] = reserve / npls if npls else 0
    
    # Loan-to-Deposit Ratio
    deposits = data.get("customer_deposits", 0)
    metrics["ldr"] = gross_loans / deposits if deposits else 0
    
    # Capital Adequacy Ratio
    metrics["car"] = data.get("capital_adequacy_ratio", 0)
    metrics["car_buffer"] = metrics["car"] - MIN_CAR_REQUIREMENT
    
    # Credit Loss Rate
    provisions = data.get("loan_loss_provisions", 0)
    metrics["credit_loss_rate"] = provisions / gross_loans if gross_loans else 0
    
    return metrics


def liquidity_solvency_ratios(data, derived_income, derived_balance):
    """
    Liquidity & Solvency ratios.
    """
    ratios = {}
    cl = derived_balance["total_current_liabilities"]
    
    ratios["current_ratio"] = (
        derived_balance["total_current_assets"] / cl if cl else 0
    )
    ratios["quick_ratio"] = (
        (derived_balance["total_current_assets"] - data["inventory"]) / cl 
        if cl else 0
    )
    ratios["cash_ratio"] = data["cash_equivalents"] / cl if cl else 0
    
    equity = derived_balance["shareholders_equity"]
    ratios["debt_to_equity"] = derived_balance["total_debt"] / equity if equity else 0
    ratios["debt_to_assets"] = (
        derived_balance["total_debt"] / derived_balance["total_assets"] 
        if derived_balance["total_assets"] else 0
    )
    
    ebitda = derived_income.get("ebitda", 0)
    ratios["net_debt_ebitda"] = derived_balance["net_debt"] / ebitda if ebitda else 0
    
    interest = data["interest_expense"]
    ratios["interest_coverage"] = derived_income["ebit"] / interest if interest else 0
    
    return ratios


def efficiency_ratios(data, derived_balance):
    """
    Operational Efficiency: DSO, DIO, DPO, Cash Conversion Cycle
    """
    ratios = {}
    rev = data["revenue"]
    cogs = data["cost_of_goods_sold"]
    
    ratios["asset_turnover"] = (
        rev / derived_balance["total_assets"] if derived_balance["total_assets"] else 0
    )
    ratios["dso"] = (data["trade_receivables"] / rev * 365) if rev else 0
    ratios["dio"] = (data["inventory"] / cogs * 365) if cogs else 0
    ratios["dpo"] = (data["trade_payables"] / cogs * 365) if cogs else 0
    ratios["ccc"] = ratios["dso"] + ratios["dio"] - ratios["dpo"]
    
    return ratios


def calculate_all_analytics(data, company_type="Non-Bank"):
    """
    Master function that replicates the entire ANALYTICS ENGINE sheet.
    Returns a complete dictionary of all financial analytics.
    """
    # Step 1: Derived income statement items
    derived_income = calculate_income_statement_derived(data)
    
    # Step 2: Derived balance sheet items
    derived_balance = calculate_balance_sheet_derived(data, derived_income)
    
    # Step 3: Profitability ratios
    profitability = calculate_profitability_ratios(data, derived_income, derived_balance)
    
    # Step 4: DuPont decomposition
    dupont = dupont_decomposition(profitability, derived_balance, data)
    
    # Step 5: Liquidity & Solvency
    liquidity = liquidity_solvency_ratios(data, derived_income, derived_balance)
    
    # Step 6: Efficiency
    efficiency = efficiency_ratios(data, derived_balance)
    
    # Step 7: Z-Score (different model for banks vs non-banks)
    if company_type == "Bank":
        z_score = altman_z_score_bank(data, derived_income, derived_balance)
        bank_metrics = calculate_bank_metrics(data, derived_income, derived_balance)
    else:
        z_score = altman_z_score_non_bank(data, derived_income, derived_balance)
        bank_metrics = None
    
    # Market data calculations
    shares = data.get("shares_outstanding", 1)
    price = data.get("share_price", 0)
    market_cap = price * shares
    enterprise_value = market_cap + derived_balance["net_debt"]
    
    # Per share metrics
    eps = derived_income["net_profit"] / shares * 1000 if shares else 0
    dps = data.get("dividends_per_share", 0)
    
    # Valuation multiples
    pe_ratio = price / eps if eps else None
    pb_ratio = price / derived_balance["bvps"] if derived_balance["bvps"] else None
    ev_ebitda = enterprise_value / derived_income["ebitda"] if derived_income["ebitda"] else None
    ev_ebit = enterprise_value / derived_income["ebit"] if derived_income["ebit"] else None
    fcf_yield = derived_balance["free_cash_flow"] / market_cap if market_cap else None
    div_yield = dps / price if price else None
    
    return {
        "derived_income": derived_income,
        "derived_balance": derived_balance,
        "profitability": profitability,
        "dupont": dupont,
        "liquidity": liquidity,
        "efficiency": efficiency,
        "z_score": z_score,
        "bank_metrics": bank_metrics,
        "market_data": {
            "market_cap": market_cap,
            "enterprise_value": enterprise_value,
            "eps": eps,
            "bvps": derived_balance["bvps"],
            "dps": dps,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "ev_ebitda": ev_ebitda,
            "ev_ebit": ev_ebit,
            "fcf_yield": fcf_yield,
            "div_yield": div_yield,
            "free_cash_flow": derived_balance["free_cash_flow"]
        }
    }