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

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
bars = 300

# ----------- Fetch Historical Data -----------
rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
mt5.shutdown()

# ----------- Prepare Data -----------
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)
df_plot = df[['open', 'high', 'low', 'close', 'tick_volume']].copy()
df_plot.columns = ['open', 'high', 'low', 'close', 'volume']

# ----------- Detect Supports and Resistances -----------
def find_swing_levels(df, window=10):
    supports = []
    resistances = []
    for i in range(window, len(df) - window):
        low = df['low'].iloc[i]
        high = df['high'].iloc[i]
        # Support
        if all(low < df['low'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            supports.append(low)
        # Resistance
        if all(high > df['high'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            resistances.append(high)
    return supports, resistances

supports_raw, resistances_raw = find_swing_levels(df_plot)

# ----------- Group into Zones -----------
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

support_zones = group_zones(supports_raw, threshold=2.0)
resistance_zones = group_zones(resistances_raw, threshold=2.0)

df['EMA'] = df['close'].ewm(span=200).mean()


# ----------- Plot with Support & Resistance Zones -----------
apds = []

apds.append(mpf.make_addplot(df['EMA'], color='blue', width=1))


# Plot supports
for low, high in support_zones[-3:]:  # Limit to last 5 zones for clarity
    apds.append(mpf.make_addplot([low] * len(df_plot), color='green', linestyle='dotted'))
    plt.axhspan(low, high, color='green', alpha=0.15)
    print('support -- ',low)
    percent_change = ((low - df.iloc[-1].close) / df.iloc[-1].close) * 100
    print(f'Price is {round(percent_change*100,2)} % far from Support')

# Plot resistances
for low, high in resistance_zones[-3:]:
    apds.append(mpf.make_addplot([high] * len(df_plot), color='red', linestyle='dotted'))
    plt.axhspan(low, high, color='red', alpha=0.15)
    print('Resistance -- ', high)
    percent_change = (( high - df.iloc[-1].close) / df.iloc[-1].close) * 100
    print(f'Price is {round(percent_change*100,2)} % far from Resistance')

print("EMA DIFF --->> ", (( df.iloc[-1].EMA - df.iloc[-1].close) / df.iloc[-1].close) * 100 * 100)



# Plot candlestick chart
mpf.plot(
    df_plot,
    type='candle',
    style='yahoo',
    title='Support & Resistance Zones - '+symbol,
    addplot=apds,
    volume=False,
    figsize=(14, 7)
)
