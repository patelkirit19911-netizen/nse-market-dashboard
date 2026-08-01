import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
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

selected_sector = None
chart_df = pd.DataFrame(
    list(sector_change.items()),
    columns=["Sector", "Change"]
)

chart_df = chart_df.sort_values("Change", ascending=False)
html = """
<style>
.row{
display:flex;
align-items:center;
margin:8px 0;
font-family:Arial;
}
.name{
width:120px;
font-weight:bold;
}
.barbg{
width:260px;
height:18px;
background:#eeeeee;
border-radius:10px;
margin:0 10px;
overflow:hidden;
}
.bar{
height:18px;
}
.value{
width:60px;
font-weight:bold;
}
</style>
"""

for _, row in chart_df.iterrows():
    if pd.isna(row["Change"]):
        continue
    color = "#0a9d36" if row["Change"] >= 0 else "#d62828"

    width = max(2, min(abs(row["Change"]) * 60, 260))
    html += f"""
    <div class="row">
        <div class="name">{row['Sector']}</div>

        <div class="barbg">
            <div class="bar"
                 style="width:{width}px;background:{color};">
            </div>
        </div>

        <div class="value">{row['Change']:.2f}%</div>
    </div>
    """

components.html(html, height=700, scrolling=True)
col3, col4 = st.columns([3,2])

daily_breakout = []
high_volume = []

for stock in sector_df["SYMBOL"]:
    try:
        daily = yf.Ticker(stock + ".NS").history(
            period="5d",
            interval="1d",
            auto_adjust=True
        )

        if len(daily) >= 2:
            previous_day_high = daily["High"].iloc[-2]
            today_high = daily["High"].iloc[-1]
            ltp = daily["Close"].iloc[-1]

            avg_5d_volume = daily["Volume"].mean()
            today_volume = daily["Volume"].iloc[-1]
            volume_ratio = today_volume / avg_5d_volume

            if today_high > previous_day_high and ltp > previous_day_high:
                breakout_pct = round(
                    ((today_high - previous_day_high) / previous_day_high) * 100,
                    2
                )

                daily_breakout.append({
                    "Stock": stock,
                    "Prev Day High": round(previous_day_high, 2),
                    "Today High": round(today_high, 2),
                    "LTP": round(ltp, 2),
                    "Breakout %": f"{breakout_pct}%"
                })

            if volume_ratio >= 2:
                high_volume.append({
                    "Stock": stock,
                    "Avg 5D Volume": int(avg_5d_volume),
                    "Today Volume": int(today_volume),
                    "Volume Spike": f"{round(volume_ratio, 2)}x"
                })

    except Exception:
        pass

with col3:
    st.markdown("""
<style>
[data-testid="stDataFrame"] td:nth-child(5){
    color: green !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)
    st.subheader("📅 Daily Breakout")
    if daily_breakout:
        df = pd.DataFrame(daily_breakout)

df["Breakout %"] = df["Breakout %"].apply(
    lambda x: f'<span style="color:green;font-weight:bold">{x}</span>'
)

st.write(
    df.to_html(index=False, escape=False),
    unsafe_allow_html=True
)
        
    else:
        st.info("No Daily Breakout Today")   
with col4:
    st.subheader("🔥 Last 5 Days High Volume")
    if high_volume:
        st.dataframe(
        pd.DataFrame(high_volume),
        use_container_width=True,
        hide_index=True
        )
    else:
        st.info("No High Volume Stocks Today")
st.subheader("📈 Weekly Breakout")
weekly_breakout = []

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
                    ((today_high - previous_week_high) / previous_week_high) * 100
                )

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
    st.dataframe(
        pd.DataFrame(weekly_breakout),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No Weekly Breakout Today")
    

