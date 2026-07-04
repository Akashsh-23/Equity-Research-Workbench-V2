import streamlit as st
import sys
sys.path.append(".")
import pandas as pd
import plotly.graph_objects as go

from core.database import get_latest_snapshot_per_ticker
from core.percentile_score import calculate_percentile_score

st.set_page_config(page_title="Compare", page_icon="⚖️", layout="wide")
st.title("⚖️ Compare Companies")
st.caption("Pulls from your search history (SQLite). All scores are percentile-based "
           "and recalculate live — search a few tickers on the Search page first.")

snapshots = get_latest_snapshot_per_ticker()

if not snapshots:
    st.warning("No companies in your history yet. Go search a few tickers first.")
    st.stop()

rows = []
for snap in snapshots:
    t = snap["ticker"]
    score = calculate_percentile_score(t, snap)
    rows.append({
        "Ticker": t,
        "Name": snap["name"],
        "Sector": snap["sector"],
        "Overall Score": score["overall_score"],
        "Grade": score["grade"],
        "Net Margin %": snap["net_margin"],
        "ROE %": snap["roe"],
        "ROCE %": snap["roce"],
        "Current Ratio": snap["current_ratio"],
        "Debt to Equity": snap["debt_to_equity"],
        "Revenue Growth %": snap["revenue_growth"],
    })

df = pd.DataFrame(rows)

available_tickers = df["Ticker"].tolist()
selected = st.multiselect(
    "Select companies to compare",
    options=available_tickers,
    default=available_tickers[:min(4, len(available_tickers))]
)

if not selected:
    st.info("Select at least one company above.")
    st.stop()

filtered = df[df["Ticker"].isin(selected)].sort_values("Overall Score", ascending=False)

st.subheader("Side-by-side comparison")
st.dataframe(filtered.set_index("Ticker"), use_container_width=True)

st.divider()

st.subheader("Overall Health Score (percentile)")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=filtered["Ticker"],
    y=filtered["Overall Score"],
    marker_color="#2563eb",
    text=filtered["Overall Score"],
    textposition="outside"
))
fig.update_layout(yaxis=dict(range=[0, 110]), height=350,
                   margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Ratio comparison")
ratio_choice = st.selectbox(
    "Pick a ratio to compare",
    ["Net Margin %", "ROE %", "ROCE %", "Current Ratio", "Debt to Equity", "Revenue Growth %"]
)
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=filtered["Ticker"],
    y=filtered[ratio_choice],
    marker_color="#16a34a",
    text=filtered[ratio_choice],
    textposition="outside"
))
fig2.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0),
                    yaxis_title=ratio_choice)
st.plotly_chart(fig2, use_container_width=True)
