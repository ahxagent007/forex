import datetime as dt
import json
from mt5_utils import get_order_positions_count
import numpy as np
from ta.volatility import AverageTrueRange



def tick_type(candle):
    if candle['close'] > candle['open']:
        return 'bull'
    elif candle['close'] < candle['open']:
        return 'bear'
    else:
        return 'doji'

def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:
        #Over midnight:
        return nowTime >= startTime or nowTime <= endTime

def read_json(json_file_name):
    with open('time_counts/'+json_file_name+'.json') as json_file:
        data = json.load(json_file)
        return data

def check_duplicate_orders(symbol, skip_min, json_file_name):
    orders = get_order_positions_count(symbol)
    orders_json = read_json(json_file_name)

    try:
        last_trade_time = orders_json[symbol]

        start_hour = last_trade_time['h']
        start_min = last_trade_time['m']
        end_hour = last_trade_time['h']
        end_min = last_trade_time['m']+skip_min

        if end_min > 60:
            end_hour += 1
            end_min -= 60
            if end_hour >= 24:
                end_hour = 0

        if orders == 0:
            orders_json[symbol] = {
                'h': dt.datetime.now().hour,
                'm': dt.datetime.now().minute,
            }
            return False, orders_json

        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), dt.datetime.now().time()):
            print(symbol, 'TRADE SKIPPED for MULTIPLE [',orders,']', json_file_name)
            return True, orders_json
        else:
            orders_json[symbol] = {
                'h': dt.datetime.now().hour,
                'm': dt.datetime.now().minute,
            }
    except Exception as e:
        orders_json[symbol] = {
            'h': dt.datetime.now().hour,
            'm': dt.datetime.now().minute,
        }

    return False, orders_json

def write_json(json_dict, json_file_name):
    with open('time_counts/'+json_file_name+'.json', 'w') as outfile:
        json.dump(json_dict, outfile)

def get_sl_tp_pips(df):

    # Calculate ATR
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ATR'] = atr.average_true_range()

    # Define multipliers for SL and TP
    SL_MULTIPLIER = 1.5
    TP_MULTIPLIER = 3.0

    # Initialize lists to store SL and TP values in pips
    sl_pips = []
    tp_pips = []

    # Calculate SL and TP in pips based on ATR
    for i in range(len(df)):
        if i < 14:  # Ensure we have enough data for ATR calculation
            sl_pips.append(np.nan)
            tp_pips.append(np.nan)
        else:
            atr_value = df['ATR'].iloc[i]
            sl_pip = SL_MULTIPLIER * atr_value * 10000  # Convert ATR value to pips
            tp_pip = TP_MULTIPLIER * atr_value * 10000  # Convert ATR value to pips
            sl_pips.append(sl_pip)
            tp_pips.append(tp_pip)

    # Add SL and TP pips to the dataframe
    df['SL_pips'] = sl_pips
    df['TP_pips'] = tp_pips

    result = {
        'SL': sl_pips[-1],
        'TP': tp_pips[-1]
    }

    return result
