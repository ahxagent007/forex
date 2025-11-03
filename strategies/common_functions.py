import datetime as dt
import json

import pandas as pd

from mt5_utils import get_order_positions_count, get_all_positions, update_magic_number
import numpy as np
#from ta.volatility import AverageTrueRange

import MetaTrader5 as mt5
import csv

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

def check_dup_orders_count(symbol):
    order_count = get_order_positions_count(symbol)
    if order_count > 0:
        return True
    else:
        return False

def check_duplicate_orders(symbol, skip_min, json_file_name):

    orders_json = read_json(json_file_name)

    order_count = get_order_positions_count(symbol)

    try:
        last_trade_time = orders_json[symbol]

        if order_count > 0:
            #print('Multiple ORDER COUNT -->>', symbol)
            return True, orders_json

        start_hour = last_trade_time['h']
        start_min = last_trade_time['m']
        end_hour = last_trade_time['h']
        end_min = last_trade_time['m']+skip_min

        if end_min > 60:
            end_hour += 1
            end_min -= 60
            if end_hour >= 24:
                end_hour = 0

        # if orders == 0:
        #     orders_json[symbol] = {
        #         'h': dt.datetime.now().hour,
        #         'm': dt.datetime.now().minute,
        #     }
        #     return False, orders_json

        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), dt.datetime.now().time()):
            #print(symbol, 'TRADE SKIPPED for TIME MULTIPLE [',orders,']', json_file_name)
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
def check_duplicate_orders_is_time(symbol, skip_min, json_file_name):
    orders = get_order_positions_count(symbol)
    orders_json = read_json(json_file_name)

    order_count = get_order_positions_count(symbol)

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

        # if orders == 0:
        #     orders_json[symbol] = {
        #         'h': dt.datetime.now().hour,
        #         'm': dt.datetime.now().minute,
        #     }
        #     return False, orders_json

        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), dt.datetime.now().time()):
            #print(symbol, 'TRADE SKIPPED for TIME [',orders,']', json_file_name)
            return True, orders_json, True
        else:

            orders_json[symbol] = {
                'h': dt.datetime.now().hour,
                'm': dt.datetime.now().minute,
            }

            if order_count > 0:
                #print('Multiple ORDER COUNT -->>', symbol)
                return True, orders_json, False
    except Exception as e:
        orders_json[symbol] = {
            'h': dt.datetime.now().hour,
            'm': dt.datetime.now().minute,
        }

    return False, orders_json, True
def check_duplicate_orders_time(symbol, skip_min, json_file_name):
    orders = get_order_positions_count(symbol)
    orders_json = read_json(json_file_name)

    order_count = get_order_positions_count(symbol)

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


        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), dt.datetime.now().time()):
            #print(symbol, 'TRADE SKIPPED for TIME MULTIPLE [',orders,']', json_file_name)
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

def skip_trade_time(symbol, skip_min, json_file_name):
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

        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), dt.datetime.now().time()):
            #print(symbol, 'TRADE SKIPPED for TIME MULTIPLE [',orders,']', json_file_name)
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

def check_duplicate_orders_magic(symbol, code=0):
    trade_numbers = read_json('trade_number')
    symbol_code = symbol+str(code)

    try:
        MAGIC_NUMBER = trade_numbers[symbol_code]

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
                print('MULTIPLE TRADE BY MAGIC NUMBER', symbol_code)
                return True
            else:
                trade_numbers[symbol] = None
                update_magic_number(symbol_code, None)
                return False

    except Exception as e:
        trade_numbers[symbol] = None
        update_magic_number(symbol_code, None)
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
    #print('SKIPPING TIME UPDATED ---->>>', json_dict)
    with open('time_counts/'+json_file_name+'.json', 'w') as outfile:
        json.dump(json_dict, outfile)

def add_csv(data_lst):
    with open(r'data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data_lst)

def price_distance_percent(distance_price, current_price):
    distance_percent = round(((distance_price - current_price) / current_price) * 100, 4)
    return distance_percent
