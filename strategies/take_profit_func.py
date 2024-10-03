import time
from xian import take_the_profit
from mt5_utils import initialize_mt5


def start_live_trade():
    initialize_mt5()

    while True:
        for symbol in ['EURUSD', 'XAUUSD', 'USDJPY', 'EURJPY']:
            take_the_profit(symbol)
            time.sleep(1)




start_live_trade()