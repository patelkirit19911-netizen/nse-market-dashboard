import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from orb_scanner import get_orb_scanner
from five_days_volume import get_high_volume
st.set_page_config(page_title="NSE Market Dashboard", layout="wide")

st.title("📊 NSE MARKET DASHBOARD")

# Sector mapping
sector_df = pd.read_csv("sector_mapping.csv")

strength = {}
sector_change = {}
for sector in sector_df["SECTOR"].unique():

    stocks = sector_df[sector_df["SECTOR"] == sector]["SYMBOL"]

    changes = []

    for stock in stocks:
        try:
            data = yf.Ticker(stock + ".NS").history(
                period="2d",
                interval="1d",
                auto_adjust=True
            )

            if len(data) >= 2:
                prev_close = data["Close"].iloc[-2]
                last_close = data["Close"].iloc[-1]

                change = ((last_close - prev_close) / prev_close) * 100
                changes.append(change)

        except:
            pass

    if changes:
        sector_change[sector] = round(sum(changes) / len(changes), 2)

# ===========================
# DASHBOARD V2 - PART 1
# ===========================

import streamlit.components.v1 as components

st.subheader("📊 Sector Performance (1D)")

chart_df = pd.DataFrame(
    list(sector_change.items()),
    columns=["Sector", "Change"]
).sort_values("Change", ascending=False)

for _, row in chart_df.iterrows():

    sector = row["Sector"]
    change = row["Change"]

    


col3, col4 = st.columns([3,2])
high_volume = get_high_volume(sector_df["SYMBOL"].tolist())

            
with col3:
    st.subheader("🔥 Last 5 Days High Volume")
    if not high_volume.empty:
        st.dataframe(
            high_volume.style.map(
                lambda v: "color: green; font-weight: bold;",
                subset=["Volume Spike"]),use_container_width=True,hide_index=True)
    else:
        st.info("No High Volume Stocks Today")

st.subheader("📈 Weekly Breakout")
weekly_breakout = []
orb_scanner = []
for stock in sector_df["SYMBOL"]:
    try:
        # Weekly (1W) data
        weekly = yf.Ticker(stock + ".NS").history(
            period="3mo",
            interval="1wk",
            auto_adjust=True
        )

        if len(weekly) >= 2:

            # Previous completed weekly candle
            previous_week_high = weekly["High"].iloc[-2]

            # Current week candle
            daily = yf.Ticker(stock + ".NS").history(
            period="10d",
            interval="1d",
            auto_adjust=True
            )
            today_high = daily["High"].iloc[-1]
            yesterday_high = daily["High"].iloc[-2]
            ltp = daily["Close"].iloc[-1]

            if yesterday_high <= previous_week_high and today_high > previous_week_high:

                breakout_pct = round(
                    ((today_high - previous_week_high) / previous_week_high) * 100)



                weekly_breakout.append({
                    "Stock": stock,
                    "Prev Week High": round(previous_week_high, 2),
                    "Today High": round(today_high, 2),
                    "LTP": round(ltp, 2),
                    "Breakout %": f"{breakout_pct}%"
                })

    except:
        pass

if weekly_breakout:
    df = pd.DataFrame(weekly_breakout)
    st.dataframe(
            df.style.format({"Prev Week High": "{:.2f}","Today High": "{:.2f}","LTP": "{:.2f}"}).map(
                lambda v: "color: green; font-weight: bold;",
                subset=["Breakout %"]),use_container_width=True,hide_index=True)

else:
    st.info("No Weekly Breakout Today")
st.subheader("⭐ ORB Scanner")

orb_df = get_orb_scanner(sector_df)

if not orb_df.empty:
    st.dataframe(
        orb_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No ORB Signal Today")
