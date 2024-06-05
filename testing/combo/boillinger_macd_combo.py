import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mt5_utils import get_data


# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1  # 1-hour timeframe

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

# Function to calculate MACD
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df['ema_short'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['ema_long'] = df['close'].ewm(span=long_window, adjust=False).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['signal_line'] = df['macd'].ewm(span=signal_window, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['signal_line']
    return df

# Function to generate Bollinger Bands + MACD signals
def generate_signals(df):
    df['signal'] = 0
    for i in range(1, len(df)):
        if df['macd'].iloc[i] > df['signal_line'].iloc[i] and df['close'].iloc[i] < df['lower_band'].iloc[i]:
            df['signal'].iloc[i] = 1  # Buy signal
        elif df['macd'].iloc[i] < df['signal_line'].iloc[i] and df['close'].iloc[i] > df['upper_band'].iloc[i]:
            df['signal'].iloc[i] = -1  # Sell signal
    return df

# Parameters
start = datetime.now() - timedelta(days=60)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate Bollinger Bands and MACD
df = calculate_bollinger_bands(df)
df = calculate_macd(df)

# Generate signals
df = generate_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'upper_band', 'middle_band', 'lower_band', 'macd', 'signal_line', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['upper_band'], label='Upper Band', linestyle='--')
plt.plot(df.index, df['middle_band'], label='Middle Band', linestyle='--')
plt.plot(df.index, df['lower_band'], label='Lower Band', linestyle='--')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Bollinger Bands + MACD Signals')
plt.legend()

plt.show()

# Shutdown MetaTrader 5 connection
mt5.shutdown()
