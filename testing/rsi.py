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

# Function to calculate RSI
def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# Function to generate RSI signals
def rsi_signals(df, overbought=70, oversold=30):
    df['signal'] = 0
    df.loc[df['rsi'] > overbought, 'signal'] = -1  # Sell signal
    df.loc[df['rsi'] < oversold, 'signal'] = 1   # Buy signal
    return df

# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate RSI
df = calculate_rsi(df)

# Generate RSI signals
df = rsi_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'rsi', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Close Price and RSI Signals')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df.index, df['rsi'], label='RSI')
plt.axhline(y=70, color='r', linestyle='--', label='Overbought')
plt.axhline(y=30, color='g', linestyle='--', label='Oversold')
plt.title('RSI')
plt.legend()

plt.tight_layout()
plt.show()
