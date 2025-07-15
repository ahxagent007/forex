import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime


# ----------- Initialize MT5 -----------


path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

login = 273524617
password = "abcdABCD123!@#"
server = "Exness-MT5Trial6"

## REAL
# login = 104541427
# password = "abcdABCD123!@#"
# server = "Exness-MT5Real15"

timeout = 10000
portable = False
if mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
    print("Initialization successful")
else:
    print('Initialize failed')

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M15
bars = 500

# ----------- Get Historical Data -----------
rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)


# ----------- Convert to DataFrame -----------
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# ----------- Detect Support & Resistance -----------
def detect_support_resistance(data, window=3):
    support_levels = []
    resistance_levels = []
    for i in range(window, len(data) - window):
        low = data['low'].iloc[i]
        high = data['high'].iloc[i]

        if all(low < data['low'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            support_levels.append((data.index[i], low))

        if all(high > data['high'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            resistance_levels.append((data.index[i], high))
    return support_levels, resistance_levels

supports, resistances = detect_support_resistance(df)

# ----------- Plotting with mplfinance -----------
# Convert to OHLC format
df_plot = df[['open', 'high', 'low', 'close', 'tick_volume']].copy()
df_plot.columns = ['open', 'high', 'low', 'close', 'volume']

# Create horizontal line overlays
hlines = [price for _, price in supports[-5:]] + [price for _, price in resistances[-5:]]
hl_colors = ['g']*5 + ['r']*5  # Green for support, Red for resistance

# Plot
mpf.plot(
    df_plot,
    type='candle',
    volume=False,
    style='yahoo',
    title=f"{symbol} Support & Resistance",
    hlines=dict(hlines=hlines, colors=hl_colors, linestyle='--'),
    figsize=(12, 6)
)
