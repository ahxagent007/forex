import pickle
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from stable_baselines3 import PPO
import time
from datetime import datetime
from common_functions import check_duplicate_orders, write_json
from mt5_utils import initialize_mt5, get_magic_number, trade_order_magic, get_live_data, get_all_positions, \
    close_all_positions
import pandas_ta as ta



#SYMBOL = "EURUSD"
WINDOW_SIZE = 100
DELAY = 60 * 5 #60 * 5 # seconds between candles

initialize_mt5()
time_frame = 'M5'

tp_dict = {
    'BTCUSD': 20000,
    'EURUSD': 400,
    'AUDUSD': 400,
    'GBPUSD': 400,
    'NZDUSD': 210,
    'EURCHF': 210,
    'GBPCHF': 400,
    'AUDCHF': 400,
    'USDCHF': 400,
    'AUDCAD': 400,
    'NZDCAD': 400,
    'USDCAD': 400,
    'EURCAD': 400,
    'GBPCAD': 400,
    'EURNZD': 1000,
    'EURGBP': 400,
    'EURAUD': 2000,
    'GBPNZD': 1200,
    'CADJPY': 600,
    'USDJPY': 600,
    'EURJPY': 600,
    'GBPJPY': 600,
    'CHFJPY': 600,
    'AUDJPY': 600,
    'XAUUSD': 40000
}

sl_dict = {
    'BTCUSD': 20000,
    'EURUSD': 100,
    'AUDUSD': 100,
    'GBPUSD': 100,
    'NZDUSD': 70,
    'EURCHF': 70,
    'GBPCHF': 100,
    'AUDCHF': 100,
    'USDCHF': 100,
    'AUDCAD': 100,
    'NZDCAD': 100,
    'USDCAD': 100,
    'EURCAD': 100,
    'GBPCAD': 100,
    'EURNZD': 250,
    'EURGBP': 100,
    'EURAUD': 500,
    'GBPNZD': 300,
    'CADJPY': 200,
    'USDJPY': 200,
    'EURJPY': 200,
    'GBPJPY': 200,
    'CHFJPY': 200,
    'AUDJPY': 200,
    'XAUUSD': 14000
}

symbol_list = ['BTCUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'EURCHF', 'GBPCHF', 'AUDCHF', 'USDCHF', 'AUDCAD', 'NZDCAD', 'USDCAD', 'EURCAD',
               'GBPCAD', 'EURNZD', 'EURGBP', 'EURAUD', 'GBPNZD', 'CADJPY', 'USDJPY', 'EURJPY', 'GBPJPY', 'CHFJPY', 'AUDJPY', 'XAUUSD']

#symbol_list = ['EURUSD']
# Real-time loop $ 779.55
while True:
    for SYMBOL in symbol_list:
        close_all_positions(SYMBOL)

    for SYMBOL in symbol_list:
        skip_min = 5
        json_file_name = 'RL'
        running_trade_status, orders_json = check_duplicate_orders(symbol=SYMBOL, skip_min=skip_min,
                                                                   json_file_name=json_file_name)
        # if running_trade_status:
        #     time.sleep(DELAY)
        #     continue

        # Load model
        model = PPO.load("models/ppo_forex_model_indicator_" + SYMBOL + "_" + time_frame)

        df_live = get_live_data(symbol=SYMBOL, time_frame=time_frame, prev_n_candles=WINDOW_SIZE)
        if df_live is None or len(df_live) < WINDOW_SIZE:
            print("Waiting for enough data...")
            time.sleep(10)
            continue

        # Add indicators
        df_live.ta.rsi(length=14, append=True)
        df_live.ta.macd(append=True)
        df_live.ta.adx(length=14, append=True)
        df_live.ta.ema(length=50, append=True)
        df_live['EMA_DIFF'] = df_live['EMA_50'] - df_live['close']
        df_live.dropna(inplace=True)
        df_live.reset_index(drop=True, inplace=True)

        ## NORMALIZE DATA
        with open("models/feature_stats_{0}_{1}.pkl".format(SYMBOL, time_frame), "rb") as f:
            stats = pickle.load(f)

        feature_means = stats["mean"]
        feature_stds = stats["std"]
        features = stats['features']

        df_live[features] = (df_live[features] - feature_means) / feature_stds

        row = df_live.iloc[-1]  # latest row
        # obs = np.array([
        #     row['close'],
        #     row['RSI_14'],
        #     row['MACD_12_26_9'],
        #     row['MACDh_12_26_9'],
        #     row['MACDs_12_26_9'],
        #     row['ADX_14']
        # ], dtype=np.float32).reshape(1, -1)
        #
        # print(obs)
        i = 0
        data = df_live.tail(2)
        print(data.shape)
        obs = data[['close', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'ADX_14', 'EMA_DIFF']].values
        obs = obs.flatten().astype(np.float32)  # shape: (history_length * features,)

        # Predict action
        action, _ = model.predict(obs, deterministic=True)

        print(f"{datetime.now()} | Action: {action} | Price: {row['close']}")

        # Optional: Send order to MT5
        tp = tp_dict[SYMBOL]/2
        sl = sl_dict[SYMBOL]/2


        if action == 1:

            # send_order(symbol, 'buy', volume=0.1)
            MAGIC_NUMBER = get_magic_number()
            trade_order_magic(symbol=SYMBOL, tp_point=tp, sl_point=sl, lot=0.1, action='buy', magic=True,
                              code=106049, MAGIC_NUMBER=MAGIC_NUMBER)
            write_json(json_dict=orders_json, json_file_name=json_file_name)

        elif action == 2:
            MAGIC_NUMBER = get_magic_number()
            trade_order_magic(symbol=SYMBOL, tp_point=tp, sl_point=sl, lot=0.1, action='sell', magic=True,
                              code=106049, MAGIC_NUMBER=MAGIC_NUMBER)
            write_json(json_dict=orders_json, json_file_name=json_file_name)

    time.sleep(DELAY)  # Wait
