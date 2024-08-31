from mt5_utils import get_live_data, get_magic_number, trade_order_magic
from common_functions import check_duplicate_orders, write_json, add_csv, check_duplicate_orders_time, \
    check_duplicate_orders_magic
from akash import get_avg_candle_size

def boil_macd(symbol, window=20, num_std=2):

    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'EURGPB', 'XAUUSD']
    json_file_name = 'boil_macd'
    skip_min = 6
    time_frame = 'M5'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=77)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])


    # Function to calculate MACD
    short_window=12
    long_window=26
    signal_window=9

    df['ema_short'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['ema_long'] = df['close'].ewm(span=long_window, adjust=False).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['signal_line'] = df['macd'].ewm(span=signal_window, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['signal_line']

    i = -1
    action = None
    if df['macd'].iloc[i] > df['signal_line'].iloc[i] and df['close'].iloc[i] < df['lower_band'].iloc[i]:
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'buy'
    elif df['macd'].iloc[i] < df['signal_line'].iloc[i] and df['close'].iloc[i] > df['upper_band'].iloc[i]:
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'sell'
    else:
        action = None


    if action:
        print(symbol, 'boil_macd')
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, 6, 3)

        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=2, MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame,  MAGIC_NUMBER, avg_candle_size, action, tp, sl, 'boil_macd', data]
        add_csv(data_lst)
