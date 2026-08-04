import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from orb_scanner import get_orb_scanner
from five_days_volume import get_high_volume
from Intraday_Gainer import get_intraday_gainer
st.set_page_config(page_title="NSE Market Dashboard", layout="wide")

st.title("📊 NSE MARKET DASHBOARD")

# Sector mapping
sector_df = pd.read_csv("sector_mapping.csv")

strength = {}
sector_change = {}

symbols = [s + ".NS" for s in sector_df["SYMBOL"].unique()]

try:
    data = yf.download(
        tickers=symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=False
    )

    for sector in sector_df["SECTOR"].unique():

        stocks = sector_df[sector_df["SECTOR"] == sector]["SYMBOL"]

        changes = []

        for stock in stocks:
            try:
                df = data[stock + ".NS"]

                if len(df) >= 2:
                    prev_close = df["Close"].iloc[-2]
                    last_close = df["Close"].iloc[-1]

                    change = (
                        (last_close - prev_close)
                        / prev_close
                    ) * 100

                    changes.append(change)

            except:
                pass

        if changes:
            sector_change[sector] = round(
                sum(changes) / len(changes), 2
            )

except:
    sector_change = {}

st.subheader("📊 Sector Performance (1D)")

chart_df = pd.DataFrame(
    list(sector_change.items()),
    columns=["Sector", "Change"]
).sort_values("Change", ascending=False)


for _, row in chart_df.iterrows():

    sector = row["Sector"]
    change = row["Change"]
    with st.expander(f"{sector} ({change:.2f}%)"):

        sector_stocks = sector_df[
            sector_df["SECTOR"] == sector
        ]["SYMBOL"].tolist()
        
        stock_data = []

        for stock in sector_stocks:
            try:
                data = yf.Ticker(stock + ".NS").history(
                    period="5d",
                    auto_adjust=True
                )
                

                if len(data) >= 2:
                    chg = (
                        (data["Close"].iloc[-1] - data["Close"].iloc[-2])
                        / data["Close"].iloc[-2]
                    ) * 100

                    stock_data.append((stock, chg))

            except Exception as e:
                pass
        stock_data = sorted(stock_data, key=lambda x: x[1], reverse=True)
        
        for s, c in stock_data:

            try:
                c = float(c)
                if c >= 0:
                    color = "🟢"
                    bar = "🟩" * min(int(abs(c) * 2), 10)
                else:
                    color = "🔴"
                    bar = "🟥" * min(int(abs(c) * 2), 10)
            except:
                color = "⚪"
                bar = ""
            st.markdown(
                f"{color} **{s}** {c:+.2f}% &nbsp;&nbsp; {bar}",
                unsafe_allow_html=True
        )   
col3, col4 = st.columns([3,2])
intraday_df = get_intraday_gainer(sector_df)
high_volume = get_high_volume(sector_df["SYMBOL"].tolist())

            
with col3:
    st.subheader("🚀 Intraday Gainer")

if not intraday_df.empty:
    st.dataframe(
        intraday_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No Intraday Gainer")
    
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
