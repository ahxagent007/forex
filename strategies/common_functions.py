import datetime as dt
import json


def get_magic_number():
    with open("magic_number.txt", "w+") as myfile:
        for line in myfile:
            magic_number = int(line.strip())
        myfile.write(str(magic_number+1))

    return magic_number

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

    orders_json = read_json(json_file_name)

    try:
        last_trade_time = orders_json[symbol]

        start_hour = last_trade_time['h']
        start_min = last_trade_time['m']
        end_hour = last_trade_time['h']
        end_min = last_trade_time['m']+skip_min

        if end_min > 60:
            end_hour += 1
            if end_hour > 24:
                end_hour = 0

        if isNowInTimePeriod(dt.time(start_hour, start_min), dt.time(end_hour, end_min), dt.datetime.now().time()):
            print(symbol, 'TRADE SKIPPED for MULTIPLE', json_file_name)
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
