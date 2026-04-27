"""
TECHNICAL ANALYSIS ENGINE
RSI, MACD, Bollinger Bands, Moving Averages, Composite Momentum Score
Mirrors the TECHNICAL ENGINE sheet.
"""

import numpy as np


def calculate_rsi(prices, period=14):
    """
    RSI (Relative Strength Index) using Wilder's smoothing method.
    """
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    MACD Line, Signal Line, and Histogram.
    """
    if len(prices) < slow + signal:
        return None
    
    ema_fast = _calculate_ema(prices, fast)
    ema_slow = _calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = _calculate_ema_single([macd_line], signal)
    histogram = macd_line - signal_line
    
    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram
    }


def calculate_bollinger_bands(prices, period=20, num_std=2):
    """
    Bollinger Bands: Middle (SMA), Upper, Lower.
    """
    if len(prices) < period:
        return None
    
    sma = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    
    return {
        "middle": sma,
        "upper": sma + num_std * std,
        "lower": sma - num_std * std,
        "bandwidth": (2 * num_std * std) / sma
    }


def calculate_ma(prices, period):
    """Simple Moving Average."""
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])


def _calculate_ema(data, period):
    """Calculate EMA for a series."""
    if len(data) < period:
        return data[-1] if len(data) > 0 else 0
    multiplier = 2 / (period + 1)
    ema = np.mean(data[:period])
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    return ema


def _calculate_ema_single(series, period):
    """Calculate EMA for a single series."""
    if len(series) < period:
        return series[-1] if len(series) > 0 else 0
    multiplier = 2 / (period + 1)
    ema = np.mean(series[:period])
    for val in series[period:]:
        ema = (val - ema) * multiplier + ema
    return ema


def composite_momentum_score(prices, volumes):
    """
    Weighted Multi-Factor Momentum Score (0-100).
    
    Components:
    - MA Positioning (30 pts): Price vs MA20, MA50
    - RSI Signal (25 pts): RSI zones
    - MACD Signal (25 pts): MACD vs Signal line
    - Volume Trend (20 pts): Volume vs average
    """
    if len(prices) < 50:
        return None
    
    current_price = prices[-1]
    ma20 = calculate_ma(prices, 20)
    ma50 = calculate_ma(prices, 50)
    rsi = calculate_rsi(prices)
    macd_data = calculate_macd(prices)
    avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
    current_volume = volumes[-1]
    
    score = 0
    signals = {}
    
    # 1. MA Positioning (30 points)
    if ma20 and ma50:
        if current_price > ma20 and ma20 > ma50:
            score += 30
            signals["ma_position"] = "Price > MA20 > MA50 - Strong Bullish"
        elif current_price > ma20 and current_price > ma50:
            score += 22
            signals["ma_position"] = "Price above both MAs"
        elif current_price > ma20:
            score += 15
            signals["ma_position"] = "Price above MA20"
        elif current_price > ma50:
            score += 8
            signals["ma_position"] = "Price above MA50"
        else:
            signals["ma_position"] = "Below all MAs"
    
    # 2. RSI Signal (25 points)
    if rsi:
        if rsi < 30:
            score += 23
            signals["rsi"] = f"Oversold ({rsi:.0f}) - Potential reversal"
        elif rsi < 42:
            score += 25
            signals["rsi"] = f"Healthy ({rsi:.0f}) - Room to run"
        elif rsi < 55:
            score += 18
            signals["rsi"] = f"Neutral-Bullish ({rsi:.0f})"
        elif rsi < 65:
            score += 12
            signals["rsi"] = f"Elevated ({rsi:.0f})"
        elif rsi < 70:
            score += 6
            signals["rsi"] = f"Near Overbought ({rsi:.0f})"
        else:
            signals["rsi"] = f"Overbought ({rsi:.0f})"
    
    # 3. MACD Signal (25 points)
    if macd_data:
        macd = macd_data["macd_line"]
        sig = macd_data["signal_line"]
        if macd > sig and macd > 0:
            score += 25
            signals["macd"] = "MACD > Signal, positive - Bullish"
        elif macd > sig and macd < 0:
            score += 18
            signals["macd"] = "MACD > Signal, negative - Recovering"
        elif macd < sig and macd > 0:
            score += 8
            signals["macd"] = "MACD < Signal, positive - Weakening"
        else:
            signals["macd"] = "MACD < Signal, negative - Bearish"
    
    # 4. Volume Trend (20 points)
    if avg_volume:
        vol_ratio = current_volume / avg_volume
        if vol_ratio > 1.5:
            score += 20
            signals["volume"] = "Very High Volume - Strong confirmation"
        elif vol_ratio > 1.2:
            score += 16
            signals["volume"] = "Above Average Volume - Confirming"
        elif vol_ratio > 1.0:
            score += 11
            signals["volume"] = "Normal Volume"
        elif vol_ratio > 0.7:
            score += 5
            signals["volume"] = "Below Average Volume - Weak"
        else:
            signals["volume"] = "Very Low Volume - Unreliable signal"
    
    # Verdict
    if score >= 80:
        verdict = "STRONG BULLISH"
    elif score >= 62:
        verdict = "BULLISH"
    elif score >= 48:
        verdict = "NEUTRAL"
    elif score >= 30:
        verdict = "BEARISH"
    else:
        verdict = "STRONG BEARISH"
    
    return {
        "score": score,
        "verdict": verdict,
        "signals": signals,
        "ma20": ma20,
        "ma50": ma50,
        "rsi": rsi,
        "macd": macd_data,
        "golden_cross": ma20 > ma50 if ma20 and ma50 else None
    }