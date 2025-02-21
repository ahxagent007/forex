import MetaTrader5 as mt5
import time

# **CONFIGURATION**
SYMBOL = "BTCUSD"  # Currency pair
LOT_SIZE = 0.1  # Lot size per trade
SCALP_TAKE_PROFIT = 100000  # Profit in pips before closing trade
SLIPPAGE = 5000  # Slippage in points
MAGIC_NUMBER = 3669  # Unique identifier for trades

# Initialize MT5
path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

# # NEW ACC LIVE
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
    print("❌ MT5 Initialization Failed!")
    quit()


def get_price():
    """ Get the current bid and ask prices. """
    price = mt5.symbol_info_tick(SYMBOL)
    return price.bid, price.ask


def place_order(order_type, lot, price):
    """ Places a buy or sell order. """
    # request = {
    #     "action": mt5.TRADE_ACTION_DEAL,
    #     "symbol": SYMBOL,
    #     "volume": lot,
    #     "type": order_type,
    #     "price": price,
    #     "magic": MAGIC_NUMBER,
    #     "comment": "Scalping Hedging",
    #     "type_time": mt5.ORDER_TIME_GTC,
    #     "type_filling": mt5.ORDER_FILLING_IOC
    # }

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": float(lot),
        "type": order_type,
        "price": price,
        "magic": MAGIC_NUMBER,
        "comment": str(order_type),
    }
    print(request)
    result = mt5.order_send(request)
    print(result)
    return result


def get_open_trades():
    """ Get all open trades for the given symbol. """
    return mt5.positions_get(symbol=SYMBOL)


def close_trade(order):
    """ Close an open trade. """
    action = None
    if order.type == mt5.ORDER_TYPE_BUY:
        trade_type = mt5.ORDER_TYPE_SELL
        action = mt5.ORDER_TYPE_BUY
    else:
        trade_type = mt5.ORDER_TYPE_BUY
        action = mt5.ORDER_TYPE_SELL

    price = get_price()[0] if trade_type == mt5.ORDER_TYPE_SELL else get_price()[1]

    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": order.volume,
        "type": trade_type,
        "position": order.ticket,
        "price": price,
        "slippage": SLIPPAGE,
        "magic": MAGIC_NUMBER,
        "comment": "Closing Scalping Hedge",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(close_request)


    place_order(action, LOT_SIZE, bid)
    print("🔄 Reopened Hedge Positions")
    return result


# **Step 1: Open Hedging Orders (BUY & SELL)**
bid, ask = get_price()
buy_order = place_order(mt5.ORDER_TYPE_BUY, LOT_SIZE, ask)
sell_order = place_order(mt5.ORDER_TYPE_SELL, LOT_SIZE, bid)

if buy_order.retcode == mt5.TRADE_RETCODE_DONE and sell_order.retcode == mt5.TRADE_RETCODE_DONE:
    print(f"✅ Hedge Opened: BUY @ {ask}, SELL @ {bid}")
else:
    print("❌ Error placing initial hedge orders.")
    mt5.shutdown()
    quit()

# **Step 2: Monitor Trades and Close Profitable One**
while True:
    time.sleep(0.1)  # Check price every 2 seconds
    open_trades = get_open_trades()

    if not open_trades or len(open_trades) < 2:
        print("⚠️ No active trades found. Exiting.")
        break

    bid, ask = get_price()

    for trade in open_trades:
        entry_price = trade.price_open
        pips_profit = round(
            (bid - entry_price) * 10000 if trade.type == mt5.ORDER_TYPE_BUY else (entry_price - ask) * 10000, 2)

        print(f"🔍 Checking Trade {trade.ticket}: {pips_profit} pips")

        if pips_profit >= SCALP_TAKE_PROFIT:
            close_result = close_trade(trade)

            if close_result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Trade {trade.ticket} closed at {pips_profit} pips profit")
            else:
                print(f"❌ Failed to close trade {trade.ticket}")

    # # **Step 3: Reopen Hedging Position**
    # if len(get_open_trades()) < 2:
    #     bid, ask = get_price()
    #     place_order(mt5.ORDER_TYPE_BUY, LOT_SIZE, ask)
    #     place_order(mt5.ORDER_TYPE_SELL, LOT_SIZE, bid)
    #     print("🔄 Reopened Hedge Positions")

# **Shutdown MT5 Connection**
mt5.shutdown()