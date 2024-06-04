import time
from mt5_utils import initialize_mt5
from three_white_soldiers_three_back_crows import strategy_3ws_3bc

def trade(symbol):

    # Three White Soldiers & Three Black Crows
    strategy_3ws_3bc(symbol)


def start_live_trade():
    initialize_mt5()

    delay_sec = 8.5

    symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']

    ## 200 -->

    while True:
        for symbol in symbol_list:
            trade(symbol)
            time.sleep(delay_sec)


        # trade('EURUSD')
        # time.sleep(delay_sec)

        # if isNowInTimePeriod(dt.time(4, 00), dt.time(21, 00), dt.datetime.now().time()):
        #     for symbol in symbol_list:
        #         trade(symbol)
        #         time.sleep(delay_sec)
        #     # trade('EURUSD')
        #     # time.sleep(delay_sec)
        # else:
        #     print(dt.datetime.now().time(), '>>> > >> NOT A GOOD TIME FOR TRADE')
        #     time.sleep(60*5)


start_live_trade()