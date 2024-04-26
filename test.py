import time
import json
import datetime as dt

def write_json(json_dict):
    with open('json_data.json', 'w') as outfile:
        json.dump(json_dict, outfile)

def read_json():
    with open('json_data.json') as json_file:
        data = json.load(json_file)
        return data



symbol = 'XIAN'

while True:
    print(dt.datetime.now().time())
    orders_json = read_json()
    try:
        current_time = round(time.time() * 1000)
        ten_mins = (orders_json[symbol] + (60000 * 3))
        print(ten_mins, current_time)
        if ten_mins < current_time:
            orders_json[symbol] = current_time
            write_json(orders_json)
            print('Trade Done if')
        else:
            print('Not in time')
    except Exception as e:
        orders_json[symbol] = current_time
        write_json(orders_json)
        print('Trade Done except')

    time.sleep(60)