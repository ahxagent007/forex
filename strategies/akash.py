import numpy as np
import pandas as pd

from common_functions import check_duplicate_orders_magic_v2, check_duplicate_orders, write_json
from mt5_utils import get_live_data, trade_order, get_current_price
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

    #print('ADX VALUE -->>',data['ADX'].iloc[-1])
    adx_min = 25
    if data['ADX'].iloc[-1] >= adx_min:
        #YES TRADE
        if (data['+DI'].iloc[-1] > data['-DI'].iloc[-1]) and (data['+DI'].iloc[-1] > adx_min):
            return 'buy'
        elif (data['-DI'].iloc[-1] > adx_min):
            return 'sell'

    else:
        return None

def moving_average_signal(symbol):
    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD']
    skip_min = 5
    time_frame = 'M5'

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

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    # Moving Average
    df['MA_50'] = df['close'].rolling(window=50).mean()

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


    tp_dict = {
        'EURUSD': 150,
        'AUDUSD': 400,
        'GBPUSD': 100,
        'USDCAD': 200,
        'USDJPY': 500,
        'EURGPB': 300,
        'USDCHF': 400,
        'XAUUSD': 5000
    }

    tp_dict_2 = {
        'EURUSD': 120,
        'AUDUSD': 200,
        'GBPUSD': 80,
        'USDCAD': 100,
        'USDJPY': 150,
        'EURGPB': 150,
        'USDCHF': 200,
        'XAUUSD': 3000
    }

    tp_dict_3 = {
        'EURUSD': 90,
        'AUDUSD': 100,
        'GBPUSD': 50,
        'USDCAD': 70,
        'USDJPY': 100,
        'EURGPB': 100,
        'USDCHF': 100,
        'XAUUSD': 1500
    }

    sl_dict = {
        'EURUSD': 30,
        'AUDUSD': 50,
        'GBPUSD': 30,
        'USDCAD': 20,
        'USDJPY': 50,
        'EURGPB': 50,
        'USDCHF': 50,
        'XAUUSD': 500
    }

    sl = sl_dict[symbol]
    tp = tp_dict[symbol] #300 #hour chart 500/600
    tp2 = tp_dict_2[symbol] #300 #hour chart 500/600
    tp3 = tp_dict_3[symbol] #300 #hour chart 500/600

    if (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-2]) \
            or (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
        action = 'buy'
    elif (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-2]) \
            or (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
        action = 'sell'
    else:
        action = None


    #print(symbol)
    adx_signal = adx_decision(data=df, period=14)

    # if (df['MA_50'].iloc[-1] < df['close'].iloc[-2] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
    #     action = 'buy'
    # elif (df['MA_50'].iloc[-1] > df['close'].iloc[-2] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
    #     action = 'sell'
    # else:
    #     action = None


    if action:
        print(symbol, 'ADX Signal -->> ', adx_signal, ' <<--- ORIGINAL --->>', action)
        if not action == adx_signal:
            return None

        trade_order(symbol=symbol, tp_point=None, sl_point=sl, lot=0.1, action=action, magic=True)
        trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=0.1, action=action, magic=False)
        trade_order(symbol=symbol, tp_point=tp2, sl_point=sl, lot=0.1, action=action, magic=False)
        trade_order(symbol=symbol, tp_point=tp3, sl_point=sl, lot=0.1, action=action, magic=False)

        write_json(json_dict=orders_json, json_file_name=json_file_name)


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
