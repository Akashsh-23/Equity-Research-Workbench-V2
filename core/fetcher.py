import yfinance as yf
import pandas as pd
import os

CACHE_DIR = "data/cache"

def get_company_info(ticker_symbol):
    """Fetch basic company information for a given NSE/BSE ticker."""
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info

    company_data = {
        "name":         info.get("longName", "N/A"),
        "sector":       info.get("sector", "N/A"),
        "industry":     info.get("industry", "N/A"),
        "market_cap":   info.get("marketCap", 0),
        "current_price":info.get("currentPrice", 0),
        "week_high_52": info.get("fiftyTwoWeekHigh", 0),
        "week_low_52":  info.get("fiftyTwoWeekLow", 0),
        "pe_ratio":     info.get("trailingPE", 0),
        "description":  info.get("longBusinessSummary", "N/A"),
    }

    return company_data


def get_financials(ticker_symbol):
    """Fetch annual income statement, balance sheet, and cash flow data."""
    ticker = yf.Ticker(ticker_symbol)

    income_statement = ticker.financials
    balance_sheet    = ticker.balance_sheet
    cash_flow        = ticker.cashflow

    return {
        "income_statement": income_statement,
        "balance_sheet":    balance_sheet,
        "cash_flow":        cash_flow,
    }


def get_stock_history(ticker_symbol, period="1y"):
    """Fetch historical price data."""
    ticker = yf.Ticker(ticker_symbol)
    history = ticker.history(period=period)
    return history
