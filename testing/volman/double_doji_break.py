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
    data = get_data(symbol)
    return data


# Function to identify Doji candles
def is_doji(row, threshold=0.1):
    body_size = abs(row['open'] - row['close'])
    total_range = row['high'] - row['low']
    return body_size <= threshold * total_range


# Function to identify Double Doji patterns and generate signals
def double_doji_break(df, threshold=0.1):
    df['doji'] = df.apply(lambda row: is_doji(row, threshold), axis=1)
    df['double_doji'] = (df['doji'] & df['doji'].shift(1))

    df['signal'] = 0
    for i in range(1, len(df)):
        if df['double_doji'].iloc[i]:
            if df['high'].iloc[i] > df['high'].iloc[i - 1]:
                df['signal'].iloc[i + 1] = 1  # Buy signal
            elif df['low'].iloc[i] < df['low'].iloc[i - 1]:
                df['signal'].iloc[i + 1] = -1  # Sell signal

    return df


# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify Double Doji patterns and generate signals
df = double_doji_break(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'doji', 'double_doji', 'signal']].tail(20))

# Plotting
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal',
            zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal',
            zorder=5)
plt.title('EURUSD Double Doji Break Signals')
plt.legend()
plt.show()

