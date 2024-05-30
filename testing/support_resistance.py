import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime
import matplotlib.pyplot as plt
from mt5_utils import get_data
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time


# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1  # 1-hour timeframe

# Function to fetch historical data from MT5
def fetch_historical_data(symbol):
    data = get_data(symbol)
    return data



# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1  # 1-hour timeframe

# Function to calculate support and resistance levels
def calculate_support_resistance(df, window=14):
    df['support'] = df['low'].rolling(window=window).min()
    df['resistance'] = df['high'].rolling(window=window).max()
    return df

# Function to generate trading signals based on support and resistance levels
def generate_sr_signals(df):
    df['signal'] = 0
    df.loc[df['close'] > df['resistance'], 'signal'] = -1  # Sell signal
    df.loc[df['close'] < df['support'], 'signal'] = 1    # Buy signal
    return df

# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol)

# Calculate support and resistance levels
df = calculate_support_resistance(df)

# Generate support and resistance signals
df = generate_sr_signals(df)

# Display signals
print(df[['close', 'support', 'resistance', 'signal']].tail())

# Plotting
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['support'], label='Support', linestyle='--')
plt.plot(df.index, df['resistance'], label='Resistance', linestyle='--')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Support and Resistance Signals')
plt.legend()
plt.show()


