
from Nahid.testing.akash.mt5_utils import get_data

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Define the symbol and timeframe
symbol = "USDJPY"
timeframe = mt5.TIMEFRAME_H1  # 1-hour timeframe

# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)

# Function to calculate Ichimoku Cloud
def calculate_ichimoku(df):
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2

    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2

    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    df['chikou_span'] = df['close'].shift(-26)
    return df

# Function to calculate Stochastic Oscillator
def calculate_stochastic(df, k_window=14, d_window=3):
    df['min_low'] = df['low'].rolling(window=k_window).min()
    df['max_high'] = df['high'].rolling(window=k_window).max()
    df['%K'] = (df['close'] - df['min_low']) / (df['max_high'] - df['min_low']) * 100
    df['%D'] = df['%K'].rolling(window=d_window).mean()
    return df

# Function to generate Ichimoku Cloud + Stochastic Oscillator signals
def generate_signals(df):
    df['signal'] = 0
    for i in range(1, len(df)):
        if (df['tenkan_sen'].iloc[i] > df['kijun_sen'].iloc[i] and
            df['close'].iloc[i] > df['senkou_span_a'].iloc[i] and
            df['close'].iloc[i] > df['senkou_span_b'].iloc[i] and
            df['%K'].iloc[i] < 20 and df['%D'].iloc[i] < 20 and
            df['%K'].iloc[i] > df['%D'].iloc[i]):
            df['signal'].iloc[i] = 1  # Buy signal
        elif (df['tenkan_sen'].iloc[i] < df['kijun_sen'].iloc[i] and
              df['close'].iloc[i] < df['senkou_span_a'].iloc[i] and
              df['close'].iloc[i] < df['senkou_span_b'].iloc[i] and
              df['%K'].iloc[i] > 80 and df['%D'].iloc[i] > 80 and
              df['%K'].iloc[i] < df['%D'].iloc[i]):
            df['signal'].iloc[i] = -1  # Sell signal
    return df

# Parameters
start = datetime.now() - timedelta(days=365)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate Ichimoku Cloud and Stochastic Oscillator
df = calculate_ichimoku(df)
df = calculate_stochastic(df)

# Generate signals
df = generate_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span', '%K', '%D', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

# Plot Close Price with Ichimoku Cloud
plt.subplot(3, 1, 1)
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['tenkan_sen'], label='Tenkan-sen')
plt.plot(df.index, df['kijun_sen'], label='Kijun-sen')
plt.plot(df.index, df['senkou_span_a'], label='Senkou Span A', linestyle='--')
plt.plot(df.index, df['senkou_span_b'], label='Senkou Span B', linestyle='--')
plt.fill_between(df.index, df['senkou_span_a'], df['senkou_span_b'], where=(df['senkou_span_a'] >= df['senkou_span_b']), color='lightgreen', alpha=0.5)
plt.fill_between(df.index, df['senkou_span_a'], df['senkou_span_b'], where=(df['senkou_span_a'] < df['senkou_span_b']), color='lightcoral', alpha=0.5)
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Ichimoku Cloud + Stochastic Oscillator Signals')
plt.legend()

# Plot Stochastic Oscillator
plt.subplot(3, 1, 2)
plt.plot(df.index, df['%K'], label='%K')
plt.plot(df.index, df['%D'], label='%D')
plt.axhline(y=80, color='r', linestyle='--', label='Overbought')
plt.axhline(y=20, color='g', linestyle='--', label='Oversold')
plt.legend()

plt.tight_layout()
plt.show()

# Shutdown MetaTrader 5 connection
mt5.shutdown()
