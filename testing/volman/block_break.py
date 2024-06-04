from mt5_utils import get_data

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time

# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M5  # 5-minute timeframe


# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)


# Function to identify the Block Break signal
def block_break(df, consolidation_window=10, breakout_window=10):
    df['signal'] = 0
    for i in range(consolidation_window + breakout_window, len(df)):
        consolidation_high = max(df['high'].iloc[i - consolidation_window:i])
        consolidation_low = min(df['low'].iloc[i - consolidation_window:i])

        # Look for breakout after consolidation
        for j in range(i - breakout_window, i):
            if df['close'].iloc[j] > consolidation_high:
                df['signal'].iloc[i] = 1  # Buy signal
                break
            elif df['close'].iloc[j] < consolidation_low:
                df['signal'].iloc[i] = -1  # Sell signal
                break
    return df


# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify the Block Break signals
df = block_break(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'signal']].tail(20))

# Plotting
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal',
            zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal',
            zorder=5)
plt.title('EURUSD Block Break Signals')
plt.legend()
plt.show()

