import time

#from ai_strategies import ai_trade
from boillinger_macd_combo import boil_macd
from fibonacci_price_action_combo import fibonacci_price_action
from ichimoku_cloud_stochastic_oscillator_combo import ichimoku_stochastic
from mac_rsi_combo import mac_rsi
from akash import moving_average_signal, moving_average_crossover, rsi_ma15, probability_trade, rsi_adx, ma_adx_rsi, \
    moving_average_crossover_15_100, moving_average_nahid_signal
from volman_strategies import volman_strategies
from mt5_utils import initialize_mt5
from three_white_soldiers_three_back_crows import strategy_3ws_3bc
from all_combo_strategies import combo_strategies
#from ai_strategies import ai_trade
from boilinger_bands_xian import boil_xian
from common_functions import add_csv

def trade(symbol):
    delay_sec = 1
    # Three White Soldiers & Three Black Crows
    #strategy_3ws_3bc(symbol)
    #
    # ## TUNE
    # time.sleep(delay_sec)
    # try:
    #     boil_macd(symbol)
    #     #print(symbol, 'boil_macd')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # time.sleep(delay_sec)
    # try:
    #     fibonacci_price_action(symbol)
    #     print('fibonacci_price_action')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # ## TUNE
    # time.sleep(delay_sec)
    #
    # try:
    #     ichimoku_stochastic(symbol)
    #     #print(symbol, 'ichimoku_stochastic')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # time.sleep(delay_sec)
    # try:
    #     mac_rsi(symbol)
    #     print('mac_rsi')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))



    # ##AI Trade
    # try:
    #     ai_trade(symbol)
    # except Exception as e:
    #     print( e)
    #
    # ## TUNE
    # time.sleep(delay_sec)
    # ##Bob Volman
    # #volman_strategies(symbol)
    # try:
    #     volman_strategies(symbol)
    #     #print(symbol, 'volman_strategies')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    ##Akash
    #
    # time.sleep(delay_sec)
    # try:
    #     ma_adx_rsi(symbol)
    # except Exception as e:
    #     print(symbol, "AKASH ERROR ma_adx_rsi", str(e))
    #
    # time.sleep(delay_sec)
    # try:
    #     rsi_adx(symbol)
    # except Exception as e:
    #      print(symbol, "AKASH ERROR", str(e))

    ## LATEST --------------
    # time.sleep(delay_sec)
    #
    # try:
    #     moving_average_crossover_15_100(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))
    #
    # time.sleep(delay_sec)
    # try:
    #     moving_average_signal(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))
    #
    # time.sleep(delay_sec)
    # try:
    #     moving_average_crossover(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))
    #
    # time.sleep(delay_sec)
    # try:
    #     rsi_ma15(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # time.sleep(delay_sec)
    # # Probability 129
    # try:
    #     probability_trade(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # ### XIAN
    # time.sleep(delay_sec)
    # try:
    #     boil_xian(symbol)
    #     #print(symbol, 'boil_xian')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))


    time.sleep(delay_sec)
    try:
        moving_average_nahid_signal(symbol)
        #print(symbol, 'boil_xian')
    except Exception as e:
        print(symbol, "ERROR", str(e))




def start_live_trade():
    initialize_mt5()



    #symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY']

    #symbol_list = ['EURUSD', 'XAUUSD', 'GBPUSD']
    symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'EURJPY']


    while True:
        for symbol in symbol_list:
            trade(symbol)


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