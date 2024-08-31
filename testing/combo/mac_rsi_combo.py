import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from testing.akash.mt5_utils import get_data

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


# Function to calculate moving averages
def calculate_moving_averages(df, short_window=50, long_window=200):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    return df

# Function to calculate RSI
def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# Function to identify RSI divergence
def identify_rsi_divergence(df):
    df['rsi_divergence'] = 0
    for i in range(2, len(df)):
        if (df['rsi'].iloc[i] < df['rsi'].iloc[i - 1] < df['rsi'].iloc[i - 2] and
                df['close'].iloc[i] > df['close'].iloc[i - 1] > df['close'].iloc[i - 2]):
            #df['rsi_divergence'].iloc[i] = -1  # Bearish divergence
            df.loc[i, 'rsi_divergence'] = -1
        elif (df['rsi'].iloc[i] > df['rsi'].iloc[i - 1] > df['rsi'].iloc[i - 2] and
              df['close'].iloc[i] < df['close'].iloc[i - 1] < df['close'].iloc[i - 2]):
            #df['rsi_divergence'].iloc[i] = 1  # Bullish divergence
            df.loc[i, 'rsi_divergence'] = 1
    return df

# Function to generate signals based on Moving Average Crossover + RSI Divergence
def generate_signals(df):
    df['signal'] = 0
    for i in range(1, len(df)):
        if (df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and
            df['short_ma'].iloc[i-1] < df['long_ma'].iloc[i-1] and
            df['rsi_divergence'].iloc[i] == 1):
            df['signal'].iloc[i] = 1  # Buy signal
        elif (df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and
              df['short_ma'].iloc[i-1] > df['long_ma'].iloc[i-1] and
              df['rsi_divergence'].iloc[i] == -1):
            df['signal'].iloc[i] = -1  # Sell signal
    return df

# Parameters
start = datetime.now() - timedelta(days=365)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate Moving Averages and RSI
df = calculate_moving_averages(df)
df = calculate_rsi(df)

# Identify RSI divergence
df = identify_rsi_divergence(df)

# Generate signals
df = generate_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'short_ma', 'long_ma', 'rsi', 'rsi_divergence', 'signal']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(df.index, df['close'], label='Close Price')
plt.plot(df.index, df['short_ma'], label='50-period MA')
plt.plot(df.index, df['long_ma'], label='200-period MA')
plt.scatter(df[df['signal'] == 1].index, df[df['signal'] == 1]['close'], marker='^', color='g', label='Buy Signal', zorder=5)
plt.scatter(df[df['signal'] == -1].index, df[df['signal'] == -1]['close'], marker='v', color='r', label='Sell Signal', zorder=5)
plt.title('EURUSD Moving Average Crossover + RSI Divergence Signals')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(df.index, df['rsi'], label='RSI')
plt.axhline(y=70, color='r', linestyle='--', label='Overbought')
plt.axhline(y=30, color='g', linestyle='--', label='Oversold')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['rsi_divergence'] == 1].index, df[df['rsi_divergence'] == 1]['close'], marker='^', color='g', label='Bullish Divergence', zorder=5)
plt.scatter(df[df['rsi_divergence'] == -1].index, df[df['rsi_divergence'] == -1]['close'], marker='v', color='r', label='Bearish Divergence', zorder=5)
plt.legend()

plt.tight_layout()
plt.show()

# Shutdown MetaTrader 5 connection
mt5.shutdown()
