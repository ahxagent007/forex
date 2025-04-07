import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from stable_baselines3 import PPO
import time
from datetime import datetime
from mt5_utils import initialize_mt5, get_magic_number, trade_order_magic, get_live_data
import pandas_ta as ta



SYMBOL = "BTCUSD"
WINDOW_SIZE = 26
DELAY = 60*5  # seconds between candles

initialize_mt5()


# Load model
model = PPO.load("ppo_forex_model_indicator")

# Real-time loop
symbol = 'BTCUSD'
time_frame = 'M5'
while True:
    df_live = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)
    if df_live is None or len(df_live) < 30:
        print("Waiting for enough data...")
        time.sleep(10)
        continue

    # Add indicators
    df_live.ta.rsi(length=14, append=True)
    df_live.ta.macd(append=True)
    df_live.ta.adx(length=14, append=True)
    df_live.dropna(inplace=True)
    df_live.reset_index(drop=True, inplace=True)

    row = df_live.iloc[-1]  # latest row
    obs = np.array([
        row['close'],
        row['RSI_14'],
        row['MACD_12_26_9'],
        row['MACDh_12_26_9'],
        row['MACDs_12_26_9'],
        row['ADX_14']
    ], dtype=np.float32).reshape(1, -1)

    # Predict action
    action, _ = model.predict(obs, deterministic=True)

    print(f"{datetime.now()} | Action: {action} | Price: {row['close']}")

    # Optional: Send order to MT5
    tp = 20000
    sl = 10000
    if action == 1:
        #send_order(symbol, 'buy', volume=0.1)
        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=SYMBOL, tp_point=tp, sl_point=sl, lot=0.1, action='buy', magic=True,
                          code=106049, MAGIC_NUMBER=MAGIC_NUMBER)
    elif action == 2:
        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=SYMBOL, tp_point=tp, sl_point=sl, lot=0.1, action='sell', magic=True,
                          code=106049, MAGIC_NUMBER=MAGIC_NUMBER)

    time.sleep(DELAY)  # Wait for next M5 candle
