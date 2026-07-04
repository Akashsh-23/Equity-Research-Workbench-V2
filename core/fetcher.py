import yfinance as yf
import pandas as pd
import os

CACHE_DIR = "data/cache"

def get_company_info(ticker_symbol):
    """
    Fetch basic company information for a given NSE/BSE ticker.
    Example: ticker_symbol = "RELIANCE.NS"
    """
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info

    # We only pull what we actually need — nothing extra
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
    """
    Fetch the 3 financial statements for a company.
    Returns income statement, balance sheet, cash flow — all annual.
    """
    ticker = yf.Ticker(ticker_symbol)

    income_statement = ticker.financials        # revenue, profit, etc.
    balance_sheet    = ticker.balance_sheet     # assets, liabilities, equity
    cash_flow        = ticker.cashflow          # operating, investing, financing

    return {
        "income_statement": income_statement,
        "balance_sheet":    balance_sheet,
        "cash_flow":        cash_flow,
    }


def get_stock_history(ticker_symbol, period="1y"):
    """
    Fetch historical price data.
    period options: "1mo", "3mo", "6mo", "1y", "3y", "5y"
    """
    ticker = yf.Ticker(ticker_symbol)
    history = ticker.history(period=period)
    return history