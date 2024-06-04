import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mt5_utils import get_live_data, buy_order
from common_functions import check_duplicate_orders, write_json


def if_3ws_3bc(df):
    i = -1

    if (df['close'].iloc[i] > df['open'].iloc[i] and
        df['close'].iloc[i-1] > df['open'].iloc[i-1] and
        df['close'].iloc[i-2] > df['open'].iloc[i-2] and
        df['open'].iloc[i] > df['close'].iloc[i-1]):
        return 'buy'
    elif (df['close'].iloc[i] < df['open'].iloc[i] and
        df['close'].iloc[i-1] < df['open'].iloc[i-1] and
        df['close'].iloc[i-2] < df['open'].iloc[i-2] and
        df['open'].iloc[i] < df['close'].iloc[i-1]):
        return 'sell'
    else:
        return None

def strategy_3ws_3bc(symbol):
    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'USDJPY']
    json_file_name = '3ws_3bc'

    if not symbol in accepted_symbol_list:
        print('Symbol Not supported')
        return

    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=60, json_file_name=json_file_name)
    if running_trade_status:
        return None

    time_frame = 'H1'
    prev_n_candles = 10
    data_df = get_live_data(symbol, time_frame, prev_n_candles)

    action = if_3ws_3bc(data_df)

    if action:
        tp_point = 100
        sl_point = 50
        lot = 0.01
        buy_order(symbol, tp_point, sl_point, lot, action)

        write_json(json_dict=orders_json, json_file_name=json_file_name)
