import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
from hmmlearn import hmm
from sklearn.preprocessing import MinMaxScaler
from mt5_utils import get_data


# Initialize MT5 connection

# Define symbol and timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1

# Get historical data
df = get_data('EURUSD')

# Calculate returns and additional features
df['returns'] = df['close'].pct_change().dropna()
df['SMA'] = df['close'].rolling(window=20).mean()
df['EMA'] = df['close'].ewm(span=20, adjust=False).mean()
df.dropna(inplace=True)

# Normalize data
scaler = MinMaxScaler()
df[['close', 'returns', 'SMA', 'EMA']] = scaler.fit_transform(df[['close', 'returns', 'SMA', 'EMA']])

# Prepare data for HMM
features = df[['returns', 'SMA', 'EMA']].values

# Initialize and fit HMM
model = hmm.GaussianHMM(n_components=4, covariance_type="full", n_iter=1000)
model.fit(features)

# Predict hidden states
hidden_states = model.predict(features)

# Add hidden states to the dataframe
df['hidden_state'] = hidden_states

# Visualize the hidden states
import matplotlib.pyplot as plt

plt.figure(figsize=(15, 8))
for i in range(model.n_components):
    state = (hidden_states == i)
    plt.plot(df.index[state], df['close'][state], '.', label=f'State {i}')
plt.legend()
plt.title('Hidden States')
plt.show()

# Generate trading signals based on hidden states
signals = []
for i in range(1, len(hidden_states)):
    if hidden_states[i] == 0:
        signals.append('Buy')
    elif hidden_states[i] == 1:
        signals.append('Sell')
    else:
        signals.append('Hold')

# Add 'Hold' signal for the first entry
signals.insert(0, 'Hold')

# Add signals to the dataframe
df['signal'] = signals

# Display the dataframe with signals
print(df[['close', 'hidden_state', 'signal']].tail(20))

# Backtest the strategy
initial_balance = 10000
balance = initial_balance
position = 0  # 0 means no position, 1 means long position, -1 means short position

for i in range(1, len(df)):
    if df['signal'].iloc[i] == 'Buy' and position != 1:
        balance -= df['close'].iloc[i]
        position = 1
    elif df['signal'].iloc[i] == 'Sell' and position != -1:
        balance += df['close'].iloc[i]
        position = -1
    elif df['signal'].iloc[i] == 'Hold' and position == 1:
        balance += df['close'].iloc[i]
        position = 0
    elif df['signal'].iloc[i] == 'Hold' and position == -1:
        balance -= df['close'].iloc[i]
        position = 0

final_balance = balance + (df['close'].iloc[-1] * position)
print(f'Initial Balance: ${initial_balance}')
print(f'Final Balance: ${final_balance}')
print(f'Return: {((final_balance - initial_balance) / initial_balance) * 100:.2f}%')

