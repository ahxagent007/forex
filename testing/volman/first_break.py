from mt5_utils import get_data

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time


symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M5  # 5-minute timeframe

# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)

# Function to identify consolidation periods
def identify_consolidation(df, window=20, threshold=0.01):
    df['range'] = df['high'] - df['low']
    df['rolling_range'] = df['range'].rolling(window=window).mean()
    df['consolidation'] = df['rolling_range'] < threshold
    return df

# Function to identify the first break
def first_break(df):
    df['signal'] = 0
    consolidation = False
    for i in range(1, len(df)):
        if df['consolidation'].iloc[i] and not consolidation:
            consolidation = True
        elif not df['consolidation'].iloc[i] and consolidation:
            if df['close'].iloc[i] > df['high'].iloc[i-1]:
                df['signal'].iloc[i] = 1  # Buy signal
                consolidation = False
            elif df['close'].iloc[i] < df['low'].iloc[i-1]:
                df['signal'].iloc[i] = -1  # Sell signal
                consolidation = False
    return df

# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify consolidation periods
df = identify_consolidation(df)

# Identify the first break and generate signals
df = first_break(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'rolling_range', 'consolidation', 'signal']].tail(20))

# Plotting
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD First Break Signals')
plt.legend()
plt.show()

