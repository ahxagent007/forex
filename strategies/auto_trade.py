import time
import datetime as dt
#from ai_strategies import ai_trade
from xian import price_action, moving_average_crossover_cci, moving_average_crossover_01, take_the_profit
from nahid_sir import bot_1
from boillinger_macd_combo import boil_macd
from fibonacci_price_action_combo import fibonacci_price_action
from ichimoku_cloud_stochastic_oscillator_combo import ichimoku_stochastic
from mac_rsi_combo import mac_rsi
from akash import moving_average_signal, rsi_ma15, probability_trade, rsi_adx, ma_adx_rsi, \
    moving_average_crossover_15_100, moving_average_nahid_signal, adx_slop
from volman_strategies import volman_strategies
from mt5_utils import initialize_mt5, get_magic_number, trade_order_magic
from three_white_soldiers_three_back_crows import strategy_3ws_3bc
from all_combo_strategies import combo_strategies
from ai_strategies import ai_trade
from boilinger_bands_xian import boil_xian, boil_xian_akash
from common_functions import add_csv, isNowInTimePeriod, check_duplicate_orders_is_time, write_json


def trade(symbol):
    delay_sec = 1

    # ## TUNE
    # time.sleep(delay_sec)
    # try:
    #     boil_macd(symbol)
    #     #print(symbol, 'boil_macd')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))
    #
    # ## TUNE
    # time.sleep(delay_sec)
    #
    # try:
    #     ichimoku_stochastic(symbol)
    #     #print(symbol, 'ichimoku_stochastic')
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))
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
    #
    #

    time.sleep(delay_sec)

    try:
        moving_average_crossover_01(symbol, 5, 50)
    except Exception as e:
        print(symbol, "ERROR", str(e))


    # try:
    #     moving_average_crossover(symbol, 8, 50)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))
    #
    #
    # time.sleep(delay_sec)
    # try:
    #     price_action(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

    # time.sleep(delay_sec)
    # #adx_slop(symbol)
    # try:
    #     adx_slop(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

def start_live_trade():
    initialize_mt5()

    #symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURGBP', 'EURJPY']

    #symbol_list = ['EURUSD', 'XAUUSD', 'GBPUSD']
    symbol_list = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY', 'EURJPY']

    # # ## test order
    # json_file_name = 'akash_strategies_ma_ema_5_100'
    # symbol = 'XAUUSD'
    # skip_min = 3
    # running_trade_status, orders_json, is_time = check_duplicate_orders_is_time(symbol=symbol, skip_min=skip_min,
    #                                                                             json_file_name=json_file_name)
    # MAGIC_NUMBER = get_magic_number()
    # sl = 2633.900
    # tp = 2625.325
    # lot = 0.01
    # action = 'sell'
    # trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=888,
    #                   MAGIC_NUMBER=MAGIC_NUMBER)
    # write_json(json_dict=orders_json, json_file_name=json_file_name)

    while True:
        # for symbol in symbol_list:
        #     trade(symbol)

        for symbol in symbol_list:
            time.sleep(1)
            take_the_profit(symbol)

            if isNowInTimePeriod(dt.time(10, 00), dt.time(23, 59), dt.datetime.now().time()):
                trade(symbol)


start_live_trade()