from mt5_utils import trade_order
from ai_hmm import hmm_model_signal
from ai_cnn import cnn_model_signal
from ai_random_forests import random_forest_signal
from common_functions import check_duplicate_orders, check_duplicate_orders_magic, write_json
from mt5_utils import get_live_data, get_order_positions_count
from ai_lstm import lstm_signal

def ai_trade(symbol):
    symbol_list = ['EURUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURJPY', 'XAUUSD']

    if not symbol in symbol_list:
        return None

    json_file_name ='ai_strategies'
    skip_min = 5

    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        print(symbol, 'MULTIPLE TRADE >>>>')
        return None

    # order_count = get_order_positions_count(symbol)
    # if order_count>0:
    #     print(symbol, 'AI MULTIPLE TRADE >>>>', order_count)
    #     return None

    # if_duplicate = check_duplicate_orders_magic(symbol)
    #
    # if if_duplicate:
    #     print('DUPLICATE AI FOR >> ',symbol)
    #     return None

    all_signals = []

    hmm = hmm_model_signal(symbol)
    if hmm:
        all_signals.append(hmm)

    #TUNE
    cnn = cnn_model_signal(symbol)
    if cnn:
        all_signals.append(cnn)

    #TUNE
    rf = random_forest_signal(symbol)
    if rf:
        all_signals.append(rf)


    lstm = lstm_signal(symbol)
    if lstm:
        all_signals.append(lstm)


    buy_signals = 0
    sell_signals = 0

    for signal in all_signals:
        if signal == 'buy':
            buy_signals += 1
        elif signal == 'sell':
            sell_signals += 1

    # Set SL TP
    # df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=20)
    # sl_tp = get_sl_tp_pips(df=df, sl=5, tp=10)
    # tp_point = sl_tp['TP']
    # sl_point = sl_tp['SL']

    tp_dict = {
        'EURUSD': 80,
        'XAUUSD': 5000
    }
    sl_dict = {
        'EURUSD': 80,
        'XAUUSD': 2000
    }

    tp_point = tp_dict[symbol]
    sl_point = sl_dict[symbol]

    lot = 0.02

    print('SL TP -->> ', sl_point, tp_point)
    print('Hidden Markov Model', hmm)
    print('CNN ', cnn)
    print('Random Forest ', rf)
    print('Long Short Trm Memory ', lstm)
    ## 144.44

    ## Doubel check with MA
    # Moving Average
    # df = get_live_data(symbol=symbol, time_frame='M1', prev_n_candles=100)
    # df['MA_15'] = df['close'].rolling(window=15).mean()
    #
    # ma_action = None
    # if df['MA_15'].iloc[-1] > df['close'].iloc[-1]:
    #     ma_action = 'sell'
    # elif df['MA_15'].iloc[-1] < df['close'].iloc[-1]:
    #     ma_action = 'buy'

    # if buy_signals > sell_signals:
    #     action = 'buy'
    #     if action == ma_action:
    #         trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=action, magic=True)
    #     else:
    #         print('MA TRADE SKIPPED')
    #
    # elif sell_signals < buy_signals:
    #     action = 'sell'
    #     if action == ma_action:
    #         trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=action, magic=True)
    #     else:
    #         print('MA TRADE SKIPPED')

    action = None

    if buy_signals > sell_signals:
        action = 'buy'
    elif sell_signals > buy_signals:
        action = 'sell'

    print('FINAL ACTION -->>', action)

    if action:
        trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=action, magic=True)
        write_json(json_dict=orders_json, json_file_name=json_file_name)
