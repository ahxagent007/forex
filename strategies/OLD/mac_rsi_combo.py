from mt5_utils import get_live_data, get_magic_number, trade_order_magic
from common_functions import check_duplicate_orders, write_json, add_csv, check_duplicate_orders_time, \
    check_duplicate_orders_magic
from akash import get_avg_candle_size


def mac_rsi(symbol, short_window=50, long_window=200):

    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'EURGPB', 'XAUUSD']
    json_file_name = 'mac_rsi'
    skip_min = 2
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



    # Function to calculate moving averages

    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()


    # Function to calculate RSI
    window=14

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Function to identify RSI divergence

    df['rsi_divergence'] = 0
    for i in range(2, len(df)):
        if (df['rsi'].iloc[i] < df['rsi'].iloc[i - 1] < df['rsi'].iloc[i - 2] and
                df['close'].iloc[i] > df['close'].iloc[i - 1] > df['close'].iloc[i - 2]):
            #df['rsi_divergence'].iloc[i] = -1  # Bearish divergence
            df.loc[i, "rsi_divergence"] = -1
        elif (df['rsi'].iloc[i] > df['rsi'].iloc[i - 1] > df['rsi'].iloc[i - 2] and
              df['close'].iloc[i] < df['close'].iloc[i - 1] < df['close'].iloc[i - 2]):
            #df['rsi_divergence'].iloc[i] = 1  # Bullish divergence
            df.loc[i, "rsi_divergence"] = 1

    # Function to generate signals based on Moving Average Crossover + RSI Divergence

    df['signal'] = 0

    i = -1

    if (df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and
        df['short_ma'].iloc[i-1] < df['long_ma'].iloc[i-1] and
        df['rsi_divergence'].iloc[i] == 1):
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'buy'
    elif (df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and
          df['short_ma'].iloc[i-1] > df['long_ma'].iloc[i-1] and
          df['rsi_divergence'].iloc[i] == -1):
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        action = 'sell'
    else:
        action = None

    if action:
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df)

        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=3,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ""
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, action, tp, sl, 'mac_rsi', data]
        add_csv(data_lst)
