import time
import datetime as dt
from mt5_utils import get_live_data, trade_order_price, calculate_lot_size, initialize_mt5, trade_order_wo_tp_sl, \
    close_all_positions
from common_functions import check_duplicate_orders_time, check_duplicate_orders_magic, check_duplicate_orders, \
    write_json, check_duplicate_orders_is_time, isNowInTimePeriod


def boil_bands_data(symbol, window=14, num_std=2):

    json_file_name = 'boil_xian'
    time_frame = 'M5'
    skip_min = 20

    # running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
    #                                                            json_file_name=json_file_name)

    running_trade_status, orders_json, is_time = check_duplicate_orders_is_time(symbol, skip_min, json_file_name)

    if running_trade_status and is_time:
        return {
        'upper_band': None,
        'lower_band': None,
        'high_band_diff': None,
        'low_band_diff': None,
        'band_diff': None,
        'action': None,
        'tp': None,
        'sl': None,
        'tp_sl_dif': None,
        'orders_json': None,
        'json_file_name': json_file_name
    }

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
        'json_file_name': json_file_name
    }



mt5 = initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']

PREVIOUS_TRADE = {
    'GBPUSD': None,
    'USDCHF': None,
     'USDJPY': None,
     'US30': None,
     'EURGBP': None,
     'AUDUSD': None,
     'XAUUSD': None,
     'EURUSD': None
}

BASE_RISK = 0.05
RISK_PERCENT = {
    'GBPUSD': BASE_RISK,
    'USDCHF': BASE_RISK,
     'USDJPY': BASE_RISK,
     'US30': BASE_RISK,
     'EURGBP': BASE_RISK,
     'AUDUSD': BASE_RISK,
     'XAUUSD': BASE_RISK,
     'EURUSD': BASE_RISK
}

START_HOUR = 0
START_MIN = 0
END_HOUR = 16
END_MIN = 0

while True:

    for symbol in SYMBOL_LIST:

        boil_data = boil_bands_data(symbol)
        tp_sl_dif = boil_data['tp_sl_dif']
        tp = boil_data['tp']
        sl = boil_data['sl']
        trade_action = boil_data['action']
        orders_json = boil_data['orders_json']
        json_file_name = boil_data['json_file_name']

        if trade_action:
            #print(symbol, trade_action, PREVIOUS_TRADE[symbol])
            if PREVIOUS_TRADE[symbol] is None:
                PREVIOUS_TRADE[symbol] = trade_action
                # Close all trade
                close_all_positions(symbol)
            elif not PREVIOUS_TRADE[symbol] == trade_action:
                # Close all trade
                close_all_positions(symbol)
                PREVIOUS_TRADE[symbol] = trade_action

                RISK_PERCENT[symbol] = BASE_RISK

            if isNowInTimePeriod(dt.time(START_HOUR, START_MIN),
                                 dt.time(END_HOUR, END_MIN),
                                 dt.datetime.now().time()):
                trade_allowed = True

                RISK_PERCENT[symbol] = RISK_PERCENT[symbol] * 2
            else:
                if symbol == 'XAUUSD':
                    trade_allowed = True
                else:
                    PREVIOUS_TRADE[symbol] = None
                    trade_allowed = False

                    #time.sleep(1)

            if trade_allowed:

                try:
                    lot = calculate_lot_size(symbol, tp_sl_dif, RISK_PERCENT[symbol])
                except Exception as e :
                    print('error', str(e), symbol, tp_sl_dif, RISK_PERCENT[symbol])
                    lot = 1.0

                fixed_lot = 20.0
                lot_multi = int(lot / fixed_lot)
                lot_extra = lot % fixed_lot

                for i in range(0, lot_multi):
                    trade_order_wo_tp_sl(symbol, fixed_lot, trade_action, magic=False)
                trade_order_wo_tp_sl(symbol, lot_extra, trade_action, magic=False)

                write_json(json_dict=orders_json, json_file_name=json_file_name)
    time.sleep(1)

