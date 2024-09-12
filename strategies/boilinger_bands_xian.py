from akash import calculate_rsi, adx_decision, get_avg_candle_size, create_adx, adx_decision_prev
from mt5_utils import get_live_data, trade_order, trade_order_wo_sl, trade_order_magic, get_magic_number, \
    trade_order_wo_tp_sl, get_all_positions, clsoe_position
from common_functions import check_duplicate_orders_time, write_json, check_duplicate_orders_magic, add_csv
import talib

def calculate_ADX_updated(df):
    # Calculate ADX, +DI, and -DI
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['+DI'] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
    df['-DI'] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=14)

    return df

def boil_xian(symbol, window=20, num_std=2):

    accepted_symbol_list = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    json_file_name = 'boil_xian'
    time_frame = 'M5'
    skip_min = 6

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=7)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])

    curr_idx = -2
    prev_idx = -3

    # action = None
    # if df['high'].iloc[curr_idx] > df['upper_band'].iloc[curr_idx]:
    #     if df['open'].iloc[curr_idx] > df['close'].iloc[curr_idx]:
    #         action = 'sell'
    #         #band_diff = df['upper_band'].iloc[curr_idx] - df['middle_band'].iloc[curr_idx]
    # elif df['low'].iloc[curr_idx] < df['lower_band'].iloc[curr_idx]:
    #     if df['open'].iloc[curr_idx] < df['close'].iloc[curr_idx]:
    #         action = 'buy'
    #         #band_diff = df['middle_band'].iloc[curr_idx] - df['lower_band'].iloc[curr_idx]

    # if df['low'].iloc[-1] < df['lower_band'].iloc[curr_idx] and df['open'].iloc[-1] < df['close'].iloc[-1]:
    #     action = 'buy'
    # elif df['high'].iloc[-1] < df['upper_band'].iloc[curr_idx] and df['open'].iloc[-1] > df['close'].iloc[-1]:
    #     action = 'sell'


    high_band_diff = df['close'].iloc[curr_idx] - df['middle_band'].iloc[curr_idx]
    low_band_diff = df['middle_band'].iloc[curr_idx] - df['close'].iloc[curr_idx]

    if high_band_diff > 0:
        band_diff = high_band_diff
    else:
        band_diff = low_band_diff

    ## MIDDLE BAND CROSS
    # middle_band_signal = None
    # adx_signal = adx_decision(df)
    #
    # if df['high'].iloc[-1] > df['middle_band'].iloc[-1] and df['close'].iloc[-1] < df['middle_band'].iloc[-1]:
    #     middle_band_signal = 'sell'
    # elif df['low'].iloc[-1] < df['middle_band'].iloc[-1] and df['close'].iloc[-1] > df['middle_band'].iloc[-1]:
    #     middle_band_signal = 'sell'
    #
    # if not middle_band_signal == adx_signal:
    #     middle_band_signal = None

    ## AVG Candle

    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[
        -5] + df['high'].iloc[-6]) / 7
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 7

    avg_candle_size = avg_high - avg_low

    # # Tick Volume Analysis
    # tick_signal = False
    # if df['tick_volume'].iloc[-1] > df['tick_volume'].iloc[-2] > df['tick_volume'].iloc[-3]:
    #     tick_signal = True

    ## RSI
    # df['RSI'] = calculate_rsi(df)

    # rsi_action = None
    # if df['RSI'].iloc[curr_idx] >= 65:
    #     ## Overbought
    #     if df['RSI'].iloc[curr_idx] < df['RSI'].iloc[prev_idx]:
    #         rsi_action = 'sell'
    # elif df['RSI'].iloc[curr_idx] <= 35:
    #     ## Oversold
    #     if df['RSI'].iloc[curr_idx] > df['RSI'].iloc[prev_idx]:
    #         rsi_action = 'buy'

    if symbol == 'XAUUSD':
        ## 0.8 == 800
        avg_tp = avg_candle_size * 1000 * 1.5
        avg_sl = avg_candle_size * 1000 * 1.5 + df['spread'].iloc[-1]

    elif symbol == 'EURUSD':
        avg_tp = avg_candle_size * 100000 * 1.5
        avg_sl = avg_candle_size * 100000 * 1.5 + df['spread'].iloc[-1]

    elif symbol == 'GBPUSD':
        avg_tp = avg_candle_size * 100000 * 1.5
        avg_sl = avg_candle_size * 100000 * 1.5 + df['spread'].iloc[-1]

    elif symbol == 'USDJPY':
        avg_tp = avg_candle_size * 1000 * 1.5
        avg_sl = avg_candle_size * 1000 * 1.5 + df['spread'].iloc[-1]


    if symbol == 'XAUUSD':
        ## 0.8 == 800
        diff_tp = band_diff * 1000 * 1.5
        diff_sl = band_diff * 1000 * 1.5 + df['spread'].iloc[-1]

    elif symbol == 'EURUSD':
        diff_tp = band_diff * 100000 * 1.5
        diff_sl = band_diff * 100000 * 1.5 + df['spread'].iloc[-1]

    elif symbol == 'GBPUSD':
        diff_tp = band_diff * 100000 * 1.5
        diff_sl = band_diff * 100000 * 1.5 + df['spread'].iloc[-1]

    elif symbol == 'USDJPY':
        diff_tp = band_diff * 1000 * 1.5
        diff_sl = band_diff * 1000 * 1.5 + df['spread'].iloc[-1]

    # if avg_tp < diff_tp:
    #     tp = avg_tp
    #     sl = avg_sl
    # else:
    #     tp = diff_tp
    #     sl = diff_s

    tp = avg_tp
    sl = avg_sl

    # print(symbol, ' ## AVG -->>',avg_candle_size,'## TP -->',tp,'## SL -->',sl, '## RSI -->>', df['RSI'].iloc[-1], rsi_action, '## Tick Power -->>',
    #       tick_signal, '## TP Diff-->> ', band_diff, '## Spread -->', df['spread'].iloc[-1])
    #print('-----------------------------------------------------------------------------------------------------------')

    df = calculate_ADX_updated(df)

    # if df['+DI'].iloc[curr_idx] > df['-DI'].iloc[curr_idx]:
    #     adx_signal = 'buy'
    # elif df['+DI'].iloc[curr_idx] < df['-DI'].iloc[curr_idx]:
    #     adx_signal = 'sell'
    # else:
    #     adx_signal = None
    if df['ADX'].iloc[curr_idx] > 20:
        if df['+DI'].iloc[curr_idx] - df['+DI'].iloc[curr_idx-1] < 0:
            adx_signal = 'sell'
        elif df['-DI'].iloc[curr_idx] - df['-DI'].iloc[curr_idx-1] < 0:
            adx_signal = 'buy'
        else:
            adx_signal = None
    else:
        adx_signal = None


    if adx_signal: #action and

        print(symbol, 'boil_xian')
        print(symbol, adx_signal, '+DI', df['+DI'].iloc[curr_idx], '-DI', df['-DI'].iloc[curr_idx])
        lot = 0.1

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=adx_signal, magic=True, code=7,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = {

        }
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, adx_signal, tp, sl, 'boil_xian', data]
        add_csv(data_lst)

    #print('-----------------------------------------------------------------------------------------------------------')

def boil_xian_akash(symbol, window=20, num_std=2):
    accepted_symbol_list = ['XAUUSD']
    json_file_name = 'boil_xian_akash'
    time_frame = 'M5'
    skip_min = 6
    curr_idx = -2


    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=7)

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    if running_trade_status_time or running_trade_status_magic:
        df = create_adx(df)
        trade_run_status =True
        if df['-DI'].iloc[curr_idx] < df['+DI'].iloc[curr_idx]:
            if df['-DI'].iloc[curr_idx] - df['-DI'].iloc[curr_idx-1] > 0:
                # Stop trade
                trade_run_status = False
        elif df['-DI'].iloc[curr_idx] > df['+DI'].iloc[curr_idx]:
            if df['+DI'].iloc[curr_idx] - df['+DI'].iloc[curr_idx-1] > 0:
                # Stop trade
                trade_run_status = False

        if not trade_run_status:
            positions = get_all_positions(symbol)

            for position in positions:
                print(position.profit)
                print(position)
                clsoe_position(symbol, ticket=position.ticket)

        return None


    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])


    action = None
    if df['close'].iloc[curr_idx] > df['upper_band'].iloc[curr_idx]:
            action = adx_decision(df)
    elif df['close'].iloc[curr_idx] < df['lower_band'].iloc[curr_idx]:
            action = adx_decision(df)


    print('ADX ACTION >> ', action)

    if action:
        print(symbol, 'boil_xian_akash DONE')
        lot = 0.09

        #MAGIC_NUMBER = get_magic_number()
        trade_order_wo_tp_sl(symbol=symbol, lot=lot, action=action, magic=False)
        write_json(json_dict=orders_json, json_file_name=json_file_name)
