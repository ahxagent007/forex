import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from mt5_utils import get_data

# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1  # 1-hour timeframe


# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)


# Function to calculate Fibonacci retracement levels
def calculate_fibonacci_retracement(df, window=20):
    df['max_high'] = df['high'].rolling(window=window).max()
    df['min_low'] = df['low'].rolling(window=window).min()

    df['fib_0'] = df['max_high']
    df['fib_23.6'] = df['max_high'] - 0.236 * (df['max_high'] - df['min_low'])
    df['fib_38.2'] = df['max_high'] - 0.382 * (df['max_high'] - df['min_low'])
    df['fib_50'] = df['max_high'] - 0.5 * (df['max_high'] - df['min_low'])
    df['fib_61.8'] = df['max_high'] - 0.618 * (df['max_high'] - df['min_low'])
    df['fib_100'] = df['min_low']

    return df


# Function to generate Fibonacci retracement signals
def fibonacci_retracement_signals(df):
    df['signal'] = 0
    for i in range(1, len(df)):
        if df['close'].iloc[i] < df['fib_38.2'].iloc[i] and df['close'].iloc[i] > df['fib_50'].iloc[i]:
            df['signal'].iloc[i] = 1  # Buy signal
        elif df['close'].iloc[i] > df['fib_61.8'].iloc[i] and df['close'].iloc[i] < df['fib_50'].iloc[i]:
            df['signal'].iloc[i] = -1  # Sell signal
    return df


# Parameters
start = datetime.now() - timedelta(days=60)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate Fibonacci retracement levels
df = calculate_fibonacci_retracement(df)

# Generate Fibonacci retracement signals
df = fibonacci_retracement_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'fib_23.6', 'fib_38.2', 'fib_50', 'fib_61.8', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['fib_0'], label='Fib 0%', linestyle='--')
plt.plot(df.index, df['fib_23.6'], label='Fib 23.6%', linestyle='--')
plt.plot(df.index, df['fib_38.2'], label='Fib 38.2%', linestyle='--')
plt.plot(df.index, df['fib_50'], label='Fib 50%', linestyle='--')
plt.plot(df.index, df['fib_61.8'], label='Fib 61.8%', linestyle='--')
plt.plot(df.index, df['fib_100'], label='Fib 100%', linestyle='--')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal',
            zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal',
            zorder=5)
plt.title('EURUSD Fibonacci Retracement Signals')
plt.legend()

plt.show()
