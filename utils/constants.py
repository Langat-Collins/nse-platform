"""
Global constants - mirrors the _MASTER sheet's GLOBAL CONSTANTS section.
Update quarterly from cited sources.
"""

# CBK Monetary Policy (update monthly from cbk.go.ke)
RISK_FREE_RATE = 0.135  # 91-day T-Bill rate

# Damodaran Kenya Equity Risk Premium (update annually from stern.nyu.edu/~adamodar)
EQUITY_RISK_PREMIUM = 0.065

# Kenya Corporate Tax Rate (Income Tax Act Cap 470)
CORPORATE_TAX_RATE = 0.30

# IMF World Economic Outlook
GDP_GROWTH = 0.053

# KNBS CPI
CPI_INFLATION = 0.062

# CBK Prudential Guidelines
MIN_CAR_REQUIREMENT = 0.145

# NSE Market Data (update annually)
NASI_5Y_ANNUAL_RETURN = 0.082
NASI_5Y_STD_DEV = 0.195

# Sector Multiples (update quarterly from NSE/CMA reports)
SECTOR_PE_MEDIAN = {
    "Telecoms": 12.5,
    "Banking": 6.8,
    "Consumer Goods": 14.0,
    "Construction": 10.5,
    "Insurance": 8.2,
    "Default": 10.0
}

SECTOR_EV_EBITDA = {
    "Telecoms": 8.5,
    "Banking": 5.2,
    "Consumer Goods": 9.0,
    "Construction": 7.5,
    "Insurance": 6.0,
    "Default": 7.0
}

# Banking Industry Averages
NPL_INDUSTRY_AVG = 0.142
COST_TO_INCOME_AVG = 0.565

# Monte Carlo Settings
MONTE_CARLO_ITERATIONS = 1000  # 5000 for publication quality

# Altman Z-Score Thresholds
Z_SCORE_SAFE = 2.6
Z_SCORE_GREY = 1.1
Z_SCORE_DISTRESS = 1.1

# Bank Z''-Score Thresholds
Z_BANK_SAFE = 1.23
Z_BANK_GREY = 1.0