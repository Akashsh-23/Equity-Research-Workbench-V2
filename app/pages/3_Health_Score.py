import streamlit as st
import sys
sys.path.append(".")
import plotly.graph_objects as go
from datetime import datetime

from core.percentile_score import calculate_percentile_score
from core.database import get_latest_snapshot
from core.excel_report import build_report

st.set_page_config(page_title="Health Score", page_icon="🏥", layout="wide")
st.title("🏥 Financial Health Score")

if "ticker" not in st.session_state:
    st.warning("Please search for a company on the Search page first.")
    st.stop()

ticker = st.session_state["ticker"]
st.subheader(st.session_state["info"]["name"])
st.caption(
    "Scored as a **percentile rank** against companies in your SQLite database — "
    "sector peers when there are enough of them, otherwise the whole dataset."
)

with st.spinner("Calculating health score..."):
    try:
        snap_row = get_latest_snapshot(ticker)
        if not snap_row:
            st.warning("Search this ticker on the Financials page first, then come back here.")
            st.stop()

        score = calculate_percentile_score(ticker, snap_row)
        overall = score["overall_score"]
        grade = score["grade"]
        cats = score["category_scores"]
        sample_info = score["sample_info"]

        if   overall >= 80: color = "#16a34a"
        elif overall >= 65: color = "#2563eb"
        elif overall >= 50: color = "#d97706"
        elif overall >= 35: color = "#ea580c"
        else:               color = "#dc2626"

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style='text-align:center; padding:2rem; border-radius:16px;
                        border: 2px solid {color}'>
                <div style='font-size:4rem; font-weight:700;
                            color:{color}'>{overall}</div>
                <div style='font-size:1rem; color:gray'>percentile out of 100</div>
                <div style='font-size:1.2rem; font-weight:600;
                            margin-top:0.5rem'>{grade}</div>
            </div>
            """, unsafe_allow_html=True)

            compared_to = (
                f"vs {sample_info['sample_size']} peers in **{sample_info['sector']}**"
                if sample_info["compared_against"] == "sector"
                else f"vs all {sample_info['sample_size']} companies in your dataset"
            )
            st.caption(f"Compared {compared_to}")

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(cats.keys()),
                y=list(cats.values()),
                marker_color=[
                    "#16a34a" if v >= 70
                    else "#d97706" if v >= 40
                    else "#dc2626"
                    for v in cats.values()
                ],
                text=[f"{v}/100" for v in cats.values()],
                textposition="outside"
            ))
            fig.update_layout(
                yaxis=dict(range=[0, 110]),
                yaxis_title="Percentile",
                height=320,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("How the score is calculated")
        st.markdown(f"""
        | Category | Weight | What it measures |
        |---|---|---|
        | Profitability | 30% | ROE, ROCE, Net Margin |
        | Liquidity | 20% | Current Ratio, Quick Ratio |
        | Leverage | 20% | Debt/Equity, Interest Coverage |
        | Growth | 15% | Revenue growth YoY |
        | Cash Flow | 15% | Free Cash Flow |

        Each ratio is converted to a **percentile rank** against the comparison
        group above, rather than a fixed threshold — a score of 73 means this
        company beats 73% of its peers on that metric. The score recalculates
        live every time this page loads, using whatever is currently in the
        database, so it automatically recalibrates as more companies are added.

        **Limitation:** percentile ranks need a reasonable sample size to be
        meaningful — sector comparisons kick in once 5+ peers exist, otherwise
        it falls back to the whole dataset.
        """)

        st.divider()

        if "ratios" in st.session_state:
            excel_buffer = build_report(
                ticker,
                st.session_state["info"],
                st.session_state["ratios"],
                score,
            )
            st.download_button(
                label="📥 Download Excel Report",
                data=excel_buffer,
                file_name=f"{ticker}_health_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.caption("Visit the Financials page first to enable the Excel report download.")

    except Exception as e:
        st.error("Could not calculate health score.")
        st.caption(f"Error: {e}")
