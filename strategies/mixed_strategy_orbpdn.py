import threading
import time

from Nahid.strategies.ORB_XIAN import check_status, get_orb_high_low, support_resistance_ema, update_trade_log
from mt5_utils import initialize_mt5, get_live_data, get_all_positions, close_position, trade_order_wo_tp, get_balance, \
    calculate_lot_size_point, trade_order, calculate_lot_size, trade_order_price


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

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']

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


lock = threading.Lock()  # To avoid race conditions

def news_trade():
    # Main loop
    while True:
        for symbol in SYMBOL_LIST:
            df_m1 = get_live_data(symbol=symbol, time_frame='M1', prev_n_candles=10)
            with lock:
                # check if there is any sudden price movement
                current_price = df_m1.iloc[-1].close
                if prev_price_dict[symbol] == 0:
                    prev_price_dict[symbol] = current_price

                movement_percent = round(((prev_price_dict[symbol] - current_price) / current_price) * 100, 2)
                prev_price_dict[symbol] = current_price
                print(
                    f"[{prev_price_dict[symbol]}, {current_price}] price movement percent for {symbol} is {movement_percent}%")

                # Negative buy, positive sell
                if abs(movement_percent) > 0.1:
                    sl_tp_diff = abs(df_m1.df_m1.iloc[-2].open - df_m1.df_m1.iloc[-2].close)

                    if movement_percent < 0:
                        # Buy
                        action = 'buy'
                        tp_news = current_price + sl_tp_diff
                        sl_news = current_price - sl_tp_diff
                    else:
                        # Sell
                        action = 'sell'
                        tp_news = current_price - sl_tp_diff
                        sl_news = current_price + sl_tp_diff

                    lot = calculate_lot_size(symbol, sl_tp_diff)

                    trade_order_price(symbol=symbol, tp_price=tp_news, sl_price=sl_news, lot=lot, action=action,
                                      magic=False, code=0, MAGIC_NUMBER=0)

        time.sleep(2)

# Start background thread
thread = threading.Thread(target=news_trade)
thread.daemon = True
thread.start()

# Main loop
while True:
    for symbol in SYMBOL_LIST:
        time.sleep(1)
        #print(symbol)
        #get_high_low(symbol=symbol, hour=0, min=15)

        ready_trade = check_status(symbol)

        if ready_trade:
            data_df = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=300)

            orb_high, orb_low = get_orb_high_low(symbol)
            current_price = 0

            if not orb_high:
                print('ORB NOT CREATED')
                continue

            orb_diff = orb_high - orb_low

            # Check if price closed ORB
            ORB_Action = None
            if data_df['close'].iloc[-2] > orb_high:
                print(symbol+' PRICE BROKE >>>> UP')
                current_price = data_df['close'].iloc[-1]
                # ORB Break BUY
                ORB_Action = 'buy'

                entry_price_1 = orb_high
                entry_price_2 = (orb_high + orb_low) / 2 # PROBLEM
                entry_price_3 = orb_low


                #sl_1 = entry_price_1 - orb_diff
                sl_1 = current_price - orb_diff
                sl_2 = entry_price_2 - orb_diff
                sl_3 = entry_price_3 - orb_diff

                #tp_1 = entry_price_1 + orb_diff*1.5
                tp_1 = current_price + orb_diff*1.5
                tp_2 = entry_price_2 + orb_diff*1.5
                tp_3 = entry_price_3 + orb_diff*2.5


            elif data_df['close'].iloc[-2] < orb_low:
                print(symbol+' PRICE BROKE  >>> DOWN')
                # ORB Break SELL
                current_price = data_df['close'].iloc[-1]
                ORB_Action = 'sell'

                entry_price_1 = orb_low
                entry_price_2 = (orb_high + orb_low) / 2
                entry_price_3 = orb_high

                #sl_1 = current_price + orb_diff
                sl_1 = entry_price_1 + orb_diff
                sl_2 = entry_price_2 + orb_diff
                sl_3 = entry_price_3 + orb_diff

                #tp_1 = current_price - orb_diff*1.5
                tp_1 = entry_price_1 - orb_diff*1.5
                tp_2 = entry_price_2 - orb_diff*1.5
                tp_3 = entry_price_3 - orb_diff*2.5



            if ORB_Action:

                trade_type = None
                closest_support_percent, closest_resistance_percent, ema_diff_percent = support_resistance_ema(data_df)
                print(F"Closest Support {closest_support_percent}, closest Resistance {closest_resistance_percent} and 200 EMA {ema_diff_percent}")

                ## Trade Logic
                if ORB_Action == 'buy':

                    if abs(closest_support_percent) < 15:
                        if abs(ema_diff_percent) < 5:
                            trade_type = 'now'
                        elif -5 > ema_diff_percent < -25:
                            trade_type = 'now'
                        elif -25 > ema_diff_percent < -50:
                            trade_type = 'middle'
                        elif ema_diff_percent > -50:
                            trade_type = 'bottom'

                    elif -15 > closest_support_percent < -40:

                        if abs(ema_diff_percent) < 5:
                            trade_type = 'top'
                        elif -5 > ema_diff_percent < -25:
                            trade_type = 'middle'
                        elif -25 > ema_diff_percent < -50:
                            trade_type = 'bottom'
                        elif ema_diff_percent > -50:
                            trade_type = None

                    elif -40 > closest_support_percent < -60:

                        if abs(ema_diff_percent) < 5:
                            if closest_resistance_percent > 30:
                                trade_type = 'top'
                        elif -5 > ema_diff_percent < -25:
                            trade_type = 'bottom'
                        elif -25 > ema_diff_percent < -50:
                            trade_type = None
                        elif ema_diff_percent > -50:
                            trade_type = None
                elif ORB_Action == 'sell':

                    if abs(closest_resistance_percent) < 15:

                        if abs(ema_diff_percent) < 5:
                            trade_type = 'now'
                        elif 5 > ema_diff_percent < 25:
                            trade_type = 'now'
                        elif 25 > ema_diff_percent < 50:
                            trade_type = 'middle'
                        elif ema_diff_percent > 50:
                            trade_type = 'bottom'

                    elif 15 > closest_resistance_percent < 40:

                        if abs(ema_diff_percent) < 5:
                            trade_type = 'top'
                        elif 5 > ema_diff_percent < 25:
                            trade_type = 'middle'
                        elif 25 > ema_diff_percent < 50:
                            trade_type = 'bottom'
                        elif ema_diff_percent > 50:
                            trade_type = None

                    elif 40 > closest_resistance_percent < 60:

                        if abs(ema_diff_percent) < 5:
                            if closest_support_percent > 30:
                                trade_type = 'top'
                        elif 5 > ema_diff_percent < 25:
                            trade_type = 'bottom'
                        elif 25 > ema_diff_percent < 50:
                            trade_type = None
                        elif ema_diff_percent > 50:
                            trade_type = None


                if trade_type:

                    lot = calculate_lot_size(symbol, orb_diff)

                    if trade_type == 'now':
                        #Trade now
                        trade_order_price(symbol=symbol, tp_price=tp_1, sl_price=sl_1, lot=lot, action=ORB_Action, magic=False, code=0, MAGIC_NUMBER=0)


                    entries = {
                        'action': ORB_Action,
                        'trade_type': trade_type,
                        'entry': {
                            'price': current_price,
                            'sl': sl_1,
                            'tp': tp_1
                        },
                        'data':{
                            'support': closest_support_percent,
                            'resistance': closest_resistance_percent,
                            'ema': ema_diff_percent
                        }
                    }
                    update_trade_log(symbol, entries)
