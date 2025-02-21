import pandas as pd
import MetaTrader5 as mt5
import matplotlib.pyplot as plt

from common_functions import check_duplicate_orders, write_json
from xian import cumulative_lot
from mt5_utils import get_live_data, initialize_mt5, convert_price_diff_to_pips, trade_order
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


def detect_strong_engulfing_candle(open_prev, close_prev, high_prev, low_prev, open_curr, close_curr, high_curr,
                                   low_curr):
    """
    Detect strong Bullish or Bearish Engulfing candlestick patterns with a significant body size.
    :param open_prev: Previous candle open price.
    :param close_prev: Previous candle close price.
    :param high_prev: Previous candle high price.
    :param low_prev: Previous candle low price.
    :param open_curr: Current candle open price.
    :param close_curr: Current candle close price.
    :param high_curr: Current candle high price.
    :param low_curr: Current candle low price.
    :return: 'Strong Bullish Engulfing', 'Strong Bearish Engulfing', or 'None'
    """
    body_prev = abs(high_prev - low_prev)
    body_curr = abs(close_curr - open_curr)

    if open_curr < close_prev and close_curr > open_prev and close_curr > open_curr and body_curr > 1.1 * body_prev:
        return "Bullish_Engulfing"
    elif open_curr > close_prev and close_curr < open_prev and close_curr < open_curr and body_curr > 1.1 * body_prev:
        return "Bearish_Engulfing"
    else:
        return "None"

initialize_mt5()

while True:

    #symbol_list = ['XAUUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY', 'GBPJPY']
    symbol_list = ['NZDCAD', 'AUDUSD', 'NZDUSD', 'EURGBP', 'USDCAD', 'USDJPY', 'EURUSD', 'GBPAUD', 'GBPCAD', 'AUDCAD', 'EURJPY',
                   'CADJPY', 'GBPJPY', 'CHFJPY', 'GBPUSD', 'EURNZD', 'GBPCHF', 'EURAUD', 'AUDJPY', 'GBPNZD', 'EURCAD', 'USDCHF', 'XAUUSD']

    for symbol in symbol_list:
        time.sleep(2)
        skip_min = 50
        json_file_name = 'fx_alex'
        running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                                   json_file_name=json_file_name)
        if running_trade_status:
            #print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
            continue

        df_h2 = get_live_data(symbol=symbol, time_frame='H2', prev_n_candles=50)
        df_h4 = get_live_data(symbol=symbol, time_frame='H4', prev_n_candles=50)
        df_d1 = get_live_data(symbol=symbol, time_frame='D1', prev_n_candles=50)
        df_w1 = get_live_data(symbol=symbol, time_frame='W1', prev_n_candles=50)

        df_h2['time'] = pd.to_datetime(df_h2['time'], unit='s')  # Convert time to datetime
        df_h4['time'] = pd.to_datetime(df_h4['time'], unit='s')  # Convert time to datetime
        df_d1['time'] = pd.to_datetime(df_d1['time'], unit='s')  # Convert time to datetime
        df_w1['time'] = pd.to_datetime(df_w1['time'], unit='s')  # Convert time to datetime

        # Identify HH and HL
        df_h2 = identify_trend_points(df_h2)
        df_h4 = identify_trend_points(df_h4)
        df_d1 = identify_trend_points(df_d1)
        df_w1 = identify_trend_points(df_w1)

        # Display the results
        #print(df[df['Structure'].notnull()])  # Print only rows with HH or HL

        # Determine market trend
        market_trend_h4 = determine_market_trend(df_h4)
        market_trend_d1 = determine_market_trend(df_d1)
        market_trend_w1 = determine_market_trend(df_w1)

        # print('------------------------------------')
        # print(symbol)
        # print(f"H4 The market trend is: {market_trend_h4}")
        # print(f"D1 The market trend is: {market_trend_d1}")
        # print(f"W1 The market trend is: {market_trend_w1}")
        # print('------------------------------------')

        market_signal = None
        if (market_trend_w1 == market_trend_d1 == market_trend_h4 == 'Bullish') or (market_trend_w1 == 'Bullish'
                                                                                    and market_trend_d1 == 'Bullish' and market_trend_h4 == 'Bearish'):
            market_signal = 'buy'
        elif (market_trend_w1 == market_trend_d1 == market_trend_h4 == 'Bearish') or (market_trend_w1 == 'Bearish'
                                                                                      and market_trend_d1 == 'Bearish' and market_trend_h4 == 'Bullish'):
            market_signal = 'sell'




        ## Check for Engulfing at 2hr
        engulf_pattern = detect_strong_engulfing_candle(
            open_prev = df_h2['open'].iloc[-3],
            close_prev = df_h2['close'].iloc[-3],
            high_prev = df_h2['high'].iloc[-3],
            low_prev = df_h2['low'].iloc[-3],
            open_curr = df_h2['open'].iloc[-2],
            close_curr = df_h2['close'].iloc[-2],
            high_curr = df_h2['high'].iloc[-2],
            low_curr = df_h2['low'].iloc[-2]
        )
        action = None
        if engulf_pattern == 'Bullish_Engulfing':
            action = 'buy'

        elif engulf_pattern == 'Bearish_Engulfing':
            action = 'sell'

        if action and market_signal:
            if action == market_signal:
                sl = 0
                if action == 'buy':

                    ## get the SL
                    sl_open = min(df_h2['open'].iloc[-1], df_h2['open'].iloc[-2], df_h2['open'].iloc[-3],
                                  df_h2['open'].iloc[-4], df_h2['open'].iloc[-5])
                    sl_close = min(df_h2['close'].iloc[-1], df_h2['close'].iloc[-2], df_h2['close'].iloc[-3],
                                   df_h2['close'].iloc[-4], df_h2['close'].iloc[-5])

                    print(sl_open, sl_close)
                    if sl_open < sl_close:
                        sl = abs(sl_open - df_h2['close'].iloc[-1])
                    else:
                        sl = abs(sl_close - df_h2['close'].iloc[-1])

                elif action == 'sell':
                    ## get the SL
                    sl_open = max(df_h2['open'].iloc[-1], df_h2['open'].iloc[-2], df_h2['open'].iloc[-3],
                                  df_h2['open'].iloc[-4], df_h2['open'].iloc[-5])
                    sl_close = max(df_h2['close'].iloc[-1], df_h2['close'].iloc[-2], df_h2['close'].iloc[-3],
                                   df_h2['close'].iloc[-4], df_h2['close'].iloc[-5])

                    print(sl_open, sl_close)

                    if sl_open > sl_close:
                        sl = abs(sl_open - df_h2['close'].iloc[-1])
                    else:
                        sl = abs(sl_close - df_h2['close'].iloc[-1])


                sl_pips = convert_price_diff_to_pips(symbol, sl)
                tp_pips = sl_pips * 1.1
                print('SL:TP -->', sl_pips, tp_pips)
                lot = cumulative_lot()

                ## TRADE
                trade_order(symbol=symbol, tp_point=tp_pips, sl_point=sl_pips, lot=lot, action=action, magic=True)
                write_json(json_dict=orders_json, json_file_name=json_file_name)




