import time

from akash import moving_average_signal
from volman_strategies import volman_strategies
from mt5_utils import initialize_mt5
from three_white_soldiers_three_back_crows import strategy_3ws_3bc
from all_combo_strategies import combo_strategies
#from ai_strategies import ai_trade
def trade(symbol):

    # Three White Soldiers & Three Black Crows
    #strategy_3ws_3bc(symbol)

    # # Combo Strategies
    # combo_strategies(symbol)
    #
    # # AI Trade
    # try:
    #     ai_trade(symbol)
    # except Exception as e:
    #     print( e)
    #
    # # Bob Volman
    # volman_strategies(symbol)

    #Akash
    try:
        moving_average_signal(symbol)
    except Exception as e:
        print(symbol, "ERROR", str(e))


def start_live_trade():
    initialize_mt5()

    delay_sec = 1

    #symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY']

    symbol_list = ['EURUSD', 'XAUUSD', 'GBPUSD']

    ## 200 --> 198.64 [23] 23
    ## 198.64 --> 203.42 [14] 37
    ## 203.42 --> 201.53 [13] 50
    ## 201.53 --> 195.54 [41] 91 <<ACCIDENT>>
    ## 200 -->> 205.91 AI
    ## 200 -->>

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