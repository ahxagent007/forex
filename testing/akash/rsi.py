import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mt5_utils import get_data

# Sample data
data = get_data('EURUSD')
print(data.columns)


def calculate_rsi(data, window):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# Calculate the 14-period RSI
data['RSI'] = calculate_rsi(data, 14)

# Generate signals
data['signal'] = 0
data['signal'][data['RSI'] < 30] = 1  # Buy signal
data['signal'][data['RSI'] > 70] = -1  # Sell signal

# Plotting the results
plt.figure(figsize=(14, 7))

plt.subplot(2, 1, 1)
plt.plot(data['time'], data['close'], label='Close Price')
plt.title('Close Price and RSI')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(data['time'], data['RSI'], label='RSI', color='orange')
plt.axhline(40, linestyle='--', alpha=0.5, color='red')
plt.axhline(60, linestyle='--', alpha=0.5, color='red')
plt.legend()

plt.show()

# Display the data with RSI and signals
print(data[['time', 'close', 'RSI', 'signal']])
