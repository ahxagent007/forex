import numpy as np
import pandas as pd

from common_functions import check_duplicate_orders_magic_v2, check_duplicate_orders, write_json, check_duplicate_orders_time, check_duplicate_orders_magic
from mt5_utils import get_live_data, trade_order, get_current_price, get_order_positions_count, trade_order_magic
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

    #print('ADX VALUE -->>',data['ADX'].iloc[-1], data['+DI'].iloc[-1], data['-DI'].iloc[-1])
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

    if data['+DI'].iloc[-1] > data['-DI'].iloc[-1]:
        return 'buy'
    else:
        return 'sell'


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


def moving_average_crossover(symbol):
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

    accepted_symbol_list = ['XAUUSD']
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

    accepted_symbol_list = ['XAUUSD']
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

    ## AVG Candle
    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[
        -5] + df['high'].iloc[-6]) / 7
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 7

    avg_candle_size = avg_high - avg_low

    ## 0.8 == 800
    tp = avg_candle_size * 1000
    sl = avg_candle_size * 1000

    if tp > 600:
        tp = 600
        sl = 600

    lot = 0.05

    print('ADX -->', adx_cur,'rsi_cur_avg -->', rsi_cur_avg,'rsi_prev_avg -->', rsi_prev_avg,'ma_signal -->',
          ma_signal,'tp -->', tp, 'sl -->', sl)
    print('-----------------------------------------------------------------------------------------------------------')

    if rsi_signal:
        # if ma_signal == rsi_signal:
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=rsi_signal, magic=True, code=trade_code)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

def moving_average_crossover_15_100(symbol):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY']
    skip_min = 5
    time_frame = 'M5'

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
    if df['EMA_15'].iloc[-1] > df['MA_100'].iloc[-1] and df['EMA_15'].iloc[-2] < df['MA_100'].iloc[-2]:
        action = 'buy'
    elif df['EMA_15'].iloc[-1] < df['MA_100'].iloc[-1] and df['EMA_15'].iloc[-2] > df['MA_100'].iloc[-2]:
        action = 'sell'

    # Average Candle Size
    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[
        -5] + df['high'].iloc[-6]) / 7
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 7

    avg_candle_size = avg_high - avg_low

    if symbol == 'XAUUSD':
        ## 0.8 == 800
        tp = avg_candle_size * 1000 * 6
        sl = avg_candle_size * 1000 * 2 #+ df['spread'].iloc[-1]

    elif symbol == 'EURUSD':
        ## 0.00016 = 16
        tp = avg_candle_size * 100000 * 6
        sl = avg_candle_size * 100000 * 2 #+ df['spread'].iloc[-1]
    elif symbol == 'USDJPY':
        ##  0.00017 = 17
        tp = avg_candle_size * 10000 * 6
        sl = avg_candle_size * 10000 * 2 #+ df['spread'].iloc[-1]
    elif symbol == 'GBPUSD':
        ## 0.00023 = 23
        tp = avg_candle_size * 100000 * 6
        sl = avg_candle_size * 100000 * 2 #+ df['spread'].iloc[-1]

    lot = 0.1

    print(symbol, '## TP -->', tp,  '## SL -->', sl,  '## AVG -->', avg_candle_size,  '## ACTION -->', action)
    if action:
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=0)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

