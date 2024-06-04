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
# ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
symbol = "USDCHF"
timeframe = mt5.TIMEFRAME_D1  # Daily timeframe

# Function to fetch historical data from MT5
def fetch_historical_data(symbol, timeframe, start, end):
    return get_data(symbol)

# Function to identify Three White Soldiers pattern
def identify_three_white_soldiers(df):
    df['pattern'] = 0
    for i in range(2, len(df)):
        if (df['close'].iloc[i] > df['open'].iloc[i] and
            df['close'].iloc[i-1] > df['open'].iloc[i-1] and
            df['close'].iloc[i-2] > df['open'].iloc[i-2] and
            df['open'].iloc[i] > df['close'].iloc[i-1]):
            df['pattern'].iloc[i] = 1  # Bullish pattern
    return df

# Function to identify Three Black Crows pattern
def identify_three_black_crows(df):
    df['pattern'] = 0
    for i in range(2, len(df)):
        if (df['close'].iloc[i] < df['open'].iloc[i] and
            df['close'].iloc[i-1] < df['open'].iloc[i-1] and
            df['close'].iloc[i-2] < df['open'].iloc[i-2] and
            df['open'].iloc[i] < df['close'].iloc[i-1]):
            df['pattern'].iloc[i] = -1  # Bearish pattern
    return df

# Parameters
start = datetime.now() - timedelta(days=365)
end = datetime.now()

# Fetch historical data
df = fetch_historical_data(symbol, timeframe, start, end)

# Identify patterns
df = identify_three_white_soldiers(df)
df = identify_three_black_crows(df)

# Display signals
print(df[['open', 'high', 'low', 'close', 'pattern']].tail(20))

# Plotting
plt.figure(figsize=(12, 8))
plt.plot(df.index, df['close'], label='Close Price')
plt.scatter(df[df['pattern'] == 1].index, df[df['pattern'] == 1]['close'], marker='^', color='g', label='Three White Soldiers', zorder=5)
plt.scatter(df[df['pattern'] == -1].index, df[df['pattern'] == -1]['close'], marker='v', color='r', label='Three Black Crows', zorder=5)
plt.title(symbol+' Three White Soldiers and Three Black Crows Patterns')
plt.legend()
plt.show()

# Shutdown MetaTrader 5 connection
mt5.shutdown()
