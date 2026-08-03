import yfinance as yf
import pandas as pd

def get_intraday_gainer(sector_df):

    results = []

    for _, row in sector_df.iterrows():

        stock = row["SYMBOL"]
        sector = row["SECTOR"]

        try:
            # Daily Data
            daily = yf.download(
                stock + ".NS",
                period="5d",
                interval="1d",
                progress=False
            )

            if len(daily) < 2:
                continue

            # 5 Minute Data
            intraday = yf.download(
                stock + ".NS",
                period="1d",
                interval="5m",
                progress=False
            )

            if len(intraday) < 7:
                continue

            # Previous Day High
            previous_day_high = daily["High"].iloc[-2]

            # Today's High
            today_high = intraday["High"].max()

            # First 5 Minute Candle
            first_candle = intraday.iloc[0]

            # Last Candle
            last_candle = intraday.iloc[-1]

            # Previous 5 Candles
            prev_5 = intraday.iloc[-6:-1]

            # Condition 1
            condition1 = today_high > previous_day_high

            # Condition 2
            condition2 = last_candle["High"] > first_candle["High"]

            # Condition 3
            condition3 = (
                last_candle["Volume"] >
                prev_5["Volume"].max()
            )

            if condition1 and condition2 and condition3:

                results.append({
                    "Stock": stock,
                    "Sector": sector,
                    "LTP": round(last_candle["Close"], 2),
                    "Signal": "BUY"
                })

        except:
            pass

    return pd.DataFrame(results)
