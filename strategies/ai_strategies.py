from mt5_utils import trade_order
from ai_hmm import hmm_model_signal
from ai_cnn import cnn_model_signal
from ai_random_forests import random_forest_signal
from common_functions import get_sl_tp_pips
from mt5_utils import get_live_data

def ai_trade(symbol):
    symbol_list = ['EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']

    if not symbol_list in symbol_list:
        return None

    all_signals = []

    hmm = hmm_model_signal(symbol)
    if hmm:
        print('Hidden Markov Model', hmm)
        all_signals.append(hmm)

    cnn = cnn_model_signal(symbol)
    if cnn:
        print('CNN ', cnn)
        all_signals.append(cnn)

    rf = random_forest_signal(symbol)
    if rf:
        print('Random Forest ', rf)
        all_signals.append(rf)

    buy_signals = 0
    sell_signals = 0

    for signal in all_signals:
        if signal == 'buy':
            buy_signals += 1
        elif signal == 'sell':
            sell_signals += 1

    # Set SL TP
    df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=4)
    sl_tp = get_sl_tp_pips(df)
    # tp_point = 150
    # sl_point = 50

    lot = 0.01

    tp_point = sl_tp['TP']
    sl_point = sl_tp['SL']


    if buy_signals > sell_signals:
        action = 'buy'
        trade_order(symbol, tp_point, sl_point, lot, action)
    elif sell_signals > buy_signals:
        action = 'sell'
        trade_order(symbol, tp_point, sl_point, lot, action)
