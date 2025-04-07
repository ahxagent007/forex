import gym
import numpy as np
import pandas as pd
import pandas_ta as ta
from gym import spaces
from stable_baselines3 import PPO
import matplotlib.pyplot as plt
from mt5_utils import get_live_data, initialize_mt5

# === Global settings ===
window_size = 26

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

        # === Action and observation space ===
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32)

        self._add_indicators()
        self._normalize_data()

        # === Action counter ===
        self.action_counts = {0: 0, 1: 0, 2: 0}

    def _add_indicators(self):
        self.df.ta.rsi(length=14, append=True)
        self.df.ta.macd(append=True)
        self.df.ta.adx(length=14, append=True)
        self.df.dropna(inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    def _normalize_data(self):
        features = ['close', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'ADX_14']
        self.feature_means = self.df[features].mean()
        self.feature_stds = self.df[features].std()
        self.df[features] = (self.df[features] - self.feature_means) / self.feature_stds

    def _get_obs(self):
        row = self.df.iloc[self.current_step]
        obs = np.array([
            row['close'],
            row['RSI_14'],
            row['MACD_12_26_9'],
            row['MACDh_12_26_9'],
            row['MACDs_12_26_9'],
            row['ADX_14']
        ], dtype=np.float32)
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

        # === Trading logic ===
        if action == 1:  # Buy
            if self.position == 0:
                self.position = 1
                self.entry_price = price
            elif self.position == -1:
                reward = self.entry_price - price
                self.position = 0
        elif action == 2:  # Sell
            if self.position == 0:
                self.position = -1
                self.entry_price = price
            elif self.position == 1:
                reward = price - self.entry_price
                self.position = 0

        # === Reward shaping while holding ===
        if self.position == 1:
            reward += price - self.entry_price
        elif self.position == -1:
            reward += self.entry_price - price

        # Penalty for holding
        if action == 0:
            reward -= 0.01

        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            done = True
            print("Final Action Counts:", self.action_counts)

        obs = self._get_obs()

        return obs, reward, done, {}

# === Initialize and run training ===
initialize_mt5()
SYMBOL = 'EURUSD'
df = get_live_data(symbol=SYMBOL, time_frame='M5', prev_n_candles=99000)

env = ForexIndicatorEnv(df)

model = PPO("MlpPolicy", env, verbose=1, ent_coef=0.01)
model.learn(total_timesteps=1_000_000)

model.save("ppo_forex_model_indicator_"+SYMBOL)
print("✅ Model saved!")
