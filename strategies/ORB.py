import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time

# CONFIGURATION
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
LOT = 0.1
RISK_MULTIPLIER = 1.5
MAGIC = 55555

# Time settings
OR_START = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
OR_END = OR_START + timedelta(minutes=30)
TRADE_END = OR_START + timedelta(hours=2)

# Initialize
mt5.initialize()

def get_data(symbol, timeframe, start_time, end_time):
    rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_opening_range():
    df = get_data(SYMBOL, TIMEFRAME, OR_START, OR_END)
    if df.empty:
        return None
    return df['high'].max(), df['low'].min()

def check_breakout(high, low):
    current_price = mt5.symbol_info_tick(SYMBOL).last
    if current_price > high:
        return "buy"
    elif current_price < low:
        return "sell"
    else:
        return None

def place_orb_trade(direction, high, low):
    price = mt5.symbol_info_tick(SYMBOL).ask if direction == "buy" else mt5.symbol_info_tick(SYMBOL).bid
    sl = low if direction == "buy" else high
    tp = price + RISK_MULTIPLIER * (high - low) if direction == "buy" else price - RISK_MULTIPLIER * (high - low)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT,
        "type": mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": MAGIC,
        "comment": "ORB_Breakout",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print(f"{direction.upper()} ORDER SENT: {result}")

def already_in_trade():
    positions = mt5.positions_get(symbol=SYMBOL)
    return len(positions) > 0

# === MAIN LOOP ===
print("ORB Strategy Started...")
orb_high, orb_low = None, None
trade_taken = False

while True:
    now = datetime.utcnow()

    if now < OR_END:
        print("Waiting for opening range to complete...")
        time.sleep(30)
        continue

    if now >= OR_END and orb_high is None:
        print("Calculating Opening Range...")
        opening = get_opening_range()
        if opening:
            orb_high, orb_low = opening
            print(f"Opening Range: High={orb_high:.2f}, Low={orb_low:.2f}")
        else:
            print("Failed to get opening range. Retrying...")
            time.sleep(30)
        continue

    if OR_END <= now <= TRADE_END and not trade_taken:
        direction = check_breakout(orb_high, orb_low)
        if direction and not already_in_trade():
            place_orb_trade(direction, orb_high, orb_low)
            trade_taken = True

    if now > TRADE_END:
        print("Trading window closed. Exiting.")
        break

    time.sleep(15)
