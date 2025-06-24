import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
import ta


def initialize_mt5():
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

    # # NEW ACC LIVE 178.39
    # login = 181244000
    # password = 'ABCabc123!@#'
    # server = 'Exness-MT5Trial6'

    # ## PRO NEW
    login = 182331894
    password = 'ABCabc123!@#'
    server = 'Exness-MT5Trial6'

    timeout = 10000
    portable = False
    if mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
        print("Initialization successful")
    else:
        print('Initialize failed')

# ========== CONFIG ========== #
SYMBOL = "BTCUSD"
TIMEFRAME = mt5.TIMEFRAME_M2
LOT = 0.1
RISK_PER_TRADE = 0.01  # 1% risk
SL_ATR_MULT = 2.5
TP_RATIO = 1.5
MAGIC = 123456
MAX_SPREAD = 2200  # in points

# ========== INIT ========== #
initialize_mt5()

def get_data(symbol, timeframe, bars=200):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def calculate_indicators(df):
    df['ema14'] = ta.trend.ema_indicator(df['close'], window=14)
    df['ema28'] = ta.trend.ema_indicator(df['close'], window=28)
    df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=9)
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=12).rsi()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    df['willr'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=50)
    df['high_55'] = df['high'].rolling(window=55).max()
    df['low_55'] = df['low'].rolling(window=55).min()
    return df

def check_spread():
    symbol_info = mt5.symbol_info(SYMBOL)
    return (symbol_info.ask - symbol_info.bid) < MAX_SPREAD * mt5.symbol_info(SYMBOL).point

def place_order(direction, sl_price, tp_price):
    price = mt5.symbol_info_tick(SYMBOL).ask if direction == "buy" else mt5.symbol_info_tick(SYMBOL).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT,
        "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "magic": MAGIC,
        "comment": "golden_scalp_bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print(f"Order result: {result}")
    return result

# ========== MAIN SCANNER LOOP ========== #
def scan_and_trade():
    df = get_data(SYMBOL, TIMEFRAME)
    df = calculate_indicators(df)
    last = df.iloc[-1]

    if not check_spread():
        print("Spread too high, skipping...")
        return

    # Entry Signals
    if last['ema14'] > last['ema28'] and \
       last['adx'] > 25 and \
       last['close'] > last['high_55'] and \
       last['rsi'] > 55:

        sl = last['close'] - SL_ATR_MULT * last['atr']
        tp = last['close'] + (last['close'] - sl) * TP_RATIO
        print("LONG SIGNAL")
        place_order("buy", sl_price=sl, tp_price=tp)

    elif last['ema14'] < last['ema28'] and \
         last['adx'] > 25 and \
         last['close'] < last['low_55'] and \
         last['rsi'] < 45:

        sl = last['close'] + SL_ATR_MULT * last['atr']
        tp = last['close'] - (sl - last['close']) * TP_RATIO
        print("SHORT SIGNAL")
        place_order("sell", sl_price=sl, tp_price=tp)

# ========== LOOP IT (like every 5 minutes) ========== #
while True:
    now = datetime.now()
    if now.minute % 2 == 0:  # every 5 min candle close
        print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scanning...")
        scan_and_trade()
        time.sleep(60)
    else:
        time.sleep(20)
