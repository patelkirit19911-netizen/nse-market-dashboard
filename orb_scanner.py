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
            intraday["VWAP"] = (
                (intraday["Close"] * intraday["Volume"]).cumsum()
                / intraday["Volume"].cumsum())
            
            orb_volume = intraday["Volume"].iloc[:3].sum()
            current_volume = intraday["Volume"].iloc[-1]
            if len(intraday) < 4:
                continue

            orb_high = intraday["High"].iloc[:3].max()
            orb_low = intraday["Low"].iloc[:3].min()
            
            current_price = intraday["Close"].iloc[-1]
            current_vwap = intraday["VWAP"].iloc[-1]
            previous_close = intraday["Close"].iloc[-2]

            change_pct = round(
                ((current_price - previous_close) / previous_close) * 100,
                2
            )

            signal = ""

            if (current_price > orb_high * 1.002
                and current_volume > (orb_volume * 0.50)
                and current_price > current_vwap):
                    signal = "🟢 BUY"
            elif (current_price < orb_low * 0.998
                  and current_volume > (orb_volume * 0.50)
                  and current_price < current_vwap):
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

    df = pd.DataFrame(orb_scanner)

    if not df.empty:
        df["abs_change"] = df["%"].str.replace("%", "").astype(float).abs()
        df = df.sort_values("abs_change", ascending=False)
        df = df.drop(columns=["abs_change"])
        df = df.head(3)
    return df
