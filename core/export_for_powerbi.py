"""Export the latest company snapshots and scores for Power BI."""

import sys
sys.path.append(".")
import csv

from core.database import get_latest_snapshot_per_ticker
from core.percentile_score import calculate_percentile_score

OUTPUT_PATH = "data/powerbi_export.csv"


def export():
    snapshots = get_latest_snapshot_per_ticker()
    if not snapshots:
        print("No data in database yet. Run core/seed_data.py or search some tickers first.")
        return

    rows = []
    for snap in snapshots:
        score = calculate_percentile_score(snap["ticker"], snap)
        rows.append({
            "Ticker": snap["ticker"],
            "Name": snap["name"],
            "Sector": snap["sector"],
            "Industry": snap["industry"],
            "Snapshot Date": snap["snapshot_date"],
            "Overall Score": score["overall_score"],
            "Grade": score["grade"],
            "Profitability Score": score["category_scores"]["Profitability"],
            "Liquidity Score": score["category_scores"]["Liquidity"],
            "Leverage Score": score["category_scores"]["Leverage"],
            "Growth Score": score["category_scores"]["Growth"],
            "Cash Flow Score": score["category_scores"]["Cash Flow"],
            "Net Margin %": snap["net_margin"],
            "Operating Margin %": snap["operating_margin"],
            "Gross Margin %": snap["gross_margin"],
            "ROE %": snap["roe"],
            "ROCE %": snap["roce"],
            "Current Ratio": snap["current_ratio"],
            "Quick Ratio": snap["quick_ratio"],
            "Debt to Equity": snap["debt_to_equity"],
            "Interest Coverage": snap["interest_coverage"],
            "Asset Turnover": snap["asset_turnover"],
            "Free Cash Flow (Cr)": snap["free_cash_flow"],
            "Revenue Growth %": snap["revenue_growth"],
            "Compared Against": score["sample_info"]["compared_against"],
            "Sample Size": score["sample_info"]["sample_size"],
        })

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} companies to {OUTPUT_PATH}")


if __name__ == "__main__":
    export()
