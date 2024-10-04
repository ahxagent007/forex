import json

import numpy as np
import pandas as pd
# from stock_indicators import indicators
# from stock_indicators import Quote
import time
from akash import get_avg_candle_size, calculate_ema, ADX_stakoverflow
from common_functions import check_duplicate_orders_time, check_duplicate_orders_magic, add_csv, \
    write_json, check_duplicate_orders, check_duplicate_orders_is_time

from mt5_utils import get_live_data, get_prev_data, initialize_mt5, get_magic_number, trade_order_magic, \
    get_all_positions, clsoe_position, trade_order_magic_value
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def create_candle_type(df):
    df['candle_type'] = None

    for idx, row in df.iterrows():
        high = row['high']
        low = row['low']
        open = row['open']
        close = row['close']

        #AVG
        diff_array = []
        for i in range(1, 6):
            try:
                diff = abs(df.loc[idx-i, 'open'] - df.loc[idx-1, 'close'])
                diff_array.append(diff)
            except:
                None
        try:
            prev_5_avg_candle_size = sum(diff_array) / len(diff_array)
        except:
            prev_5_avg_candle_size = 0

        length = abs(high - low)

        hc_diff = abs(high - close)
        lo_diff = abs(low - open)

        ho_diff = abs(high - open)
        lc_diff = abs(low - close)

        oc_diff = abs(open-close)

        ## Bullish Marubozu
        if (hc_diff/length)*100 < 5 and (lo_diff/length)*100 < 5 and close>open and oc_diff > prev_5_avg_candle_size:
            df.loc[idx, 'candle_type'] = 'bullish_marubozu'

        ## bearish Marubozu
        elif (ho_diff/length)*100 < 5 and (lc_diff/length)*100 < 5 and open>close and oc_diff > prev_5_avg_candle_size:
            df.loc[idx, 'candle_type'] = 'bearish_marubozu'

        ## Hammer
        elif (oc_diff/length)*100 < 10 and (hc_diff/length)*100 < 15 and lo_diff > oc_diff*2 and close>open:
            df.loc[idx, 'candle_type'] = 'bullish_hammer'

        ## Hanging Man
        elif (oc_diff/length)*100 < 10 and (ho_diff/length)*100 < 15 and lc_diff > oc_diff*2 and open>close:
            df.loc[idx, 'candle_type'] = 'bearish_hanging_man'

        ## inverted Hammer
        elif (oc_diff/length)*100 < 10 and (lo_diff/length)*100 < 15 and hc_diff > oc_diff*2 and close>open:
            df.loc[idx, 'candle_type'] = 'bullish_inverted_hammer'

        ## Shooting Star
        elif (oc_diff/length)*100 < 10 and (lc_diff/length)*100 < 15 and ho_diff > oc_diff*2 and open>close:
            df.loc[idx, 'candle_type'] = 'bearish_shooting_star'

        ## Doji
        elif (oc_diff/length)*100 < 5:
            df.loc[idx, 'candle_type'] = 'doji'

    return df

def plot_data(df):
    fig = go.Figure(data=[go.Candlestick(x=df['time'],
                                         open=df['open'], high=df['high'],
                                         low=df['low'], close=df['close'])
                          ])

    for idx, row in df.iterrows():
        if row['candle_type']:
            fig.add_annotation(x=row['time'], y=row['low']-0.0005, text=row['candle_type'], showarrow=False,
                               font=dict(size=12, color='black'), textangle=90)
    #fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()

def plot_line(df):
    # plotting a line graph
    print("Line graph: ")
    plt.plot(df["time"], df["close"])
    plt.savefig('img/image.jpg')
    plt.show()



def ADX_stakoverflow_check(data: pd.DataFrame, period: int, idx: int):
    """
    Computes the ADX indicator.
    """

    df = data.copy()
    alpha = 1 / period

    # TR
    df['H-L'] = df['high'] - df['low']
    df['H-C'] = np.abs(df['high'] - df['close'].shift(1))
    df['L-C'] = np.abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    del df['H-L'], df['H-C'], df['L-C']

    # ATR
    df['ATR'] = df['TR'].ewm(alpha=alpha, adjust=False).mean()

    # +-DX
    df['H-pH'] = df['high'] - df['high'].shift(1)
    df['pL-L'] = df['low'].shift(1) - df['low']
    df['+DX'] = np.where(
        (df['H-pH'] > df['pL-L']) & (df['H-pH'] > 0),
        df['H-pH'],
        0.0
    )
    df['-DX'] = np.where(
        (df['H-pH'] < df['pL-L']) & (df['pL-L'] > 0),
        df['pL-L'],
        0.0
    )
    del df['H-pH'], df['pL-L']

    # +- DMI
    df['S+DM'] = df['+DX'].ewm(alpha=alpha, adjust=False).mean()
    df['S-DM'] = df['-DX'].ewm(alpha=alpha, adjust=False).mean()
    df['+DMI'] = (df['S+DM'] / df['ATR']) * 100
    df['-DMI'] = (df['S-DM'] / df['ATR']) * 100
    del df['S+DM'], df['S-DM']

    # ADX
    df['DX'] = (np.abs(df['+DMI'] - df['-DMI']) / (df['+DMI'] + df['-DMI'])) * 100
    df['ADX'] = df['DX'].ewm(alpha=alpha, adjust=False).mean()
    #del df['DX'], df['ATR'], df['TR'], df['-DX'], df['+DX'], df['+DMI'], df['-DMI']

    adx_min = 20
    if df['ADX'].iloc[idx] > adx_min:
        print('ADX', df['ADX'].iloc[idx])
        return True
    else:
        print('ADX', df['ADX'].iloc[idx])
        return False

def test_xian():

    initialize_mt5()

    symbol = 'EURUSD'
    time_frame = 'M10'
    df = get_prev_data(symbol=symbol, time_frame=time_frame, prev_start_min=5000, prev_end_min=500)

    df = create_candle_type(df)
    df.to_csv('img/data.csv')
    plot_line(df)

def price_action(symbol):
    time_frame = 'M10'
    skip_min = 11
    json_file_name = 'xian_price_action'
    code = 69

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=code)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=500)

    df = create_candle_type(df)

    df['ema'] = df['close'].ewm(span=8, adjust=False).mean()

    action = None
    if df['candle_type'].iloc[-2] == 'bullish_marubozu' and df['open'].iloc[-2] < df['ema'].iloc[-2] and \
            df['close'].iloc[-2] > df['ema'].iloc[-2]:
        action = 'buy'
    elif df['candle_type'].iloc[-2] == 'bearish_marubozu' and df['open'].iloc[-2] > df['ema'].iloc[-2] and \
            df['close'].iloc[-2] < df['ema'].iloc[-2]:
        action = 'sell'


    if action:
        print(symbol, 'volman_strategies')
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, 2, 1)

        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=code,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, action, tp, sl, 'volman_strategies', data]
        add_csv(data_lst)


def calculate_cci(data, period=20):
    # Calculate the typical price (TP)
    data['TP'] = (data['high'] + data['low'] + data['close']) / 3

    # Calculate the simple moving average of typical price (SMA_TP)
    data['SMA_TP'] = data['TP'].rolling(window=period).mean()

    # Calculate the Mean Absolute Deviation (MAD)
    def mean_absolute_deviation(series):
        return series.mad() if hasattr(series, 'mad') else (series - series.mean()).abs().mean()

    # # Calculate the Mean Absolute Deviation (MAD)
    # data['MAD'] = data['TP'].rolling(window=period).apply(lambda x: pd.Series(x).mad(), raw=True)

    # Apply the MAD function
    data['MAD'] = data['TP'].rolling(window=period).apply(mean_absolute_deviation)

    # Calculate the CCI (Commodity Channel Index)
    data['CCI'] = (data['TP'] - data['SMA_TP']) / (0.015 * data['MAD'])


    return data['CCI']

def cci_signal(df):
    df['CCI_14'] = calculate_cci(data=df, period=14)
    df['CCI_25'] = calculate_cci(data=df, period=25)
    df['CCI_50'] = calculate_cci(data=df, period=50)

    if df['CCI_14'].iloc[-1] > 0 and df['CCI_25'].iloc[-1] > 0 and df['CCI_50'].iloc[-1] > 0:
        return 'buy'
    elif df['CCI_14'].iloc[-1] < 0 and df['CCI_25'].iloc[-1] < 0 and df['CCI_50'].iloc[-1] < 0:
        return 'sell'
    else:
        return None

def moving_average_crossover_cci(symbol, short, long):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'EURJPY']
    skip_min = 2
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name = 'akash_strategies_ma_ema_'+str(short)+'_'+str(long)
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        #print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['EMA_short'] = calculate_ema(df, short)
    df['MA_long'] = df['close'].rolling(window=long).mean()

    action = None
    # if df['EMA_short'].iloc[-1] > df['MA_long'].iloc[-1] and df['EMA_short'].iloc[-3] < df['MA_long'].iloc[-1]:
    #     action = 'buy'
    # elif df['EMA_short'].iloc[-1] < df['MA_long'].iloc[-1] and df['EMA_short'].iloc[-3] > df['MA_long'].iloc[-1]:
    #     action = 'sell'

    if df['close'].iloc[-1] > df['MA_long'].iloc[-1] and df['close'].iloc[-3] < df['MA_long'].iloc[-1]:
        action = 'buy'
    elif df['close'].iloc[-1] < df['MA_long'].iloc[-1] and df['close'].iloc[-3] > df['MA_long'].iloc[-1]:
        action = 'sell'

    df = ADX_stakoverflow(df, 14)

    df['CCI_14'] = calculate_cci(data=df, period=14)
    df['CCI_25'] = calculate_cci(data=df, period=25)
    df['CCI_50'] = calculate_cci(data=df, period=50)
    # print(df.columns)
    # quotes_list = [
    #     Quote(d, o, h, l, c, v)
    #     for d, o, h, l, c, v
    #     in zip(df['time'], df['open'], df['high'], df['low'], df['close'], df['tick_volume'])
    # ]
    #
    # df['CCI_14'] = indicators.get_cci(quotes_list, 14)
    # df['CCI_25'] = indicators.get_cci(quotes_list, 25)
    # df['CCI_50'] = indicators.get_cci(quotes_list, 50)


    lot = 0.02


    if action:

        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, 2, 1)
        if avg_candle_size is None:
            return
        print(symbol, '## TP -->', tp, '## SL -->', sl, '## AVG -->', avg_candle_size, '## ACTION -->', action,
              'ADX -->', df['ADX'].iloc[-1])
        print('CCI 14', df['CCI_14'].iloc[-1], 'CCI 25', df['CCI_25'].iloc[-1], 'CCI 50', df['CCI_50'].iloc[-1])
        print('-----------------------------------------------------------------------------------------')

        if action == 'buy':
            if not (df['CCI_14'].iloc[-1] > 0 and df['CCI_25'].iloc[-1] > 0 and df['CCI_50'].iloc[-1] > 0):
                print('CCI BUY RETURNED')
                return None
        elif action == 'sell':
            if not (df['CCI_14'].iloc[-1] < 0 and df['CCI_25'].iloc[-1] < 0 and df['CCI_50'].iloc[-1] < 0):
                print('CCI SELL RETURNED')
                return None

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=888, MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data_lst = [symbol, time_frame,  MAGIC_NUMBER, avg_candle_size, action, tp, sl, df['ADX'].iloc[-1], ]
        add_csv(data_lst)


def moving_average_crossover_01(symbol, short, long):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'EURJPY', 'BTCUSD']
    skip_min = 3
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name = 'akash_strategies_ma_ema_'+str(short)+'_'+str(long)
    running_trade_status, orders_json, is_time = check_duplicate_orders_is_time(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        #print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        # if not is_time:
        #     take_the_profit(symbol) #706.70
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['short'] = df['close'].rolling(window=short).mean()
    df['long'] = df['close'].rolling(window=long).mean()

    action = None
    if df['short'].iloc[-1] > df['long'].iloc[-1] and df['short'].iloc[-3] < df['long'].iloc[-1]:
        action = 'buy'
    elif df['short'].iloc[-1] < df['long'].iloc[-1] and df['short'].iloc[-3] > df['long'].iloc[-1]:
        action = 'sell'

    # if df['close'].iloc[-1] > df['MA_long'].iloc[-1] and df['close'].iloc[-3] < df['MA_long'].iloc[-1]:
    #     action = 'buy'
    # elif df['close'].iloc[-1] < df['MA_long'].iloc[-1] and df['close'].iloc[-3] > df['MA_long'].iloc[-1]:
    #     action = 'sell'


    lot = 0.1


    if action:
        adx_min_bool = ADX_stakoverflow_check(df, 14, -1)
        if not adx_min_bool:
            print(symbol,'ADX', adx_min_bool)
            if symbol == 'BTCUSD':
                None
            elif symbol == 'XAUUSD':
                None
            else:
                return

        if action == 'buy':
            sl_value = df['low'].iloc[-1]
        else:
            sl_value = df['high'].iloc[-1]

        sl_multi = 3
        tp_multi = 12
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, tp_multi, sl_multi)
        if avg_candle_size is None:
            return
        print(symbol, '## TP -->', tp, '## SL -->', sl, '## AVG -->', avg_candle_size, '## ACTION -->', action)

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic_value(symbol=symbol, tp_point=tp, sl_value=sl_value, lot=lot, action=action, magic=True, code=888, MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, action, tp, sl, json_file_name, data]
        add_csv(data_lst)

def current_milli_time():
    return round(time.time() * 1000)

def take_the_profit(symbol):
    json_file_name_lst = ['xian_trade', 'akash_02']
    skip_min = 3

    for json_file_name in json_file_name_lst:
        run_take_the_profit = False
        running_trade_status_time, orders_json, is_time = check_duplicate_orders_is_time(symbol=symbol, skip_min=skip_min,
                                                                                         json_file_name=json_file_name)
        running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=77)
        if running_trade_status_time or running_trade_status_magic:
            if not is_time:
                run_take_the_profit = True

        if not run_take_the_profit:
            return
        # get all positions
        positions = get_all_positions(symbol)

        # loop through all
        for position in positions:
            # read the data file
            magic_id = position.magic
            file_name = 'magics/' + symbol + '_' + str(magic_id) + '.json'
            data = {
                'symbol': symbol,
                'magic': None,
                'profit_1': {
                    'profit': None,
                    'time': 0
                },
                'profit_2': {
                    'profit': None,
                    'time': 0
                },
                'profit_3': {
                    'profit': None,
                    'time': 0
                }
            }

            try:
                with open(file_name) as json_file:
                    data = json.load(json_file)

            except:
                with open(file_name, 'x') as outfile:
                    json.dump(data, outfile)

            current_profit = position.profit
            current_millis = current_milli_time()

            time_gap = 20000
            
            # check the logic
            if data['profit_1']['profit'] is None:
                data['profit_1']['profit'] = current_profit
                data['profit_1']['time'] = current_millis

            if (data['profit_1']['time'] + time_gap) < current_millis:
                if data['profit_2']['profit'] is None:
                    data['profit_2']['profit'] = data['profit_1']['profit']
                    data['profit_2']['time'] = data['profit_1']['time']

                    data['profit_1']['profit'] = current_profit
                    data['profit_1']['time'] = current_millis
                elif data['profit_3']['profit'] is None:
                    data['profit_3']['profit'] = data['profit_2']['profit']
                    data['profit_3']['time'] = data['profit_2']['time']

                    data['profit_2']['profit'] = data['profit_1']['profit']
                    data['profit_2']['time'] = data['profit_1']['time']

                    data['profit_1']['profit'] = current_profit
                    data['profit_1']['time'] = current_millis
                else:
                    data['profit_3']['profit'] = data['profit_2']['profit']
                    data['profit_3']['time'] = data['profit_2']['time']

                    data['profit_2']['profit'] = data['profit_1']['profit']
                    data['profit_2']['time'] = data['profit_1']['time']

                    data['profit_1']['profit'] = current_profit
                    data['profit_1']['time'] = current_millis

            print(current_millis)
            print(symbol, data['profit_3']['profit'], data['profit_2']['profit'], data['profit_1']['profit'])
            print(symbol, data['profit_3']['time'], data['profit_2']['time'], data['profit_1']['time'])

            if data['profit_3']['profit'] and data['profit_2']['profit'] and data['profit_1']['profit']:
                # if profit_1 < profit_2 < profit_3
                if data['profit_3']['profit'] > data['profit_2']['profit'] > data['profit_1']['profit']:
                    print(position.profit)
                    print(position)
                    # close the trade
                    clsoe_position(symbol, ticket=position.ticket)
                    data = {
                        'symbol': symbol,
                        'magic': None,
                        'profit_1': {
                            'profit': None,
                            'time': 0
                        },
                        'profit_2': {
                            'profit': None,
                            'time': 0
                        },
                        'profit_3': {
                            'profit': None,
                            'time': 0
                        }
                    }
                    with open(file_name, 'w') as outfile:
                        json.dump(data, outfile)

                else:
                    # else write the data file
                    with open(file_name, 'w') as outfile:
                        json.dump(data, outfile)
            else:
                # else write the data file
                with open(file_name, 'w') as outfile:
                    json.dump(data, outfile)



