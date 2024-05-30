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


# Function to identify the Second Break signal
def second_break(df, breakout_window=20, pullback_window=5, threshold=0.01):
    df['high_breakout'] = df['high'].rolling(window=breakout_window).max()
    df['low_breakout'] = df['low'].rolling(window=breakout_window).min()

    df['signal'] = 0
    for i in range(breakout_window, len(df)):
        # Identify the initial breakout
        if df['close'].iloc[i] > df['high_breakout'].iloc[i - 1]:
            # Look for a pullback
            pullback_high = df['high'].iloc[i - pullback_window:i].max()
            if df['close'].iloc[i] < pullback_high - threshold:
                # Look for the second breakout
                for j in range(i + 1, len(df)):
                    if df['close'].iloc[j] > pullback_high:
                        df['signal'].iloc[j] = 1  # Buy signal
                        break

        elif df['close'].iloc[i] < df['low_breakout'].iloc[i - 1]:
            # Look for a pullback
            pullback_low = df['low'].iloc[i - pullback_window:i].min()
            if df['close'].iloc[i] > pullback_low + threshold:
                # Look for the second breakout
                for j in range(i + 1, len(df)):
                    if df['close'].iloc[j] < pullback_low:
                        df['signal'].iloc[j] = -1  # Sell signal
                        break
    return df


# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify the Second Break signals
df = second_break(df)

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
plt.title('EURUSD Second Break Signals')
plt.legend()
plt.show()

