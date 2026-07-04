import streamlit as st
import sys
sys.path.append(".")
import plotly.graph_objects as go

from core.fetcher import get_financials
from core.ratios  import calculate_all_ratios
from core.database import save_snapshot

st.set_page_config(page_title="Financials", page_icon="📈", layout="wide")
st.title("📈 Financial Statements & Ratios")

# Check if user has searched a company
if "ticker" not in st.session_state:
    st.warning("Please search for a company on the Search page first.")
    st.stop()

ticker = st.session_state["ticker"]
st.subheader(f"{st.session_state['info']['name']} — {ticker}")

with st.spinner("Loading financial statements..."):
    try:
        financials = get_financials(ticker)
        income     = financials["income_statement"]
        balance    = financials["balance_sheet"]
        cashflow   = financials["cash_flow"]
        ratios     = calculate_all_ratios(income, balance, cashflow)

        # Store ratios for health score page
        st.session_state["ratios"] = ratios

        # Persist this snapshot to SQLite so we can trend/compare it later
        save_snapshot(ticker, st.session_state["info"], ratios)

        # --- Tabs for the 3 statements ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "Income Statement", "Balance Sheet", "Cash Flow", "Ratio Dashboard"
        ])

        with tab1:
            st.caption("All values in ₹ (as reported)")
            st.dataframe(
                income.map(lambda x: f"₹{x/1e7:,.0f} Cr" if isinstance(x, float) else x),
                use_container_width=True
            )

        with tab2:
            st.caption("All values in ₹ (as reported)")
            st.dataframe(
                balance.map(lambda x: f"₹{x/1e7:,.0f} Cr" if isinstance(x, float) else x),
                use_container_width=True
            )

        with tab3:
            st.caption("All values in ₹ (as reported)")
            st.dataframe(
                cashflow.map(lambda x: f"₹{x/1e7:,.0f} Cr" if isinstance(x, float) else x),
                use_container_width=True
            )

        with tab4:
            st.subheader("Financial Ratios")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Profitability**")
                st.metric("Gross Margin",     f"{ratios['Gross Margin %']}%")
                st.metric("Operating Margin", f"{ratios['Operating Margin %']}%")
                st.metric("Net Margin",       f"{ratios['Net Margin %']}%")
                st.metric("ROE",              f"{ratios['ROE %']}%")
                st.metric("ROCE",             f"{ratios['ROCE %']}%")

                st.markdown("**Growth**")
                st.metric("Revenue Growth",   f"{ratios['Revenue Growth %']}%")

            with col2:
                st.markdown("**Liquidity**")
                st.metric("Current Ratio",    ratios["Current Ratio"])
                st.metric("Quick Ratio",      ratios["Quick Ratio"])

                st.markdown("**Leverage**")
                st.metric("Debt to Equity",   ratios["Debt to Equity"])
                st.metric("Interest Coverage",ratios["Interest Coverage"])

                st.markdown("**Cash Flow**")
                st.metric("Free Cash Flow",   f"₹{ratios['Free Cash Flow (Cr)']:,} Cr")

            # Revenue trend chart
            st.divider()
            st.subheader("Revenue Trend")
            try:
                revenue_row = income.loc["Total Revenue"].dropna()
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=[str(d.year) for d in revenue_row.index],
                    y=revenue_row.values / 1e7,
                    marker_color="#2563eb",
                    name="Revenue (Cr)"
                ))
                fig.update_layout(
                    yaxis_title="Revenue (₹ Crores)",
                    height=350,
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.caption("Revenue chart not available.")

    except Exception as e:
        st.error("Could not load financial data.")
        st.caption(f"Error: {e}")