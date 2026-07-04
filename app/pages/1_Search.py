import streamlit as st
import sys
sys.path.append(".")

from core.fetcher import get_company_info, get_stock_history
import plotly.graph_objects as go

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
st.title("🔍 Company Search")

ticker_input = st.text_input(
    "Enter NSE ticker symbol",
    placeholder="e.g. RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS",
    help="Add .NS for NSE stocks, .BO for BSE stocks"
)

if ticker_input:
    with st.spinner(f"Fetching data for {ticker_input.upper()}..."):
        try:
            info = get_company_info(ticker_input.upper())
            history = get_stock_history(ticker_input.upper(), period="1y")

            st.session_state["ticker"] = ticker_input.upper()
            st.session_state["info"]   = info

            st.subheader(info["name"])
            col1, col2, col3 = st.columns(3)
            col1.metric("Sector",   info["sector"])
            col2.metric("Industry", info["industry"])
            col3.metric("P/E Ratio", f"{info['pe_ratio']:.2f}" if info['pe_ratio'] else "N/A")

            st.divider()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"₹{info['current_price']:,.2f}")
            col2.metric("Market Cap",    f"₹{info['market_cap']/1e12:.2f}T")
            col3.metric("52W High",      f"₹{info['week_high_52']:,.2f}")
            col4.metric("52W Low",       f"₹{info['week_low_52']:,.2f}")

            st.divider()

            st.subheader("Price History — 1 Year")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["Close"],
                mode="lines",
                name="Close Price",
                line=dict(color="#2563eb", width=2)
            ))
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                height=400,
                margin=dict(l=0, r=0, t=10, b=0),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("About the Company")
            st.write(info["description"])

        except Exception as e:
            st.error(f"Could not fetch data for '{ticker_input}'. Check the ticker symbol and try again.")
            st.caption(f"Error: {e}")
