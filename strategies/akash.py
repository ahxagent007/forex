import pandas as pd

from common_functions import check_duplicate_orders_magic_v2, check_duplicate_orders, write_json
from mt5_utils import get_live_data, trade_order, get_current_price
import MetaTrader5 as mt5


def moving_average_signal(symbol):
    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'EURGPB', 'USDCHF']
    skip_min = 30
    time_frame = 'M30'

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
        'EURUSD': 400,
        'AUDUSD': 400,
        'GBPUSD': 400,
        'USDCAD': 200,
        'USDJPY': 500,
        'EURGPB': 300,
        'USDCHF': 400
    }

    tp_dict_2 = {
        'EURUSD': 200,
        'AUDUSD': 200,
        'GBPUSD': 200,
        'USDCAD': 100,
        'USDJPY': 150,
        'EURGPB': 150,
        'USDCHF': 200
    }

    tp_dict_3 = {
        'EURUSD': 120,
        'AUDUSD': 100,
        'GBPUSD': 100,
        'USDCAD': 70,
        'USDJPY': 100,
        'EURGPB': 100,
        'USDCHF': 100
    }

    sl = 50
    tp = tp_dict[symbol] #300 #hour chart 500/600
    tp2 = tp_dict_2[symbol] #300 #hour chart 500/600
    tp3 = tp_dict_3[symbol] #300 #hour chart 500/600

    # if (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-2]) \
    #         or (df['MA_50'].iloc[-1] < df['close'].iloc[-1] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
    #     action = 'buy'
    # elif (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-2]) \
    #         or (df['MA_50'].iloc[-1] > df['close'].iloc[-1] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
    #     action = 'sell'
    # else:
    #     action = None
    if (df['MA_50'].iloc[-1] < df['close'].iloc[-2] and df['MA_50'].iloc[-1] > df['close'].iloc[-3]):
        action = 'buy'
    elif (df['MA_50'].iloc[-1] > df['close'].iloc[-2] and df['MA_50'].iloc[-1] < df['close'].iloc[-3]):
        action = 'sell'
    else:
        action = None

    if action:
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
