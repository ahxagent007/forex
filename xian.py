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
    # rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=prev_min),
    #                              datetime.now())

    # window = 10
    pt = datetime.now()-timedelta(days=2) #+ timedelta(minutes=window)
    rates = mt5.copy_rates_range("EURUSDm", mt5.TIMEFRAME_M10, pt - timedelta(days=4), pt)

    ticks_frame = pd.DataFrame(rates)
    print('ticks_frame--> Size: ',ticks_frame.shape)
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
    tp = 0
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

    tp_change = 0.0004
    sl_change = 0.0008

    if three_white_solders:
        sl = last_4_candles['low'].max()
        tp = last_4_candles['close'].max() + tp_change
        action = 'buy'
    if three_black_crows:
        sl = last_4_candles['high'].max()
        tp = last_4_candles['close'].max() - tp_change
        action = 'sell'
    data = {
        'three_white_solders': three_white_solders,
        'three_black_crows': three_black_crows,
        'last_candle': last_4_candles.iloc[-1].to_dict(),
        'sl': sl,
        'tp':tp,
        'action': action
    }
    #print(data)

    return data

def test_tade_result(trade_dec, sl, tp, current_candle):
    print(trade_dec, '=> SL:',sl,' TP:', tp,'\ncurrent_candle', current_candle.to_dict())
    if trade_dec == 'buy':
        if sl >= current_candle['low']:
            print('SL Crossed low')
            return False
        elif tp <= current_candle['high']:
            return True
        else:
            return None
    elif trade_dec == 'sell':
        if sl <= current_candle['high']:
            print('SL Crossed high')
            return False
        elif tp >= current_candle['low']:
            return True
        else:
            return None


def show_plot(ticks_df):
    fig = go.Figure(data=[go.Candlestick(x=ticks_df['time'],
                    open=ticks_df['open'],
                    high=ticks_df['high'],
                    low=ticks_df['low'],
                    close=ticks_df['close'])])

    fig.show()
initialize_mt5()

ticks_df = get_rates(symbol='EURUSDm', prev_min=50000)

tws = 0
tbc = 0
sell_total_win = 0
sell_total_loss = 0
buy_total_win = 0
buy_total_loss = 0

for i in range(0, ticks_df.shape[0]-4):
    last_4_candles = ticks_df[i:i+4]
    data = trade_logic(last_4_candles)


    try:
        if data['three_white_solders'] or data['three_black_crows']:
            result = None
            j = 5
            while result is None:
                result = test_tade_result(trade_dec=data['action'],
                                          sl=data['sl'],
                                          tp=data['tp'],
                                          current_candle=ticks_df.iloc[i + j])
                j += 1

            if data['three_white_solders']:
                tws += 1
                if result:
                    buy_total_win += 1
                else:
                    buy_total_loss += 1

            if data['three_black_crows']:
                tbc += 1
                if result:
                    sell_total_win += 1
                else:
                    sell_total_loss += 1


    except:
        print('Trade Not closed')


print('Total Candle:', ticks_df.shape[0], '\nTWS:', tws, '\nTBC:',tbc, '\nBUY WIN:',buy_total_win, '\nBUY LOSS:',buy_total_loss,
      '\nSELL WIN:',sell_total_win, '\nSELL LOSS:',sell_total_loss)
print('Success % : ', ((buy_total_win+sell_total_win)/(tws+tbc))*100)

show_plot(ticks_df)