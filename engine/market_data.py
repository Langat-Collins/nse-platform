"""
Live NSE Market Data - Scrapes AFX (afx.kwayisi.org/nse/)
Free, no API key needed. ~15 min delay.
"""

import requests
import re
from datetime import datetime

AFX_URL = "https://afx.kwayisi.org/nse/"
OUR_TICKERS = ["SCOM", "EQTY", "KCB", "EABL"]


def fetch_our_prices():
    """Scrape AFX and return prices for our tracked tickers."""
    try:
        response = requests.get(AFX_URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch: {e}"}

    text = response.text
    results = {}
    
    for ticker in OUR_TICKERS:
        # Find ticker position in text
        idx = text.find(ticker)
        if idx == -1:
            results[ticker] = {"ticker": ticker, "price": None, "error": "Not found"}
            continue
        
        # Grab 300 characters starting from the ticker
        snippet = text[idx:idx+300]
        
        # The pattern we saw: ticker, company name, then volume,price,change
        # Example: SCOM Safaricom Plc 417,911 29.90 +0.00
        # After the company name (which may have spaces), find numbers
        
        # Strategy: Find all number patterns like 29.90 or 417,911
        # Price is usually a decimal like xx.xx
        # Volume is usually like xxx,xxx
        
        # Find price: a number with exactly 2 decimal places (like 29.90 or 247.50)
        price_match = re.search(r'(\d+\.\d{2})', snippet)
        price = float(price_match.group(1)) if price_match else None
        
        # Find volume: a number with commas (like 417,911)
        vol_match = re.search(r'(\d{1,3}(?:,\d{3})+)', snippet)
        volume = int(vol_match.group(1).replace(",", "")) if vol_match else None
        
        results[ticker] = {
            "ticker": ticker,
            "price": price,
            "volume": volume,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    return results


def get_single_price(ticker):
    """Get price for a single ticker."""
    all_data = fetch_our_prices()
    if "error" in all_data:
        return {"ticker": ticker, "price": None, "error": all_data["error"]}
    return all_data.get(ticker, {"ticker": ticker, "price": None})