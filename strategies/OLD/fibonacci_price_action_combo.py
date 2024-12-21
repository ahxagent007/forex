from mt5_utils import get_live_data, get_magic_number, trade_order_magic
from common_functions import check_duplicate_orders, write_json, add_csv, check_duplicate_orders_time, \
    check_duplicate_orders_magic
from akash import get_avg_candle_size

def fibonacci_price_action(symbol, lookback=20):
    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'EURGPB', 'XAUUSD']
    json_file_name = 'fibonacci_price_action'
    skip_min = 2
    time_frame = 'M1'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=77)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    #  calculate Fibonacci retracement levels

    df['swing_high'] = df['high'].rolling(window=lookback).max()
    df['swing_low'] = df['low'].rolling(window=lookback).min()

    df['fib_0'] = df['swing_high']
    df['fib_23.6'] = df['swing_high'] - 0.236 * (df['swing_high'] - df['swing_low'])
    df['fib_38.2'] = df['swing_high'] - 0.382 * (df['swing_high'] - df['swing_low'])
    df['fib_50'] = df['swing_high'] - 0.5 * (df['swing_high'] - df['swing_low'])
    df['fib_61.8'] = df['swing_high'] - 0.618 * (df['swing_high'] - df['swing_low'])
    df['fib_100'] = df['swing_low']


    # identify price action patterns (pin bars and engulfing bars)

    df['pin_bar'] = 0
    df['engulfing'] = 0

    for i in range(1, len(df)):
        # Identify Pin Bars
        if (df['high'].iloc[i] - df['close'].iloc[i] > (df['high'].iloc[i] - df['low'].iloc[i]) * 2 / 3 and
                df['close'].iloc[i] > df['open'].iloc[i]):
            #df['pin_bar'].iloc[i] = 1  # Bullish pin bar
            df.loc[i, 'pin_bar'] = 1
        elif (df['close'].iloc[i] - df['low'].iloc[i] > (df['high'].iloc[i] - df['low'].iloc[i]) * 2 / 3 and
              df['close'].iloc[i] < df['open'].iloc[i]):
            #df['pin_bar'].iloc[i] = -1  # Bearish pin bar
            df.loc[i, 'pin_bar'] = -1

        # Identify Engulfing Bars
        if (df['close'].iloc[i] > df['open'].iloc[i] and
                df['close'].iloc[i] > df['open'].iloc[i - 1] > df['close'].iloc[i - 1] > df['open'].iloc[i]):
            #df['engulfing'].iloc[i] = 1  # Bullish engulfing
            df.loc[i, 'engulfing'] = 1
        elif (df['close'].iloc[i] < df['open'].iloc[i] and
              df['close'].iloc[i] < df['open'].iloc[i - 1] < df['close'].iloc[i - 1] < df['open'].iloc[i]):
            #df['engulfing'].iloc[i] = -1  # Bearish engulfingengulfing
            df.loc[i, 'engulfing'] = -1

    # Function to generate signals based on Fibonacci retracement levels and price action patterns

    df['signal'] = 0
    i = -1

    if (df['pin_bar'].iloc[i] == 1 or df['engulfing'].iloc[i] == 1) and (
            df['close'].iloc[i] > df['fib_50'].iloc[i] and df['close'].iloc[i] < df['fib_38.2'].iloc[i]):
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'buy'
    elif (df['pin_bar'].iloc[i] == -1 or df['engulfing'].iloc[i] == -1) and (
            df['close'].iloc[i] < df['fib_50'].iloc[i] and df['close'].iloc[i] > df['fib_61.8'].iloc[i]):
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'sell'
    else:
        action = None

    if action:
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df)

        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=4,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, action, tp, sl, 'fibonacci_price_action', data]
        add_csv(data_lst)

