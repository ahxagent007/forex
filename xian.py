import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def initialize_mt5():
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    login = 124207670
    password = "abcdABCD123!@#"
    server = "Exness-MT5Trial7"
    timeout = 10000
    portable = False
    if mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
        print("Initialization successful")
    else:
        print('Initialize failed')

def get_position(symbol='EURUSDm'):
    orders_eurousdm = mt5.positions_get(symbol=symbol)
    return orders_eurousdm

def get_rates(symbol='EURUSDm', prev_min=720):
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=prev_min),
                                 datetime.now())
    ticks_frame = pd.DataFrame(rates)

    print(ticks_frame.shape)
    return ticks_frame

def candle_type(candle):
    if candle['open'] > candle['close']:
        # red
        return 'bearish'
    elif candle['close'] > candle['open']:
        # green
        return 'bullish'
    else:
        # Doji
        return 'doji'

def trade_logic(last_4_candles):

    three_white_solders = True
    three_black_crows = True
    sl = 0
    action = None

    logic_three_white_solders = ['bearish', 'bullish', 'bullish', 'bullish']
    logic_three_black_crows = ['bullish', 'bearish', 'bearish', 'bearish']

    i = 0

    for idx, row in last_4_candles.iterrows():
        if not logic_three_white_solders[i] == candle_type(row):
            three_white_solders = False
        if not logic_three_black_crows[i] == candle_type(row):
            three_black_crows = False
        i+=1

    if three_white_solders:
        sl = last_4_candles['low'].max()
        action = 'buy'
    if logic_three_black_crows:
        sl = last_4_candles['high'].max()
        action = 'sell'

    data = {
        'three_white_solders': three_white_solders,
        'three_black_crows': three_black_crows,
        'last_candle': last_4_candles.iloc[-1].to_dict(),
        'sl': sl,
        'action': action
    }
    #print(data)

    return data




initialize_mt5()

ticks_df = get_rates(symbol='EURUSDm', prev_min=5000)

tws = 0
tbc = 0

for i in range(0, ticks_df.shape[0]-4):
    last_4_candles = ticks_df[i:i+4]
    data = trade_logic(last_4_candles)

    if data['three_white_solders']:
        tws+=1
        print(data)
    if data['three_black_crows']:
        tbc+=1
        print(data)

print('Total Candle:', ticks_df.shape[0], '\nTWS:', tws, '\nTBC:',tbc)

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'],
                high=df['AAPL.High'],
                low=df['AAPL.Low'],
                close=df['AAPL.Close'])])

fig.show()