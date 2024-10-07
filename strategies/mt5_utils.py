import json

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.  pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import datetime as dt
from scipy.signal import argrelextrema



def get_magic_number():
    with open('magic_number.json') as json_file:
        data = json.load(json_file)
        magic_number = data['magic_number']
        magic_number += 1
        data = {
            'magic_number': magic_number
        }
    json_file.close()

    with open('magic_number.json', 'w') as outfile:
        json.dump(data, outfile)
    json_file.close()

    return magic_number


def initialize_mt5():
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

    # # NEW ACC
    login = 181244000
    password = 'ABCabc123!@#'
    server = 'Exness-MT5Trial6'

    ## Standard
    #login = 181931686
    #password = 'ABCabc123!@#'
    #server = 'Exness-MT5Trial6'

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
        '10021': 'There are no quotes to process the request',
        '10018': 'Market is closed'
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
    elif time_frame == 'M15':
        TIME_FRAME = mt5.TIMEFRAME_M15
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
def get_prev_data(symbol, time_frame, prev_start_min, prev_end_min):

    if time_frame == 'M1':
        TIME_FRAME = mt5.TIMEFRAME_M1
    elif time_frame == 'M5':
        TIME_FRAME = mt5.TIMEFRAME_M5
    elif time_frame == 'M10':
        TIME_FRAME = mt5.TIMEFRAME_M10
    elif time_frame == 'M15':
        TIME_FRAME = mt5.TIMEFRAME_M15
    elif time_frame == 'M30':
        TIME_FRAME = mt5.TIMEFRAME_M30
    elif time_frame == 'H1':
        TIME_FRAME = mt5.TIMEFRAME_H1
    elif time_frame == 'H4':
        TIME_FRAME = mt5.TIMEFRAME_H4
    elif time_frame == 'D1':
        TIME_FRAME = mt5.TIMEFRAME_D1

    #rates = mt5.copy_rates_from(symbol, TIME_FRAME, datetime.today(), PREV_N_CANDLES)
    rates = mt5.copy_rates_range(symbol, TIME_FRAME,
                                 datetime.now() - timedelta(minutes=prev_start_min),
                                 datetime.now() - timedelta(minutes=prev_end_min))


    ticks_frame = pd.DataFrame(rates)
    #print(ticks_frame.head())

    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

    return ticks_frame

def trade_order(symbol, tp_point, sl_point, lot, action, magic=False):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        spread = abs(price - bid_price) / point

        if tp_point:
            tp = price + tp_point * point
            sl = price - sl_point * point
        else:
            sl = price - sl_point * point

    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        spread = abs(price - ask_price) / point

        if tp_point:
            tp = price - tp_point * point
            sl = price + sl_point * point
        else:
            sl = price + sl_point * point

    print(symbol, 'Spread pip: ', spread)

    spread_dict = {
        'EURUSD': 15,
        'XAUUSD': 150,
        'BTCUSD': 1900
    }

    if spread > spread_dict[symbol]:
        print('High Spread')
        return None

    deviation = 20
    MAGIC_NUMBER = get_magic_number()
    if tp_point:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            #"type_time": mt5.ORDER_TIME_GTC,
            #"type_filling": mt5.ORDER_FILLING_IOC,
        }
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "sl": sl,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            # "type_time": mt5.ORDER_TIME_GTC,
            # "type_filling": mt5.ORDER_FILLING_IOC,
        }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))

        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)## update magic number
            if magic:
                update_magic_number(symbol, MAGIC_NUMBER)
    except Exception as e:
        print('Result '+action+' >> ', str(e))

def trade_order_wo_sl(symbol, tp_point, lot, action, magic=False):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        spread = abs(price - bid_price) / point

        if tp_point:
            tp = price + tp_point * point


    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        spread = abs(price - ask_price) / point

        if tp_point:
            tp = price - tp_point * point


    print(symbol, 'Spread pip: ', spread)

    spread_dict = {
        'EURUSD': 15,
        'XAUUSD': 150,
        'BTCUSD': 1900
    }

    if spread > spread_dict[symbol]:
        print('High Spread')
        return None

    deviation = 20
    MAGIC_NUMBER = get_magic_number()
    if tp_point:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "tp": tp,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            #"type_time": mt5.ORDER_TIME_GTC,
            #"type_filling": mt5.ORDER_FILLING_IOC,
        }
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            # "type_time": mt5.ORDER_TIME_GTC,
            # "type_filling": mt5.ORDER_FILLING_IOC,
        }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))

        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)## update magic number
            if magic:
                update_magic_number(symbol, MAGIC_NUMBER)
    except Exception as e:
        print('Result '+action+' >> ', str(e))

def trade_order_wo_tp_sl(symbol, lot, action, magic=False):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        spread = abs(price - bid_price) / point
    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        spread = abs(price - ask_price) / point


    print(symbol, 'Spread pip: ', spread)

    spread_dict = {
        'EURUSD': 15,
        'EURJPY': 15,
        'USDJPY': 15,
        'XAUUSD': 150,
        'BTCUSD': 1900,
        'GBPUSD': 15
    }

    if spread > spread_dict[symbol]:
        print('High Spread')
        return None

    deviation = 20

    MAGIC_NUMBER = get_magic_number()

    request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open"
        }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))

        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)## update magic number
            if magic:
                update_magic_number(symbol, MAGIC_NUMBER)
    except Exception as e:
        print('Result '+action+' >> ', str(e))

def trade_order_magic(symbol, tp_point, sl_point, lot, action, magic=False, code=0, MAGIC_NUMBER=0):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        spread = abs(price - bid_price) / point

        if tp_point:
            tp = price + tp_point * point
            sl = price - sl_point * point


    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        spread = abs(price - ask_price) / point

        if tp_point:
            tp = price - tp_point * point
            sl = price + sl_point * point


    print(symbol, 'Spread pip: ', spread)

    spread_dict = {
        'EURUSD': 15,
        'XAUUSD': 150,
        'BTCUSD': 2000,
        'USDJPY': 15,
        'GBPUSD': 15,
        'EURJPY': 20
    }

    if spread > spread_dict[symbol]:
        print('High Spread')
        return None
    if tp_point <= spread or sl_point <= spread:
        print('LOW TP/SL')
        return None

    deviation = 20
    # MAGIC_NUMBER = get_magic_number()
    if tp_point:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "tp": tp,
            "sl": sl,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            #"type_time": mt5.ORDER_TIME_GTC,
            #"type_filling": mt5.ORDER_FILLING_IOC,
        }
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "sl": sl,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            # "type_time": mt5.ORDER_TIME_GTC,
            # "type_filling": mt5.ORDER_FILLING_IOC,
        }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))

        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)## update magic number
            if magic:
                update_magic_number(symbol+str(code), MAGIC_NUMBER)
    except Exception as e:
        print('Result '+action+' >> ', str(e))

def trade_order_magic_value(symbol, tp_point, sl_value, lot, action, magic=False, code=0, MAGIC_NUMBER=0):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        spread = abs(price - bid_price) / point

        if tp_point:
            tp = price + tp_point * point
            sl = sl_value


    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        spread = abs(price - ask_price) / point

        if tp_point:
            tp = price - tp_point * point
            sl = sl_value


    print(symbol, 'Spread pip: ', spread)

    spread_dict = {
        'EURUSD': 15,
        'XAUUSD': 150,
        'BTCUSD': 2000,
        'USDJPY': 15,
        'GBPUSD': 15,
        'EURJPY': 20
    }

    if spread > spread_dict[symbol]:
        print('High Spread')
        return None
    if tp_point <= spread:
        print('LOW TP !!!!!!')
        return None

    deviation = 20
    # MAGIC_NUMBER = get_magic_number()
    if tp_point:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "tp": tp,
            "sl": sl,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            #"type_time": mt5.ORDER_TIME_GTC,
            #"type_filling": mt5.ORDER_FILLING_IOC,
        }
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "sl": sl,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            # "type_time": mt5.ORDER_TIME_GTC,
            # "type_filling": mt5.ORDER_FILLING_IOC,
        }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))

        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)## update magic number
            if magic:
                update_magic_number(symbol+str(code), MAGIC_NUMBER)
    except Exception as e:
        print('Result '+action+' >> ', str(e))


def trade_order_wo_sl_magic(symbol, tp_point, lot, action, magic=False, code=0):


    if action == 'buy':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY

        spread = abs(price - bid_price) / point

        if tp_point:
            tp = price + tp_point * point


    elif action == 'sell':
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid
        ask_price = mt5.symbol_info_tick(symbol).ask
        type = mt5.ORDER_TYPE_SELL

        spread = abs(price - ask_price) / point

        if tp_point:
            tp = price - tp_point * point


    print(symbol, 'Spread pip: ', spread)

    spread_dict = {
        'EURUSD': 15,
        'XAUUSD': 150,
        'BTCUSD': 1900
    }

    if spread > spread_dict[symbol]:
        print('High Spread')
        return None

    deviation = 20
    MAGIC_NUMBER = get_magic_number()
    if tp_point:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "tp": tp,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            #"type_time": mt5.ORDER_TIME_GTC,
            #"type_filling": mt5.ORDER_FILLING_IOC,
        }
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": type,
            "price": price,
            "deviation": deviation,
            "magic": MAGIC_NUMBER,
            "comment": "python script open",
            # "type_time": mt5.ORDER_TIME_GTC,
            # "type_filling": mt5.ORDER_FILLING_IOC,
        }
    print(request)
    # send a trading request
    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', action+' not done', result.retcode, MT5_error_code(result.retcode))

        else:
            print('>>>>>>>>>>>> ## ## ## '+action+' done with bot ', symbol)## update magic number
            if magic:
                update_magic_number(symbol+str(code), MAGIC_NUMBER)
    except Exception as e:
        print('Result '+action+' >> ', str(e))

def get_order_positions_count(symbol):
    try:
        return len(mt5.positions_get(symbol=symbol))
    except:
        return 0

def get_all_positions(symbol):
    return mt5.positions_get(symbol=symbol)
def clsoe_position(symbol, ticket):
    mt5.Close(symbol, ticket=ticket)


def update_magic_number(symbol, MAGIC_NUMBER):
    #print('updating',symbol,MAGIC_NUMBER)
    file_name = 'time_counts/trade_number.json'
    json_data = {}
    with open(file_name) as json_file:
        json_data = json.load(json_file)

    json_data[symbol] = MAGIC_NUMBER

    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile)


def get_current_price(symbol):
    # Get current price
    price_info = mt5.symbol_info_tick(symbol)

    # Check if price information is retrieved successfully
    if price_info is None:
        print(f"Failed to get price information for {symbol}, error code =", mt5.last_error())
        return None

    # Extract bid and ask prices
    bid_price = price_info.bid
    ask_price = price_info.ask

    # Print the current bid and ask prices
    # print(f"Current bid price for {symbol}: {bid_price}")
    # print(f"Current ask price for {symbol}: {ask_price}")
    data = {
        'bid_price': bid_price,
        'ask_price': ask_price
    }

    return data

