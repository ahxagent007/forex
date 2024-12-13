# This is a sample Python script.
import time
import math
from datetime import datetime
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import time
from sklearn.linear_model import LinearRegression
from numpy.ma.core import angle
from scipy.signal import argrelextrema

from xian import cumulative_lot
from mt5_utils import initialize_mt5, get_all_positions, get_live_data, trade_order_wo_tp_sl, \
    close_position


def Ma(prices):
    a = prices['close'].rolling(window=50).mean()
    return a


def Ema(prices):
    a = prices['close'].ewm(span=20, adjust=False).mean()
    return a

def calculate_rsi(prices, window=14):
    delta = prices['close'].diff()  # Price changes
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()  # Average gain
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()  # Average loss

    rs = gain / loss  # Relative Strength
    rsi = 100 - (100 / (1 + rs))  # RSI formula
    return rsi


def detect_lev(df,n):
      # Number of neighbors to consider for local extrema
    df['Min'] = df.iloc[argrelextrema(df['close'].values, np.less_equal, order=n)[0]]['close']
    df['Max'] = df.iloc[argrelextrema(df['close'].values, np.greater_equal, order=n)[0]]['close']

    return df
def is_near_level(levels, value, tolerance):
    return any(abs(level - value) <= tolerance for level in levels)
def bot_1(symbol, lot):
    # Actions: 0 = Hold, 1 = Buy, 2 = Sell
    positions = get_all_positions(symbol)
    ticks_frame1 = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=300)

    ma=Ma(ticks_frame1)
    ema=Ema(ticks_frame1)
    t=detect_lev(ticks_frame1,10)
    buy=[]
    buy.append(False)
    sell=[]
    sell.append(False)
    rsi = calculate_rsi(ticks_frame1)
    for i in range(1,len(t)):
        if (math.isnan(t.iloc[i - 1]['Min'])):
            # print('nan')
            buy.append(False)
        elif (ticks_frame1.iloc[i]['close'] > ticks_frame1.iloc[i - 1]['close'] and rsi[i]<30):
            # print('hello')
            buy.append(True)
        else:
            buy.append(False)

        if (math.isnan(t.iloc[i - 1]['Max'])):
            # print('nan')
            sell.append(False)
        elif (ticks_frame1.iloc[i]['close'] < ticks_frame1.iloc[i - 1]['close'] and rsi[i]>70):
            # print('hello')
            sell.append(True)

        else:
            # print('hello')
            sell.append(False)

    buy_exit = []
    buy_exit.append(False)
    sell_exit = []
    sell_exit.append(False)


    for i in range(1,len(t)):
        if (math.isnan(t.iloc[i - 2]['Min'])==False ):
            sell_exit.append(True)
        else:
            sell_exit.append(False)
        if (math.isnan(t.iloc[i - 2]['Max'])==False ):
            buy_exit.append(True)
        else:
            buy_exit.append(False)


    '''
    plt.figure(figsize=(15, 8))
    plt.subplot(2, 1, 1)
    plt.plot(ticks_frame1['time'], ticks_frame1['close'], label='Close Price', color='blue')
    plt.plot(ticks_frame1['time'], ma, label='Close Price', color='Orange')
    plt.plot(ticks_frame1['time'], ema, label='Close Price', color='red')
    plt.scatter(ticks_frame1['time'][buy_exit],
                ticks_frame1['close'][buy_exit], color='green',
                label='Preliminary Support (PS)', marker='*')
    plt.scatter(ticks_frame1['time'][sell_exit],
                ticks_frame1['close'][sell_exit], color='red',
                label='Preliminary Support (PS)', marker='*')

    plt.scatter(ticks_frame1['time'][buy],
                ticks_frame1['close'][buy], color='green',
                label='Preliminary Support (PS)', marker='^')

    plt.scatter(ticks_frame1['time'][sell],
                ticks_frame1['close'][sell], color='red',
                label='Preliminary Support (PS)', marker='v')

    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Wyckoff Phase A Detection')
    plt.legend()
    plt.xticks(rotation=45)

    plt.subplot(2, 1, 2)
    #plt.plot(rsi, label='RSI', color='red')
    plt.plot(ticks_frame1['time'], rsi, label='Close Price', color='blue')
    plt.scatter(ticks_frame1['time'][buy],
                rsi[buy], color='green',
                label='Preliminary Support (PS)', marker='^')

    plt.scatter(ticks_frame1['time'][sell],
                rsi[sell], color='red',
                label='Preliminary Support (PS)', marker='v')

    plt.axhline(70, linestyle='--', color='gray', label='Overbought (70)')
    plt.axhline(30, linestyle='--', color='gray', label='Oversold (30)')
    plt.title('Relative Strength Index (RSI)')
    plt.legend(loc='upper left')

    plt.show()

    '''
    if len(positions) == 0:

        i = -1
        print(buy[i], '----', sell[i])
        if (buy[i] == True):
            print('buy')
            trade_order_wo_tp_sl(symbol, lot, 'buy', magic=False)

        elif (sell[i] == True):
            print('sell')
            trade_order_wo_tp_sl(symbol, lot, 'sell', magic=False)
        else:
            print('no')
        # Visualize Accumulation and Markup
        # for i in range(len(wyckoff_data)):
    elif len(positions) > 0:
        print(buy[-1], '----', sell[-1])
        for position in positions:
            if (position.comment == 'buy' and buy_exit[-1] == True):

                close_position(symbol, position.ticket)
                print('buy_exit')

            elif (position.comment == 'sell' and sell_exit[-1] == True):
                close_position(symbol, position.ticket)
                print('sell_exit')

def botexit(symbol):
    positions = get_all_positions(symbol)
    if(len(positions) > 0):
        for position in positions:
            current_lot = position.volume
            sl = -(100 * current_lot)
            tp = 500 * current_lot
            if (position.profit <= sl or position.profit >= tp):
                close_position(symbol, position.ticket)



def Mt5_backTest(muldhon, Current_time, window, totalTime):
    initialize_mt5()

    isOneCandle = False
    prev_time = datetime.now().minute
    symbol_list = ['XAUUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP',
                   'EURJPY']
    while True:
        for symbol in symbol_list:
            botexit(symbol)
        # botexit('EURUSD')
        # botexit('EURJPY')
        # botexit('USDJPY')
        # botexit('GBPUSD')
        # botexit('XAUUSD')
        # print(prev_time,'    ',cur_time)
        cur_time = datetime.now().minute
        if prev_time == cur_time:
            isOneCandle = False
        else:
            isOneCandle = True
        if (cur_time % 5) == 0 and isOneCandle:
            print()
            for symbol in symbol_list:
                lot = cumulative_lot()
                bot_1(symbol, lot)

            # bot_1('EURUSD', 0.01)
            # bot_1('EURJPY', 0.01)
            # bot_1('USDJPY', 0.01)
            # bot_1('GBPUSD', 0.01)
            # bot_1('XAUUSD', 0.01)
            print('------------------------------------------')
            prev_time = cur_time


    #mt5.shutdown()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Mt5()
    Mt5_backTest(5000, datetime.now() - timedelta(days=0.5), 60, timedelta(minutes=120))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/