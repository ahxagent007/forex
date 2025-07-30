
import threading
import time

from mt5_utils import initialize_mt5, get_live_data, get_all_positions, close_position, trade_order_wo_tp, get_balance


def calculate_lot_size_point(symbol, sl_point):



    risk = 2

    balance = get_balance()

    pip_value = {
        'GBPUSD': 10,
        'USDCHF': 10.97,
        'USDJPY': 6.48,
        'US30': 1,
        'EURGBP': 12.48,
        'AUDUSD': 10,
        'XAUUSD': 1,
        'EURUSD': 10,
        'BTCUSD': 0.1
    }
    # Lot Size = (Account Balance × Risk %) / (Stop Loss (in pips) × Pip Value per lot)
    lot_size = round(balance * (risk / 100) / (pip_value[symbol] * sl_point), 2)

    return round(lot_size * 10, 2)

def get_fixed_sl_tp_point(symbol, RR):

    fixed_sl_tp = {
        'XAUUSD' : {
            'tp':8000,
            'sl': 3000
        },
        'US30' : {
            'tp': 1000,
            'sl': 300
        },
        'EURUSD' : {
            'tp': 100,
            'sl': 30
        },
        'USDJPY' : {
            'tp': 100,
            'sl': 30
        },
        'GBPUSD' : {
            'tp': 100,
            'sl': 30
        },
        'USDCHF' : {
            'tp': 100,
            'sl': 30
        },
        'EURGBP' : {
            'tp': 100,
            'sl': 30
        },
        'AUDUSD' : {
            'tp': 100,
            'sl': 30
        },
        'USDCAD' : {
            'tp': 100,
            'sl': 30
        },
        'BTCUSD' : {
            'tp': 40000,
            'sl': 20000
        }
    }
    return fixed_sl_tp[symbol]['sl'] * RR, fixed_sl_tp[symbol]['sl']


mt5 = initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD', 'BTCUSD']

#SYMBOL_LIST = ['BTCUSD']

prev_price_dict = {
    'GBPUSD': 0,
    'USDCHF': 0,
    'USDJPY': 0,
    'US30': 0,
    'EURGBP': 0,
    'AUDUSD': 0,
    'XAUUSD': 0,
    'EURUSD': 0,
    'BTCUSD': 0
}
profit_dict = {
}

lock = threading.Lock()  # To avoid race conditions

def check_trade():
    global k
    global SYMBOL_LIST
    while True:
        with lock:
            # CHeck if there is any trade and close trade
            print('profit_dict', profit_dict)
            for symbol in SYMBOL_LIST:
                positions = get_all_positions(symbol)
                for pos in positions:
                    current_profit = pos.profit

                    try:
                        profit_dict[pos.identifier]['profit_1']
                    except:
                        profit_dict[pos.identifier] = {}
                        profit_dict[pos.identifier]['profit_1'] = current_profit
                        profit_dict[pos.identifier]['profit_2'] = current_profit
                        profit_dict[pos.identifier]['profit_3'] = current_profit

                    # if current_profit < profit_dict[pos.identifier]['profit_1'] and \
                    #         profit_dict[pos.identifier]['profit_1'] < profit_dict[pos.identifier]['profit_2'] and \
                    #         profit_dict[pos.identifier]['profit_2'] < profit_dict[pos.identifier]['profit_3']:
                    if current_profit < profit_dict[pos.identifier]['profit_1'] < profit_dict[pos.identifier]['profit_2'] < profit_dict[pos.identifier]['profit_3']:
                        # Close position
                        close_position(symbol, pos.ticket)
                        del profit_dict[pos.identifier]
                    else:
                        profit_dict[pos.identifier]['profit_3'] = profit_dict[pos.identifier]['profit_2']
                        profit_dict[pos.identifier]['profit_2'] = profit_dict[pos.identifier]['profit_1']
                        profit_dict[pos.identifier]['profit_1'] = current_profit



        time.sleep(2)

# Start background thread
thread = threading.Thread(target=check_trade)
thread.daemon = True
thread.start()

# Main loop
while True:
    for symbol in SYMBOL_LIST:
        df = get_live_data(symbol=symbol, time_frame='M1', prev_n_candles=10)
        with lock:
            # check if there is any sudden price movement
            current_price = df.iloc[-1].close
            if prev_price_dict[symbol] == 0:
                prev_price_dict[symbol] = current_price

            movement_percent = round(((prev_price_dict[symbol] - current_price) / current_price) * 100, 2)
            prev_price_dict[symbol] = current_price
            print(f"[{prev_price_dict[symbol]}, {current_price}] price movement percent for {symbol} is {movement_percent}%")

            # Negative buy, positive sell
            if abs(movement_percent) > 0.04:
                if movement_percent < 0:
                    # Buy
                    action = 'buy'
                else:
                    # Sell
                    action = 'sell'

                tp_point, sl_point = get_fixed_sl_tp_point(symbol=symbol, RR=2)
                lot = calculate_lot_size_point(symbol, sl_point)
                trade_order_wo_tp(symbol=symbol, sl_point=sl_point, lot=lot, action=action, magic=False)

    time.sleep(2)