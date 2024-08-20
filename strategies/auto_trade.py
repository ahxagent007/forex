import time

from ai_strategies import ai_trade
from akash import moving_average_signal, moving_average_crossover, rsi_ma15, probability_trade, rsi_adx
from volman_strategies import volman_strategies
from mt5_utils import initialize_mt5
from three_white_soldiers_three_back_crows import strategy_3ws_3bc
from all_combo_strategies import combo_strategies
#from ai_strategies import ai_trade
from boilinger_bands_xian import boil_xian

def trade(symbol):

    # Three White Soldiers & Three Black Crows
    #strategy_3ws_3bc(symbol)

    # # Combo Strategies
    # combo_strategies(symbol)
    #
    # AI Trade
    # try:
    #     ai_trade(symbol)
    # except Exception as e:
    #     print( e)

    # Bob Volman
    # volman_strategies(symbol)

    #Akash

    # try:
    #     rsi_adx(symbol)
    # except Exception as e:
    #      print(symbol, "AKASH ERROR", str(e))

    ## LATEST --------------

    # try:
    #     moving_average_signal(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # try:
    #     moving_average_crossover(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # try:
    #     rsi_ma15(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    ## Probability 129
    # try:
    #     probability_trade(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # ### XIAN
    try:
        boil_xian(symbol)
    except Exception as e:
        print(symbol, "ERROR", str(e))


def start_live_trade():
    initialize_mt5()

    delay_sec = 2

    #symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY']

    #symbol_list = ['EURUSD', 'XAUUSD', 'GBPUSD']
    symbol_list = ['XAUUSD']


    while True:
        for symbol in symbol_list:
            trade(symbol)
            time.sleep(delay_sec)

        ## BTCUSD 161.43

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