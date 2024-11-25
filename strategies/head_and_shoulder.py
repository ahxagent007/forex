from mt5_utils import get_live_data, initialize_mt5
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# Function to check Head and Shoulders pattern
def is_head_and_shoulders(peaks, valleys, prices):
    if len(peaks) < 3 or len(valleys) < 2:
        return False, None

    for i in range(1, len(peaks) - 1):
        # Ensure there are two shoulders and one head
        left_peak, head, right_peak = peaks[i - 1], peaks[i], peaks[i + 1]
        left_valley = valleys[valleys < head][-1] if len(valleys[valleys < head]) > 0 else None
        right_valley = valleys[valleys > head][0] if len(valleys[valleys > head]) > 0 else None

        if left_valley is None or right_valley is None:
            continue

        # Check for Head and Shoulders structure
        if (
            prices[left_peak] < prices[head]
            and prices[right_peak] < prices[head]  # Head is higher than shoulders
            and abs(prices[left_peak] - prices[right_peak]) < 0.03 * prices[head]  # Shoulders roughly equal
            and prices[left_valley] > prices[left_peak]
            and prices[right_valley] > prices[right_peak]
        ):
            return True, (left_peak, head, right_peak, left_valley, right_valley)

    return False, None

def detect_HAS(data):
    # Load forex or stock data (CSV with 'Date', 'Close' columns)
    data['Index'] = range(len(data))

    # Ensure data has the correct format
    if 'close' not in data.columns:
        raise ValueError("Data must contain a 'Close' column.")

    # Parameters for peak detection
    PEAK_DISTANCE = 10  # Minimum distance between peaks
    PEAK_PROMINENCE = 0.01  # Minimum prominence of peaks

    # Find peaks (potential "shoulders" and "head")
    peaks, _ = find_peaks(data['close'], distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE)

    # Find valleys (inverse peaks for "neckline")
    valleys, _ = find_peaks(-data['close'], distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE)

    # Check for Head and Shoulders pattern
    has_hs, pattern_points = is_head_and_shoulders(peaks, valleys, data['close'])

    if has_hs:
        print("Head and Shoulders pattern detected!")
        left_peak, head, right_peak, left_valley, right_valley = pattern_points

        # Plot the data and pattern
        plt.figure(figsize=(12, 6))
        plt.plot(data['Index'], data['close'], label='Close Price')
        plt.scatter(peaks, data['close'].iloc[peaks], color='red', label='Peaks (Shoulders/Head)', zorder=5)
        plt.scatter(valleys, data['close'].iloc[valleys], color='green', label='Valleys (Neckline)', zorder=5)

        # Highlight the pattern
        plt.scatter(
            [left_peak, head, right_peak],
            data['close'].iloc[[left_peak, head, right_peak]],
            color='purple', label='Head and Shoulders'
        )
        plt.plot(
            [left_valley, right_valley],
            data['close'].iloc[[left_valley, right_valley]],
            color='blue', linestyle='--', label='Neckline'
        )

        plt.title('Head and Shoulders Pattern')
        plt.xlabel('Index')
        plt.ylabel('Price')
        plt.legend()
        plt.grid()
        plt.show()
    else:
        #print("No Head and Shoulders pattern detected.")
        None


import pandas as pd
import numpy as np


def detect_head_shoulder(df, window=3):
    # Define the rolling window
    roll_window = window
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['high'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['low'].rolling(window=roll_window).min()
    # Create a boolean mask for Head and Shoulder pattern
    mask_head_shoulder = ((df['high_roll_max'] > df['high'].shift(1)) & (df['high_roll_max'] > df['high'].shift(-1)) & (
                df['high'] < df['high'].shift(1)) & (df['high'] < df['high'].shift(-1)))
    # Create a boolean mask for Inverse Head and Shoulder pattern
    mask_inv_head_shoulder = ((df['low_roll_min'] < df['low'].shift(1)) & (df['low_roll_min'] < df['low'].shift(-1)) & (
                df['low'] > df['low'].shift(1)) & (df['low'] > df['low'].shift(-1)))
    # Create a new column for Head and Shoulder and its inverse pattern and populate it using the boolean masks
    df['head_shoulder_pattern'] = np.nan
    df.loc[mask_head_shoulder, 'head_shoulder_pattern'] = 'Head and Shoulder'
    df.loc[mask_inv_head_shoulder, 'head_shoulder_pattern'] = 'Inverse Head and Shoulder'
    return df
    # return not df['head_shoulder_pattern'].isna().any().item()


def detect_multiple_tops_bottoms(df, window=3):
    # Define the rolling window
    roll_window = window
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['High'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['Low'].rolling(window=roll_window).min()
    df['close_roll_max'] = df['Close'].rolling(window=roll_window).max()
    df['close_roll_min'] = df['Close'].rolling(window=roll_window).min()
    # Create a boolean mask for multiple top pattern
    mask_top = (df['high_roll_max'] >= df['High'].shift(1)) & (df['close_roll_max'] < df['Close'].shift(1))
    # Create a boolean mask for multiple bottom pattern
    mask_bottom = (df['low_roll_min'] <= df['Low'].shift(1)) & (df['close_roll_min'] > df['Close'].shift(1))
    # Create a new column for multiple top bottom pattern and populate it using the boolean masks
    df['multiple_top_bottom_pattern'] = np.nan
    df.loc[mask_top, 'multiple_top_bottom_pattern'] = 'Multiple Top'
    df.loc[mask_bottom, 'multiple_top_bottom_pattern'] = 'Multiple Bottom'
    return df


def calculate_support_resistance(df, window=3):
    # Define the rolling window
    roll_window = window
    # Set the number of standard deviation
    std_dev = 2
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['High'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['Low'].rolling(window=roll_window).min()
    # Calculate the mean and standard deviation for High and Low
    mean_high = df['High'].rolling(window=roll_window).mean()
    std_high = df['High'].rolling(window=roll_window).std()
    mean_low = df['Low'].rolling(window=roll_window).mean()
    std_low = df['Low'].rolling(window=roll_window).std()
    # Create a new column for support and resistance
    df['support'] = mean_low - std_dev * std_low
    df['resistance'] = mean_high + std_dev * std_high
    return df


def detect_triangle_pattern(df, window=3):
    # Define the rolling window
    roll_window = window
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['High'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['Low'].rolling(window=roll_window).min()
    # Create a boolean mask for ascending triangle pattern
    mask_asc = (df['high_roll_max'] >= df['High'].shift(1)) & (df['low_roll_min'] <= df['Low'].shift(1)) & (
                df['Close'] > df['Close'].shift(1))
    # Create a boolean mask for descending triangle pattern
    mask_desc = (df['high_roll_max'] <= df['High'].shift(1)) & (df['low_roll_min'] >= df['Low'].shift(1)) & (
                df['Close'] < df['Close'].shift(1))
    # Create a new column for triangle pattern and populate it using the boolean masks
    df['triangle_pattern'] = np.nan
    df.loc[mask_asc, 'triangle_pattern'] = 'Ascending Triangle'
    df.loc[mask_desc, 'triangle_pattern'] = 'Descending Triangle'
    return df


def detect_wedge(df, window=3):
    # Define the rolling window
    roll_window = window
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['High'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['Low'].rolling(window=roll_window).min()
    df['trend_high'] = df['High'].rolling(window=roll_window).apply(
        lambda x: 1 if (x[-1] - x[0]) > 0 else -1 if (x[-1] - x[0]) < 0 else 0)
    df['trend_low'] = df['Low'].rolling(window=roll_window).apply(
        lambda x: 1 if (x[-1] - x[0]) > 0 else -1 if (x[-1] - x[0]) < 0 else 0)
    # Create a boolean mask for Wedge Up pattern
    mask_wedge_up = (df['high_roll_max'] >= df['High'].shift(1)) & (df['low_roll_min'] <= df['Low'].shift(1)) & (
                df['trend_high'] == 1) & (df['trend_low'] == 1)
    # Create a boolean mask for Wedge Down pattern
    # Create a boolean mask for Wedge Down pattern
    mask_wedge_down = (df['high_roll_max'] <= df['High'].shift(1)) & (df['low_roll_min'] >= df['Low'].shift(1)) & (
                df['trend_high'] == -1) & (df['trend_low'] == -1)
    # Create a new column for Wedge Up and Wedge Down pattern and populate it using the boolean masks
    df['wedge_pattern'] = np.nan
    df.loc[mask_wedge_up, 'wedge_pattern'] = 'Wedge Up'
    df.loc[mask_wedge_down, 'wedge_pattern'] = 'Wedge Down'
    return df


def detect_channel(df, window=3):
    # Define the rolling window
    roll_window = window
    # Define a factor to check for the range of channel
    channel_range = 0.1
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['High'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['Low'].rolling(window=roll_window).min()
    df['trend_high'] = df['High'].rolling(window=roll_window).apply(
        lambda x: 1 if (x[-1] - x[0]) > 0 else -1 if (x[-1] - x[0]) < 0 else 0)
    df['trend_low'] = df['Low'].rolling(window=roll_window).apply(
        lambda x: 1 if (x[-1] - x[0]) > 0 else -1 if (x[-1] - x[0]) < 0 else 0)
    # Create a boolean mask for Channel Up pattern
    mask_channel_up = (df['high_roll_max'] >= df['High'].shift(1)) & (df['low_roll_min'] <= df['Low'].shift(1)) & (
                df['high_roll_max'] - df['low_roll_min'] <= channel_range * (
                    df['high_roll_max'] + df['low_roll_min']) / 2) & (df['trend_high'] == 1) & (df['trend_low'] == 1)
    # Create a boolean mask for Channel Down pattern
    mask_channel_down = (df['high_roll_max'] <= df['High'].shift(1)) & (df['low_roll_min'] >= df['Low'].shift(1)) & (
                df['high_roll_max'] - df['low_roll_min'] <= channel_range * (
                    df['high_roll_max'] + df['low_roll_min']) / 2) & (df['trend_high'] == -1) & (df['trend_low'] == -1)
    # Create a new column for Channel Up and Channel Down pattern and populate it using the boolean masks
    df['channel_pattern'] = np.nan
    df.loc[mask_channel_up, 'channel_pattern'] = 'Channel Up'
    df.loc[mask_channel_down, 'channel_pattern'] = 'Channel Down'
    return df


def detect_double_top_bottom(df, window=3, threshold=0.05):
    # Define the rolling window
    roll_window = window
    # Define a threshold to check for the range of pattern
    range_threshold = threshold

    # Create a rolling window for High and Low
    df['high_roll_max'] = df['High'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['Low'].rolling(window=roll_window).min()

    # Create a boolean mask for Double Top pattern
    mask_double_top = (df['high_roll_max'] >= df['High'].shift(1)) & (df['high_roll_max'] >= df['High'].shift(-1)) & (
                df['High'] < df['High'].shift(1)) & (df['High'] < df['High'].shift(-1)) & (
                                  (df['High'].shift(1) - df['Low'].shift(1)) <= range_threshold * (
                                      df['High'].shift(1) + df['Low'].shift(1)) / 2) & (
                                  (df['High'].shift(-1) - df['Low'].shift(-1)) <= range_threshold * (
                                      df['High'].shift(-1) + df['Low'].shift(-1)) / 2)
    # Create a boolean mask for Double Bottom pattern
    mask_double_bottom = (df['low_roll_min'] <= df['Low'].shift(1)) & (df['low_roll_min'] <= df['Low'].shift(-1)) & (
                df['Low'] > df['Low'].shift(1)) & (df['Low'] > df['Low'].shift(-1)) & (
                                     (df['High'].shift(1) - df['Low'].shift(1)) <= range_threshold * (
                                         df['High'].shift(1) + df['Low'].shift(1)) / 2) & (
                                     (df['High'].shift(-1) - df['Low'].shift(-1)) <= range_threshold * (
                                         df['High'].shift(-1) + df['Low'].shift(-1)) / 2)

    # Create a new column for Double Top and Double Bottom pattern and populate it using the boolean masks
    df['double_pattern'] = np.nan
    df.loc[mask_double_top, 'double_pattern'] = 'Double Top'
    df.loc[mask_double_bottom, 'double_pattern'] = 'Double Bottom'

    return df


def detect_trendline(df, window=2):
    # Define the rolling window
    roll_window = window
    # Create new columns for the linear regression slope and y-intercept
    df['slope'] = np.nan
    df['intercept'] = np.nan

    for i in range(window, len(df)):
        x = np.array(range(i - window, i))
        y = df['Close'][i - window:i]
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        df.at[df.index[i], 'slope'] = m
        df.at[df.index[i], 'intercept'] = c

    # Create a boolean mask for trendline support
    mask_support = df['slope'] > 0

    # Create a boolean mask for trendline resistance
    mask_resistance = df['slope'] < 0

    # Create new columns for trendline support and resistance
    df['support'] = np.nan
    df['resistance'] = np.nan

    # Populate the new columns using the boolean masks
    df.loc[mask_support, 'support'] = df['Close'] * df['slope'] + df['intercept']
    df.loc[mask_resistance, 'resistance'] = df['Close'] * df['slope'] + df['intercept']

    return df


def find_pivots(df):
    # Calculate differences between consecutive highs and lows
    high_diffs = df['high'].diff()
    low_diffs = df['low'].diff()

    # Find higher high
    higher_high_mask = (high_diffs > 0) & (high_diffs.shift(-1) < 0)

    # Find lower low
    lower_low_mask = (low_diffs < 0) & (low_diffs.shift(-1) > 0)

    # Find lower high
    lower_high_mask = (high_diffs < 0) & (high_diffs.shift(-1) > 0)

    # Find higher low
    higher_low_mask = (low_diffs > 0) & (low_diffs.shift(-1) < 0)

    # Create signals column
    df['signal'] = ''
    df.loc[higher_high_mask, 'signal'] = 'HH'
    df.loc[lower_low_mask, 'signal'] = 'LL'
    df.loc[lower_high_mask, 'signal'] = 'LH'
    df.loc[higher_low_mask, 'signal'] = 'HL'

    return df


def run_HS():
    initialize_mt5()

    symbol = 'XAUUSD'
    time_frame = 'M1'
    max_candle = 50000
    data = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=max_candle)
    print(data.shape)
    for i in range(0, int(max_candle/100)):
        n = i
        per = 100
        start = n * per
        end = start + per
        #print(start, end)
        temp_data = data.loc[start:end, :]
        print(temp_data.shape)
        detect_HAS(temp_data)


initialize_mt5()

symbol = 'XAUUSD'
time_frame = 'M1'
max_candle = 1000
data = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=max_candle)

df = detect_head_shoulder(data)
