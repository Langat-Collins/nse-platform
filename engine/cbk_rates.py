"""
CBK Rate Fetcher - Scrapes Central Bank of Kenya for latest T-Bill rates.
Source: https://www.centralbank.go.ke/treasury-bills/
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


def fetch_cbk_tbill_rate():
    """
    Attempt to fetch the latest 91-day T-Bill rate from CBK website.
    Falls back to the hardcoded constant if scraping fails.
    """
    try:
        # CBK treasury bills page
        url = "https://www.centralbank.go.ke/treasury-bills/"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        
        # Look for 91-day rate pattern (usually like "9.xxx%" or "10.xxx%")
        # Search for numbers near "91-day" or "91 day"
        pattern_91 = re.compile(r'91[- ]?day.*?(\d+\.\d+)%?', re.IGNORECASE)
        match = pattern_91.search(text)
        
        if match:
            rate = float(match.group(1)) / 100
            return {
                "rate": rate,
                "source": "CBK Website",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "success": True
            }
        
        # Fallback: look for any percentage near "Treasury Bill"
        pattern_tbill = re.compile(r'Treasury\s*Bill.*?(\d+\.\d+)%?', re.IGNORECASE)
        match = pattern_tbill.search(text)
        if match:
            rate = float(match.group(1)) / 100
            return {
                "rate": rate,
                "source": "CBK Website (generic)",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "success": True
            }
            
    except Exception as e:
        pass
    
    # If all scraping fails, return None so constants.py default is used
    return {
        "rate": None,
        "source": "Default constant",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "success": False,
        "message": "Could not fetch from CBK. Using default rate."
    }


def get_risk_free_rate():
    """
    Get current risk-free rate. Try CBK first, fall back to constant.
    """
    cbk_result = fetch_cbk_tbill_rate()
    
    if cbk_result["success"] and cbk_result["rate"] is not None:
        return cbk_result["rate"]
    
    # Fallback to hardcoded constant
    from utils.constants import RISK_FREE_RATE
    return RISK_FREE_RATE