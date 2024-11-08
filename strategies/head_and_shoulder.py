import pandas as pd
import matplotlib.pyplot as plt

# Load data
from mt5_utils import get_live_data, initialize_mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

initialize_mt5()

symbol = 'XAUUSD'
time_frame = 'H1'
data = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=1000)
data.set_index('time', inplace=True)


# Identify peaks and troughs with error handling
def find_head_and_shoulders(data):
    # Find all peaks in the close price data
    peaks, _ = find_peaks(data['close'], distance=5)
    troughs, _ = find_peaks(-data['close'], distance=5)

    # Convert peaks and troughs to a list of points
    peaks_prices = data['close'].iloc[peaks]
    troughs_prices = data['close'].iloc[troughs]

    # Initialize empty list to store valid patterns
    patterns = []

    # Loop through peaks to identify potential head and shoulders
    for i in range(1, len(peaks) - 1):
        # Check if indices are in bounds
        if peaks[i - 1] < len(data) and peaks[i + 1] < len(data):
            left_shoulder = peaks[i - 1]
            head = peaks[i]
            right_shoulder = peaks[i + 1]

            # Validate head and shoulders pattern
            if (data['close'].iloc[left_shoulder] < data['close'].iloc[head] and
                    data['close'].iloc[right_shoulder] < data['close'].iloc[head] and
                    np.isclose(data['close'].iloc[left_shoulder], data['close'].iloc[right_shoulder], atol=0.01)):
                patterns.append((left_shoulder, head, right_shoulder))

    return patterns, peaks_prices, troughs_prices


# Run the head and shoulders detection
patterns, peaks_prices, troughs_prices = find_head_and_shoulders(data)

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(data['close'], label='Close Price', color='blue')
plt.plot(peaks_prices, 'ro', label='Peaks')  # Mark peaks
plt.plot(troughs_prices, 'go', label='Troughs')  # Mark troughs

# Mark identified head and shoulders patterns
for (left, head, right) in patterns:
    plt.plot(data.index[[left, head, right]], data['close'].iloc[[left, head, right]], 'r-', linewidth=2)

plt.title('Forex Price with Potential Head and Shoulders Pattern')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()
plt.show()