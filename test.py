import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample historical price data
data = {
    'Date': pd.date_range(start='2023-01-01', periods=50, freq='T'),  # Minute data for 50 minutes
    'Open': [1.10, 1.11, 1.11, 1.12, 1.12, 1.13, 1.13, 1.14, 1.14, 1.15, 1.15, 1.14, 1.14, 1.13, 1.13, 1.12, 1.12, 1.11, 1.11, 1.10, 1.10, 1.09, 1.09, 1.08, 1.08, 1.07, 1.07, 1.06, 1.06, 1.05, 1.05, 1.04, 1.04, 1.03, 1.03, 1.02, 1.02, 1.01, 1.01, 1.00, 1.00, 0.99, 0.99, 0.98, 0.98, 0.97, 0.97, 0.96, 0.96, 0.95],
    'High': [1.11, 1.12, 1.12, 1.13, 1.13, 1.14, 1.14, 1.15, 1.15, 1.16, 1.16, 1.15, 1.15, 1.14, 1.14, 1.13, 1.13, 1.12, 1.12, 1.11, 1.11, 1.10, 1.10, 1.09, 1.09, 1.08, 1.08, 1.07, 1.07, 1.06, 1.06, 1.05, 1.05, 1.04, 1.04, 1.03, 1.03, 1.02, 1.02, 1.01, 1.01, 1.00, 1.00, 0.99, 0.99, 0.98, 0.98, 0.97, 0.97, 0.96],
    'Low': [1.09, 1.10, 1.10, 1.11, 1.11, 1.12, 1.12, 1.13, 1.13, 1.14, 1.14, 1.13, 1.13, 1.12, 1.12, 1.11, 1.11, 1.10, 1.10, 1.09, 1.09, 1.08, 1.08, 1.07, 1.07, 1.06, 1.06, 1.05, 1.05, 1.04, 1.04, 1.03, 1.03, 1.02, 1.02, 1.01, 1.01, 1.00, 1.00, 0.99, 0.99, 0.98, 0.98, 0.97, 0.97, 0.96, 0.96, 0.95, 0.95, 0.94],
    'Close': [1.11, 1.12, 1.12, 1.13, 1.13, 1.14, 1.14, 1.15, 1.15, 1.16, 1.16, 1.15, 1.15, 1.14, 1.14, 1.13, 1.13, 1.12, 1.12, 1.11, 1.11, 1.10, 1.10, 1.09, 1.09, 1.08, 1.08, 1.07, 1.07, 1.06, 1.06, 1.05, 1.05, 1.04, 1.04, 1.03, 1.03, 1.02, 1.02, 1.01, 1.01, 1.00, 1.00, 0.99, 0.99, 0.98, 0.98, 0.97, 0.97, 0.96]
}

df = pd.DataFrame(data)

# Function to identify the inside range
def identify_inside_range(df, lookback=5):
    for i in range(lookback, len(df)):
        recent_data = df.iloc[i-lookback:i]
        range_high = recent_data['High'].max()
        range_low = recent_data['Low'].min()
        current_close = df.iloc[i]['Close']
        if current_close > range_high:
            return 'Buy', df.iloc[i]['Date'], current_close, range_high, range_low
        elif current_close < range_low:
            return 'Sell', df.iloc[i]['Date'], current_close, range_high, range_low
    return None, None, None, None, None

# Get the inside range breakout signal
lookback_period = 5
signal, signal_date, signal_price, range_high, range_low = identify_inside_range(df, lookback=lookback_period)

# Display the result
if signal:
    print(f"Signal: {signal} on {signal_date} at price {signal_price}")
else:
    print("No breakout detected.")

# Define trade parameters
if signal:
    entry_price = signal_price
    stop_loss = range_low if signal == 'Buy' else range_high
    if signal == 'Buy':
        take_profit = entry_price + 2 * (entry_price - stop_loss)  # 1:2 risk-reward ratio
    elif signal == 'Sell':
        take_profit = entry_price - 2 * (stop_loss - entry_price)  # 1:2 risk-reward ratio

    print(f"Executing {signal} Trade at {entry_price}")
    print(f"Stop Loss set at {stop_loss}")
    print(f"Take Profit set at {take_profit}")

    # Plot the price data and the signal
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Close'], label='Close Price', marker='o')

    # Mark the range high and low
    plt.axhline(range_high, color='r', linestyle='--', label='Range High')
    plt.axhline(range_low, color='g', linestyle='--', label='Range Low')

    # Mark the breakout signal
    color = 'b' if signal == 'Buy' else 'r'
    plt.scatter(signal_date, signal_price, color=color, label=f'{signal} Signal', zorder=5)
    plt.annotate(f'{signal} Signal', (signal_date, signal_price), textcoords="offset points", xytext=(0,10), ha='center', fontsize=12, color=color)

    # Mark the stop loss and take profit levels
    plt.axhline(stop_loss, color='red', linestyle='--', label='Stop Loss')
    plt.axhline(take_profit, color='green', linestyle='--', label='Take Profit')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Inside Range Break Strategy')
    plt.legend()
    plt.grid(True)
    plt.show()
