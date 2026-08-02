import pandas as pd
import yfinance as yf

def get_orb_scanner(sector_df):

    orb_scanner = []

    for _, row in sector_df.iterrows():

        stock = row["SYMBOL"]
        sector = row["SECTOR"]

        try:
            intraday = yf.Ticker(stock + ".NS").history(
                period="1d",
                interval="5m",
                auto_adjust=True
            )

            if len(intraday) < 2:
                continue

            orb_high = intraday["High"].iloc[0]
            orb_low = intraday["Low"].iloc[0]

            current_price = intraday["Close"].iloc[-1]
            previous_close = intraday["Close"].iloc[-2]

            change_pct = round(
                ((current_price - previous_close) / previous_close) * 100,
                2
            )

            signal = ""

            if current_price > orb_high:
                signal = "🟢 BUY"
            elif current_price < orb_low:
                signal = "🔴 SELL"
            else:
                continue

            orb_scanner.append({
                "Stock": stock,
                "Sector": sector,
                "Current Price": round(current_price, 2),
                "%": f"{change_pct:+.2f}%",
                "Signal": signal
            })

        except:
            pass

    return pd.DataFrame(orb_scanner)
