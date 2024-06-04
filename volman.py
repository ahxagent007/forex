import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.  pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import datetime as dt
from scipy.signal import argrelextrema

pd.options.mode.chained_assignment = None

'''
Asian Trading Session: 8:00 PM – 4:00 AM BST. 
European Trading Session: 4:00 AM – 12:00 PM BST. 
North American Trading Session: 8:00 AM – 4:00 PM BST
4 AM to 4 PM
'''

'''
COMBO
1. Moving Average Crossover + RSI
2. Bollinger Bands + MACD
3. Fibonacci Retracement + Price Action Patterns
4. Ichimoku Cloud + Stochastic Oscillator
5. Trend Following + Mean Reversion
6. Volume Profile + Support and Resistance
7. ATR (Average True Range) + Breakout Strategy
8. Heikin Ashi + Moving Average
9. Keltner Channel + RSI
10. Volume Weighted Average Price (VWAP) + MACD

'''


MAGIC_NUMBER = 0

def get_magic_number():
    global MAGIC_NUMBER
    MAGIC_NUMBER += 1
    add_data('magic', MAGIC_NUMBER)
    return MAGIC_NUMBER

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

def note_trade(txt):
    with open("trades.txt", "a") as myfile:
        myfile.write(txt+'\n')


def export_df(symbol):
    TIME_FRAME = mt5.TIMEFRAME_M1
    PREV_MIN_CHART = 7200

    rates = mt5.copy_rates_range(symbol, TIME_FRAME, datetime.now() - timedelta(minutes=PREV_MIN_CHART),
                                 datetime.now())
    ticks_frame = pd.DataFrame(rates)
    ticks_frame.to_csv('csv/'+symbol+'.csv')

def candle_pattern(candle):
    #Doji Condition=∣Close−Open∣≤k×(High−Low)
    if abs(candle['close']-candle['open']) <= 0.2 * abs(candle['high']-candle['low']):
        if candle['close'] > candle['open']:
            return 'doji'
            #return 'doji_bull'
        elif candle['close'] < candle['open']:
            return 'doji'
            #return 'doji_bear'
        else:
            return 'doji'
    elif candle['close'] > candle['open']:
        return 'bull'
    elif candle['close'] < candle['open']:
        return 'bear'
    else:
        return None

def show_candle_plot(ticks_df):
    fig = go.Figure(data=[go.Candlestick(x=ticks_df['time'],
                    open=ticks_df['open'],
                    high=ticks_df['high'],
                    low=ticks_df['low'],
                    close=ticks_df['close'])])

    fig.show()

def buy_order(symbol, tp_point, sl_point, lot):
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    bid_price = mt5.symbol_info_tick(symbol).bid

    spread = abs(price-bid_price)/point
    print(symbol, 'Spread pip: ', spread)

    if spread > 4:
        print('High Spread')
        clear_data()
        return None

    add_data('spreads', spread)

    tp = price + tp_point * point
    sl = price - sl_point * point

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
            print(symbol, ' ', 'buy not done', result.retcode, MT5_error_code(result.retcode))
            clear_data()
        else:
            print('>>>>>>>>>>>> ## ## ## buy done with bot ', symbol)
            write_data()
    except Exception as e:
        print('Result BUY >> ', str(e))

def sell_order(symbol, tp_point, sl_point, lot):
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).bid
    ask_price = mt5.symbol_info_tick(symbol).ask

    spread = abs(price - ask_price) / point
    print('Spread pip: ', spread)
    if spread > 4:
        print(symbol, 'High Spread')
        clear_data()
        return None

    add_data('spreads', spread)

    tp = price - tp_point * point
    sl = price + sl_point * point
    # sl = data['sl']

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
        "magic": get_magic_number(),
        "comment": "python script close",
        #"type_time": mt5.ORDER_TIME_GTC,
        #"type_filling": mt5.ORDER_FILLING_IOC,
    }
    print(request)

    # send a trading request

    result = mt5.order_send(request)
    print(result)

    try:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(symbol, ' ', 'sell not done', result.retcode, MT5_error_code(result.retcode))
            clear_data()
        else:
            print('>>>>>>>>>>>> ## ## ## sell done with bot ', symbol)
            write_data()
    except Exception as e:
        print('Result SELL >> ', str(e))

def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:
        #Over midnight:
        return nowTime >= startTime or nowTime <= endTime

# NAHID
def ema(prices):
    ema_values = prices['close'].ewm(span=70).mean()
    #a = ema_values.shift(1)
    #return ema, a

    if ema_values.iloc[-5] > ema_values.iloc[-1]:
        # Down Trend
        return 'sell'
    elif ema_values.iloc[-5] < ema_values.iloc[-1]:
        # up Trend
        return 'buy'

def support_resistance_strategy(df, window=20):
    print('==============',df.shape)
    # Calculate rolling minimum of the low prices
    df['RollingMin'] = df['low'].rolling(window=window).min()

    # Calculate rolling maximum of the high prices
    df['RollingMax'] = df['high'].rolling(window=window).max()

    # Identify support and resistance levels
    support_levels = df[df['low'] <= df['RollingMin']]['low'].unique()
    resistance_levels = df[df['high'] >= df['RollingMax']]['high'].unique()
    #print(df['RollingMin'])
    #print(resistance_levels)
    # Initialize variables
    position = None
    entry_price = None

    # List to store trade results
    trade_results = []

    # Iterate over each row in the DataFrame
    for i in range(0, len(df)):
        if df.loc[i, 'low'] <= df.loc[i, 'RollingMin'] and df.loc[i, 'low'] in support_levels:
            # Enter long position at support level
            trade_results.append('buy')
        elif df.loc[i, 'high'] <= df.loc[i, 'RollingMax'] and df.loc[i, 'high'] in resistance_levels:
            trade_results.append('sell')
        else:
            trade_results.append(None)
    return trade_results

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

# XIAN

def tick_type(candle):
    if candle['close'] > candle['open']:
        return 'bull'
    elif candle['close'] < candle['open']:
        return 'bear'
    else:
        return 'doji'


def moving_average_crossover(data):
    # Calculate short-term and long-term moving averages
    short_window = 5
    long_window = 10

    data['Short_MA'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    data['Long_MA'] = data['close'].rolling(window=long_window, min_periods=1).mean()

    # Identify crossover points
    data['Signal'] = 0
    #data['Signal'][short_window:] = np.where(data['Short_MA'][short_window:] > data['Long_MA'][short_window:], 1, 0)
    data.loc[short_window:, 'Signal'] = np.where(data.loc[short_window:, 'Short_MA'] > data.loc[short_window:, 'Long_MA'], 1, 0)
    data['Position'] = data['Signal'].diff()

    # get the latest signal
    if data['Position'].iloc[-1] == 1:
        return 'buy'
    elif data['Position'].iloc[-1] == -1:
        return 'sell'
    else:
        return None

def bollinger_bands(data):
    # Calculate Bollinger Bands
    window = 20
    data['Middle_Band'] = data['close'].rolling(window=window).mean()
    data['Standard_Deviation'] = data['close'].rolling(window=window).std()
    data['Upper_Band'] = data['Middle_Band'] + (data['Standard_Deviation'] * 2)
    data['Lower_Band'] = data['Middle_Band'] - (data['Standard_Deviation'] * 2)

    # Generate signals
    data['Signal'] = 0
    data['Signal'] = np.where(data['close'] < data['Lower_Band'], 1, data['Signal'])  # Buy signal
    data['Signal'] = np.where(data['close'] > data['Upper_Band'], -1, data['Signal'])  # Sell signal

    # get the latest signal
    if data['Signal'].iloc[-1] == 1:
        return 'buy'
    elif data['Signal'].iloc[-1] == -1:
        return 'sell'
    else:
        return None

def trendline_scalping(data):
    # Find local minima and maxima to draw trendlines
    n = 10  # Number of points to look ahead for finding local minima and maxima
    data['Min'] = data.iloc[argrelextrema(data['close'].values, np.less_equal, order=n)[0]]['close']
    data['Max'] = data.iloc[argrelextrema(data['close'].values, np.greater_equal, order=n)[0]]['close']

    # Generate signals based on trendline bounces
    data['Signal'] = 0
    for i in range(n, len(data)):
        if data['close'].iloc[i] < data['Min'].iloc[i - n:i].min():
            #data['Signal'].iloc[i] = 1  # Buy signal
            data.loc[i, "Signal"] = 1
        elif data['close'].iloc[i] > data['Max'].iloc[i - n:i].max():
            #data['Signal'].iloc[i] = -1  # Sell signal
            data.loc[i, "Signal"] = -1

    # get the latest signal
    if data['Signal'].iloc[-1] == 1:
        return 'buy'
    elif data['Signal'].iloc[-1] == -1:
        return 'sell'
    else:
        return None


# Function to calculate Fibonacci retracement levels


# def calculate_fibonacci_levels(data, period=20):
#     data['high_fl'] = data['close'].rolling(window=period).max()
#     data['low'] = data['close'].rolling(window=period).min()
#
#     data['Fib_38.2'] = data['high_fl'] - 0.382 * (data['high_fl'] - data['low'])
#     data['Fib_50.0'] = data['high_fl'] - 0.500 * (data['high_fl'] - data['low'])
#     data['Fib_61.8'] = data['high_fl'] - 0.618 * (data['high_fl'] - data['low'])
#     return data
#
# def fibonacci_retracements_levels(data):
#
#     # Calculate Fibonacci levels
#     data = calculate_fibonacci_levels(data)
#
#     # Generate signals based on Fibonacci Retracement levels
#     data['Signal'] = 0
#
#     for i in range(len(data)):
#         if data['close'].iloc[i] < data['Fib_61.8'].iloc[i]:
#             #data['Signal'].iloc[i] = 1  # Buy signal
#             data.loc[i, "Signal"] = 1
#         elif data['close'].iloc[i] > data['Fib_38.2'].iloc[i]:
#             #data['Signal'].iloc[i] = -1  # Sell signal
#             data.loc[i, "Signal"] = -1
#
#     # get the latest signal
#     if data['Signal'].iloc[-1] == 1:
#         return 'buy'
#     elif data['Signal'].iloc[-1] == -1:
#         return 'sell'
#     else:
#         return None


# Pin Bar Strategy
def is_pin_bar(row):
    body = abs(row['close'] - row['open'])
    upper_shadow = row['high'] - max(row['close'], row['open'])
    lower_shadow = min(row['close'], row['open']) - row['low']

    # Criteria for a Pin Bar: Long tail (shadow) compared to the body
    if lower_shadow > 2 * body and upper_shadow < body:
        return 1  # Bullish Pin Bar
    elif upper_shadow > 2 * body and lower_shadow < body:
        return -1  # Bearish Pin Bar
    else:
        return 0  # No Pin Bar

def pin_bar_strategy(data):
    # Apply the function to the data
    data['Pin_Bar_Signal'] = data.apply(is_pin_bar, axis=1)

    if data['Pin_Bar_Signal'].iloc[-1] == 1:
        return 'buy'
    elif data['Pin_Bar_Signal'].iloc[-1] == -1:
        return 'sell'
    else:
        return None

# Inside Bar Strategy


# Engulfing Bar Strategy
## Going good
def engulfing_bar_signal(df):
    df['engulfing'] = ((df['close'] > df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & (df['close'] >= df['open'].shift(1)) & (df['open'] <= df['close'].shift(1))) | \
                      ((df['close'] < df['open']) & (df['close'].shift(1) > df['open'].shift(1)) & (df['close'] <= df['open'].shift(1)) & (df['open'] >= df['close'].shift(1)))

    i = -1
    if df['engulfing'].iloc[i]:
        if df['close'].iloc[i] > df['open'].iloc[i]:
            return 'buy'
        elif df['close'].iloc[i] < df['open'].iloc[i]:
            return 'sell'
        else:
            return None


# Breakout Strategy

# False Breakout (Fakeout) Strategy

# FB: First Break


# SB: Second Break


# BB: Block Break

# RB: Range Break
def range_break(df):
    lookback = 70
    recent_data = df[-lookback:]
    range_high = recent_data['High'].max()
    range_low = recent_data['Low'].min()

    i = -1

    if df.loc[i, 'close'] > range_high:
        return 'buy'
    elif df.loc[i, 'close'] < range_low:
        return 'sell'
    else:
        return None

# IRB: Inside Range Break

# ARB: Advance Range Break

# Double Doji Break


# RSI
def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_rsi_signals(df, rsi_window=14, overbought=40, oversold=30):
    df['RSI'] = calculate_rsi(df, window=rsi_window)
    df['signal'] = 0
    df.loc[df['RSI'] > overbought, 'signal'] = -1  # Sell signal
    df.loc[df['RSI'] < oversold, 'signal'] = 1  # Buy signal
    return df

def rsi_signal(df):
    df = generate_rsi_signals(df)
    latest_rsi = df['RSI'].iloc[-1]
    latest_signal = df['signal'].iloc[-1]

    if latest_signal == 1:
        return 'buy'
    elif latest_signal == -1:
        return 'sell'
    else:
        return None


## MACD
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df['EMA_12'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal_Line']
    return df

def generate_macd_signals(df):
    df['signal'] = 0
    df.loc[df['MACD'] > df['Signal_Line'], 'signal'] = 1
    df.loc[df['MACD'] < df['Signal_Line'], 'signal'] = -1

    return df

def macd_signal(df):
    df = calculate_macd(df)
    df = generate_macd_signals(df)

    latest_macd = df['MACD'].iloc[-1]
    latest_signal_line = df['Signal_Line'].iloc[-1]
    latest_signal = df['signal'].iloc[-1]

    if latest_signal == 1 and latest_macd > latest_signal_line:
        return 'buy'
    elif latest_signal == -1 and latest_macd < latest_signal_line:
        return 'sell'
    else:
        return None


def xian_signal(df):
    tick_types = []

    for idx, row in df.iterrows():
        tick_types.append(tick_type(row))

    if tick_types[-3] == 'bull' and tick_types[-2] == 'bear' and tick_types[-1] == 'bear':
        return 'sell'
    elif tick_types[-3] == 'bear' and tick_types[-2] == 'bull' and tick_types[-1] == 'bull':
        return 'buy'
    elif tick_types[-3] == 'bear' and tick_types[-2] == 'bear' and tick_types[-1] == 'bear':
        return 'sell'
    elif tick_types[-3] == 'bull' and tick_types[-2] == 'bull' and tick_types[-1] == 'bull':
        return 'buy'
    else:
        return None



def get_trade_action(ticks_frame):
    # tp_point = 10
    # sl_point = 10
    # lot = 0.01

    signals = []

    # 162.71 --> 155.67
    bb = bollinger_bands(ticks_frame)
    if bb:
        # BB: Bollinger Bands

        print('Bollinger Bands --> ', bb)
        add_data('bollinger_bands', bb)
        signals.append(bb)

        # if bb == 'buy':
        #     buy_order(symbol, tp_point, sl_point, lot)
        # elif bb == 'sell':
        #     sell_order(symbol, tp_point, sl_point, lot)
        # return bb

    # Not tested
    ts = trendline_scalping(ticks_frame)
    if ts:
        # TS: Trendline Scalping
        print('Trendline Scalping --> ', ts)
        add_data('trendline_scalping', ts)
        signals.append(ts)

        # if ts == 'buy':
        #     buy_order(symbol, tp_point, sl_point, lot)
        # elif ts == 'sell':
        #     sell_order(symbol, tp_point, sl_point, lot)
        # return ts

    # 155.67 --> 151.85
    pin_bar = pin_bar_strategy(ticks_frame)
    if pin_bar:
        print('Pin Bar --> ', pin_bar)
        add_data('pin_bar_strategy', pin_bar)
        signals.append(pin_bar)

        # if pin_bar == 'buy':
        #     buy_order(symbol, tp_point, sl_point, lot)
        # elif pin_bar == 'sell':
        #     sell_order(symbol, tp_point, sl_point, lot)
        # return pin_bar

    # # 151.85 --> 151.25
    # ddb = double_doji_break(ticks_frame)
    # if ddb:
    #     # DD: Double Doji Break
    #     print('Double Doji Break --> ', ddb)
    #     signals.append(ddb)
    #
    #     # if ddb == 'buy':
    #     #     buy_order(symbol, tp_point, sl_point, lot)
    #     # elif ddb == 'sell':
    #     #     sell_order(symbol, tp_point, sl_point, lot)
    #     # return ddb

    # macd = macd_signal(ticks_frame)
    # if macd:
    #     print('MACD --> ', macd)
    #     signals.append(macd)

    rsi = rsi_signal(ticks_frame)
    if rsi:
        print('RSI --> ', rsi)
        add_data('rsi_signal', rsi)
        signals.append(rsi)

    # Key ERROR
    # inside_bar = inside_bar_strategy(ticks_frame)
    # if inside_bar:
    #     print('Inside Bar --> ', inside_bar)
    #
    #     if inside_bar == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif inside_bar == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #
    #     # return inside_bar

    # # Key Error
    # frl = fibonacci_retracements_levels(ticks_frame)
    # if frl:
    #     # FRL: Fibonacci Retracement levels
    #     print('Fibonacci Retracement levels --> ', frl)
    #     signals.append(frl)
    #
    #     # if frl == 'buy':
    #     #     buy_order(symbol, tp_point, sl_point, lot)
    #     # elif frl == 'sell':
    #     #     sell_order(symbol, tp_point, sl_point, lot)
    #
    #     # return frl



    # fb_signal = first_break(ticks_frame)
    # if fb_signal:
    #     print("First Break --> ", fb_signal)
    #
    #     if fb_signal == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif fb_signal == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #
    #     # return fb_signal

    # print(ticks_frame.shape)
    # print(ticks_frame.head())
    # print(634)
    #
    # sb_signal = second_break(ticks_frame)
    # if sb_signal:
    #     print('Second Break -->', second_break)
    #
    #     if second_break == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif second_break == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #
    #     # return second_break
    #
    # print(ticks_frame.shape)
    # print(ticks_frame.head())
    # print(645)
    #
    # bb_signal = block_break(ticks_frame)
    # if bb_signal:
    #     print('Block Break -->', bb_signal)
    #
    #     if bb_signal == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif bb_signal == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #
    #     # return bb_signal
    # print(ticks_frame.shape)
    # print(ticks_frame.head())
    # print(656)
    #
    # range_break_signal = range_break(ticks_frame)
    # if range_break_signal:
    #     print('Range Break -->', range_break_signal)
    #
    #     if range_break_signal == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif range_break_signal == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #     # return range_break_signal
    #
    # print(ticks_frame.shape)
    # print(ticks_frame.head())
    # print(666)
    #
    # irb = inside_range_break(ticks_frame)
    # if irb:
    #     print('Inside Range Break -->', irb)
    #
    #     if irb == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif irb == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #     # return irb
    #
    # print(ticks_frame.shape)
    # print(ticks_frame.head())
    # print(676)
    #
    # arb = advance_range_break(ticks_frame)
    # if arb:
    #     print('Advance Range Break --> ', arb)
    #
    #     if arb == 'buy':
    #         buy_order(symbol, tp_point, sl_point, lot)
    #     elif arb == 'sell':
    #         sell_order(symbol, tp_point, sl_point, lot)
    #     # return arb
    #
    # print(ticks_frame.shape)
    # print(ticks_frame.head())
    # print(686)

    ## 24.83 -->
    xs = xian_signal(ticks_frame)
    if xs:
        print('Xian Signal --> ', xs)
        add_data('xian_signal', xs)
        signals.append(xs)

    engulfing_signal = engulfing_bar_signal(ticks_frame)
    if engulfing_signal:
        print('Engulfing Bar  --> ', engulfing_signal)
        add_data('engulfing_signal', engulfing_signal)
        signals.append(engulfing_signal)


    return signals

trade_data = {
        'symbol':'',
        'action':'',
        'magic':'',
        'spreads':'',
        'bollinger_bands':'',
        'trendline_scalping':'',
        'pin_bar_strategy':'',
        'rsi_signal':'',
        'xian_signal':'',
        'engulfing_signal':'',
        'double_doji_break_signal':'',
        'first_break_signal':'',
        'second_break_signal':'',
        'block_break_signal':'',
        'range_break_signal':'',
        'inside_range_break_signal':'',
        'advance_range_break_signal':''

    }

def clear_data():
    global trade_data
    trade_data = {
        'symbol':'',
        'action':'',
        'magic':'',
        'spreads':'',
        'bollinger_bands':'',
        'trendline_scalping':'',
        'pin_bar_strategy':'',
        'rsi_signal':'',
        'xian_signal':'',
        'engulfing_signal':''
    }


def add_data(key, value):
    global trade_data
    trade_data[key] = value

def write_data():
    global trade_data

    df = pd.DataFrame([trade_data])
    df.to_csv('trade_output.csv', mode='a', header=False)

    clear_data()

def combination_trade(ticks_frames):
    bb = bollinger_bands(ticks_frames)
    rsi = rsi_signal(ticks_frames)
    if bb and rsi:
        if bb == rsi:
            return bb
        else:
            return None
    else:
        return None

#### BOB VOLMAN STRATEGIES

# Function to identify Doji candles
def is_doji(row, threshold=0.1):
    body_size = abs(row['open'] - row['close'])
    total_range = row['high'] - row['low']
    return body_size <= threshold * total_range

# Function to identify Double Doji patterns and generate signals
def double_doji_break_signal(df, threshold=0.1):
    df['doji'] = df.apply(lambda row: is_doji(row, threshold), axis=1)
    df['double_doji'] = (df['doji'] & df['doji'].shift(1))

    df['signal'] = 0
    i = -1
    if df['double_doji'].iloc[i]:
        if df['high'].iloc[i] > df['high'].iloc[i - 1]:
            return 'buy'
        elif df['low'].iloc[i] < df['low'].iloc[i - 1]:
            return 'sell'
        else:
            return None

    return None


## FIRST BREAK

def first_break_signal(df):
    window = 20
    threshold = 0.01

    df['range'] = df['high'] - df['low']
    df['rolling_range'] = df['range'].rolling(window=window).mean()
    df['consolidation'] = df['rolling_range'] < threshold

    df['signal'] = 0
    consolidation = False

    i = -1

    if df['consolidation'].iloc[i] and not consolidation:
        consolidation = True
    elif not df['consolidation'].iloc[i] and consolidation:
        if df['close'].iloc[i] > df['high'].iloc[i - 1]:
            return 'buy'
            consolidation = False
        elif df['close'].iloc[i] < df['low'].iloc[i - 1]:
            return 'sell'
            consolidation = False

    return None


### SECOND BREAK
def second_break_signal(df, breakout_window=40, pullback_window=5, threshold=0.01):
    df['high_breakout'] = df['high'].rolling(window=breakout_window).max()
    df['low_breakout'] = df['low'].rolling(window=breakout_window).min()

    df['signal'] = 0

    i = -1

    if df['close'].iloc[i] > df['high_breakout'].iloc[i - 1]:
        # Look for a pullback
        pullback_high = df['high'].iloc[i - pullback_window:i].max()
        if df['close'].iloc[i] < pullback_high - threshold:
            # Look for the second breakout
            for j in range(i + 1, len(df)):
                if df['close'].iloc[j] > pullback_high:
                    return 'buy'
                    break

    elif df['close'].iloc[i] < df['low_breakout'].iloc[i - 1]:
        # Look for a pullback
        pullback_low = df['low'].iloc[i - pullback_window:i].min()
        if df['close'].iloc[i] > pullback_low + threshold:
            # Look for the second breakout
            for j in range(i + 1, len(df)):
                if df['close'].iloc[j] < pullback_low:
                    return 'sell'
                    break

    return None

# Function to identify the Block Break signal
def block_break_signal(df, consolidation_window=40, breakout_window=60):
    df['signal'] = 0

    j = -1
    consolidation_high = max(df['high'].iloc[consolidation_window:len(df)])
    consolidation_low = min(df['low'].iloc[consolidation_window:len(df)])

    if df['close'].iloc[j] > consolidation_high:
        return 'buy'
    elif df['close'].iloc[j] < consolidation_low:
        return 'sell'
    else:
        return None

## RANGE BREAK

def range_break_signal(df, range_window=40, breakout_window=5):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()

    df['signal'] = 0

    i = range_window + breakout_window

    range_high = df['high_range'].iloc[-i]
    range_low = df['low_range'].iloc[-i]

    # Look for breakout after range
    j = -1

    if df['close'].iloc[j] > range_high:
        return 'buy'
    elif df['close'].iloc[j] < range_low:
        return 'sell'
    return None

### INSIDE RANGE BREAK

def inside_range_break_signal(df):
    df['inside_bar'] = (df['high'] < df['high'].shift(1)) & (df['low'] > df['low'].shift(1))

    df['signal'] = 0
    i = -1
    if df['inside_bar'].iloc[i]:
        high_range = df['high'].iloc[i-1]
        low_range = df['low'].iloc[i-1]
        # Check for breakout
        if df['close'].iloc[i] > high_range:
            return 'buy'
        elif df['close'].iloc[i] < low_range:
            return 'sell'
    return None


## ADVANCE RANGE BREAK
def advance_range_break_signal(df, range_window=20, breakout_window=5, confirmation_window=3):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()

    df['signal'] = 0

    i = range_window + breakout_window
    range_high = df['high_range'].iloc[i]
    range_low = df['low_range'].iloc[i]

    # Look for breakout after range
    j = -1
    if df['close'].iloc[j] > range_high:
        # Confirmation criteria: Check if price stays above the range high for a few candles
        if df['close'].iloc[j + 1:j + 1 + confirmation_window] > range_high:
            return 'buy'
    elif df['close'].iloc[j] < range_low:
        # Confirmation criteria: Check if price stays below the range low for a few candles
        if df['close'].iloc[j + 1:j + 1 + confirmation_window] < range_low:
            return 'sell'
    return None

def bob_volman_strategy(tick_frames):

    try:
        ddb = double_doji_break_signal(tick_frames)
        if ddb:
            print('Double Doji', ddb)
            add_data('double_doji_break_signal', ddb)
            return ddb

        fb = first_break_signal(tick_frames)
        if fb:
            print('First Break', fb)
            add_data('first_break_signal', fb)
            return fb

        sb = second_break_signal(tick_frames)
        if sb:
            print('Second Break', sb)
            add_data('second_break_signal', sb)
            return sb

        bb = block_break_signal(tick_frames)
        if bb:
            print('Block Break', bb)
            add_data('block_break_signal', bb)
            return bb

        rb = range_break_signal(tick_frames)
        if rb:
            print('Range Break', rb)
            add_data('range_break_signal', rb)
            return rb

        irb = inside_range_break_signal(tick_frames)
        if irb:
            print('Inside Range Break', irb)
            add_data('inside_range_break_signal', irb)
            return irb

        arb = advance_range_break_signal(tick_frames)
        if arb:
            print('Advance Range Break', arb)
            add_data('advance_range_break_signal', arb)
            return arb
    except:
        return None

    return None





def trade(symbol):
    #print(symbol, ' >>>>>>>>>>>>>>-------------------------------------------')
    clear_data()
    add_data('symbol', symbol)
    TIME_FRAME = mt5.TIMEFRAME_M5
    PREV_N_CANDLES = 70

    tp_point = 10
    sl_point = 10
    lot = 0.01

    # multiple order Skip
    # orders = mt5.positions_get(symbol=symbol)
    # if not orders is None and len(orders) > 0:
    #     print('Multiple Trade',symbol)
    #     return None

    rates = mt5.copy_rates_from_pos(symbol, TIME_FRAME, 0, PREV_N_CANDLES)

    ticks_frame = pd.DataFrame(rates)
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

    if not ticks_frame.shape[0] > 0:
        print(ticks_frame.shape[0])
        return None

    # signals = get_trade_action(ticks_frame)
    # print(symbol, signals)
    #
    # if not len(signals) > 1:
    #     return None
    #
    # buy_count = 0
    # sell_count = 0
    #
    # for signal in signals:
    #     if signal == 'buy':
    #         buy_count += 1
    #     elif signal == 'sell':
    #         sell_count += 1
    #
    # if buy_count>sell_count:
    #     trade_action = 'buy'
    # elif sell_count>buy_count:
    #     trade_action = 'sell'
    # else:
    #     return None
    ## 177.91 -->> 174.16
    #trade_action = combination_trade(ticks_frame)

    ## BOB VOLMAN
    ## 200.16 -->>  159.85
    ## 159.85 -->>
    trade_action = bob_volman_strategy(ticks_frame)

    add_data('action', trade_action)

    if trade_action == 'buy':
        buy_order(symbol, tp_point, sl_point, lot)
    elif trade_action == 'sell':
        sell_order(symbol, tp_point, sl_point, lot)

    #show_plot(ticks_frame)
    #print(ema(ticks_frame))
    #print('-------------------------------------------<<<<<<<<<<<<<<<')


def test_trade(symbol):
    ticks_frame = pd.read_csv('csv/'+symbol+'.csv')

    for i in range(0, ticks_frame.shape[0]-70):
        temp_ticks = ticks_frame.loc[i:i+69]

        get_trade_action(temp_ticks)

    #show_candle_plot(ticks_frame)


def start_live_trade():
    initialize_mt5()

    delay_sec = 60

    symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']

    ## 200 -->

    while True:
        # for symbol in symbol_list:
        #     trade(symbol)
        #     time.sleep(delay_sec)


        trade('EURUSD')
        time.sleep(delay_sec)

        # if isNowInTimePeriod(dt.time(4, 00), dt.time(21, 00), dt.datetime.now().time()):
        #     for symbol in symbol_list:
        #         trade(symbol)
        #         time.sleep(delay_sec)
        #     # trade('EURUSD')
        #     # time.sleep(delay_sec)
        # else:
        #     print(dt.datetime.now().time(), '>>> > >> NOT A GOOD TIME FOR TRADE')
        #     time.sleep(60*5)



#185.17

# test_trade('EURUSD')

start_live_trade()

