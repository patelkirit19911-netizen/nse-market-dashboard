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

            # First 5 Minute Candle (9:15)
            first_candle = intraday.iloc[0]
            first_high = first_candle["High"]

            # Condition 1
            condition1 = today_high > previous_day_high

            # Check every 5-minute candle after 9:15
            for i in range(6, len(intraday)):

                candle = intraday.iloc[i]

                # Previous 5 completed candles
                prev_5 = intraday.iloc[i-5:i]

                # Condition 2
                condition2 = candle["High"] > first_high

                # Condition 3
                condition3 = (
                    candle["Volume"] >
                    prev_5["Volume"].max()
                )

                if condition1 and condition2 and condition3:

                    results.append({
                        "Stock": stock,
                        "Sector": sector,
                        "LTP": round(candle["Close"], 2),
                        "Signal": "BUY"
                    })

                    break

        except:
            pass

    return pd.DataFrame(results)
