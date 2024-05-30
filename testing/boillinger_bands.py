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

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(df, window=20, num_std=2):
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])
    return df

# Function to generate Bollinger Bands signals
def bollinger_bands_signals(df):
    df['signal'] = 0
    df.loc[df['close'] > df['upper_band'], 'signal'] = -1  # Sell signal
    df.loc[df['close'] < df['lower_band'], 'signal'] = 1   # Buy signal
    return df

# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate Bollinger Bands
df = calculate_bollinger_bands(df)

# Generate Bollinger Bands signals
df = bollinger_bands_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'upper_band', 'middle_band', 'lower_band', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['upper_band'], label='Upper Band', linestyle='--')
plt.plot(df.index, df['middle_band'], label='Middle Band', linestyle='--')
plt.plot(df.index, df['lower_band'], label='Lower Band', linestyle='--')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Bollinger Bands Signals')
plt.legend()

plt.show()
