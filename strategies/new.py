import random
import time

from common_functions import check_duplicate_orders, write_json
from fx_alex import identify_trend_points, determine_market_trend
from mt5_utils import get_all_positions, trade_order_wo_tp_sl, close_position, initialize_mt5, get_live_data, \
    trade_order_magic, get_magic_number

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def detect_bos(data, lookback=5):
    data['Previous_High'] = data['high'].rolling(lookback).max().shift(1)
    data['Previous_Low'] = data['low'].rolling(lookback).min().shift(1)

    data['BOS_Up'] = (data['close'] > data['Previous_High'])
    data['BOS_Down'] = (data['close'] < data['Previous_Low'])

    data['BOS_Signal'] = np.where(data['BOS_Up'], 'Bullish BOS',
                                  np.where(data['BOS_Down'], 'Bearish BOS', 'No BOS'))
    return data

def plot_bos(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['close'], label='Close Price', color='blue')
    plt.plot(data.index, data['Previous_High'], label='Previous High', linestyle='--', color='green')
    plt.plot(data.index, data['Previous_Low'], label='Previous Low', linestyle='--', color='red')

    # Plot BOS signals
    bullish_bos = data[data['BOS_Signal'] == 'Bullish BOS']
    bearish_bos = data[data['BOS_Signal'] == 'Bearish BOS']
    plt.scatter(bullish_bos.index, bullish_bos['close'], marker='^', color='green', label='Bullish BOS', s=100)
    plt.scatter(bearish_bos.index, bearish_bos['close'], marker='v', color='red', label='Bearish BOS', s=100)

    plt.title('Break of Structure (BOS) Detection')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()


def start_sos():
    symbol_list = ['XAUUSD', 'BTCUSD']
    for symbol in symbol_list:
        time.sleep(10)
        print('debug')

        skip_min = 1
        json_file_name = 'bos'
        running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                                   json_file_name=json_file_name)
        if running_trade_status:
            # print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
            return

        df = get_live_data(symbol=symbol, time_frame='M1', prev_n_candles=200)

        # Detect BOS
        result_df = detect_bos(df)
        print(result_df[['close', 'Previous_High', 'Previous_Low', 'BOS_Signal']].tail(20))

        # Alex G
        df_high = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=200)
        df_high = identify_trend_points(df_high)
        market_trend = determine_market_trend(df_high)
        print(market_trend)

        # plot graph
        # plot_bos(result_df)

        # Bullish BOS / Bearish BOS

        if result_df['BOS_Signal'].iloc[-1] == 'Bullish BOS' and market_trend == 'Bullish':
            # BUY
            action = 'buy'
        elif result_df['BOS_Signal'].iloc[-1] == 'Bearish BOS' and market_trend == 'Bearish':
            # Sell
            action = 'sell'
        else:
            action = None

        if action:
            MAGIC_NUMBER = get_magic_number()
            lot = 0.1
            if symbol == 'XAUUSD':
                tp_point = lot * 30000
                sl_point = lot * 15000
            elif symbol == 'BTCUSD':
                tp_point = lot * 200000
                sl_point = lot * 100000

            trade_order_magic(symbol=symbol, tp_point=3000, sl_point=1500, lot=lot, action=action, magic=True,
                              code=106049, MAGIC_NUMBER=MAGIC_NUMBER)
            write_json(json_dict=orders_json, json_file_name=json_file_name)



initialize_mt5()

while True:
    
    start_sos()