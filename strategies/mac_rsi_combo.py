from mt5_utils import get_live_data
from common_functions import check_duplicate_orders, write_json


def mac_rsi(symbol, short_window=50, long_window=200):

    accepted_symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'USDCAD', 'USDJPY', 'EURGPB']
    json_file_name = 'mac_rsi'

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    # running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=60,
    #                                                            json_file_name=json_file_name)
    # if running_trade_status:
    #     return None

    df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=100)



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
        return 'buy'
    elif (df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and
          df['short_ma'].iloc[i-1] > df['long_ma'].iloc[i-1] and
          df['rsi_divergence'].iloc[i] == -1):
        #write_json(json_dict=orders_json, json_file_name=json_file_name)
        return 'sell'
    else:
        return None