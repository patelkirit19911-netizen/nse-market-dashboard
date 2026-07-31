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

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.subheader("📊 Sector Performance (1D)")
    

    chart_df = pd.DataFrame(
        list(sector_change.items()),
        columns=["Sector", "Change"]
    )
    chart_df = chart_df.sort_values("Change", ascending=True)
    

    colors = ["green" if x >= 0 else "red" for x in chart_df["Change"]]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=chart_df["Change"],
        y=chart_df["Sector"],
        orientation="h",
        marker_color=colors,
        text=[f"{x:.2f}%" for x in chart_df["Change"]],
        textposition="outside"
    ))

    fig.update_layout(
        height=700,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)
    with col3:
        st.subheader("📂 Select Sector")

        for sector in chart_df["Sector"]:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.write(sector)
            with c2:
                if st.button("📂", key=sector):
                    st.session_state["selected_sector"] = sector
    
with col2:
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

col3, col4 = st.columns(2)

with col3:
    st.subheader("📅 Daily Breakout")
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
              "Volume Spike": f"{round(volume_ratio, 2)}x"})
         

    except:
        pass

if daily_breakout:
    st.dataframe(
        pd.DataFrame(daily_breakout),
        use_container_width=True,
        hide_index=True
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

