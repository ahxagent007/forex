import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mt5_utils import get_data

# Connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1  # 1-hour timeframe

# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)

# Function to calculate ATR
def calculate_atr(df, window=14):
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=window).mean()
    return df

# Function to calculate moving averages
def calculate_moving_averages(df, short_window=50, long_window=200):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    return df

# Function to generate trend-following signals with ATR-based stop-loss
def generate_signals(df, atr_multiplier=1.5):
    df['signal'] = 0
    df['stop_loss'] = 0.0
    for i in range(1, len(df)):
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] <= df['long_ma'].iloc[i-1]:
            df['signal'].iloc[i] = 1  # Buy signal
            df['stop_loss'].iloc[i] = df['close'].iloc[i] - atr_multiplier * df['atr'].iloc[i]
        elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] >= df['long_ma'].iloc[i-1]:
            df['signal'].iloc[i] = -1  # Sell signal
            df['stop_loss'].iloc[i] = df['close'].iloc[i] + atr_multiplier * df['atr'].iloc[i]
    return df

# Parameters
start = datetime.now() - timedelta(days=365)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate ATR and moving averages
df = calculate_atr(df)
df = calculate_moving_averages(df)

# Generate signals
df = generate_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'short_ma', 'long_ma', 'atr', 'signal', 'stop_loss']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

# Plot Close Price with Moving Averages
plt.subplot(2, 1, 1)
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['short_ma'], label='50-period MA')
plt.plot(df.index, df['long_ma'], label='200-period MA')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Trend Following with ATR Signals')
plt.legend()

# Plot ATR
plt.subplot(2, 1, 2)
plt.plot(df.index, df['atr'], label='ATR')
plt.title('Average True Range (ATR)')
plt.legend()

plt.tight_layout()
plt.show()

# Shutdown MetaTrader 5 connection
mt5.shutdown()
