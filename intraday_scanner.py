import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="Intraday Scanner",
    layout="wide"
)

st.title("📈 Nifty 100 Intraday Scanner")

# Load Sector Mapping
sector_df = pd.read_csv("sector_mapping.csv")
sector_df.columns = sector_df.columns.str.strip()

sector_dict = dict(zip(
    sector_df["SYMBOL"],
    sector_df["SECTOR"]
))

# Nifty 100 Stocks
stocks = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS",
    "INFY.NS","LT.NS","ITC.NS","AXISBANK.NS","KOTAKBANK.NS",
    "HINDUNILVR.NS","BHARTIARTL.NS","ASIANPAINT.NS","BAJFINANCE.NS",
    "MARUTI.NS","M&M.NS","TITAN.NS","SUNPHARMA.NS","ULTRACEMCO.NS",
    "NESTLEIND.NS","POWERGRID.NS","NTPC.NS","ONGC.NS","ADANIPORTS.NS",
    "ADANIENT.NS","TATASTEEL.NS","JSWSTEEL.NS","HCLTECH.NS",
    "WIPRO.NS","TECHM.NS","INDUSINDBK.NS","BAJAJFINSV.NS",
    "BAJAJ-AUTO.NS","EICHERMOT.NS","HINDALCO.NS","COALINDIA.NS",
    "GRASIM.NS","CIPLA.NS","DRREDDY.NS","APOLLOHOSP.NS",
    "TATAMOTORS.NS","BEL.NS","TRENT.NS","DIVISLAB.NS",
    "BRITANNIA.NS","HEROMOTOCO.NS","SHRIRAMFIN.NS","BPCL.NS",
    "PIDILITIND.NS","SBILIFE.NS","HDFCLIFE.NS","DMART.NS"
]

scanner = []

for stock in stocks:

    try:

        df = yf.download(
            stock,
            period="2d",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if len(df) < 2:
            continue

        today = df.iloc[-1]
        yesterday = df.iloc[-2]

        open_price = float(today["Open"])
        low_price = float(today["Low"])
        last_price = float(today["Close"])
        prev_close = float(yesterday["Close"])

        open_low = abs(open_price - low_price) <= 0.01
        open_prev = abs(open_price - prev_close) <= 0.01

        if open_low:
            signal = "🟢 BUY"
        elif open_prev:
            if last_price >= open_price:
                signal = "🟢 BUY"
            else:
                signal = "🔴 SELL"
            else:
                continue

symbol = stock.replace(".NS", "")

scanner.append({
    "Symbol": symbol,
    "Sector": sector_dict.get(symbol, "Unknown"),
    "Open": round(open_price, 2),
    "Low": round(low_price, 2),
    "Last Price": round(last_price, 2),
    "% Change": round(((last_price - prev_close) / prev_close) * 100, 2),
    "Signal": signal
})

    except:
        pass

scanner_df = pd.DataFrame(scanner)

st.subheader("📈 Intraday Scanner")

if scanner_df.empty:
    st.info("No Intraday Scanner Stock Found")
else:
    st.dataframe(scanner_df, use_container_width=True, hide_index=True)
# Column Order
scanner_df = scanner_df[
    [
        "Symbol",
        "Sector",
        "Open",
        "Low",
        "Last Price",
        "% Change",
        "Signal"
    ]
]

st.subheader("📈 Intraday Scanner")

if scanner_df.empty:
    st.warning("No Intraday Scanner Stock Found")
else:
    def color_signal(val):
    if "BUY" in val:
        return "color: green; font-weight: bold;"
    elif "SELL" in val:
        return "color: red; font-weight: bold;"
    return ""
st.dataframe(
    scanner_df.style.applymap(
        color_signal,
        subset=["Signal"]
    ),
    use_container_width=True,
    hide_index=True
)
if scanner_df.empty:
    st.warning("No Intraday Scanner Stock Found")
    
