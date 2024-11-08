import gym
from gym import spaces
import numpy as np
import pandas as pd
import ta  # For technical indicators
from stable_baselines3 import DQN

from mt5_utils import get_live_data
from xian import initialize_mt5


class ForexTradingEnv(gym.Env):
    def __init__(self, df, window_size=10, initial_balance=10000, slippage=0.0001):
        super(ForexTradingEnv, self).__init__()

        # Data and parameters
        self.df = df
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.slippage = slippage
        self.current_step = 0

        # Initialize trading metrics
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.position = 0
        self.entry_price = 0

        # Action and observation spaces
        self.action_space = spaces.Discrete(3)  # 0 = Hold, 1 = Buy, 2 = Sell
        self.observation_space = spaces.Box(low=-1, high=1, shape=(window_size, len(df.columns)), dtype=np.float32)

    def reset(self):
        # Reset trading metrics
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.position = 0
        self.current_step = self.window_size
        self.entry_price = 0

        return self._get_observation()

    def step(self, action):
        current_price = self.df['close'].iloc[self.current_step]
        reward = 0
        done = False

        # Apply action: 0 = Hold, 1 = Buy, 2 = Sell
        if action == 1 and self.position == 0:  # Buy action
            self.position = 1
            self.entry_price = current_price * (1 + self.slippage)

        elif action == 2 and self.position == 1:  # Sell action
            reward = (current_price - self.entry_price) * 100 - self.slippage
            self.position = 0
            self.balance += reward

        # Update net worth and move to the next step
        self.net_worth = self.balance + (self.position * (current_price - self.entry_price))
        self.current_step += 1
        done = self.current_step >= len(self.df) - 1

        # Compute observation and reward
        obs = self._get_observation()
        return obs, reward, done, {}

    def _get_observation(self):
        return np.array(self.df.iloc[self.current_step - self.window_size:self.current_step].values)

    def render(self, mode='human'):
        profit = self.net_worth - self.initial_balance
        print(f'Step: {self.current_step}, Net Worth: {self.net_worth:.2f}, Profit: {profit:.2f}')

def preprocess_data(df):
    # Normalize close prices and add technical indicators
    df['close'] = (df['close'] - df['close'].min()) / (df['close'].max() - df['close'].min())
    df['rsi'] = ta.momentum.rsi(df['close'], window=14) / 100  # Normalize RSI
    df['macd'] = ta.trend.macd_diff(df['close'])
    df = df.fillna(0)
    return df



def train_rl_model(df, total_timesteps=50000):
    df = preprocess_data(df)
    env = ForexTradingEnv(df, window_size=10)

    model = DQN('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    return model

def real_time_trading(model, df):
    df = preprocess_data(df)
    env = ForexTradingEnv(df, window_size=10)
    obs = env.reset()
    done = False

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _ = env.step(action)
        env.render()


initialize_mt5()
symbol = 'EURUSD'
time_frame = 'M1'
full_live_data = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=50000)
# print(full_live_data.shape)
# # Load your forex data
# df = full_live_data[0:40000]
#
# # Train the model
# model = train_rl_model(df, total_timesteps=50000)
#
# # Test the model on new data
# df_test = full_live_data[40000:50000]  # Replace with test data file
# real_time_trading(model, df_test)

full_live_data['symbol'] = 'EURUSD'
full_live_data.to_csv('eurusd_1m.csv')