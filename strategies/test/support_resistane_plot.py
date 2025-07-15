import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import mplfinance as mpf
import matplotlib.pyplot as plt

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


symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M5
bars = 500

# ----------- Fetch Historical Data -----------
rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
mt5.shutdown()

# ----------- Prepare Data -----------
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)
df_plot = df[['open', 'high', 'low', 'close', 'tick_volume']].copy()
df_plot.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# ----------- Detect Swing Low Supports -----------
def find_supports(df, window=3):
    supports = []
    for i in range(window, len(df) - window):
        low = df['Low'].iloc[i]
        if all(low < df['Low'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            supports.append(low)
    return supports

raw_supports = find_supports(df_plot)

# ----------- Group into Support Zones -----------
def group_zones(levels, threshold=2.0):
    zones = []
    levels.sort()
    zone = [levels[0]]
    for level in levels[1:]:
        if abs(level - zone[-1]) <= threshold:
            zone.append(level)
        else:
            zones.append((min(zone), max(zone)))
            zone = [level]
    if zone:
        zones.append((min(zone), max(zone)))
    return zones

support_zones = group_zones(raw_supports, threshold=2.0)

# ----------- Plot with Shaded Support Zones -----------
addplots = []

for low, high in support_zones[-5:]:  # last 5 zones
    addplots.append(
        mpf.make_addplot(
            [low] * len(df_plot),
            panel=0,
            type='line',
            color='green',
            linestyle='dotted'
        )
    )
    # Add shaded zone
    plt.axhspan(low, high, color='green', alpha=0.15)

# Plot candlesticks + support zones
mpf.plot(
    df_plot,
    type='candle',
    style='yahoo',
    title='Support Zones - XAUUSD',
    addplot=addplots,
    volume=False,
    figsize=(12, 6)
)
