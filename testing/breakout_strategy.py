from mt5_utils import get_data

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt

# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M15  # 15-minute timeframe


# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)


# Function to identify Breakout signals
def breakout_signals(df, range_window=20):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()
    df['signal'] = 0

    for i in range(range_window, len(df)):
        if df['close'].iloc[i] > df['high_range'].iloc[i - 1]:
            df['signal'].iloc[i] = 1  # Buy signal
        elif df['close'].iloc[i] < df['low_range'].iloc[i - 1]:
            df['signal'].iloc[i] = -1  # Sell signal

    return df


# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify Breakout signals
df = breakout_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'high_range', 'low_range', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['high_range'], label='High Range', linestyle='--')
plt.plot(df.index, df['low_range'], label='Low Range', linestyle='--')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal',
            zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal',
            zorder=5)
plt.title('EURUSD Breakout Signals')
plt.legend()
plt.show()


