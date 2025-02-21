import time
import datetime as dt

from common_functions import isNowInTimePeriod
from OLD.fibonacci_price_action_combo import fibonacci_price_action
from OLD.ichimoku_cloud_stochastic_oscillator_combo import ichimoku_stochastic
from OLD.mac_rsi_combo import mac_rsi
from OLD.volman_strategies import volman_strategies
from OLD.boillinger_macd_combo import boil_macd
from nahid_wyckoff_v2 import wyckoff_bot_v2
from xian import trailing_stop, get_prev_sl, take_the_profit, take_the_profit_shot, tp_manual, take_the_profit_v2, \
    boil_rsi
from mt5_utils import initialize_mt5, get_live_data, trade_order_wo_tp, trade_order_wo_tp_price, trade_order_wo_tp_sl, \
    get_all_positions


def trade(symbol):
    delay_sec = 1

    # time.sleep(delay_sec)
    #
    # try:
    #     boil_rsi(symbol)
    # except Exception as e:
    #      print(symbol, "ERROR", str(e))

    time.sleep(delay_sec)

    try:
        wyckoff_bot_v2(symbol, 0.01)
    except Exception as e:
         print(symbol, "ERROR", str(e))





def trade_test(symbol):
    delay_sec = 1

    time.sleep(delay_sec)
    #price_action(symbol)
    try:
        # time_frame = 'M1'
        # ticks_frame1 = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)
        # lot = 0.01
        # order_type = 'buy'
        # sl = get_prev_sl(ticks_frame1, order_type)
        positions = get_all_positions(symbol)
        if len(positions) > 0:
            return
        lot = 0.1
        trade_order_wo_tp_sl(symbol, lot, 'buy', magic=False)
        #trade_order_wo_tp_sl(symbol, lot, 'sell', magic=False)
    except Exception as e:
        print(symbol, "ERROR", str(e))




def start_live_trade():
    initialize_mt5()

    symbol_list = [
                    'AUDUSD', 'DXY', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY',
                    'AUDCAD',  'AUDCHF', 'AUDJPY',  'AUDNZD',  'CADCHF',  'CADJPY',  'CHFJPY',  'EURAUD',  'EURCAD',  'EURCHF',
                    'EURGBP',  'EURJPY', 'EURNZD',  'GBPAUD', 'GBPCAD',  'GBPCHF',  'GBPJPY',  'HKDJPY', 'NZDCAD', 'NZDCHF',
                    'XAUUSD',  'USOIL', 'XAGUSD',
                    'BTCUSD', 'BTCAUD', 'ETHUSD', 'BTCXAU'
                ]
    while True:
        #take_the_profit_v2(symbol_list)
        #
        # for symbol in symbol_list:
        #
        #     server_start = 4
        #     server_end = 17
        #     local_start = 10
        #     local_end = 23
        #     local_end_min = 59
        #
        #     if isNowInTimePeriod(dt.time(local_start, 00), dt.time(local_end, local_end_min), dt.datetime.now().time()):
        #         trade(symbol)

        for symbol in symbol_list:
            trade(symbol)



start_live_trade()