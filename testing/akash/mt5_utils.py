import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.  pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import datetime as dt
from scipy.signal import argrelextrema


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

def get_data(symbol):
    initialize_mt5()

    TIME_FRAME = mt5.TIMEFRAME_M30
    PREV_N_CANDLES = 100


    rates = mt5.copy_rates_from_pos(symbol, TIME_FRAME, 0, PREV_N_CANDLES)

    ticks_frame = pd.DataFrame(rates)
    print(ticks_frame.head())
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

    return ticks_frame

def get_order_positions(symbol):
    return mt5.positions_get(symbol=symbol)