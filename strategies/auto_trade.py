import time
import datetime as dt
#from ai_strategies import ai_trade
from threading import Thread

from xian import price_action, moving_average_crossover_cci, moving_average_crossover_01, take_the_profit
from nahid_sir import bot_1
from boillinger_macd_combo import boil_macd
from fibonacci_price_action_combo import fibonacci_price_action
from ichimoku_cloud_stochastic_oscillator_combo import ichimoku_stochastic
from mac_rsi_combo import mac_rsi
from akash import moving_average_signal, rsi_ma15, probability_trade, rsi_adx, ma_adx_rsi, \
    moving_average_crossover_15_100, moving_average_nahid_signal, adx_slop, get_avg_candle_size, akash_02
from volman_strategies import volman_strategies
from mt5_utils import initialize_mt5, get_magic_number, trade_order_magic, get_live_data, trade_order_magic_value
from three_white_soldiers_three_back_crows import strategy_3ws_3bc
from all_combo_strategies import combo_strategies
# from ai_strategies import ai_trade
from boilinger_bands_xian import boil_xian, boil_xian_akash
from common_functions import add_csv, isNowInTimePeriod, check_duplicate_orders_is_time, write_json


def trade(symbol):
    delay_sec = 2


    time.sleep(delay_sec)

    try:
        moving_average_crossover_01(symbol, 1, 100)
    except Exception as e:
        print(symbol, "ERROR", str(e))


    # try:
    #     akash_02(symbol)
    # except Exception as e:
    #     print(symbol, "ERROR", str(e))

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

    #symbol_list = ['EURUSD', 'XAUUSD', 'USDJPY', 'EURJPY']
    #symbol_list = ['BTCUSD', 'XAUUSD']
    symbol_list = ['XAUUSD']


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
        for symbol in symbol_list:

            time.sleep(1)
            take_the_profit(symbol)

            server_start = 4
            server_end = 17
            local_start = 10
            local_end = 23
            local_end_min = 59
            ## trade(symbol)

            if isNowInTimePeriod(dt.time(server_start, 00), dt.time(server_end, local_end_min), dt.datetime.now().time()):
                trade(symbol)

        # print('1. BTCUSD 2. XAUUSD')
        # symbol = int(input('SYMBOL: -->>'))
        # print('1. BUY 2.SELL')
        # action = int(input('ACTION:: '))
        #
        # if symbol == 1:
        #     symbol = 'BTCUSD'
        # else:
        #     symbol = 'XAUUSD'
        #
        # if action == 1:
        #     action = 'buy'
        # else:
        #     action = 'sell'
        #
        #
        # json_file_name = 'xian_trade'
        # skip_min = 3
        # time_frame = 'M1'
        # tp_multi = 6
        # sl_multi = 2
        #
        # running_trade_status, orders_json, is_time = check_duplicate_orders_is_time(symbol=symbol, skip_min=skip_min,
        #                                                                             json_file_name=json_file_name)
        # df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)
        #
        # avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, tp_multi, sl_multi)
        # if avg_candle_size is None:
        #     return
        # if action == 'buy':
        #     sl_value = df['low'].iloc[-1]
        # else:
        #     sl_value = df['high'].iloc[-1]
        #
        # MAGIC_NUMBER = get_magic_number()
        # lot = 0.15
        # trade_order_magic_value(symbol=symbol, tp_point=tp, sl_value=sl_value, lot=lot, action=action, magic=True, code=3669,
        #                   MAGIC_NUMBER=MAGIC_NUMBER)
        # write_json(json_dict=orders_json, json_file_name=json_file_name)



start_live_trade()