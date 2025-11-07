from datetime import date, datetime
import time
from mt5_utils import get_live_data, trade_order_price, calculate_lot_size, initialize_mt5, get_spread_in_price, \
    get_balance
from common_functions import check_duplicate_orders_time, write_json, read_json, check_duplicate_orders_time_json


def detect_hammer_patterns(df):
    body = abs(df['close'] - df['open'])
    upper = df['high'] - df[['close', 'open']].max(axis=1)
    lower = df[['close', 'open']].min(axis=1) - df['low']

    df['is_hammer'] = (lower >= 2 * body) & (upper <= body)
    df['is_inv_hammer'] = (upper >= 2 * body) & (lower <= body)
    return df

def boil_bands_data(df, window=20, num_std=2):
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

    tp_sl_dif = band_diff * 2

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
        'middle_band': df['middle_band'].iloc[curr_idx],
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

def check_update_target_profit():
    TARGET_PERCENT = 6
    SL_PERCENT = 3

    current_balance = get_balance()
    current_date = date.today()

    balance_sheet = read_json('balance_sheet')
    try:
        target_current_data = balance_sheet[str(current_date)]
        target_balance = target_current_data['target']
        target_sl = target_current_data['sl']

        if current_balance > target_balance and current_balance < target_sl:
            #SKIP THIS DAY
            return True
        else:
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute
            if current_minute % SL_PERCENT == 0:
                target_current_data['history'][str(current_hour)+'_'+str(current_minute)] = current_balance
            write_json(balance_sheet, 'balance_sheet')
            return False
    except:

        target_balance = current_balance + (current_balance * TARGET_PERCENT)/100
        target_sl = current_balance - (current_balance * TARGET_PERCENT*2)/100
        balance_sheet[str(current_date)] = {'target':target_balance, 'sl': target_sl, 'history':{}}
        write_json(balance_sheet, 'balance_sheet')

        return False


mt5 = initialize_mt5()

sleep_time = 1
SYMBOL_LIST = ['XAUUSD', 'EURUSD', 'BTCUSD', 'US30']
time_frame = 'M1'

json_file_name = 'hammer_start'
skip_min = 2
tp_multi = 2
spread_multi = 2
RISK_PERCENT = 1

ORDER_JSON = {}

while True:
    # check if targeted profit
    check_sts = check_update_target_profit()
    if check_sts:
        time.sleep(60*5)
        continue
    for symbol in SYMBOL_LIST:
        running_trade_status, orders_json = check_duplicate_orders_time_json(symbol, skip_min, ORDER_JSON)

        if running_trade_status:
            continue

        try:
            df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)
            df = detect_hammer_patterns(df)

            action = None
            spread = get_spread_in_price(symbol)

            if df['is_hammer'].iloc[-2]:
                print(symbol, 'Hammer Found BUY')
                hammer_tail_size = df['close'].iloc[-2] - df['low'].iloc[-2]
                sl_price = df['low'].iloc[-2] - spread
                tp_price = df['close'].iloc[-2] + hammer_tail_size * tp_multi
                action = 'buy'

            elif df['is_inv_hammer'].iloc[-2]:
                print(symbol, 'Inverse Hammer Found SELL')
                hammer_tail_size = df['high'].iloc[-2] - df['close'].iloc[-2]
                sl_price = df['high'].iloc[-2] + spread
                tp_price = df['close'].iloc[-2] - hammer_tail_size * tp_multi
                action = 'sell'

            if action:
                print(ORDER_JSON)
                ## Calculate the spread
                if not hammer_tail_size > spread * spread_multi:
                    print(f'{symbol} SPREAD [{spread}] >> tail size [{hammer_tail_size}]')
                    ORDER_JSON = orders_json
                    continue

                boil_data = boil_bands_data(df)

                if df['close'].iloc[-1] > boil_data['middle_band'] and action == 'buy':
                    print(symbol, 'price is > middle_band')
                    ORDER_JSON = orders_json
                    continue
                elif df['close'].iloc[-1] < boil_data['middle_band'] and action == 'sell':
                    print(symbol, 'price is < middle_band')
                    ORDER_JSON = orders_json
                    continue

                print(symbol, 'running_trade_status ->', running_trade_status)

                lot = calculate_lot_size(symbol=symbol, sl_diff=hammer_tail_size, risk=RISK_PERCENT)
                trade_order_price(symbol=symbol, tp_price=tp_price, sl_price=sl_price,
                                  lot=lot, action=action)

                ORDER_JSON = orders_json
                print(ORDER_JSON)
        except Exception as e:
            print(str(e))

    time.sleep(sleep_time)


