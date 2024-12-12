import time
from nahid_wyckoff_v2 import wyckoff_bot_v2
from xian import trailing_stop
from mt5_utils import initialize_mt5


def trade(symbol):
    delay_sec = 0.2

    time.sleep(delay_sec)
    # price_action(symbol)
    try:
        wyckoff_bot_v2(symbol, 2.0)
    except Exception as e:
        print(symbol, "ERROR", str(e))


def trade_test(symbol):
    delay_sec = 1

    time.sleep(delay_sec)
    #price_action(symbol)
    try:
        wyckoff_bot_v2(symbol, 2.0)
    except Exception as e:
        print(symbol, "ERROR", str(e))




def start_live_trade():
    initialize_mt5()

    symbol_list = ['XAUUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY']

    while True:
        for symbol in symbol_list:

            server_start = 4
            server_end = 17
            local_start = 10
            local_end = 23
            local_end_min = 59
            #trailing_stop(symbol)
            trade(symbol)

            # if isNowInTimePeriod(dt.time(local_start, 00), dt.time(local_end, local_end_min), dt.datetime.now().time()):
            #     trade_test(symbol)



start_live_trade()