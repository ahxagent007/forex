import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
from mt5_utils import get_data

# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M5  # 5-minute timeframe


# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)


# Function to identify the Range Break signal
def range_break(df, range_window=20, breakout_window=5):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()

    df['signal'] = 0
    for i in range(range_window + breakout_window, len(df)):
        range_high = df['high_range'].iloc[i]
        range_low = df['low_range'].iloc[i]

        # Look for breakout after range
        for j in range(i - breakout_window, i):
            if df['close'].iloc[j] > range_high:
                df['signal'].iloc[i] = 1  # Buy signal
                break
            elif df['close'].iloc[j] < range_low:
                df['signal'].iloc[i] = -1  # Sell signal
                break
    return df


# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify the Range Break signals
df = range_break(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'high_range', 'low_range', 'signal']].tail(20))

# Plotting
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['high_range'], label='High Range', linestyle='--')
plt.plot(df.index, df['low_range'], label='Low Range', linestyle='--')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal',
            zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal',
            zorder=5)
plt.title('EURUSD Range Break Signals')
plt.legend()
plt.show()
