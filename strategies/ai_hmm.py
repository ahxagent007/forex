#pip install pandas numpy hmmlearn matplotlib
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from hmmlearn.hmm import GaussianHMM
from sklearn.preprocessing import MinMaxScaler

from akash import get_avg_candle_size
from common_functions import write_json, check_duplicate_orders, check_dup_orders_count
from xian import cumulative_lot
from mt5_utils import get_live_data, convert_price_diff_to_pips, trade_order, initialize_mt5, initialize_mt5_4000, \
    get_all_positions, get_open_positions, close_position
import joblib


def hmm_model_signal(symbol):
    time_frame = 'H1'
    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=1000)
    if df.shape[0] == 0:
        return None
    # Preprocess data: Assume 'close' prices are used
    scaler = MinMaxScaler(feature_range=(0, 1))
    df['close'] = scaler.fit_transform(df['close'].values.reshape(-1, 1))

    # Feature engineering: Calculate returns
    df['Returns'] = df['close'].pct_change().dropna()

    # Remove NaN and infinite values
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # Prepare data for HMM
    returns = df['Returns'].values.reshape(-1, 1)
    try:
        model = joblib.load('ai_models/hmm.joblib')
    except:
        print('MODEL NOT FOUND')
        # Initialize and fit HMM
        model = GaussianHMM(n_components=4, covariance_type="full", n_iter=2000)

    try:
        model.fit(returns)
    except:
        return df, None
    joblib.dump(model, 'ai_models/hmm_'+symbol+'.joblib')

    # Predict hidden states
    hidden_states = model.predict(returns)

    # Add hidden states to the dataframe
    df['Hidden State'] = hidden_states

    # Generate trading signals
    signals = []
    for i in range(1, len(hidden_states)):
        if hidden_states[i] == 0:
            signals.append('buy')
        elif hidden_states[i] == 1:
            signals.append('sell')
        else:
            signals.append(None)

    # Add 'Hold' signal for the first entry
    signals.insert(0, None)

    # Add signals to the dataframe
    df['Signal'] = signals

    return df, signals[-1]


initialize_mt5_4000()

while True:
    symbol = 'XAUUSD'
    symbol_list = ['NZDCAD', 'AUDUSD', 'NZDUSD', 'EURGBP', 'USDCAD', 'USDJPY', 'EURUSD', 'GBPAUD', 'GBPCAD', 'AUDCAD',
                   'EURJPY',
                   'CADJPY', 'GBPJPY', 'CHFJPY', 'GBPUSD', 'EURNZD', 'GBPCHF', 'EURAUD', 'AUDJPY', 'GBPNZD', 'EURCAD',
                   'USDCHF', 'XAUUSD']

    for symbol in symbol_list:
        delay_sec = 1

        time.sleep(delay_sec)

        skip_min = 25
        json_file_name = 'hmm_ai'
        # running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
        #                                                            json_file_name=json_file_name)
        running_trade_status = check_dup_orders_count(symbol)
        if running_trade_status:
            # print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
            continue

        df, action = hmm_model_signal(symbol)
        lot = 0.01  # cumulative_lot()

        if action:

            sl = 0
            if action == 'buy':

                ## get the SL
                sl_open = min(df['open'].iloc[-6], df['open'].iloc[-2], df['open'].iloc[-3],
                              df['open'].iloc[-4], df['open'].iloc[-5])
                sl_close = min(df['close'].iloc[-6], df['close'].iloc[-2], df['close'].iloc[-3],
                               df['close'].iloc[-4], df['close'].iloc[-5])

                print('sl_open, sl_close',sl_open, sl_close)
                if sl_open < sl_close:
                    sl = abs(sl_open - df['close'].iloc[-1])
                else:
                    sl = abs(sl_close - df['close'].iloc[-1])

            elif action == 'sell':
                ## get the SL
                sl_open = max(df['open'].iloc[-6], df['open'].iloc[-2], df['open'].iloc[-3],
                              df['open'].iloc[-4], df['open'].iloc[-5])
                sl_close = max(df['close'].iloc[-6], df['close'].iloc[-2], df['close'].iloc[-3],
                               df['close'].iloc[-4], df['close'].iloc[-5])

                print('sl_open, sl_close', sl_open, sl_close)

                if sl_open > sl_close:
                    sl = abs(sl_open - df['close'].iloc[-1])
                else:
                    sl = abs(sl_close - df['close'].iloc[-1])

            sl_pips = convert_price_diff_to_pips(symbol, sl)
            tp_pips = sl_pips * 2
            print('SL:TP -->', sl_pips, tp_pips)


            avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, 3, 1.5)

            ## TRADE
            trade_order(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True)
            #write_json(json_dict=orders_json, json_file_name=json_file_name)

    total_profit = 0
    positions = get_open_positions()

    for position in positions:
        profit = position.profit
        total_profit += profit
    print('total_profit',total_profit)
    if total_profit > (lot * 1000):
        # close all positions
        for position in positions:
            close_position(position.symbol, position.ticket)

