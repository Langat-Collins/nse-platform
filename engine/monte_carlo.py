"""
MONTE CARLO SIMULATION ENGINE
Box-Muller transform for normal distributions.
Mirrors the VBA code in DCF & SCENARIOS exactly.
"""

import math
import random
import numpy as np
from engine.valuation import dcf_valuation


def box_muller():
    """
    Generate a standard normal variate using Box-Muller transform.
    Mirrors the VBA: z1 = Sqr(-2*Log(u1)) * Cos(6.283185*u2)
    """
    u1 = random.random()
    if u1 == 0:
        u1 = 0.0001
    u2 = random.random()
    if u2 == 0:
        u2 = 0.0001
    
    z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return z1


def run_monte_carlo(base_fcf, wacc_mu, terminal_growth_mu, growth_1_mu,
                    shares_outstanding, net_debt, iterations=1000,
                    g1_sd=0.035, tg_sd=0.012, wacc_sd=0.018):
    """
    Monte Carlo simulation for IV/Share distribution.
    """
    results = []
    
    for i in range(iterations):
        # Generate random parameters using Box-Muller
        g1 = growth_1_mu + g1_sd * box_muller()
        tg = terminal_growth_mu + tg_sd * box_muller()
        wacc = wacc_mu + wacc_sd * box_muller()
        
        # Constrain values (mirrors VBA clamping)
        g1 = max(-0.30, min(0.50, g1))
        tg = max(0.01, tg)
        if wacc <= tg:
            tg = wacc - 0.005
        wacc = max(0.08, min(0.30, wacc))
        
        # Run DCF with these random parameters
        try:
            dcf_result = dcf_valuation(
                base_fcf=base_fcf,
                wacc=wacc,
                growth_phase1=g1,
                growth_phase2=g1 * 0.65 + tg * 0.35,
                terminal_growth=tg
            )
            
            equity_value = dcf_result["enterprise_value"] - net_debt
            iv_per_share = equity_value / shares_outstanding * 1000
            results.append(iv_per_share)
        except:
            continue
    
    if not results:
        return None
    
    # Sort results for percentile calculation
    results.sort()
    n = len(results)
    
    # Calculate statistics
    mean_iv = np.mean(results)
    std_iv = np.std(results)
    
    return {
        "mean": mean_iv,
        "std_dev": std_iv,
        "p5": results[int(n * 0.05)],
        "p25": results[int(n * 0.25)],
        "median": results[int(n * 0.50)],
        "p75": results[int(n * 0.75)],
        "p95": results[int(n * 0.95)],
        "iterations": n,
        "distribution": results
    }


def monte_carlo_probability_analysis(results, thresholds, current_price):
    """
    Calculate probability of IV exceeding various thresholds.
    """
    if not results or not results.get("distribution"):
        return None
    
    dist = results["distribution"]
    n = len(dist)
    
    probabilities = []
    for threshold in thresholds:
        count_above = sum(1 for x in dist if x > threshold)
        prob_above = count_above / n
        
        if prob_above > 0.90:
            interpretation = f"Very high confidence IV exceeds KES {threshold:.0f}"
        elif prob_above > 0.70:
            interpretation = f"Strong likelihood IV exceeds KES {threshold:.0f}"
        elif prob_above > 0.50:
            interpretation = f"More likely than not IV exceeds KES {threshold:.0f}"
        elif prob_above > 0.30:
            interpretation = f"Meaningful chance IV exceeds KES {threshold:.0f}"
        elif prob_above > 0.10:
            interpretation = f"Tail scenario: IV exceeds KES {threshold:.0f}"
        else:
            interpretation = f"Very unlikely IV exceeds KES {threshold:.0f}"
        
        probabilities.append({
            "threshold": threshold,
            "p_above": prob_above,
            "p_below": 1 - prob_above,
            "interpretation": interpretation
        })
    
    return probabilities


def calculate_margin_of_safety_distribution(results, current_price):
    """
    Calculate margin of safety distribution from Monte Carlo results.
    """
    if not results or not results.get("distribution"):
        return None
    
    mos_dist = [(iv - current_price) / iv for iv in results["distribution"]]
    
    return {
        "mean_mos": np.mean(mos_dist),
        "std_mos": np.std(mos_dist),
        "p_mos_positive": sum(1 for m in mos_dist if m > 0) / len(mos_dist),
        "p_mos_above_30": sum(1 for m in mos_dist if m > 0.30) / len(mos_dist),
    }