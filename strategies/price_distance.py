import time

from mt5_utils import get_live_data, initialize_mt5, trade_order_price, calculate_lot_size, get_all_positions

mt5 = initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']

def get_trade_max_percent(symbol):
    percent_dit = {
        'GBPUSD': 0.5,
        'USDCHF': 0.6,
        'USDJPY': 0.6,
        'US30': 0.5,
        'EURGBP': 0.7,
        'AUDUSD': 0.5,
        'XAUUSD': 1,
        'EURUSD': 0.7,

        'BTCUSD': 1
    }

    return percent_dit[symbol]

while True:
    for symbol in SYMBOL_LIST:



        df = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=300)
        df['EMA'] = df['close'].ewm(span=200).mean()
        current_price = df.iloc[-1].close
        ema = df.iloc[-1].EMA

        ema_distance_percent = round(((ema - current_price) / current_price) * 100, 2)

        print(f"{symbol} is {ema_distance_percent}% far from the price {current_price}")

        ## CHECK IF RUNNING TRADE
        running_positions = get_all_positions(symbol)



        if len(running_positions) > 0:
            time.sleep(1)
            continue

        trade_max_percent = get_trade_max_percent(symbol)

        if abs(ema_distance_percent) < trade_max_percent:
            time.sleep(1)
            continue

        ema_distance_price = ema - current_price

        tp_distance = abs(ema_distance_price) / 5
        
        sl_distance = tp_distance / 3

        lot = calculate_lot_size(symbol=symbol, sl_diff=sl_distance)
        print('lot', lot)

        if ema_distance_price > 0:
            action  = 'buy'
        else:
            action = 'sell'

        if action == 'buy':
            tp_price = current_price + tp_distance
            sl_price = current_price - sl_distance
        elif action == 'sell':
            tp_price = current_price - tp_distance
            sl_price = current_price + sl_distance


        # check if there is any running trade
        if action:
            trade_order_price(symbol=symbol, tp_price=tp_price, sl_price=sl_price, lot=lot, action=action, magic=False, code=0, MAGIC_NUMBER=0)
            #print('trade ', symbol, action)

        time.sleep(1)

