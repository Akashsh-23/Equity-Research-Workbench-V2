import streamlit as st
import requests

st.set_page_config(page_title="News", page_icon="📰", layout="wide")
st.title("📰 Company News")

if "ticker" not in st.session_state:
    st.warning("Please search for a company on the Search page first.")
    st.stop()

info   = st.session_state["info"]
ticker = st.session_state["ticker"]
name   = info["name"].split()[0]   # Use first word e.g. "Reliance"

st.subheader(f"Recent news — {info['name']}")

# Use GNews free API (no key needed for basic use)
url = f"https://gnews.io/api/v4/search?q={name}+stock&lang=en&country=in&max=10&apikey=demo"

try:
    response = requests.get(url, timeout=10)
    data     = response.json()
    articles = data.get("articles", [])

    if not articles:
        # Fallback — show a note
        st.info(
            "Live news requires a free GNews API key. "
            "Get one at gnews.io and add it to the URL in 4_News.py. "
            "For now here are the topics to search manually:"
        )
        st.markdown(f"""
        - [{info['name']} latest news](https://www.google.com/search?q={info['name']}+stock+news&tbm=nws)
        - [NSE announcements](https://www.nseindia.com/)
        - [BSE filings](https://www.bseindia.com/)
        """)
    else:
        for article in articles:
            with st.expander(article.get("title", "No title")):
                st.write(article.get("description", ""))
                st.caption(f"Source: {article.get('source', {}).get('name', '')} | "
                          f"{article.get('publishedAt', '')[:10]}")
                st.markdown(f"[Read full article →]({article.get('url', '')})")

except Exception as e:
    st.warning("Could not fetch news. Check your internet connection.")
    st.caption(f"Error: {e}")