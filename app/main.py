import streamlit as st
import sys
sys.path.append(".")
from core.database import init_db

init_db()

st.set_page_config(
    page_title="Equity Research Workbench",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Equity Research Workbench")
st.markdown("**Indian Stock Analysis Platform — NSE/BSE**")
st.divider()

st.markdown("""
### How to use this tool
1. Go to **Search** — enter any NSE ticker (e.g. `RELIANCE.NS`, `TCS.NS`, `INFY.NS`)
2. View **Financials** — income statement, balance sheet, ratios
3. Check the **Health Score** — a transparent 0–100 financial strength rating
4. Read **News** — recent headlines for the company

> ⚠️ This tool is for research and learning only. Not investment advice.
""")
