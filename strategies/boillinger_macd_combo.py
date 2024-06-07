from mt5_utils import get_live_data
from common_functions import check_duplicate_orders, write_json

def boil_macd(symbol, window=20, num_std=2):

    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
    json_file_name = 'boil_macd'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=60,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        return None

    df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=100)

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

    if df['macd'].iloc[i] > df['signal_line'].iloc[i] and df['close'].iloc[i] < df['lower_band'].iloc[i]:
        write_json(json_dict=orders_json, json_file_name=json_file_name)
        return 'buy'
    elif df['macd'].iloc[i] < df['signal_line'].iloc[i] and df['close'].iloc[i] > df['upper_band'].iloc[i]:
        write_json(json_dict=orders_json, json_file_name=json_file_name)
        return 'sell'
    else:
        return None
