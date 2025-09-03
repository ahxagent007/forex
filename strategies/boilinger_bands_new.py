import time
import datetime as dt

from news_trade import get_today_forexfactory_news
from mt5_utils import get_live_data, trade_order_price, calculate_lot_size, initialize_mt5, trade_order_wo_tp_sl, \
    close_all_positions, get_open_positions, get_all_positions
from common_functions import check_duplicate_orders_time, check_duplicate_orders_magic, check_duplicate_orders, \
    write_json, check_duplicate_orders_is_time, isNowInTimePeriod, price_distance_percent


def boil_bands_data(symbol, window=14, num_std=2):

    json_file_name = 'boil_xian'
    time_frame = 'M1'
    skip_min = 20

    # running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
    #                                                            json_file_name=json_file_name)

    running_trade_status, orders_json, is_time = check_duplicate_orders_is_time(symbol, skip_min, json_file_name)

    if running_trade_status and is_time:
        no_new_trade = True
        #print('time skip')
    #     return {
    #         'upper_band': None,
    #         'lower_band': None,
    #         'high_band_diff': None,
    #         'low_band_diff': None,
    #         'band_diff': None,
    #         'action': None,
    #         'tp': None,
    #         'sl': None,
    #         'tp_sl_dif': None,
    #         'orders_json': None,
    #         'json_file_name': json_file_name,
    #         'band_trade_close_type': -1
    # }
    else:
        no_new_trade = False

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])

    curr_idx = -1

    high_band_diff = df['close'].iloc[curr_idx] - df['middle_band'].iloc[curr_idx]
    low_band_diff = df['middle_band'].iloc[curr_idx] - df['close'].iloc[curr_idx]

    if high_band_diff > 0:
        band_diff = high_band_diff
    else:
        band_diff = low_band_diff

    tp_sl_dif = band_diff/2

    action = None
    tp = None
    sl = None

    if df['close'].iloc[curr_idx] >= df['upper_band'].iloc[curr_idx]:
        action = 'sell'
        tp = df['close'].iloc[curr_idx] - tp_sl_dif * 2
        sl = df['close'].iloc[curr_idx] + tp_sl_dif
    elif df['close'].iloc[curr_idx] <= df['lower_band'].iloc[curr_idx]:
        action = 'buy'
        tp = df['close'].iloc[curr_idx] + tp_sl_dif * 2
        sl = df['close'].iloc[curr_idx] - tp_sl_dif

    upper_distance = price_distance_percent(df['upper_band'].iloc[curr_idx], df['close'].iloc[curr_idx])
    lower_distance = price_distance_percent(df['lower_band'].iloc[curr_idx], df['close'].iloc[curr_idx])
    print(f'{symbol} ->\tupper: {upper_distance}%\t lower: {lower_distance}%')


    band_trade_close_type = -1

    # if df['close'].iloc[curr_idx] > df['upper_band'].iloc[curr_idx] and df['open'].iloc[curr_idx] < df['upper_band'].iloc[curr_idx]:
    #     # band crossing up
    #     # buy close
    #     band_trade_close_type = 0
    # elif df['close'].iloc[curr_idx] < df['lower_band'].iloc[curr_idx] and df['open'].iloc[curr_idx] > df['lower_band'].iloc[curr_idx]:
    #     # band crossing down
    #     # sell close
    #     band_trade_close_type = 1

    if abs(upper_distance) <= 0.001:
        # action = 'sell'
        # tp = df['close'].iloc[curr_idx] - tp_sl_dif * 2
        # sl = df['close'].iloc[curr_idx] + tp_sl_dif
        band_trade_close_type = 0
    elif abs(lower_distance) <= 0.001:
        # action = 'buy'
        # tp = df['close'].iloc[curr_idx] + tp_sl_dif * 2
        # sl = df['close'].iloc[curr_idx] - tp_sl_dif
        band_trade_close_type = 1

    if no_new_trade:
        return {
            'upper_band': df['upper_band'].iloc[curr_idx],
            'lower_band': df['lower_band'].iloc[curr_idx],
            'high_band_diff': high_band_diff,
            'low_band_diff': low_band_diff,
            'band_diff': band_diff,
            'action': None,
            'tp': tp,
            'sl': sl,
            'tp_sl_dif': tp_sl_dif,
            'orders_json': orders_json,
            'json_file_name': json_file_name,
            'band_trade_close_type': band_trade_close_type
        }

    else:
        return {
            'upper_band': df['upper_band'].iloc[curr_idx],
            'lower_band': df['lower_band'].iloc[curr_idx],
            'high_band_diff': high_band_diff,
            'low_band_diff': low_band_diff,
            'band_diff': band_diff,
            'action': action,
            'tp': tp,
            'sl': sl,
            'tp_sl_dif': tp_sl_dif,
            'orders_json': orders_json,
            'json_file_name': json_file_name,
            'band_trade_close_type': band_trade_close_type
        }



mt5 = initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']
#SYMBOL_LIST = ['BTCUSD']

PREVIOUS_TRADE = {
    'GBPUSD': None,
    'USDCHF': None,
     'USDJPY': None,
     'US30': None,
     'EURGBP': None,
     'AUDUSD': None,
     'XAUUSD': None,
     'EURUSD': None,
    'BTCUSD': None
}

BASE_RISK = 1
# RISK_PERCENT = {
#     'GBPUSD': BASE_RISK,
#     'USDCHF': BASE_RISK,
#      'USDJPY': BASE_RISK,
#      'US30': BASE_RISK,
#      'EURGBP': BASE_RISK,
#      'AUDUSD': BASE_RISK,
#      'XAUUSD': BASE_RISK,
#      'EURUSD': BASE_RISK,
#     'BTCUSD': BASE_RISK
# }
LOTS = {
    'GBPUSD': None,
    'USDCHF': None,
     'USDJPY': None,
     'US30': None,
     'EURGBP': None,
     'AUDUSD': None,
     'XAUUSD': None,
     'EURUSD': None,
    'BTCUSD': None    
}
fixed_lot = 5.0

START_HOUR = 6 #0
START_MIN = 0
END_HOUR = 22 #16
END_MIN = 0

FOREX_NEWS_HOUR = 0
NEWS_DF = None

def check_news_session_time(symbol):
    TOKYO_ORB_START_HOUR = 6 #0  # 6
    TOKYO_ORB_START_MIN = 0  # 15
    TOKYO_ORB_END_HOUR = 6 #0  # 9
    TOKYO_ORB_END_MIN = 30  # 00

    LONDON_ORB_START_HOUR = 13 #7  # 13
    LONDON_ORB_START_MIN = 0  # 15
    LONDON_ORB_END_HOUR = 13 #7  # 16
    LONDON_ORB_END_MIN = 30  # 00

    NY_ORB_START_HOUR = 19 #13  # 19
    NY_ORB_START_MIN = 0  # 45
    NY_ORB_END_HOUR = 19  #13  # 22
    NY_ORB_END_MIN = 30  # 00

    global FOREX_NEWS_HOUR
    global NEWS_DF

    if NEWS_DF is None or not FOREX_NEWS_HOUR == dt.datetime.now().time().hour:
        NEWS_DF = get_today_forexfactory_news()
        print('SERVER CALL')
        FOREX_NEWS_HOUR = dt.datetime.now().time().hour + 1

    if isNowInTimePeriod(dt.time(TOKYO_ORB_START_HOUR, TOKYO_ORB_START_MIN),
                         dt.time(TOKYO_ORB_END_HOUR, TOKYO_ORB_END_MIN),
                         dt.datetime.now().time()) or \
        isNowInTimePeriod(dt.time(LONDON_ORB_START_HOUR, LONDON_ORB_START_MIN),
                          dt.time(LONDON_ORB_END_HOUR, LONDON_ORB_END_MIN),
                          dt.datetime.now().time()) or \
            isNowInTimePeriod(dt.time(NY_ORB_START_HOUR, NY_ORB_START_MIN), dt.time(NY_ORB_END_HOUR, NY_ORB_END_MIN), dt.datetime.now().time()):
        print('SESSION Skip')
        return False
    else:
        symbol_news_df = NEWS_DF[NEWS_DF['currency'].str.contains(symbol[:3] + '|' + symbol[3:])]
        time_list = []

        for idx, row in symbol_news_df.iterrows():
            start_h = row['datetime'].time().hour
            start_m = row['datetime'].time().minute

            end_h = start_h
            end_m = start_m + 10

            if end_m >= 60:
                end_m = end_m % 60
                end_h = end_h + 1
                if end_h >= 24:
                    end_h = 0
            d = {
                'start_h': start_h,
                'start_m': start_m,
                'end_h': end_h,
                'end_m': end_m
            }

            time_list.append(d)

            if isNowInTimePeriod(dt.time(start_h, start_m),dt.time(end_h, end_m), dt.datetime.now().time()):
                print('NEWS Skip')
                print(symbol, '------------->>', row)
                return False

    return True


while True:

    for symbol in SYMBOL_LIST:

        boil_data = boil_bands_data(symbol)

        tp_sl_dif = boil_data['tp_sl_dif']
        tp = boil_data['tp']
        sl = boil_data['sl']
        trade_action = boil_data['action']
        orders_json = boil_data['orders_json']
        json_file_name = boil_data['json_file_name']
        band_trade_close_type = boil_data['band_trade_close_type']

        if trade_action:
            print(symbol, trade_action)

        if band_trade_close_type == 0 or band_trade_close_type == 1:
            try:
                open_positions = get_all_positions(symbol)
                position_type = open_positions[0].type
                if band_trade_close_type == position_type:
                    print(symbol, 'BAND CROSSING -------- X --------- ')
                    close_all_positions(symbol)

            except Exception as e:
                None

        if trade_action:
            open_positions = get_all_positions(symbol)
            if PREVIOUS_TRADE[symbol] is None or LOTS[symbol] is None:
                if len(open_positions) > 0:
                    position_type = open_positions[0].type
                    if position_type == 0:
                        # BUY
                        PREVIOUS_TRADE[symbol] = 'buy'
                    elif position_type == 1:
                        # SELL
                        PREVIOUS_TRADE[symbol] = 'sell'
                    LOTS[symbol] = open_positions[0].volume
                else:
                    PREVIOUS_TRADE[symbol] = trade_action
                    LOTS[symbol] = calculate_lot_size(symbol, tp_sl_dif, BASE_RISK)
            
            if not PREVIOUS_TRADE[symbol] == trade_action:
                # Close all trade
                close_all_positions(symbol)
                PREVIOUS_TRADE[symbol] = trade_action
                LOTS[symbol] = calculate_lot_size(symbol, tp_sl_dif, BASE_RISK)
            else:
                LOTS[symbol] = LOTS[symbol] * 1.5

            if isNowInTimePeriod(dt.time(START_HOUR, START_MIN),
                                 dt.time(END_HOUR, END_MIN),
                                 dt.datetime.now().time()):
                trade_allowed = True
                print('trade allowed by time ')

            else:
                if symbol == 'XAUUSD' or symbol == 'BTCUSD':
                    trade_allowed = True
                else:
                    PREVIOUS_TRADE[symbol] = None
                    trade_allowed = False
                    print('trade not allowed by time')

                    #time.sleep(1)
            if trade_allowed:
                trade_allowed = check_news_session_time(symbol)
                print('trade news check', trade_allowed)
            print('allowed trade', trade_allowed)
            if trade_allowed:
                lot = LOTS[symbol]
                lot_multi = int(lot / fixed_lot)
                lot_extra = round(lot % fixed_lot, 2)

                for i in range(0, lot_multi):
                    trade_order_wo_tp_sl(symbol, fixed_lot, trade_action, magic=False)
                trade_order_wo_tp_sl(symbol, lot_extra, trade_action, magic=False)

                write_json(json_dict=orders_json, json_file_name=json_file_name)
    time.sleep(1)

