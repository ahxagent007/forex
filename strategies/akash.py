import numpy as np
import pandas as pd

from common_functions import check_duplicate_orders_magic_v2, check_duplicate_orders, write_json, \
    check_duplicate_orders_time, check_duplicate_orders_magic, add_csv
from mt5_utils import get_live_data, trade_order, get_current_price, get_order_positions_count, trade_order_magic, \
    get_magic_number, trade_order_wo_tp_sl
import MetaTrader5 as mt5



def adx_decision(data, period=14):
    # Calculate the True Range (TR)
    data['TR'] = np.maximum((data['high'] - data['low']), np.maximum(abs(data['high'] - data['close'].shift(1)),
                                                                     abs(data['low'] - data['close'].shift(1))))

    # Calculate +DM and -DM
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           np.maximum(data['high'] - data['high'].shift(1), 0), 0)
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           np.maximum(data['low'].shift(1) - data['low'], 0), 0)

    # Calculate smoothed TR, +DM, and -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])

    # Calculate the DI Difference and DI Sum
    data['DI_diff'] = abs(data['+DI'] - data['-DI'])
    data['DI_sum'] = data['+DI'] + data['-DI']

    # Calculate the DX
    data['DX'] = 100 * (data['DI_diff'] / data['DI_sum'])

    # Calculate the ADX
    data['ADX'] = data['DX'].rolling(window=period).mean()

    print('ADX VALUE -->>',data['ADX'].iloc[-2], '+DI -->', data['+DI'].iloc[-2],'-DI -->', data['-DI'].iloc[-2])
    print('ADX VALUE -->>',data['ADX'].iloc[-1], '+DI -->', data['+DI'].iloc[-1],'-DI -->', data['-DI'].iloc[-1])

    adx_min = 20
    # if data['ADX'].iloc[-1] >= adx_min:
    #     #YES TRADE
    #     if data['+DI'].iloc[-1] > data['-DI'].iloc[-1]:
    #         return 'buy'
    #     else:
    #         return 'sell'
    #print('ADX', data['ADX'].iloc[-1])
    # if data['ADX'].iloc[-1] >= adx_min:
    #     #YES TRADE
    #     if (data['+DI'].iloc[-1] > data['-DI'].iloc[-1]) and (data['+DI'].iloc[-1] > adx_min):
    #         return 'buy'
    #     elif (data['-DI'].iloc[-1] > adx_min):
    #         return 'sell'

    if not data['ADX'].iloc[-1] >= adx_min:
        return None

    if data['+DI'].iloc[-1] > data['-DI'].iloc[-1]:
        return 'buy'
    elif data['+DI'].iloc[-1] < data['-DI'].iloc[-1]:
        return 'sell'
    else:
        return None

def adx_decision_prev(data, period=14):
    # Calculate the True Range (TR)
    data['TR'] = np.maximum((data['high'] - data['low']), np.maximum(abs(data['high'] - data['close'].shift(1)),
                                                                     abs(data['low'] - data['close'].shift(1))))

    # Calculate +DM and -DM
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           np.maximum(data['high'] - data['high'].shift(1), 0), 0)
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           np.maximum(data['low'].shift(1) - data['low'], 0), 0)

    # Calculate smoothed TR, +DM, and -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])

    # Calculate the DI Difference and DI Sum
    data['DI_diff'] = abs(data['+DI'] - data['-DI'])
    data['DI_sum'] = data['+DI'] + data['-DI']

    # Calculate the DX
    data['DX'] = 100 * (data['DI_diff'] / data['DI_sum'])

    # Calculate the ADX
    data['ADX'] = data['DX'].rolling(window=period).mean()


    adx_min = 20
    # if data['ADX'].iloc[-1] >= adx_min:
    #     #YES TRADE
    #     if data['+DI'].iloc[-1] > data['-DI'].iloc[-1]:
    #         return 'buy'
    #     else:
    #         return 'sell'
    #print('ADX', data['ADX'].iloc[-1])
    # if data['ADX'].iloc[-1] >= adx_min:
    #     #YES TRADE
    #     if (data['+DI'].iloc[-1] > data['-DI'].iloc[-1]) and (data['+DI'].iloc[-1] > adx_min):
    #         return 'buy'
    #     elif (data['-DI'].iloc[-1] > adx_min):
    #         return 'sell'

    if not data['ADX'].iloc[-2] >= adx_min:
        return None

    print('ADX', data['ADX'].iloc[-2], '+DI', data['+DI'].iloc[-2], '-DI', data['-DI'].iloc[-2])

    if data['+DI'].iloc[-2] > data['-DI'].iloc[-2]:
        return 'buy'
    elif data['+DI'].iloc[-2] < data['-DI'].iloc[-2]:
        return 'sell'
    else:
        return None


def check_adx(data, period=14):
    # Calculate the True Range (TR)
    data['TR'] = np.maximum((data['high'] - data['low']), np.maximum(abs(data['high'] - data['close'].shift(1)),
                                                                     abs(data['low'] - data['close'].shift(1))))

    # Calculate +DM and -DM
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           np.maximum(data['high'] - data['high'].shift(1), 0), 0)
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           np.maximum(data['low'].shift(1) - data['low'], 0), 0)

    # Calculate smoothed TR, +DM, and -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])

    # Calculate the DI Difference and DI Sum
    data['DI_diff'] = abs(data['+DI'] - data['-DI'])
    data['DI_sum'] = data['+DI'] + data['-DI']

    # Calculate the DX
    data['DX'] = 100 * (data['DI_diff'] / data['DI_sum'])

    # Calculate the ADX
    data['ADX'] = data['DX'].rolling(window=period).mean()

    #print('ADX VALUE -->>',data['ADX'].iloc[-1], data['+DI'].iloc[-1], data['-DI'].iloc[-1])
    adx_min = 20
    # if data['ADX'].iloc[-1] >= adx_min:
    #     #YES TRADE
    #     if data['+DI'].iloc[-1] > data['-DI'].iloc[-1]:
    #         return 'buy'
    #     else:
    #         return 'sell'
    if data['ADX'].iloc[-1] >= adx_min:
        return True
    else:
        return False


def create_adx(data, period=14):
    # Calculate the True Range (TR)
    data['TR'] = np.maximum((data['high'] - data['low']), np.maximum(abs(data['high'] - data['close'].shift(1)),
                                                                     abs(data['low'] - data['close'].shift(1))))

    # Calculate +DM and -DM
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           np.maximum(data['high'] - data['high'].shift(1), 0), 0)
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           np.maximum(data['low'].shift(1) - data['low'], 0), 0)

    # Calculate smoothed TR, +DM, and -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])

    # Calculate the DI Difference and DI Sum
    data['DI_diff'] = abs(data['+DI'] - data['-DI'])
    data['DI_sum'] = data['+DI'] + data['-DI']

    # Calculate the DX
    data['DX'] = 100 * (data['DI_diff'] / data['DI_sum'])

    # Calculate the ADX
    data['ADX'] = data['DX'].rolling(window=period).mean()


    return data

def moving_average_signal(symbol):
    accepted_symbol_list = ['XAUUSD', 'BTCUSD']
    skip_min = 2
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name ='akash_strategies'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    if_duplicate, magic_number, dup_action, positions_df = check_duplicate_orders_magic_v2(symbol)

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['MA_25'] = df['close'].rolling(window=25).mean() ## MA Change
    df['MA_50'] = df['close'].rolling(window=50).mean() ## MA Change
    df['MA_200'] = df['close'].rolling(window=200).mean()

    ## RSI
    df['RSI'] = calculate_rsi(df)

    if if_duplicate:
        action_convert = {
            1: 'buy',
            0: 'sell'
        }

        #print(action_convert[dup_action], 'DUPLICATE AKASH FOR >> ', symbol)

        prices = get_current_price(symbol)

        for idx, row in positions_df.iterrows():

            dup_action = mt5.ORDER_TYPE_SELL if row['type'] == 0 else mt5.ORDER_TYPE_BUY

            if action_convert[dup_action] == 'buy' and df['MA_50'].iloc[-1] > prices['bid_price']: # 1 = buy
                print(symbol, "POSITION CLOSE !@!!!@!@!@!@!@!@!@")
                close_position(symbol, row['magic'])
            elif action_convert[dup_action] == 'sell' and df['MA_50'].iloc[-1] < prices['bid_price']: # 0 = sell
                print(symbol, "POSITION CLOSE !@!!!@!@!@!@!@!@!@")
                close_position(symbol, row['magic'])
            else:
                return None


    ## M30/H1
    tp_dict = {
        'EURUSD': 600,
        'AUDUSD': 400,
        'GBPUSD': 600,
        'USDCAD': 200,
        'USDJPY': 500,
        'EURGPB': 300,
        'USDCHF': 400,
        'XAUUSD': 1500,
        'BTCUSD': 9000
    }

    tp_dict_2 = {
        'EURUSD': 400,
        'AUDUSD': 200,
        'GBPUSD': 400,
        'USDCAD': 100,
        'USDJPY': 150,
        'EURGPB': 150,
        'USDCHF': 200,
        'XAUUSD': 1000,
        'BTCUSD': 4000
    }

    tp_dict_3 = {
        'EURUSD': 200,
        'AUDUSD': 100,
        'GBPUSD': 200,
        'USDCAD': 70,
        'USDJPY': 100,
        'EURGPB': 100,
        'USDCHF': 100,
        'XAUUSD': 25000
    }

    sl_dict = {
        'EURUSD': 100,
        'AUDUSD': 50,
        'GBPUSD': 100,
        'USDCAD': 20,
        'USDJPY': 50,
        'EURGPB': 50,
        'USDCHF': 50,
        'XAUUSD': 1000,
        'BTCUSD': 4000
    }

    ## M5
    # tp_dict = {
    #     'EURUSD': 200,
    #     'AUDUSD': 400,
    #     'GBPUSD': 200,
    #     'USDCAD': 200,
    #     'USDJPY': 500,
    #     'EURGPB': 300,
    #     'USDCHF': 400,
    #     'XAUUSD': 25000
    # }
    #
    # tp_dict_2 = {
    #     'EURUSD': 150,
    #     'AUDUSD': 200,
    #     'GBPUSD': 150,
    #     'USDCAD': 100,
    #     'USDJPY': 150,
    #     'EURGPB': 150,
    #     'USDCHF': 200,
    #     'XAUUSD': 15000
    # }
    #
    # tp_dict_3 = {
    #     'EURUSD': 100,
    #     'AUDUSD': 100,
    #     'GBPUSD': 100,
    #     'USDCAD': 70,
    #     'USDJPY': 100,
    #     'EURGPB': 100,
    #     'USDCHF': 100,
    #     'XAUUSD': 6000
    # }
    #
    # sl_dict = {
    #     'EURUSD': 30,
    #     'AUDUSD': 30,
    #     'GBPUSD': 30,
    #     'USDCAD': 20,
    #     'USDJPY': 30,
    #     'EURGPB': 30,
    #     'USDCHF': 30,
    #     'XAUUSD': 2000
    # }

    sl = sl_dict[symbol]
    tp = tp_dict[symbol] #300 #hour chart 500/600
    # tp2 = tp_dict_2[symbol] #300 #hour chart 500/600
    # tp3 = tp_dict_3[symbol] #300 #hour chart 500/600

    ## Current Candle
    if (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-2]) \
            or (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
        action = 'buy'
    elif (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-2]) \
            or (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
        action = 'sell'
    else:
        action = None

    # if not action:
    #     if (df['MA_25'].iloc[-1] < df['close'].iloc[-1] and df['MA_25'].iloc[-1] > df['close'].iloc[-2]) \
    #             or (df['MA_25'].iloc[-1] < df['close'].iloc[-1] and df['MA_25'].iloc[-1] > df['close'].iloc[-3]):
    #         action = 'buy'
    #     elif (df['MA_25'].iloc[-1] > df['close'].iloc[-1] and df['MA_25'].iloc[-1] < df['close'].iloc[-2]) \
    #             or (df['MA_25'].iloc[-1] > df['close'].iloc[-1] and df['MA_25'].iloc[-1] < df['close'].iloc[-3]):
    #         action = 'sell'
    #     else:
    #         action = None


    #print(symbol)
    ##adx_signal = adx_decision(data=df, period=14)

    # Previous Candle
    # if (df['MA_50'].iloc[-1] < df['close'].iloc[-2] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
    #     action = 'buy'
    # elif (df['MA_50'].iloc[-1] > df['close'].iloc[-2] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
    #     action = 'sell'
    # else:
    #     action = None

    ## 200 MA Technique
    # signal_200ma = None
    # if df['MA_50'].iloc[-1] > df['MA_200'].iloc[-1]:
    #     signal_200ma = 'buy'
    # elif df['MA_50'].iloc[-1] < df['MA_200'].iloc[-1]:
    #     signal_200ma = 'sell'

    # Average candle
    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[-5] + df['high'].iloc[-6])/7
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] + df['low'].iloc[-6])/7

    avg_signal = False
    candle_avg = (avg_high - avg_low)
    if candle_avg > 0.4:
        avg_signal = True

    # Tick Volume Analysis
    tick_signal = False
    if df['tick_volume'].iloc[-1] > df['tick_volume'].iloc[-2] > df['tick_volume'].iloc[-3]:
        tick_signal = True

    ## ADX CALCULATION
    adx_signal = adx_decision(df)


    print('RSI --->>',df['RSI'].iloc[-1], '\t tick_volume --->>',df['tick_volume'].iloc[-1], '\t spread --->>',df['spread'].iloc[-1],
          '\t real_volume --->>',df['real_volume'].iloc[-1], '\t AVG Diff -->', avg_high-avg_low, '\t ADX --->>', adx_signal, '\t\t Final ACTION -->>',action)


    if action:
        # print(symbol, 'ADX Signal -->> ', adx_signal, ' <<--- ORIGINAL --->>', action, ' 200 MA -->>',signal_200ma)
        # if not action == adx_signal == signal_200ma:
        #     return None
        # if not action == adx_signal:
        #     return None

        # trade_order(symbol=symbol, tp_point=None, sl_point=sl, lot=0.1, action=action, magic=True)
        # if action == 'buy' and df['RSI'].iloc[-1] > 60:
        #     trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=action, magic=True)
        # elif action == 'sell' and df['RSI'].iloc[-1] < 40:
        #     trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=action, magic=True)
        if tick_signal and avg_signal:
            if action == adx_signal:
                trade_order(symbol=symbol, tp_point=candle_avg*1000, sl_point=candle_avg*1000, lot=0.1, action=action, magic=True)
                write_json(json_dict=orders_json, json_file_name=json_file_name)
            else:
                print('ADX WRONG SIGNAL')
        else:
            print('tick_signal and avg_signal NOT UPTO THE MARK!!')

        # trade_order(symbol=symbol, tp_point=tp2, sl_point=sl, lot=0.1, action=action, magic=False)
        #trade_order(symbol=symbol, tp_point=tp3, sl_point=sl, lot=0.1, action=action, magic=False)


def moving_average_nahid_signal(symbol):
    accepted_symbol_list = ['XAUUSD', 'EURUSD', 'EURJPY', 'USDJPY', 'GBPUSD']
    skip_min = 6
    time_frame = 'M5'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name ='akash_strategies_nahid'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)


    if_duplicate, magic_number, dup_action, positions_df = check_duplicate_orders_magic_v2(symbol)

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['MA_25'] = df['close'].rolling(window=25).mean() ## MA Change
    df['MA_50'] = df['close'].rolling(window=50).mean() ## MA Change
    df['MA_200'] = df['close'].rolling(window=200).mean()

    ## RSI
    df['RSI'] = calculate_rsi(df)

    if if_duplicate:
        stop_logic_nahid(df, symbol)

    if running_trade_status:
        #print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    if (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-2]) \
            or (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
        action = 'buy'
    elif (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-2]) \
            or (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
        action = 'sell'
    else:
        action = None


    # Tick Volume Analysis
    tick_signal = False
    if df['tick_volume'].iloc[-1] > df['tick_volume'].iloc[-2] > df['tick_volume'].iloc[-3]:
        tick_signal = True

    ## ADX CALCULATION
    adx_signal = adx_decision(df)


    # print('RSI --->>',df['RSI'].iloc[-1], '\t tick_volume --->>',df['tick_volume'].iloc[-1], '\t spread --->>',df['spread'].iloc[-1],
    #       '\t real_volume --->>',df['real_volume'].iloc[-1], '\t ADX --->>', adx_signal, '\t\t Final ACTION -->>',action)


    if action:
        # print(symbol, 'ADX Signal -->> ', adx_signal, ' <<--- ORIGINAL --->>', action, ' 200 MA -->>',signal_200ma)
        # if not action == adx_signal == signal_200ma:
        #     return None
        # if not action == adx_signal:
        #     return None

        # trade_order(symbol=symbol, tp_point=None, sl_point=sl, lot=0.1, action=action, magic=True)
        # if action == 'buy' and df['RSI'].iloc[-1] > 60:
        #     trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=action, magic=True)
        # elif action == 'sell' and df['RSI'].iloc[-1] < 40:
        #     trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=action, magic=True)
        if tick_signal:
            if action == adx_signal:
                trade_order_wo_tp_sl(symbol=symbol, lot=0.1, action=action, magic=True)
                write_json(json_dict=orders_json, json_file_name=json_file_name)
            else:
                print('ADX WRONG SIGNAL')
        else:
            print(symbol, 'tick_signal NOT UPTO THE MARK!!')

        # trade_order(symbol=symbol, tp_point=tp2, sl_point=sl, lot=0.1, action=action, magic=False)
        #trade_order(symbol=symbol, tp_point=tp3, sl_point=sl, lot=0.1, action=action, magic=False)


def close_position(symbol, magic_number):
    # Retrieve all open positions
    positions = mt5.positions_get(symbol=symbol)

    # Check if positions are retrieved successfully
    if positions is None:
        print("No positions found, error code =", mt5.last_error())
        return None

    # Convert positions to a DataFrame
    positions_df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

    # Filter the position you want to close by the magic number
    position_to_close = positions_df[positions_df['magic'] == magic_number]

    # Check if the position exists
    if position_to_close.empty:
        print(f"No position found with magic number {magic_number}")

    # Get the ticket number and volume of the position
    ticket = int(position_to_close['ticket'].iloc[0])
    volume = position_to_close['volume'].iloc[0]

    # Create a request to close the position
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL if position_to_close['type'].iloc[0] == 0 else mt5.ORDER_TYPE_BUY,
        "position": ticket,
        "price": mt5.symbol_info_tick(symbol).bid if position_to_close['type'].iloc[
                                                         0] == 0 else mt5.symbol_info_tick(symbol).ask,
        "deviation": 20,
        "magic": magic_number,
        "comment": "Close trade",
        # "type_time": mt5.ORDER_TIME_GTC,
        # "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # Send the close request
    result = mt5.order_send(request)

    # Check the result
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to close position, error code: {result.retcode}")
    else:
        print("Position closed successfully")

################################################################################

def calculate_ema(data, period):
    return data['close'].ewm(span=period, adjust=False).mean()


def moving_average_crossover_old(symbol):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD']
    skip_min = 2
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name = 'akash_strategies_ma_ema'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        #print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    # order_count = get_order_positions_count(symbol)
    #
    # if order_count > 0:
    #     print('Multiple ORDER ', symbol)
    #     return None

    # if_duplicate, magic_number, dup_action, positions_df = check_duplicate_orders_magic_v2(symbol)

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['EMA_15'] = calculate_ema(df, 15)
    df['MA_50'] = df['close'].rolling(window=25).mean()
    df['EMA_100'] = calculate_ema(df, 50)

    '''100 er upor 50 ase, ar 50 er sathe 15 cross kore upore gese , buy . 

    100 er nichee ase 50, 50 er sathe 15 cross kore niche gese , sell. 
    
    take small profit.'''
    action = None

    if df['MA_50'].iloc[-1] > df['EMA_100'].iloc[-1]:
        ## BUY
        ## 100 er upor 50 ase, ar 50 er sathe 15 cross kore upore gese , buy
        if df['EMA_15'].iloc[-2] < df['MA_50'].iloc[-1] < df['EMA_15'].iloc[-1]:
            action = 'buy'

    elif df['MA_50'].iloc[-1] < df['EMA_100'].iloc[-1]:
        ## SELL
        ## 100 er nichee ase 50, 50 er sathe 15 cross kore niche gese , sell
        if df['EMA_15'].iloc[-2] > df['MA_50'].iloc[-1] > df['EMA_15'].iloc[-1]:
            action = 'sell'


    tp_dict = {
        'EURUSD': 30,
        'AUDUSD': 30,
        'GBPUSD': 30,
        'USDCAD': 30,
        'USDJPY': 30,
        'EURGPB': 30,
        'USDCHF': 30,
        'XAUUSD': 1000
    }

    sl_dict = {
        'EURUSD': 30,
        'AUDUSD': 30,
        'GBPUSD': 30,
        'USDCAD': 30,
        'USDJPY': 30,
        'EURGPB': 30,
        'USDCHF': 30,
        'XAUUSD': 1000
    }


    sl = sl_dict[symbol]
    tp = tp_dict[symbol]

    if action:

        adx_bool = check_adx(data=df, period=14)

        print(symbol, action, 'ADX', adx_bool, df['EMA_15'].iloc[-1], df['MA_50'].iloc[-1], df['EMA_100'].iloc[-1])

        if not adx_bool:
            return None

        trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=action, magic=True)

        write_json(json_dict=orders_json, json_file_name=json_file_name)


################################################################################


# def calculate_rsi(data, window):
#     delta = data['close'].diff()
#     gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
#     loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
#
#     rs = gain / loss
#     rsi = 100 - (100 / (1 + rs))
#
#     return rsi


# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['close'].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def rsi_ma15(symbol):
    accepted_symbol_list = ['XAUUSD']
    skip_min = 2
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    # order_count = get_order_positions_count(symbol)
    #
    # if order_count > 0:
    #     print('Multiple ORDER ', symbol)
    #     return None

    json_file_name = 'akash_strategies_ma_rsi'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        # print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['MA_15'] = df['close'].rolling(window=15).mean()
    df['MA_50'] = df['close'].rolling(window=50).mean()
    df['RSI'] = calculate_rsi(df, 14)

    prices = get_current_price(symbol)

    action = None

    if df['RSI'].iloc[-1] >= 65 and df['RSI'].iloc[-2] >= 65:
        if df['RSI'].iloc[-1] > df['RSI'].iloc[-2]:
            if prices['bid_price'] > df['MA_15'].iloc[-1]:
                action = 'buy'
    elif df['RSI'].iloc[-1] <= 35 and df['RSI'].iloc[-2] <= 35:
        if df['RSI'].iloc[-1] < df['RSI'].iloc[-2]:
            if prices['ask_price'] < df['MA_15'].iloc[-1]:
                action = 'sell'


    # if df['RSI'].iloc[-1] >= 65:
    #     if df['RSI'].iloc[-1] > df['RSI'].iloc[-2]:
    #         if prices['bid_price'] > df['MA_15'].iloc[-1]:
    #             action = 'buy'
    # elif df['RSI'].iloc[-1] <= 35:
    #     if df['RSI'].iloc[-1] < df['RSI'].iloc[-2]:
    #         if prices['ask_price'] < df['MA_15'].iloc[-1]:
    #             action = 'sell'

    # if df['RSI'].iloc[-1] >= 65:
    #     if df['RSI'].iloc[-2] > df['RSI'].iloc[-3] and df['RSI'].iloc[-3] > df['RSI'].iloc[-4]:
    #         if prices['bid_price'] > df['MA_15'].iloc[-1]:
    #             action = 'buy'
    # elif df['RSI'].iloc[-1] <= 35:
    #     if df['RSI'].iloc[-2] < df['RSI'].iloc[-3] and df['RSI'].iloc[-3] < df['RSI'].iloc[-4]:
    #         if prices['ask_price'] < df['MA_15'].iloc[-1]:
    #             action = 'sell'

    ## Current Candle
    # if (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-2]) \
    #         or (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
    #     if df['RSI'].iloc[-1] >= 60:
    #         action = 'buy'
    # elif (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-2]) \
    #         or (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
    #     if df['RSI'].iloc[-1] <= 40:
    #         action = 'sell'
    # else:
    #     action = None

    # if df['RSI'].iloc[-1] > df['RSI'].iloc[-2] and df['RSI'].iloc[-1] > df['RSI'].iloc[-3] and df['RSI'].iloc[-1] > df['RSI'].iloc[-4]:
    #     if df['MA_15'].iloc[-1] > df['MA_15'].iloc[-4]:
    #         action = 'buy'
    # elif df['RSI'].iloc[-1] < df['RSI'].iloc[-2] and df['RSI'].iloc[-1] < df['RSI'].iloc[-3] and df['RSI'].iloc[-1] < df['RSI'].iloc[-4]:
    #     if df['MA_15'].iloc[-1] < df['MA_15'].iloc[-4]:
    #         action = 'sell'

    if df['MA_15'].iloc[-1] > df['MA_15'].iloc[-2] and df['MA_15'].iloc[-2] > df['MA_15'].iloc[-3] and df['MA_15'].iloc[-3] > df['MA_15'].iloc[-4]:
        if df['RSI'].iloc[-1] > df['RSI'].iloc[-2]:
            action = 'buy'
    elif df['MA_15'].iloc[-1] < df['MA_15'].iloc[-2] and df['MA_15'].iloc[-2] < df['MA_15'].iloc[-3] and df['MA_15'].iloc[-3] < df['MA_15'].iloc[-4]:
        if df['RSI'].iloc[-1] < df['RSI'].iloc[-2]:
            action = 'sell'

    tp = 800
    sl = 500

    print('RSI ==> ', df['RSI'].iloc[-1], df['RSI'].iloc[-2])

    if action:
        print('RSI ==> ', df['RSI'].iloc[-1], df['RSI'].iloc[-2])
        trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.02, action=action, magic=True)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

def probability_trade(symbol):
    accepted_symbol_list = ['XAUUSD']
    skip_min = 5
    time_frame = 'M5'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    # json_file_name = 'akash_strategies_ma_rsi'
    # running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
    #                                                            json_file_name=json_file_name)
    # if running_trade_status:
    #     # print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
    #     return None

    tp = 1000
    sl = 500

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)
    # Moving Average
    df['MA_5'] = df['close'].rolling(window=5).mean()


    buy_lot = 0.02
    sell_lot = 0.02


    trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=buy_lot, action='buy', magic=True)
    trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=sell_lot, action='sell', magic=True)

    #write_json(json_dict=orders_json, json_file_name=json_file_name)

def rsi_adx(symbol):
    ### LOGIC
    ### adx > 20
    ## RSI 3 candle

    accepted_symbol_list = ['EURUSD', 'EURJPY', 'GBPUSD', 'XAUUSD']
    skip_min = 1
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name = 'akash_adx_rsi'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)


    ## RSI
    df['RSI'] = calculate_rsi(df)

    ## ADX
    adx_status = check_adx(df)

    rsi_signal = None
    if df['RSI'].iloc[-1] > df['RSI'].iloc[-2] > df['RSI'].iloc[-3]:
        rsi_signal = 'buy'
    elif df['RSI'].iloc[-1] < df['RSI'].iloc[-2] < df['RSI'].iloc[-3]:
        rsi_signal = 'sell'


    ## 44 MA
    df['MA_44'] = df['close'].rolling(window=44).mean()

    ma_signal = None
    if df['close'].iloc[-1] > df['MA_44'].iloc[-1]:
        ma_signal = 'buy'
    elif df['close'].iloc[-1] < df['MA_44'].iloc[-1]:
        ma_signal = 'sell'

    ## AVG Candle
    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] +
                df['high'].iloc[
                    -5] + df['high'].iloc[-6]) / 7
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] +
               df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 7

    avg_candle_size = avg_high - avg_low

    ## 0.8 == 800
    tp = avg_candle_size * 1000
    sl = avg_candle_size * 1000

    # tp = 1200
    # sl = 800

    print(symbol, ' ## RSI -->> ', rsi_signal, 'ADX -->> ',adx_status, 'MA_44 --> ',ma_signal, 'SL-->>', sl, 'TP-->>', tp)

    if avg_candle_size < 0.6:
        return

    if rsi_signal:
        if adx_status:
            if rsi_signal == ma_signal:
                trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=rsi_signal, magic=True)
                write_json(json_dict=orders_json, json_file_name=json_file_name)

def ma_adx_rsi(symbol):
    '''AM50 > buy
    MA50 < sell
    ADX > 20
    AVG ADX (1,2) > AVG ADX (3,4) -> TRADE OK
    RSI AVG (1,2) > RSI AVG(3,4) —> BUY
    RSI AVG (1,2) < RSI AVG(3,4) —> SELL'''

    accepted_symbol_list = ['EURUSD', 'EURJPY', 'GBPUSD', 'XAUUSD']
    json_file_name = 'akash_ma_adx_rsi'
    time_frame = 'M1'
    skip_min = 2
    trade_code = 1

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=trade_code)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    ## RSI
    df['RSI'] = calculate_rsi(df)

    ## ADX : +DI -DI ADX
    df = create_adx(df)

    ## 50 MA
    df['MA_50'] = df['close'].rolling(window=50).mean()

    rsi_cur_avg = (df['RSI'].iloc[-1] + df['RSI'].iloc[-2]) / 2
    rsi_prev_avg = (df['RSI'].iloc[-2] + df['RSI'].iloc[-3]) / 2

    adx_cur_avg = (df['ADX'].iloc[-1] + df['ADX'].iloc[-2]) / 2
    adx_prev_avg = (df['ADX'].iloc[-2] + df['ADX'].iloc[-3]) / 2

    adx_cur = df['ADX'].iloc[-1]

    ma_signal = None
    rsi_signal = None

    if adx_cur > 20:
         if adx_cur_avg > adx_prev_avg:
            # ADX Trade OK
            if df['close'].iloc[-1] > df['MA_50'].iloc[-1]:
                ma_signal = 'buy'
            elif df['close'].iloc[-1] < df['MA_50'].iloc[-1]:
                ma_signal = 'sell'

            if rsi_cur_avg > rsi_prev_avg:
               # BUY
                rsi_signal = 'buy'
            elif rsi_cur_avg < rsi_prev_avg:
                rsi_signal = 'sell'


    print('-----------------------------------------------------------------------------------------------------------')

    if rsi_signal:
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df)

        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=rsi_signal, magic=True, code=6, MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame,  MAGIC_NUMBER, avg_candle_size, rsi_signal, tp, sl, 'ma_adx_rsi', data]
        add_csv(data_lst)

def moving_average_crossover_15_100(symbol):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY']
    skip_min = 2
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name = 'akash_strategies_ma_ema_15_100'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        #print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    # Moving Average
    df['EMA_15'] = calculate_ema(df, 15)
    df['MA_100'] = df['close'].rolling(window=100).mean()

    action = None
    if df['EMA_15'].iloc[-1] > df['MA_100'].iloc[-1] and df['EMA_15'].iloc[-3] < df['MA_100'].iloc[-1]:
        action = 'buy'
    elif df['EMA_15'].iloc[-1] < df['MA_100'].iloc[-1] and df['EMA_15'].iloc[-3] > df['MA_100'].iloc[-1]:
        action = 'sell'

    # Average Candle Size
    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[
        -5] + df['high'].iloc[-6]) / 7
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 7

    avg_candle_size = avg_high - avg_low

    df = create_adx(df)

    tp_multi = 6
    sl_multi = 2

    if df['ADX'].iloc[-1] < 23:
        print(symbol, 'LOW ON ADX', df['ADX'].iloc[-1])
        return None
    elif (df['ADX'].iloc[-2] - df['ADX'].iloc[-3]) < 0.8:
        print(symbol, "ADX falling")
        return

    # elif df['ADX'].iloc[-1] > 20 and df['ADX'].iloc[-1] < 30:
    #     tp_multi = 3
    #     sl_multi = 1.5
    # elif df['ADX'].iloc[-1] > 30: # and df['ADX'].iloc[-1] < 40:
    #     tp_multi = 4
    #     sl_multi = 2
    # elif df['ADX'].iloc[-1] > 40:
    #     tp_multi = 8
    #     sl_multi = 2
    else:
        tp_multi = 2
        sl_multi = 2

    if df['+DI'].iloc[-1] > df['-DI'].iloc[-1]:
        adx_signal = 'buy'
    elif df['+DI'].iloc[-1] < df['-DI'].iloc[-1]:
        adx_signal = 'buy'
    else:
        adx_signal = None

    avg_candle_size, sl, tp = get_avg_candle_size(symbol, df)


    lot = 0.1

    print(symbol, '## TP -->', tp,  '## SL -->', sl,  '## AVG -->', avg_candle_size,  '## ACTION -->', action)
    print('ADX -->', df['ADX'].iloc[-1], 'tp_multi -->', tp_multi)
    print('-----------------------------------------------------------------------------------------')
    if action:
        if action == adx_signal:
            MAGIC_NUMBER = get_magic_number()
            trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=8, MAGIC_NUMBER=MAGIC_NUMBER)
            write_json(json_dict=orders_json, json_file_name=json_file_name)

            data_lst = [symbol, time_frame,  MAGIC_NUMBER, avg_candle_size, action, tp, sl, df['ADX'].iloc[-1], ]
            add_csv(data_lst)


def get_avg_candle_size(symbol, df, tp_multi, sl_multi):

    avg_high = (df['high'].iloc[-7] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[
        -5] + df['high'].iloc[-6]) / 6
    avg_low = (df['low'].iloc[-7] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 6

    print(df['close'].iloc[-2], df['close'].iloc[-3],df['close'].iloc[-4],df['close'].iloc[
        -5],df['close'].iloc[-6], df['close'].iloc[-7])
    print(df['open'].iloc[-2], df['open'].iloc[-3], df['open'].iloc[-4], df['open'].iloc[-5],
               df['open'].iloc[-6], df['open'].iloc[-7])
    avg_candle_size = avg_high - avg_low
    if avg_candle_size < 0:
        avg_candle_size = avg_candle_size * -1

    print(symbol,"AVERAGE CANDLE SIZE --> ",avg_candle_size)
    if symbol == 'XAUUSD':
        ## 0.8 == 800
        tp = avg_candle_size * 1000 * tp_multi
        sl = avg_candle_size * 1000 * sl_multi #+ df['spread'].iloc[-1]

        if sl < 300:
            print('LOW SL')
            return None, None, None

    elif symbol == 'EURUSD':
        ## 0.00016 = 16
        tp = avg_candle_size * 100000 * tp_multi
        sl = avg_candle_size * 100000 * sl_multi #+ df['spread'].iloc[-1]
        print(tp, sl)

        if sl < df['spread'].iloc[-1]+10:
            print('LOW SL')
            return None, None, None

    elif symbol == 'USDJPY':
        ## 0.004857142857133567 = 48
        tp = avg_candle_size * 10000 * tp_multi
        sl = avg_candle_size * 10000 * sl_multi #+ df['spread'].iloc[-1]

        if sl < df['spread'].iloc[-1]+10:
            print('LOW SL')
            return None, None, None
    elif symbol == 'GBPUSD':
        ## 0.00023 = 23
        tp = avg_candle_size * 100000 * tp_multi
        sl = avg_candle_size * 100000 * sl_multi #+ df['spread'].iloc[-1]

        if sl < df['spread'].iloc[-1]+10:
            print('LOW SL')
            return None, None, None

    elif symbol == 'EURJPY':
        ##  0.0034285714285715585 = 34
        tp = avg_candle_size * 10000 * tp_multi
        sl = avg_candle_size * 10000 * sl_multi #+ df['spread'].iloc[-1]

        if sl < df['spread'].iloc[-1]+10:
            print('LOW SL')
            return None, None, None
    else:
        sl = 100
        tp = 400
    print(symbol, 'TP', tp, 'SL', sl)
    return avg_candle_size, sl, tp


def line_from_points(P, Q):
    # Calculate the coefficients A, B, C for the line equation Ax + By = C
    A = Q[1] - P[1]  # y2 - y1
    B = P[0] - Q[0]  # x1 - x2
    C = A * P[0] + B * P[1]  # A*x1 + B*y1
    return A, B, C


def find_intersection(P1, Q1, P2, Q2, lim):
    # Get the line equations Ax + By = C for both lines
    A1, B1, C1 = line_from_points(P1, Q1)
    A2, B2, C2 = line_from_points(P2, Q2)

    # Calculate the determinant
    determinant = A1 * B2 - A2 * B1
    #print(determinant)
    if determinant == 0:
        return "not cross"
    else:
        # Using Cramer's rule to find the intersection point (x, y)
        x = (C1 * B2 - C2 * B1) / determinant
        y = (A1 * C2 - A2 * C1) / determinant
        if (x <= lim):
            return "not cross"
        else:
            return x, y


def Ma(prices):
    a = prices['close'].rolling(window=50).mean()
    return a


def Ema(prices):
    a = prices['close'].ewm(span=5, adjust=False).mean()
    return a


def stop_logic_nahid(ticks_frame1, symbol):
    positions = mt5.positions_get(symbol=symbol)

    a = Ma(ticks_frame1)
    b = Ema(ticks_frame1)
    P1 = (0, b.iloc[-7])
    Q1 = (7, b.iloc[-1])
    # print(P1, " ", Q1)
    P2 = (0, a.iloc[-7])
    Q2 = (7, a.iloc[-1])
    # print(P2, " ", Q2)
    intersection_point = find_intersection(P1, Q1, P2, Q2, 7)
    # print(intersection_point)
    if intersection_point != 'not cross':
        print(symbol, ' ## ## # Forced off !@!@@!@!@@!@@! @!@ !@!@ !@! @ !@!@ !@ !@!@ !@')

        for position in positions:
            print(position.profit)
            mt5.Close(symbol, ticket=position.ticket)


def wilder_smoothing(values, period):
    smoothed = np.zeros_like(values)
    smoothed[period - 1] = np.sum(values[:period])
    for i in range(period, len(values)):
        smoothed[i] = (smoothed[i - 1] - (smoothed[i - 1] / period) + values[i])
    return smoothed


def calculate_adx_new(data, period=14):
    # Calculate TR (True Range)
    data['TR'] = np.maximum(data['high'] - data['low'],
                            np.maximum(abs(data['high'] - data['close'].shift(1)),
                                       abs(data['low'] - data['close'].shift(1))))

    # Calculate +DM and -DM
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           np.maximum(data['high'] - data['high'].shift(1), 0), 0)
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           np.maximum(data['low'].shift(1) - data['low'], 0), 0)

    # Apply Wilder's smoothing for TR, +DM, and -DM
    data['TR_smoothed'] = wilder_smoothing(data['TR'], period)
    data['+DM_smoothed'] = wilder_smoothing(data['+DM'], period)
    data['-DM_smoothed'] = wilder_smoothing(data['-DM'], period)

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smoothed'] / data['TR_smoothed'])
    data['-DI'] = 100 * (data['-DM_smoothed'] / data['TR_smoothed'])

    # Calculate DX (Directional Movement Index)
    data['DX'] = 100 * abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI'])

    data['ADX'] = data['DX'].rolling(window=period).mean()


    return data


def adx_slop(symbol):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'EURJPY']
    skip_min = 6
    time_frame = 'M5'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    json_file_name = 'akash_strategies_adx_meth'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        # print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    df = calculate_adx_new(df)

    cur_dx = -2
    print(symbol, '+DI',df['+DI'].iloc[cur_dx], '-DI', df['-DI'].iloc[cur_dx], df['+DI'].iloc[cur_dx] - df['+DI'].iloc[cur_dx-1], df['-DI'].iloc[cur_dx] - df['-DI'].iloc[cur_dx-1])
    if (df['+DI'].iloc[cur_dx] - df['+DI'].iloc[cur_dx-1])>0 and (df['-DI'].iloc[cur_dx] - df['-DI'].iloc[cur_dx-1])<0 and \
            (df['+DI'].iloc[cur_dx]<df['-DI'].iloc[cur_dx]):
        adx_signal = 'buy'
    elif (df['+DI'].iloc[cur_dx] - df['+DI'].iloc[cur_dx-1])<0 and (df['-DI'].iloc[cur_dx] - df['-DI'].iloc[cur_dx-1])>0 and \
            (df['+DI'].iloc[cur_dx]>df['-DI'].iloc[cur_dx]):
        adx_signal = 'sell'
    else:
        adx_signal = None


    lot = 0.1

    if adx_signal:
        avg_candle_size, sl, tp = get_avg_candle_size(symbol=symbol, df=df, tp_multi=1, sl_multi=1)

        print(symbol, '## TP -->', tp, '## SL -->', sl, '## AVG -->', avg_candle_size, '## ACTION -->', adx_signal)
        print('ADX -->', df['ADX'].iloc[-1])
        print('-----------------------------------------------------------------------------------------')

        if not avg_candle_size:
            return

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=adx_signal, magic=True, code=8,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, adx_signal, tp, sl, df['ADX'].iloc[cur_dx], ]
        add_csv(data_lst)


def ADX_stakoverflow(data: pd.DataFrame, period: int):
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

    return df