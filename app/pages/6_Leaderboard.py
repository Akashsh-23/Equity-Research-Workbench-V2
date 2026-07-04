import streamlit as st
import sys
sys.path.append(".")
import pandas as pd

from core.database import get_latest_snapshot_per_ticker
from core.percentile_score import calculate_percentile_score

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")
st.title("🏆 Leaderboard")
st.caption("Ranks every company you've researched by percentile Health Score. "
           "Scores recalculate live from SQLite every time this page loads — "
           "the more tickers in your database, the more reliable the ranking.")

snapshots = get_latest_snapshot_per_ticker()

if not snapshots:
    st.warning("No companies in your history yet. Go search a few tickers first, "
               "or run the seed script (core/seed_data.py) to preload sector peers.")
    st.stop()

rows = []
for snap in snapshots:
    t = snap["ticker"]
    score = calculate_percentile_score(t, snap)
    rows.append({
        "Ticker": t,
        "Name": snap["name"],
        "Sector": snap["sector"] or "N/A",
        "Overall Score": score["overall_score"],
        "Grade": score["grade"],
        "Net Margin %": snap["net_margin"],
        "ROE %": snap["roe"],
        "Debt to Equity": snap["debt_to_equity"],
    })

df = pd.DataFrame(rows).sort_values("Overall Score", ascending=False).reset_index(drop=True)
df.index = df.index + 1
df.index.name = "Rank"

sectors = ["All"] + sorted(df["Sector"].dropna().unique().tolist())
sector_filter = st.selectbox("Filter by sector", sectors)
if sector_filter != "All":
    df = df[df["Sector"] == sector_filter]

st.dataframe(df, use_container_width=True)

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Companies tracked", len(df))
col2.metric("Average score", f"{df['Overall Score'].mean():.1f}" if len(df) else "N/A")
col3.metric("Top performer", df.iloc[0]["Ticker"] if len(df) else "N/A")
