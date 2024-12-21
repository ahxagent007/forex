import pandas as pd
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
from mt5_utils import get_live_data, initialize_mt5
import time

def identify_trend_points(df):
    """
    Identifies Higher Highs (HH), Higher Lows (HL), Lower Highs (LH), and Lower Lows (LL) in a DataFrame.

    :param df: DataFrame containing 'close' column for prices
    :return: DataFrame with 'Structure' column indicating HH, HL, LH, or LL
    """
    df['Structure'] = None  # Initialize a new column for trend points

    for i in range(2, len(df)):
        # Higher High (HH)
        if df['close'][i] > df['close'][i - 1] and df['close'][i - 1] > df['close'][i - 2]:
            df.loc[i, 'Structure'] = 'HH'
        # Higher Low (HL)
        elif df['close'][i - 1] < df['close'][i - 2] and df['close'][i] > df['close'][i - 1]:
            df.loc[i, 'Structure'] = 'HL'
        # Lower High (LH)
        elif df['close'][i] < df['close'][i - 1] and df['close'][i - 1] < df['close'][i - 2]:
            df.loc[i, 'Structure'] = 'LH'
        # Lower Low (LL)
        elif df['close'][i - 1] > df['close'][i - 2] and df['close'][i] < df['close'][i - 1]:
            df.loc[i, 'Structure'] = 'LL'

    return df

def determine_market_trend(df):
    """
    Determines if the market is bullish or bearish based on trend points.

    :param df: DataFrame containing 'Structure' column
    :return: String indicating market trend
    """
    recent_trends = df['Structure'].dropna().tail(4).tolist()  # Get the last 4 trend points

    if recent_trends.count('HH') + recent_trends.count('HL') > recent_trends.count('LH') + recent_trends.count('LL'):
        return "Bullish"
    elif recent_trends.count('LH') + recent_trends.count('LL') > recent_trends.count('HH') + recent_trends.count('HL'):
        return "Bearish"
    else:
        return "Sideways"

def plot_trend_points(df):
    """
    Plots the price data with HH, HL, LH, and LL highlighted.

    :param df: DataFrame containing 'time', 'close', and 'Structure'
    """
    plt.figure(figsize=(12, 6))

    # Plot the close prices
    plt.plot(df['time'], df['close'], label='Close Price', color='blue', linewidth=1.5)

    # Highlight HH, HL, LH, and LL points
    hh_points = df[df['Structure'] == 'HH']
    hl_points = df[df['Structure'] == 'HL']
    lh_points = df[df['Structure'] == 'LH']
    ll_points = df[df['Structure'] == 'LL']

    plt.scatter(hh_points['time'], hh_points['close'], color='green', label='Higher High (HH)', marker='^', s=100)
    plt.scatter(hl_points['time'], hl_points['close'], color='orange', label='Higher Low (HL)', marker='v', s=100)
    plt.scatter(lh_points['time'], lh_points['close'], color='purple', label='Lower High (LH)', marker='^', s=100)
    plt.scatter(ll_points['time'], ll_points['close'], color='red', label='Lower Low (LL)', marker='v', s=100)

    plt.title('Price Chart with HH, HL, LH, and LL')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()



initialize_mt5()

while True:
    #time.sleep(10)
    # Convert data to a pandas DataFrame
    symbol = 'XAUUSD'
    symbol_list = ['XAUUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY', 'GBPJPY']

    for symbol in symbol_list:
        time.sleep(1)
        print(symbol)

        time_frame = 'M1'
        df_m1 = get_live_data(symbol=symbol, time_frame='H4', prev_n_candles=50)
        df_m5 = get_live_data(symbol=symbol, time_frame='D1', prev_n_candles=50)
        df_m15 = get_live_data(symbol=symbol, time_frame='W1', prev_n_candles=50)

        df_m1['time'] = pd.to_datetime(df_m1['time'], unit='s')  # Convert time to datetime
        df_m5['time'] = pd.to_datetime(df_m5['time'], unit='s')  # Convert time to datetime
        df_m15['time'] = pd.to_datetime(df_m15['time'], unit='s')  # Convert time to datetime

        # Identify HH and HL
        df_m1 = identify_trend_points(df_m1)
        df_m5 = identify_trend_points(df_m5)
        df_m15 = identify_trend_points(df_m15)

        # Display the results
        #print(df[df['Structure'].notnull()])  # Print only rows with HH or HL

        time.sleep(1)
        # Determine market trend
        market_trend = determine_market_trend(df_m1)
        print(f"H4 The market trend is: {market_trend}")

        market_trend = determine_market_trend(df_m5)
        print(f"D1 The market trend is: {market_trend}")

        market_trend = determine_market_trend(df_m15)
        print(f"W1 The market trend is: {market_trend}")

        print('------------------------------------')



