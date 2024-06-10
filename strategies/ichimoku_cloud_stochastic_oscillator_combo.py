from mt5_utils import get_live_data
from common_functions import check_duplicate_orders, write_json

def ichimoku_stochastic(symbol):

    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'EURGPB']
    json_file_name = 'ichimoku_stochastic'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=30,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        return None

    df = get_live_data(symbol=symbol, time_frame='M30', prev_n_candles=100)

    # Function to calculate Ichimoku Cloud

    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2

    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2

    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    df['chikou_span'] = df['close'].shift(-26)



    # Function to calculate Stochastic Oscillator
    k_window = 14
    d_window = 3

    df['min_low'] = df['low'].rolling(window=k_window).min()
    df['max_high'] = df['high'].rolling(window=k_window).max()
    df['%K'] = (df['close'] - df['min_low']) / (df['max_high'] - df['min_low']) * 100
    df['%D'] = df['%K'].rolling(window=d_window).mean()


    #generate Ichimoku Cloud + Stochastic Oscillator signals

    df['signal'] = 0
    i = -1

    if (df['tenkan_sen'].iloc[i] > df['kijun_sen'].iloc[i] and
            df['close'].iloc[i] > df['senkou_span_a'].iloc[i] and
            df['close'].iloc[i] > df['senkou_span_b'].iloc[i] and
            df['%K'].iloc[i] < 20 and df['%D'].iloc[i] < 20 and
            df['%K'].iloc[i] > df['%D'].iloc[i]):
        write_json(json_dict=orders_json, json_file_name=json_file_name)
        return 'buy'
    elif (df['tenkan_sen'].iloc[i] < df['kijun_sen'].iloc[i] and
          df['close'].iloc[i] < df['senkou_span_a'].iloc[i] and
          df['close'].iloc[i] < df['senkou_span_b'].iloc[i] and
          df['%K'].iloc[i] > 80 and df['%D'].iloc[i] > 80 and
          df['%K'].iloc[i] < df['%D'].iloc[i]):
        write_json(json_dict=orders_json, json_file_name=json_file_name)
        return 'sell'
    else:
        return None
