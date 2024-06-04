import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.  pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import datetime as dt
from scipy.signal import argrelextrema
from common_functions import get_magic_number


def initialize_mt5():
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

    login = 116644810
    password = "ABCabc123!@#"
    server = "Exness-MT5Trial6"

    timeout = 10000
    portable = False
    if mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
        print("Initialization successful")
    else:
        print('Initialize failed')


def MT5_error_code(code):
    # error codes ==> https://mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes
    mt5_error = {
        '10019': 'Not Enough Money',
        '10016': 'Invalid SL',
        '10027': 'Autotrading Disabled',
        '10014': 'Invalid volume in the request',
        '10030': 'Invalid order filling type',
        '10021': 'There are no quotes to process the request'
    }

    try:
        error = mt5_error[str(code)]
    except:
        error = None
    return error

def get_live_data(symbol, time_frame, prev_n_candles):

    if time_frame == 'M1':
        TIME_FRAME = mt5.TIMEFRAME_M1
    elif time_frame == 'M5':
        TIME_FRAME = mt5.TIMEFRAME_M5
    elif time_frame == 'M10':
        TIME_FRAME = mt5.TIMEFRAME_M10
    elif time_frame == 'M30':
        TIME_FRAME = mt5.TIMEFRAME_M30
    elif time_frame == 'H1':
        TIME_FRAME = mt5.TIMEFRAME_H1
    elif time_frame == 'H4':
        TIME_FRAME = mt5.TIMEFRAME_H4
    elif time_frame == 'D1':
        TIME_FRAME = mt5.TIMEFRAME_D1

    PREV_N_CANDLES = prev_n_candles

    rates = mt5.copy_rates_from_pos(symbol, TIME_FRAME, 0, PREV_N_CANDLES)

    ticks_frame = pd.DataFrame(rates)

    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

    return ticks_frame

def buy_order(symbol, tp_point, sl_point, lot, action):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        tp = price + tp_point * point
        sl = price - sl_point * point

    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        tp = price - tp_point * point
        sl = price + sl_point * point


    spread = abs(price-bid_price)/point
    print(symbol, 'Spread pip: ', spread)

    if spread > 15:
        print('High Spread')
        return None

    deviation = 20

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": get_magic_number(),
        "comment": "python script open",
        #"type_time": mt5.ORDER_TIME_GTC,
        #"type_filling": mt5.ORDER_FILLING_IOC,
    }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))
        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)
    except Exception as e:
        print('Result '+action+' >> ', str(e))

# def sell_order(symbol, tp_point, sl_point, lot):
#     point = mt5.symbol_info(symbol).point
#     price = mt5.symbol_info_tick(symbol).bid
#     ask_price = mt5.symbol_info_tick(symbol).ask
#
#     spread = abs(price - ask_price) / point
#     print('Spread pip: ', spread)
#     if spread > 4:
#         print(symbol, 'High Spread')
#         clear_data()
#         return None
#
#     add_data('spreads', spread)
#
#     tp = price - tp_point * point
#     sl = price + sl_point * point
#     # sl = data['sl']
#
#     deviation = 20
#     request = {
#         "action": mt5.TRADE_ACTION_DEAL,
#         "symbol": symbol,
#         "volume": lot,
#         "type": mt5.ORDER_TYPE_SELL,
#         "price": price,
#         "sl": sl,
#         "tp": tp,
#         "deviation": deviation,
#         "magic": get_magic_number(),
#         "comment": "python script close",
#         #"type_time": mt5.ORDER_TIME_GTC,
#         #"type_filling": mt5.ORDER_FILLING_IOC,
#     }
#     print(request)
#
#     # send a trading request
#
#     result = mt5.order_send(request)
#     print(result)
#
#     try:
#         if result.retcode != mt5.TRADE_RETCODE_DONE:
#             print(symbol, ' ', 'sell not done', result.retcode, MT5_error_code(result.retcode))
#             clear_data()
#         else:
#             print('>>>>>>>>>>>> ## ## ## sell done with bot ', symbol)
#             write_data()
#     except Exception as e:
#         print('Result SELL >> ', str(e))