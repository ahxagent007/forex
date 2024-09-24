from xian import take_the_profit
from mt5_utils import get_live_data, get_magic_number, trade_order_magic
from common_functions import check_duplicate_orders, write_json, add_csv, check_duplicate_orders_time, \
    check_duplicate_orders_magic, check_duplicate_orders_is_time
from akash import get_avg_candle_size


def ichimoku_stochastic(symbol):

    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'EURGPB', 'XAUUSD']
    json_file_name = 'ichimoku_stochastic'
    skip_min = 6
    time_frame = 'M5'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json, is_time = check_duplicate_orders_is_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=77)
    if running_trade_status_time or running_trade_status_magic:
        # if not is_time:
        #     take_the_profit(symbol)
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

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
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'buy'
    elif (df['tenkan_sen'].iloc[i] < df['kijun_sen'].iloc[i] and
          df['close'].iloc[i] < df['senkou_span_a'].iloc[i] and
          df['close'].iloc[i] < df['senkou_span_b'].iloc[i] and
          df['%K'].iloc[i] > 80 and df['%D'].iloc[i] > 80 and
          df['%K'].iloc[i] < df['%D'].iloc[i]):
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'sell'
    else:
        action = None


    if action:
        print(symbol, 'ichimoku_stochastic')
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, 2, 2)

        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=5,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, action, tp, sl, 'ichimoku_stochastic', data]
        add_csv(data_lst)

