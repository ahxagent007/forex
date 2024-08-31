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


# Function to calculate Fibonacci retracement levels
def calculate_fibonacci_retracement(df, lookback=20):
    df['swing_high'] = df['high'].rolling(window=lookback).max()
    df['swing_low'] = df['low'].rolling(window=lookback).min()

    df['fib_0'] = df['swing_high']
    df['fib_23.6'] = df['swing_high'] - 0.236 * (df['swing_high'] - df['swing_low'])
    df['fib_38.2'] = df['swing_high'] - 0.382 * (df['swing_high'] - df['swing_low'])
    df['fib_50'] = df['swing_high'] - 0.5 * (df['swing_high'] - df['swing_low'])
    df['fib_61.8'] = df['swing_high'] - 0.618 * (df['swing_high'] - df['swing_low'])
    df['fib_100'] = df['swing_low']

    return df


# Function to identify price action patterns (pin bars and engulfing bars)
def identify_price_action_patterns(df):
    df['pin_bar'] = 0
    df['engulfing'] = 0

    for i in range(1, len(df)):
        # Identify Pin Bars
        if (df['high'].iloc[i] - df['close'].iloc[i] > (df['high'].iloc[i] - df['low'].iloc[i]) * 2 / 3 and
                df['close'].iloc[i] > df['open'].iloc[i]):
            #df['pin_bar'].iloc[i] = 1  # Bullish pin bar
            df.loc[i, 'pin_bar'] = 1
        elif (df['close'].iloc[i] - df['low'].iloc[i] > (df['high'].iloc[i] - df['low'].iloc[i]) * 2 / 3 and
              df['close'].iloc[i] < df['open'].iloc[i]):
            #df['pin_bar'].iloc[i] = -1  # Bearish pin bar
            df.loc[i, 'pin_bar'] = -1

        # Identify Engulfing Bars
        if (df['close'].iloc[i] > df['open'].iloc[i] and
                df['close'].iloc[i] > df['open'].iloc[i - 1] > df['close'].iloc[i - 1] > df['open'].iloc[i]):
            #df['engulfing'].iloc[i] = 1  # Bullish engulfing
            df.loc[i, 'engulfing'] = 1

        elif (df['close'].iloc[i] < df['open'].iloc[i] and
              df['close'].iloc[i] < df['open'].iloc[i - 1] < df['close'].iloc[i - 1] < df['open'].iloc[i]):
            #df['engulfing'].iloc[i] = -1  # Bearish engulfing
            df.loc[i, 'engulfing'] = -1

    return df


# Function to generate signals based on Fibonacci retracement levels and price action patterns
def generate_signals(df):
    df['signal'] = 0
    for i in range(1, len(df)):
        if (df['pin_bar'].iloc[i] == 1 or df['engulfing'].iloc[i] == 1) and (
                df['close'].iloc[i] > df['fib_50'].iloc[i] and df['close'].iloc[i] < df['fib_38.2'].iloc[i]):
            df['signal'].iloc[i] = 1  # Buy signal
        elif (df['pin_bar'].iloc[i] == -1 or df['engulfing'].iloc[i] == -1) and (
                df['close'].iloc[i] < df['fib_50'].iloc[i] and df['close'].iloc[i] > df['fib_61.8'].iloc[i]):
            df['signal'].iloc[i] = -1  # Sell signal
    return df


# Parameters
start = datetime.now() - timedelta(days=365)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Calculate Fibonacci retracement levels
df = calculate_fibonacci_retracement(df)

# Identify price action patterns
df = identify_price_action_patterns(df)

# Generate signals
df = generate_signals(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'fib_23.6', 'fib_38.2', 'fib_50', 'fib_61.8', 'pin_bar', 'engulfing',
          'signal']].tail(20))

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
plt.title('EURUSD Fibonacci Retracement + Price Action Patterns Signals')
plt.legend()

plt.show()

# Shutdown MetaTrader 5 connection
mt5.shutdown()
