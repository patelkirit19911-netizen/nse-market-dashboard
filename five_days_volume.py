import pandas as pd
import yfinance as yf


def get_high_volume(stocks):
    high_volume = []

    for stock in stocks:
        try:
            daily = yf.download(
                stock + ".NS",
                period="10d",
                interval="1d",
                progress=False
            )

            if len(daily) < 6:
                continue

            avg_5d_volume = daily["Volume"].iloc[-6:-1].mean()
            today_volume = daily["Volume"].iloc[-1]

            if avg_5d_volume == 0:
                continue

            volume_ratio = today_volume / avg_5d_volume

            if volume_ratio >= 1.5:
                high_volume.append({
                    "Stock": stock,
                    "Avg 5D Volume": int(avg_5d_volume),
                    "Today Volume": int(today_volume),
                    "Volume Spike": f"{volume_ratio:.2f}x"
                })

        except Exception:
            continue

    return pd.DataFrame(high_volume)
