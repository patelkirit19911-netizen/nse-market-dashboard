import streamlit as st

st.set_page_config(page_title="NSE Market Dashboard", layout="wide")

st.title("📊 NSE MARKET DASHBOARD")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 All Sector Strength")
    st.info("Loading...")

with col2:
    st.subheader("📈 Weekly Breakout")
    st.info("Loading...")

col3, col4 = st.columns(2)

with col3:
    st.subheader("📅 Daily Breakout")
    st.info("Loading...")

with col4:
    st.subheader("🔥 Last 5 Days High Volume")
    st.info("Loading...")

st.subheader("⭐ Strong Buy (All Conditions Match)")
st.info("Loading...")
