import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="NSE Market Dashboard", layout="wide")

st.title("📊 NSE MARKET DASHBOARD")

# Sector mapping
sector_df = pd.read_csv("sector_mapping.csv")

strength = {}

for sector in sector_df["SECTOR"].unique():
    stocks = sector_df[sector_df["SECTOR"] == sector]["SYMBOL"]

    green = 0
    total = 0

    for stock in stocks:
        try:
            ticker = yf.Ticker(stock + ".NS")
            data = ticker.history(period="5d", auto_adjust=True)

            if len(data) >= 2:
                last = data["Close"].iloc[-1]
                prev = data["Close"].iloc[-2]

                if last > prev:
                    green += 1

                total += 1

        except:
            pass

    if total > 0:
        strength[sector] = round(green / total * 100)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 All Sector Strength")

    for sector, value in strength.items():
        if value >= 70:
            icon = "🟩"
        elif value >= 40:
            icon = "🟨"
        else:
            icon = "🟥"

        st.write(f"{icon} {sector} : {value}%")

with col2:
    st.subheader("📈 Weekly Breakout")
    st.info("Coming Soon")

col3, col4 = st.columns(2)

with col3:
    st.subheader("📅 Daily Breakout")
    st.info("Coming Soon")

with col4:
    st.subheader("🔥 Last 5 Days High Volume")
    st.info("Coming Soon")

