import MetaTrader5 as mt5
import gym
import numpy as np
import pandas as pd
import torch
from gym import spaces
from stable_baselines3 import PPO
import pandas as pd
import pandas_ta as ta


# Simulated price data (can be replaced with real Forex data)
from mt5_utils import initialize_mt5


def load_price_data():
    initialize_mt5()
    TIMEFRAME = mt5.TIMEFRAME_M5
    WINDOW_SIZE = 99000
    rates = mt5.copy_rates_from_pos('BTCUSD', TIMEFRAME, 0, WINDOW_SIZE)
    if rates is None or len(rates) < WINDOW_SIZE:
        raise Exception("Not enough data from MT5")
    df = pd.DataFrame(rates)
    return df

# === Custom Forex Trading Environment ===
class ForexTradingEnv(gym.Env):
    def __init__(self, df, window_size=100, initial_balance=1000):
        super(ForexTradingEnv, self).__init__()
        self.df = df.reset_index(drop=True)
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.action_space = spaces.Discrete(3)  # 0: Hold, 1: Buy, 2: Sell
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(window_size,), dtype=np.float32
        )
        self.reset()

    def reset(self):
        self.balance = self.initial_balance
        self.position = 0  # +1 = long, -1 = short, 0 = no position
        self.entry_price = 0
        self.current_step = self.window_size
        self.total_profit = 0
        return self._get_observation()

    def _get_observation(self):
        return self.df['close'].iloc[self.current_step - self.window_size:self.current_step].values.astype(np.float32)

    def step(self, action):
        price = self.df['close'].iloc[self.current_step]
        reward = 0

        if action == 1:  # Buy
            if self.position == 0:
                self.position = 1
                self.entry_price = price
            elif self.position == -1:  # closing short
                reward = self.entry_price - price
                self.total_profit += reward
                self.position = 0

        elif action == 2:  # Sell
            if self.position == 0:
                self.position = -1
                self.entry_price = price
            elif self.position == 1:  # closing long
                reward = price - self.entry_price
                self.total_profit += reward
                self.position = 0

        self.current_step += 1
        done = self.current_step >= len(self.df) - 1
        obs = self._get_observation()
        info = {"total_profit": self.total_profit}
        return obs, reward, done, info

# === Load Data and Train PPO Agent ===
if __name__ == "__main__":
    df = load_price_data()
    env = ForexTradingEnv(df)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=1_000_000)

    # Test the trained agent
    obs = env.reset()
    done = False
    total_reward = 0

    while not done:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward

    print("✅ Total test reward:", total_reward)
    print("📈 Total profit:", info['total_profit'])


    # Save the model
    model.save("ppo_forex_model_indicator")
    print("✅ Model saved!")

