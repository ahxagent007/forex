import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from mt5_utils import get_data

# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M15  # 15-minute timeframe


# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)


# Function to identify False Breakout signals
def false_breakout_signals(df, range_window=20, confirmation_window=3):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()
    df['signal'] = 0

    for i in range(range_window, len(df) - confirmation_window):
        if df['close'].iloc[i] > df['high_range'].iloc[i - 1]:
            # Check if the breakout fails within the confirmation window
            if any(df['close'].iloc[i + 1:i + 1 + confirmation_window] < df['high_range'].iloc[i - 1]):
                df['signal'].iloc[i + 1 + confirmation_window] = -1  # Sell signal (False breakout)

        elif df['close'].iloc[i] < df['low_range'].iloc[i - 1]:
            # Check if the breakout fails within the confirmation window
            if any(df['close'].iloc[i + 1:i + 1 + confirmation_window] > df['low_range'].iloc[i - 1]):
                df['signal'].iloc[i + 1 + confirmation_window] = 1  # Buy signal (False breakout)

    return df


# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify False Breakout signals
df = false_breakout_signals(df)

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
plt.title('EURUSD False Breakout Signals')
plt.legend()
plt.show()

