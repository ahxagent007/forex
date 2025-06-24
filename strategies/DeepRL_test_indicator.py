import pickle

import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from mt5_utils import get_live_data, initialize_mt5

# === Load data and indicators ===
initialize_mt5()
SYMBOL = 'EURUSD'
time_frame = 'M5'
df = get_live_data(symbol=SYMBOL, time_frame=time_frame, prev_n_candles=30000)

# === Add indicators ===
df.ta.rsi(length=14, append=True)

df.ta.macd(append=True)
df.ta.adx(length=14, append=True)
df.ta.ema(length=50, append=True)
df['EMA_DIFF'] = df['EMA_50'] - df['close']

df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

# === Normalize (same as during training) ===
#features = ['close', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'ADX_14']
# feature_means = df[features].mean()
# feature_stds = df[features].std()
# df[features] = (df[features] - feature_means) / feature_stds

# Load from file
with open("models/feature_stats_{0}_{1}.pkl".format(SYMBOL, time_frame), "rb") as f:
    stats = pickle.load(f)

feature_means = stats["mean"]
feature_stds = stats["std"]
features = stats['features']

df[features] = (df[features] - feature_means) / feature_stds

print({"mean": feature_means, "std": feature_stds, "features": features})
print("✅ Feature stats loaded!")


# === Load trained model ===
model = PPO.load("models/ppo_forex_model_indicator_"+SYMBOL+"_"+time_frame)
print("✅ Model loaded!")

# === Prepare logging ===
window_size = 50
buy_signals = []
sell_signals = []
actions = []

## BALANCE
balance = 10
position = 0
entry_price = 0
equity_curve = []

# === Prediction loop ===
for i in range(window_size, len(df)):
    row = df.iloc[i]
    obs = np.array([
        row['close'],
        row['RSI_14'],
        row['MACD_12_26_9'],
        row['MACDh_12_26_9'],
        row['MACDs_12_26_9'],
        row['ADX_14'],
        row['EMA_DIFF']
    ], dtype=np.float32)#.reshape(1, -1)

    action, _ = model.predict(obs, deterministic=True)
    actions.append(action)

    if action == 1:
        buy_signals.append(row['close'])
        sell_signals.append(np.nan)
    elif action == 2:
        buy_signals.append(np.nan)
        sell_signals.append(row['close'])
    else:
        buy_signals.append(np.nan)
        sell_signals.append(np.nan)

    ## Balance
    price = row['close']

    if action == 1 and position == 0:
        position = 1
        entry_price = price
    elif action == 2 and position == 0:
        position = -1
        entry_price = price
    elif action == 1 and position == -1:
        balance += entry_price - price
        position = 0
    elif action == 2 and position == 1:
        balance += price - entry_price
        position = 0

    # unrealized PnL
    unrealized = (price - entry_price) if position == 1 else (entry_price - price) if position == -1 else 0
    equity_curve.append(balance + unrealized)

# === Trim and attach signals for plotting ===
df = df.iloc[window_size:].copy()
df['Buy'] = buy_signals
df['Sell'] = sell_signals
df['Action'] = actions

# === Plotting ===
plt.figure(figsize=(14, 6))
plt.plot(df['close'] * feature_stds['close'] + feature_means['close'], label='Close Price', color='blue', alpha=0.5)
plt.scatter(df.index, np.array(df['Buy']) * feature_stds['close'] + feature_means['close'], label='Buy Signal', marker='^', color='green', s=80)
plt.scatter(df.index, np.array(df['Sell']) * feature_stds['close'] + feature_means['close'], label='Sell Signal', marker='v', color='red', s=80)
plt.title("📈 PPO Buy/Sell Signals")
plt.xlabel("Time Step")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# Plot profit curve
plt.figure(figsize=(12,4))
plt.plot(equity_curve, label="Equity Curve", color='purple')
plt.title("Equity Curve (Simulated PnL)")
plt.xlabel("Step")
plt.ylabel("Equity")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

