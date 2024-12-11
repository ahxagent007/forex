import time
import datetime as dt
#from ai_strategies import ai_trade
from threading import Thread

from nahid_wyckoff_v4 import bot_wyckoff_v4
from nahid_wyckoff_v2 import wyckoff_bot_v2
from nadhi_wyckoff import bot_wyckoff
from fair_value_gap import FVG_trade
from xian import price_action, moving_average_crossover_cci, moving_average_crossover_01, take_the_profit, \
    moving_average_crossover_ema_02, cumulative_lot, random_walk, random_walk_both, trailing_stop
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
            trailing_stop(symbol)
            trade(symbol)

            # if isNowInTimePeriod(dt.time(local_start, 00), dt.time(local_end, local_end_min), dt.datetime.now().time()):
            #     trade_test(symbol)



start_live_trade()