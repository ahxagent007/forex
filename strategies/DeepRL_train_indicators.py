import pickle
import sys

import gym
import numpy as np
import pandas as pd
import pandas_ta as ta
from gym import spaces
from stable_baselines3 import PPO
import matplotlib.pyplot as plt
from mt5_utils import get_live_data, initialize_mt5

time_frame = 'M5'
SYMBOL = 'BTCUSD'
HISTORY_LENGTH = 2

initialize_mt5()

# === Global settings ===
window_size = 50

class ForexIndicatorEnv(gym.Env):
    def __init__(self, df, window_size=window_size, initial_balance=1000):
        super(ForexIndicatorEnv, self).__init__()

        self.df = df.copy()
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.current_step = window_size
        self.balance = initial_balance
        self.position = 0
        self.entry_price = 0

        self.history_length = HISTORY_LENGTH

        # === Action and observation space ===
        self.action_space = spaces.Discrete(3)
        #self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(7,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.history_length * 7,), dtype=np.float32
        )

        self._add_indicators()
        self._normalize_data()

        # === Action counter ===
        self.action_counts = {0: 0, 1: 0, 2: 0}

        self.last_action_step = -10


    def _add_indicators(self):
        self.df.ta.rsi(length=14, append=True)
        self.df.ta.macd(append=True)
        self.df.ta.adx(length=14, append=True)
        self.df.ta.ema(length=50, append=True)
        self.df['EMA_DIFF'] = self.df['EMA_50'] - self.df['close']

        self.df.dropna(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        #print(self.df.columns)
        #sys.exit()


    def _normalize_data(self):
        features = ['close', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'ADX_14', 'EMA_DIFF']
        self.feature_means = self.df[features].mean()
        self.feature_stds = self.df[features].std()
        self.df[features] = (self.df[features] - self.feature_means) / self.feature_stds


        # Save to file
        with open("models/feature_stats_{0}_{1}.pkl".format(SYMBOL, time_frame), "wb") as f:
            pickle.dump({"mean": self.feature_means, "std": self.feature_stds, "features": features}, f)
            print({"mean": self.feature_means, "std": self.feature_stds, "features": features})

        print("✅ Feature stats saved!")

        # print('self.feature_means', self.feature_means)
        # print('self.feature_stds', self.feature_stds)
        # print(self.df[features].iloc[-1])
    def _get_obs(self):
        # row = self.df.iloc[self.current_step]
        # obs = np.array([
        #     row['close'],
        #     row['RSI_14'],
        #     row['MACD_12_26_9'],
        #     row['MACDh_12_26_9'],
        #     row['MACDs_12_26_9'],
        #     row['ADX_14'],
        #     row['EMA_DIFF']
        # ], dtype=np.float32)
        # return obs
        data = self.df.iloc[self.current_step - self.history_length + 1: self.current_step + 1]
        obs = data[['close', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'ADX_14', 'EMA_DIFF']].values
        obs = obs.flatten().astype(np.float32)  # shape: (history_length * features,)
        return obs

    def reset(self):
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.position = 0
        self.entry_price = 0
        self.action_counts = {0: 0, 1: 0, 2: 0}
        return self._get_obs()


    def step(self, action):
        done = False
        reward = 0

        price = self.df.iloc[self.current_step]['close']

        # === Action logging ===
        self.action_counts[action] += 1

        reward_multiply = 10

        # === Trading logic ===
        if action == 1:  # Buy
            if self.position == 0:
                self.position = 1
                self.entry_price = price
            elif self.position == -1:
                reward = (self.entry_price - price) * reward_multiply
                self.position = 0
        elif action == 2:  # Sell
            if self.position == 0:
                self.position = -1
                self.entry_price = price
            elif self.position == 1:
                reward = (price - self.entry_price) * reward_multiply
                self.position = 0

        ##=== Reward shaping while holding ===
        if self.position == 1:
            reward += (price - self.entry_price)
        elif self.position == -1:
            reward += (self.entry_price - price)

        # Penalty for holding
        # if action == 0:
        #     reward -= 0.1

        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            done = True
            print("Final Action Counts:", self.action_counts)


        #print(f"Step: {self.current_step}, Reward: {reward}")

        obs = self._get_obs()

        return obs, reward, done, {}


# === Initialize and run training ===


symbol_list = []

#symbol_list = ['BTCUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'EURCHF', 'GBPCHF', 'AUDCHF', 'USDCHF','AUDCAD', 'NZDCAD', 'USDCAD', 'EURCAD',
#               'GBPCAD','EURNZD', 'EURGBP', 'EURAUD', 'GBPNZD', 'CADJPY',  'USDJPY', 'EURJPY', 'GBPJPY', 'CHFJPY', 'AUDJPY', 'XAUUSD' ]
symbol_list = ['EURUSD']

for SYMBOL in symbol_list:
    df = get_live_data(symbol=SYMBOL, time_frame=time_frame, prev_n_candles=99000)

    env = ForexIndicatorEnv(df)

    model = PPO("MlpPolicy", env, verbose=1, ent_coef=0.005,
                normalize_advantage=True,
                n_steps=2048,
                batch_size=64,
                gae_lambda=0.95,
                gamma=0.99,
                learning_rate=3e-4,
                vf_coef=0.25,
                max_grad_norm=0.5)

    model.learn(total_timesteps=10_000_000)


    model.save("models/ppo_forex_model_indicator_"+SYMBOL+"_"+time_frame)
    print(SYMBOL, " ✅ Model saved!")


# df = get_live_data(symbol=SYMBOL, time_frame=time_frame, prev_n_candles=99999).iloc[0: 95000]
#
# env = ForexIndicatorEnv(df)
#
# model = PPO("MlpPolicy", env, verbose=1, ent_coef=0.005,
#             normalize_advantage=True,
#             n_steps=2048,
#             batch_size=64,
#             gae_lambda=0.95,
#             gamma=0.99,
#             learning_rate=3e-4,
#             vf_coef=0.25,
#             max_grad_norm=0.5)
# model.learn(total_timesteps=50_000)
#
# model.save("models/ppo_forex_model_indicator_"+SYMBOL+"_"+time_frame)
# print(SYMBOL, " ✅ Model saved!")

###############################################################################################################
###############################################################################################################
###############################################################################################################
## TESTING MODEL
df = get_live_data(symbol=SYMBOL, time_frame=time_frame, prev_n_candles=5000)

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
    # obs = np.array([
    #     row['close'],
    #     row['RSI_14'],
    #     row['MACD_12_26_9'],
    #     row['MACDh_12_26_9'],
    #     row['MACDs_12_26_9'],
    #     row['ADX_14'],
    #     row['EMA_DIFF']
    # ], dtype=np.float32)#.reshape(1, -1)

    data = df.iloc[i - HISTORY_LENGTH + 1: i + 1]
    obs = data[['close', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'ADX_14', 'EMA_DIFF']].values
    obs = obs.flatten().astype(np.float32)  # shape: (history_length * features,)

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
        balance += (entry_price - price) * 100
        position = 0
    elif action == 2 and position == 1:
        balance += (price - entry_price) * 100
        position = 0

    # unrealized PnL
    unrealized = (price - entry_price)*100 if position == 1 else (entry_price - price)*100 if position == -1 else 0
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