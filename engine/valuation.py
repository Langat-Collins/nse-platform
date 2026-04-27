"""
DCF VALUATION ENGINE: WACC, DCF, Reverse DCF, Sensitivity Matrix
Mirrors the DCF & SCENARIOS sheet exactly.
"""

import math
from utils.constants import (
    RISK_FREE_RATE, EQUITY_RISK_PREMIUM, CORPORATE_TAX_RATE,
    GDP_GROWTH, MONTE_CARLO_ITERATIONS
)


def calculate_wacc(risk_free_rate, beta, equity_risk_premium, 
                   interest_expense, total_debt, market_cap, tax_rate):
    """
    CAPM-based WACC Build-Up.
    WACC = Ke x E/(E+D) + Kd(1-t) x D/(E+D)
    """
    # Cost of Equity (CAPM)
    cost_of_equity = risk_free_rate + beta * equity_risk_premium
    
    # Pre-tax Cost of Debt
    pre_tax_cost_of_debt = interest_expense / total_debt if total_debt else 0.12
    
    # After-tax Cost of Debt
    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
    
    # Weights
    total_capital = market_cap + total_debt
    equity_weight = market_cap / total_capital if total_capital else 0.7
    debt_weight = total_debt / total_capital if total_capital else 0.3
    
    # WACC
    wacc = cost_of_equity * equity_weight + after_tax_cost_of_debt * debt_weight
    
    return {
        "cost_of_equity": cost_of_equity,
        "pre_tax_cost_of_debt": pre_tax_cost_of_debt,
        "after_tax_cost_of_debt": after_tax_cost_of_debt,
        "equity_weight": equity_weight,
        "debt_weight": debt_weight,
        "wacc": wacc
    }


def dcf_valuation(base_fcf, wacc, growth_phase1=0.10, growth_phase2=0.07, 
                  terminal_growth=0.05, projection_years=10):
    """
    10-Year DCF Model with two growth phases.
    Phase 1 (Yr 1-5): High growth
    Phase 2 (Yr 6-10): Fade to terminal
    Terminal Value: Gordon Growth Model
    """
    projections = []
    fcf = base_fcf
    pv_fcfs = 0
    
    for year in range(1, projection_years + 1):
        if year <= 5:
            fcf = fcf * (1 + growth_phase1)
        else:
            fcf = fcf * (1 + growth_phase2)
        
        discount_factor = 1 / (1 + wacc) ** year
        pv_fcf = fcf * discount_factor
        pv_fcfs += pv_fcf
        
        projections.append({
            "year": year,
            "fcf": fcf,
            "discount_factor": discount_factor,
            "pv_fcf": pv_fcf,
            "growth_phase": "Phase 1 (High Growth)" if year <= 5 else "Phase 2 (Fade)"
        })
    
    # Terminal Value (Gordon Growth Model)
    terminal_value = (fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** projection_years
    
    # Enterprise Value
    enterprise_value = pv_fcfs + pv_terminal
    
    # TV as % of EV
    tv_percentage = pv_terminal / enterprise_value if enterprise_value else 0
    
    return {
        "projections": projections,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "tv_percentage": tv_percentage,
        "enterprise_value": enterprise_value,
        "pv_fcfs_sum": pv_fcfs
    }


def reverse_dcf(enterprise_value, current_fcf, wacc):
    """
    Reverse DCF: Market-Implied Perpetuity Growth.
    g* = WACC - FCF/EV
    """
    if not enterprise_value:
        return None
    
    implied_growth = wacc - (current_fcf / enterprise_value)
    return implied_growth


def sensitivity_matrix(base_fcf, wacc_base, terminal_growth_base, 
                       shares_outstanding, net_debt):
    """
    Creates an 8x8 sensitivity matrix: IV/Share vs WACC x Terminal Growth.
    """
    wacc_values = [
        round(wacc_base - 0.03, 4),
        round(wacc_base - 0.02, 4),
        round(wacc_base - 0.01, 4),
        round(wacc_base - 0.005, 4),
        round(wacc_base, 4),
        round(wacc_base + 0.01, 4),
        round(wacc_base + 0.02, 4),
        round(wacc_base + 0.03, 4),
    ]
    
    tg_values = [0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060, 0.070]
    
    matrix = []
    for wacc_val in wacc_values:
        row = {"wacc": f"{wacc_val:.1%}"}
        for tg in tg_values:
            if tg >= wacc_val:
                row[f"g={tg:.1%}"] = None
                continue
            # Quick DCF for this combination
            fcf = base_fcf
            pv_sum = 0
            for yr in range(1, 11):
                g = 0.10 if yr <= 5 else 0.07
                fcf *= (1 + g)
                pv_sum += fcf / (1 + wacc_val) ** yr
            tv = (fcf * (1 + tg)) / (wacc_val - tg)
            pv_tv = tv / (1 + wacc_val) ** 10
            ev = pv_sum + pv_tv
            equity = ev - net_debt
            iv_per_share = equity / shares_outstanding * 1000
            row[f"g={tg:.1%}"] = round(iv_per_share, 2)
        matrix.append(row)
    
    return matrix


def calculate_margin_of_safety(intrinsic_value, current_price):
    """
    Margin of Safety = (IV - Price) / IV
    """
    if not intrinsic_value:
        return None
    return (intrinsic_value - current_price) / intrinsic_value


def dcf_verdict(margin_of_safety):
    """
    DCF Verdict based on Margin of Safety thresholds.
    """
    if margin_of_safety is None:
        return "INSUFFICIENT DATA"
    if margin_of_safety > 0.30:
        return "BUY - Deep Value"
    elif margin_of_safety > 0.10:
        return "BUY - Moderate Upside"
    elif margin_of_safety > -0.10:
        return "HOLD - Fair Value"
    else:
        return "AVOID - Overvalued"


def full_dcf_analysis(data, analytics):
    """
    Complete DCF analysis pipeline.
    """
    md = analytics["market_data"]
    db = analytics["derived_balance"]
    
    # Calculate WACC
    wacc_result = calculate_wacc(
        risk_free_rate=RISK_FREE_RATE,
        beta=data.get("beta_5y", 0.86),
        equity_risk_premium=EQUITY_RISK_PREMIUM,
        interest_expense=data.get("interest_expense", 0),
        total_debt=db["total_debt"],
        market_cap=md["market_cap"],
        tax_rate=CORPORATE_TAX_RATE
    )
    
    wacc = wacc_result["wacc"]
    
    # Base Case DCF
    dcf_result = dcf_valuation(
        base_fcf=md["free_cash_flow"],
        wacc=wacc,
        growth_phase1=0.10,
        growth_phase2=0.07,
        terminal_growth=0.05
    )
    
    # Intrinsic Value per Share
    equity_value = dcf_result["enterprise_value"] - db["net_debt"]
    shares = data.get("shares_outstanding", 1)
    intrinsic_value_per_share = equity_value / shares * 1000 if shares else 0
    
    # Margin of Safety
    current_price = data.get("share_price", 0)
    margin_of_safety = calculate_margin_of_safety(intrinsic_value_per_share, current_price)
    
    # Reverse DCF
    implied_growth = reverse_dcf(
        md["enterprise_value"], 
        md["free_cash_flow"], 
        wacc
    )
    
    # Sensitivity Matrix
    sensitivity = sensitivity_matrix(
        base_fcf=md["free_cash_flow"],
        wacc_base=wacc,
        terminal_growth_base=0.05,
        shares_outstanding=shares,
        net_debt=db["net_debt"]
    )
    
    # Verdict
    verdict = dcf_verdict(margin_of_safety)
    
    return {
        "wacc_components": wacc_result,
        "dcf_projections": dcf_result["projections"],
        "terminal_value": dcf_result["terminal_value"],
        "pv_terminal": dcf_result["pv_terminal"],
        "tv_percentage": dcf_result["tv_percentage"],
        "enterprise_value_dcf": dcf_result["enterprise_value"],
        "equity_value": equity_value,
        "intrinsic_value_per_share": intrinsic_value_per_share,
        "current_price": current_price,
        "margin_of_safety": margin_of_safety,
        "upside_percent": (intrinsic_value_per_share - current_price) / current_price if current_price else None,
        "verdict": verdict,
        "implied_growth": implied_growth,
        "implied_growth_vs_gdp": implied_growth - GDP_GROWTH if implied_growth else None,
        "sensitivity_matrix": sensitivity
    }