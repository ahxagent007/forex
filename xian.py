import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.  pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

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
    rates = mt5.copy_rates_range("EURUSDm", mt5.TIMEFRAME_M10, pt - timedelta(days=10), pt)

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

def trade_logic(last_5_candles):
    three_white_solders = True
    three_black_crows = True
    sl = 0
    tp = 0
    action = None

    logic_three_white_solders = ['bearish', 'bullish', 'bullish', 'bullish', 'bullish']
    logic_three_black_crows = ['bullish', 'bearish', 'bearish', 'bearish', 'bearish']

    i = 0

    for idx, row in last_5_candles.iterrows():
        if not logic_three_white_solders[i] == candle_type(row):
            three_white_solders = False
        if not logic_three_black_crows[i] == candle_type(row):
            three_black_crows = False

        i += 1

    tp_change = 0.0004
    sl_change = 0.0008

    if three_white_solders:
        sl = last_5_candles['low'].min()
        tp = last_5_candles['close'].max() + tp_change
        action = 'buy'
    if three_black_crows:
        sl = last_5_candles['high'].max()
        tp = last_5_candles['close'].min() - tp_change
        action = 'sell'
    data = {
        'three_white_solders': three_white_solders,
        'three_black_crows': three_black_crows,
        'last_candle': last_5_candles.iloc[-2].to_dict(),
        'sl': sl,
        'tp':tp,
        'action': action
    }
    #print(data)

    return data

def test_tade_result(trade_dec, sl, tp, current_candle):
    #print(trade_dec, '=> SL:',sl,' TP:', tp,'\ncurrent_candle', current_candle.to_dict())
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

def start_trade(symbol, lot, dec, sl):

    if dec == "buy":
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        #sl = price - 30 * point
        tp = price + 40 * point
        '''if sl>price:
            sl = price - 50 * point'''

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # send a trading request
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('not done')
        else:
            print('buy done with bot')
    elif dec == "sell":

        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid

        #sl = price + 30 * point
        tp = price - 40 * point

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # send a trading request
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('TRADE_RETCODE_DONE')
        else:
            print('sell done with bot')
    else:
        print('kiccu korar nai')

def show_plot(ticks_df):
    fig = go.Figure(data=[go.Candlestick(x=ticks_df['time'],
                    open=ticks_df['open'],
                    high=ticks_df['high'],
                    low=ticks_df['low'],
                    close=ticks_df['close'])])

    fig.show()

def back_test():
    ticks_df = get_rates(symbol='EURUSDm', prev_min=50000)

    tws = 0
    tbc = 0
    sell_total_win = 0
    sell_total_loss = 0
    buy_total_win = 0
    buy_total_loss = 0

    for i in range(0, ticks_df.shape[0] - 4):
        last_4_candles = ticks_df[i:i + 4]
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

    print('Total Candle:', ticks_df.shape[0], '\nTWS:', tws, '\nTBC:', tbc, '\nBUY WIN:', buy_total_win, '\nBUY LOSS:',
          buy_total_loss,
          '\nSELL WIN:', sell_total_win, '\nSELL LOSS:', sell_total_loss)
    print('Success % : ', ((buy_total_win + sell_total_win) / (tws + tbc)) * 100)

    show_plot(ticks_df)

import json

def write_json(json_dict):
    with open('json_data.json', 'w') as outfile:
        json.dump(json_dict, outfile)

def read_json():
    with open('json_data.json') as json_file:
        data = json.load(json_file)
        return data


def stochastic_oscillator(df, k_period=14, d_period=3):
    high = df['high']
    low = df['low']
    close = df['close']

    # Calculate %K
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k_percent = ((close - lowest_low) / (highest_high - lowest_low)) * 100

    # Calculate %D
    d_percent = k_percent.rolling(window=d_period).mean()

def stochastic_crossover_strategy(df, k_period=14, d_period=3):
    # Calculate Stochastic Oscillator %K and %D
    df['Lowest_Low'] = df['low'].rolling(window=k_period).min()
    df['Highest_High'] = df['high'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['close'] - df['Lowest_Low']) / (df['Highest_High'] - df['Lowest_Low']))
    df['%D'] = df['%K'].rolling(window=d_period).mean()

    # Initialize variables
    dec='None'

    # List to store trade results
    trade_results = []
    for i in range(len(df)):
        if df['%K'].iloc[i] > df['%D'].iloc[i] and df['%K'].iloc[i - 1] <= df['%D'].iloc[i - 1] and df['%D'].iloc[
            i] < 20:
            trade_results.append('buy')

        # Stochastic Oscillator crossover sell signal
        elif df['%K'].iloc[i] < df['%D'].iloc[i] and df['%K'].iloc[i - 1] >= df['%D'].iloc[i - 1] and df['%D'].iloc[
            i] > 80:
            trade_results.append('sell')
        else:
            trade_results.append('None')
    i=-1
    if df['%K'].iloc[i] > df['%D'].iloc[i] and df['%K'].iloc[i-1] <= df['%D'].iloc[i-1] and df['%D'].iloc[i] < 20:
        dec = 'buy'

    # Stochastic Oscillator crossover sell signal
    elif df['%K'].iloc[i] < df['%D'].iloc[i] and df['%K'].iloc[i-1] >= df['%D'].iloc[i-1] and df['%D'].iloc[i] > 80:
        dec = 'sell'

    return trade_results

def start_trading(symbol):
    lot = 0.02
    tp_point = 20
    sl_point = 100
    #10019 = Not Enough Money

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=360),
                                 datetime.now())
    ticks_frame = pd.DataFrame(rates)

    last_5_candles = ticks_frame.tail(5)

    try:
        data = trade_logic(last_5_candles)
    except:
        return None
    # data = {}
    # data['three_white_solders'] = True
    # data['three_black_crows'] = True

    if data['three_white_solders'] or data['three_black_crows']:

        #Stocokastick Crossover
        dec_stock_list = stochastic_crossover_strategy(ticks_frame, k_period=14, d_period=3)

        if dec_stock_list[-1] == 'buy' or dec_stock_list[-2] == 'buy':
            dec_stock = 'buy'
        elif dec_stock_list[-1] == 'sell' or dec_stock_list[-2] == 'sell':
            dec_stock = 'sell'
        else:
            dec_stock = None

        orders_json = read_json()

        orders = mt5.positions_get(symbol=symbol)
        if len(orders) > 0:
            try:
                current_time = round(time.time()*1000)
                ten_mins = (orders_json[symbol] + (60000*10))
                if ten_mins < current_time:
                    orders_json[symbol] = current_time
                    write_json(orders_json)
                else:
                    return
            except Exception as e:
                print('##>> ', str(e))
                orders_json[symbol] = current_time
                write_json(orders_json)

        #sl = data['sl']
        if data['action'] == 'buy' and dec_stock == 'buy':
            point = mt5.symbol_info(symbol).point
            price = mt5.symbol_info_tick(symbol).ask

            tp = price + tp_point * point
            #sl = price - sl_point * point
            sl = data['sl']

            deviation = 20
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script open",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            print(request)
            # send a trading request
            result = mt5.order_send(request)
            print(result)

            try:
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(symbol, ' ', 'buy not done', result.retcode)
                else:
                    print('>>>>>>>>>>>> ## ## ## buy done with bot ', symbol)
            except:
                print('Result None BUY')
        elif data['action'] == 'sell' and dec_stock == 'sell':
            point = mt5.symbol_info(symbol).point
            price = mt5.symbol_info_tick(symbol).bid

            tp = price - tp_point * point
            #sl = price + sl_point * point
            sl = data['sl']

            deviation = 20
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": deviation,
                "magic": 234000,
                "comment": "python script close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            print(request)

            # send a trading request

            result = mt5.order_send(request)
            print(result)

            try:
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(symbol, ' ', 'sell not done', result.retcode)
                else:
                    print('>>>>>>>>>>>> ## ## ## sell done with bot ', symbol)
            except:
                print('Result None SELL')


initialize_mt5()

while True:

    #Major
    start_trading('EURUSDm')
    time.sleep(5)
    start_trading('USDJPYm')
    time.sleep(5)
    # start_trading('AUDUSDm')
    # time.sleep(5)
    start_trading('GBPUSDm')
    time.sleep(5)
    start_trading('NZDUSDm')
    time.sleep(5)
    start_trading('USDCADm')
    time.sleep(5)
    start_trading('USDCHFm')
    time.sleep(5)


    #Minor
    start_trading('EURJPYm')
    time.sleep(5)
    # start_trading('AUDCADm')
    # time.sleep(5)
    # start_trading('AUDCHFm')
    # time.sleep(5)
    # start_trading('AUDJPYm')
    # time.sleep(5)
    # start_trading('AUDNZDm')
    # time.sleep(5)
    # start_trading('CADCHFm')
    # time.sleep(5)
    # start_trading('CHFJPYm')
    # time.sleep(5)
    start_trading('EURAUDm')
    time.sleep(5)
    start_trading('EURCADm')
    time.sleep(5)
    # start_trading('EURCHFm')
    # time.sleep(5)
    start_trading('EURGBPm')
    time.sleep(5)
    # start_trading('EURNZDm')
    # time.sleep(5)
    # start_trading('GBPAUDm')
    # time.sleep(5)
    start_trading('GBPCADm')
    time.sleep(5)
    # start_trading('GBPCHFm')
    # time.sleep(5)
    # start_trading('GBPJPYm')
    # time.sleep(5)
    # start_trading('GBPNZDm')
    # time.sleep(5)
    # start_trading('HKDJPYm')
    # time.sleep(5)
    # start_trading('NZDCADm')
    # time.sleep(5)
    # start_trading('NZDCHFm')
    # time.sleep(5)
    # start_trading('USDCNHm')
    # time.sleep(5)
    # start_trading('USDHKDm')
    # time.sleep(5)
    # start_trading('USDTHBm')
    # time.sleep(5)
    start_trading('NZDJPYm')
    time.sleep(5)
    start_trading('CADJPYm')
    time.sleep(5)
