import datetime as dt
import json

import pandas as pd

from mt5_utils import get_order_positions_count, get_all_positions
import numpy as np
#from ta.volatility import AverageTrueRange

import MetaTrader5 as mt5


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

def check_duplicate_orders_magic(symbol):
    trade_numbers = read_json('trade_number')

    try:
        MAGIC_NUMBER = trade_numbers[symbol]

        if MAGIC_NUMBER:

            # Get open positions
            positions = get_all_positions(symbol)

            # Check if positions are retrieved successfully
            if positions is None:
                # No positions found
                #trade_numbers[symbol] = MAGIC_NUMBER
                return False

            # Convert positions to a DataFrame
            positions_df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

            # Filter positions by magic number
            filtered_positions = positions_df[positions_df['magic'] == MAGIC_NUMBER]

            if filtered_positions.shape[0] > 0:
                return True
            else:
                trade_numbers[symbol] = None
                return False

    except Exception as e:
        trade_numbers[symbol] = None
        return False

    return False


def check_duplicate_orders_magic_v2(symbol):
    trade_numbers = read_json('trade_number')
    action = None
    try:
        MAGIC_NUMBER = trade_numbers[symbol]

        if MAGIC_NUMBER:

            # Get open positions
            positions = get_all_positions(symbol)

            # Check if positions are retrieved successfully
            if positions is None:
                # No positions found
                #trade_numbers[symbol] = MAGIC_NUMBER
                return False, MAGIC_NUMBER, action, pd.DataFrame()

            # Convert positions to a DataFrame
            positions_df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

            # Filter positions by magic number
            filtered_positions = positions_df[positions_df['magic'] == MAGIC_NUMBER]
            action = mt5.ORDER_TYPE_SELL if filtered_positions.iloc[0]['type'] == 0 else mt5.ORDER_TYPE_BUY

            if filtered_positions.shape[0] > 0:
                return True, MAGIC_NUMBER, action, positions_df
            else:
                trade_numbers[symbol] = None
                return False, MAGIC_NUMBER, action, positions_df

    except Exception as e:
        trade_numbers[symbol] = None
        return False, 0, action, pd.DataFrame()

    return False, 0, action, pd.DataFrame()



def write_json(json_dict, json_file_name):
    with open('time_counts/'+json_file_name+'.json', 'w') as outfile:
        json.dump(json_dict, outfile)

# def get_sl_tp_pips(df, sl, tp):
#
#     # Calculate ATR
#     atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
#     df['ATR'] = atr.average_true_range()
#
#     # Define multipliers for SL and TP
#     SL_MULTIPLIER = sl
#     TP_MULTIPLIER = tp
#
#     # Initialize lists to store SL and TP values in pips
#     sl_pips = []
#     tp_pips = []
#
#     # Calculate SL and TP in pips based on ATR
#     for i in range(len(df)):
#         if i < 14:  # Ensure we have enough data for ATR calculation
#             sl_pips.append(np.nan)
#             tp_pips.append(np.nan)
#         else:
#             atr_value = df['ATR'].iloc[i]
#             sl_pip = SL_MULTIPLIER * atr_value * 10000  # Convert ATR value to pips
#             tp_pip = TP_MULTIPLIER * atr_value * 10000  # Convert ATR value to pips
#             sl_pips.append(sl_pip)
#             tp_pips.append(tp_pip)
#
#     # Add SL and TP pips to the dataframe
#     df['SL_pips'] = sl_pips
#     df['TP_pips'] = tp_pips
#
#     result = {
#         'SL': sl_pips[-1],
#         'TP': tp_pips[-1]
#     }
#
#     return result

