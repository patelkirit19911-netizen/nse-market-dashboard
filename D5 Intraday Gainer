# Previous Day High
previous_day_high = daily_data["High"].iloc[-2]

# Current Today High
today_high = intraday["High"].max()

# Last completed 5-minute candle
last_candle = intraday.iloc[-1]

# Previous 5 completed candles (last candle ko chhodkar)
prev_5 = intraday.iloc[-6:-1]

# ----------------------------
# Condition 1
condition1 = today_high > previous_day_high

# Condition 2
# Last candle ne naya Today High banaya
condition2 = (
    last_candle["High"] >= today_high
)

# Condition 3
# Breakout candle ka volume > previous 5 candles ke highest volume
condition3 = (
    last_candle["Volume"] > prev_5["Volume"].max()
)

# Final Signal
if condition1 and condition2 and condition3:
    signal = "BUY"
else:
    signal = ""
