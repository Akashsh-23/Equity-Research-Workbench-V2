"""Seed the database with a representative set of NSE companies."""

import sys
import time
sys.path.append(".")

from core.fetcher import get_company_info, get_financials
from core.ratios import calculate_all_ratios
from core.database import init_db, save_snapshot

SEED_TICKERS = {
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT":      ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "FMCG":    ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
    "Auto":    ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "Pharma":  ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "AUROPHARMA.NS"],
    "Energy":  ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS"],
}


def seed():
    init_db()
    all_tickers = [t for group in SEED_TICKERS.values() for t in group]
    total = len(all_tickers)
    succeeded, failed = [], []

    for i, ticker in enumerate(all_tickers, start=1):
        print(f"[{i}/{total}] Fetching {ticker} ...", end=" ")
        try:
            info = get_company_info(ticker)
            financials = get_financials(ticker)
            ratios = calculate_all_ratios(
                financials["income_statement"],
                financials["balance_sheet"],
                financials["cash_flow"],
            )
            save_snapshot(ticker, info, ratios)
            succeeded.append(ticker)
            print("OK")
        except Exception as e:
            failed.append((ticker, str(e)))
            print(f"FAILED ({e})")

        time.sleep(0.5)

    print(f"\nDone. {len(succeeded)}/{total} succeeded.")
    if failed:
        print("Failed tickers:")
        for t, err in failed:
            print(f"  - {t}: {err}")


if __name__ == "__main__":
    seed()
