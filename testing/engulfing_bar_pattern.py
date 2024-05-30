import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from mt5_utils import get_data


# Define the symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M5  # 5-minute timeframe

# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)

# Function to identify Engulfing patterns
def identify_engulfing_bars(df):
    df['engulfing'] = ((df['close'] > df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & (df['close'] >= df['open'].shift(1)) & (df['open'] <= df['close'].shift(1))) | \
                      ((df['close'] < df['open']) & (df['close'].shift(1) > df['open'].shift(1)) & (df['close'] <= df['open'].shift(1)) & (df['open'] >= df['close'].shift(1)))
    return df

# Function to identify Engulfing Bar signals
def engulfing_bar_signals(df):
    df['signal'] = 0
    for i in range(1, len(df)):
        if df['engulfing'].iloc[i]:
            if df['close'].iloc[i] > df['open'].iloc[i]:
                df['signal'].iloc[i+1] = 1  # Buy signal
            elif df['close'].iloc[i] < df['open'].iloc[i]:
                df['signal'].iloc[i+1] = -1  # Sell signal
    return df

# Parameters
start = datetime.now() - timedelta(days=30)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify Engulfing patterns
df = identify_engulfing_bars(df)

# Identify Engulfing Bar signals
df = engulfing_bar_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'engulfing', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Engulfing Bar Signals')
plt.legend()
plt.show()
