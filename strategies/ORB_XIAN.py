import json
from datetime import datetime
import datetime as dt
import time

<<<<<<< HEAD
from mt5_utils import get_live_data, trade_with_price, trade_limit_with_price, initialize_mt5, cancel_all_pending_orders, get_balance
=======
from mt5_utils import get_live_data, trade_with_price, trade_limit_with_price, initialize_mt5, \
    cancel_all_pending_orders, get_balance
>>>>>>> 5bb0dae62f6be589542c24c6be3a32c730efd81e
from common_functions import isNowInTimePeriod

## TOKYO 6:00 - 9:00
## LONDON 13:00 - 16:00
## NEW YORK 19:00 - 22:00
## ORB 2:45 - 3:00

ORB_START_HOUR = 19 #19
ORB_START_MIN = 45 #45
ORB_END_HOUR = 22 #22
ORB_END_MIN = 00 #00

TOKYO_ORB_START_HOUR = 0 #6
TOKYO_ORB_START_MIN = 15 #45
TOKYO_ORB_END_HOUR = 3 #9
TOKYO_ORB_END_MIN = 00 #00


LONDON_ORB_START_HOUR = 7 #13
LONDON_ORB_START_MIN = 15 #45
LONDON_ORB_END_HOUR = 10 #16
LONDON_ORB_END_MIN = 00 #00


NY_ORB_START_HOUR = 13 #19
NY_ORB_START_MIN = 45 #45
NY_ORB_END_HOUR = 16 #22
NY_ORB_END_MIN = 00 #00

TOKYO_PENDING = False
LONDON_PENDING = False
NY_PENDING = False

SESSION = "NONE"
def check_status(symbol):
    global TOKYO_ORB_START_HOUR, TOKYO_ORB_START_MIN, TOKYO_ORB_END_HOUR, TOKYO_ORB_END_MIN

    global LONDON_ORB_START_HOUR, LONDON_ORB_START_MIN, LONDON_ORB_END_HOUR, LONDON_ORB_END_MIN

    global NY_ORB_START_HOUR, NY_ORB_START_MIN, NY_ORB_END_HOUR, NY_ORB_END_MIN

    global TOKYO_PENDING, LONDON_PENDING, NY_PENDING

    global SESSION

    
    #check if ORB complete with date and no trade

    ##TOKYO
    if isNowInTimePeriod(dt.time(TOKYO_ORB_START_HOUR, TOKYO_ORB_START_MIN), dt.time(TOKYO_ORB_END_HOUR, TOKYO_ORB_END_MIN),
                         dt.datetime.now().time()):
        TOKYO_PENDING = True
        if NY_PENDING:
            cancel_all_pending_orders()
            NY_PENDING = False

        SESSION = "TOKYO"
        date = get_date()
        try:
            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)
                symbol_data = data[date][symbol]

                #print(symbol, 'ORB STATUS CHECK >> TRADED >> ' + str(symbol_data['TRADED']))

                return not symbol_data['TRADED']

        except Exception as e:
            print('EXCEPTION >>>' + str(e))
            print('CREATING ORB')
            # ORB Created
            data_df = get_live_data(symbol=symbol, time_frame='M15', prev_n_candles=20)
            orb_high = data_df['high'].iloc[-2]
            orb_low = data_df['low'].iloc[-2]

            symbol_data = {
                "ORB_HIGH": orb_high,
                "ORB_LOW": orb_low,
                "CREATED": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "TRADED": False
            }

            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)

                try:
                    data[date][symbol] = symbol_data
                except:
                    data[date] = {}
                    data[date][symbol] = symbol_data
                #print(data)
            with open('time_counts/orb_xian.json', 'w') as outfile:
                json.dump(data, outfile)

            return True

    ## LONDON
    elif isNowInTimePeriod(dt.time(LONDON_ORB_START_HOUR, LONDON_ORB_START_MIN), dt.time(LONDON_ORB_END_HOUR, LONDON_ORB_END_MIN), dt.datetime.now().time()):
        SESSION = "LONDON"
        date = get_date()

        LONDON_PENDING = True
        if TOKYO_PENDING:
            cancel_all_pending_orders()
            TOKYO_PENDING = False

        try:
            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)
                symbol_data = data[date][symbol]

                #print(symbol, 'ORB STATUS CHECK >> TRADED >> '+str(symbol_data['TRADED']))

                return not symbol_data['TRADED']

        except Exception as e:
            print('EXCEPTION >>>'+str(e))
            print('CREATING ORB')
            # ORB Created
            data_df = get_live_data(symbol=symbol, time_frame='M15', prev_n_candles=20)
            orb_high = data_df['high'].iloc[-2]
            orb_low = data_df['low'].iloc[-2]

            symbol_data = {
                "ORB_HIGH": orb_high,
                "ORB_LOW": orb_low,
                "CREATED": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "TRADED": False
            }

            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)

                try:
                    data[date][symbol] = symbol_data
                except:
                    data[date] = {}
                    data[date][symbol] = symbol_data
                #print(data)
            with open('time_counts/orb_xian.json', 'w') as outfile:
                json.dump(data, outfile)

            return True

    ## NEW YORK
    elif isNowInTimePeriod(dt.time(NY_ORB_START_HOUR, NY_ORB_START_MIN), dt.time(NY_ORB_END_HOUR, NY_ORB_END_MIN), dt.datetime.now().time()):
        SESSION = "NY"
        date = get_date()

        NY_PENDING = True
        if LONDON_PENDING:
            cancel_all_pending_orders()
            LONDON_PENDING = False

        try:
            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)
                symbol_data = data[date][symbol]

                #print(symbol, 'ORB STATUS CHECK >> TRADED >> '+str(symbol_data['TRADED']))

                return not symbol_data['TRADED']

        except Exception as e:
            print('EXCEPTION >>>'+str(e))
            print('CREATING ORB')
            # ORB Created
            data_df = get_live_data(symbol=symbol, time_frame='M15', prev_n_candles=20)
            orb_high = data_df['high'].iloc[-2]
            orb_low = data_df['low'].iloc[-2]

            symbol_data = {
                "ORB_HIGH": orb_high,
                "ORB_LOW": orb_low,
                "CREATED": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "TRADED": False
            }

            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)

                try:
                    data[date][symbol] = symbol_data
                except:
                    data[date] = {}
                    data[date][symbol] = symbol_data
                #print(data)
            with open('time_counts/orb_xian.json', 'w') as outfile:
                json.dump(data, outfile)

            return True

    else:
        cancel_all_pending_orders()
        time.sleep(5*60)

def get_date():
    global SESSION
    # Get current date and time
    now = datetime.now()

    # Extract just the date
    current_date = now.date()

    return SESSION+"_"+current_date.strftime("%d-%m-%Y")

def get_orb_high_low(symbol):

    # json_example = {
    #     "date": {
    #         "XAUUSD": {
    #             "ORB_HIGH": 100,
    #             "ORB_LOW": 200,
    #             "CREATED": "",
    #             "TRADED": False
    #         }
    #     }
    # }

    date = get_date()

    with open('time_counts/orb_xian.json') as json_file:
        data = json.load(json_file)
        try:
            symbol_data = data[date][symbol]
            return symbol_data['ORB_HIGH'], symbol_data['ORB_LOW']
        except:
            return None, None


def update_trade_log(symbol, entries):
    #Update Json file
    date = get_date()
    with open('time_counts/orb_xian.json') as json_file:
        data = json.load(json_file)
        data[date][symbol]['TRADED'] = True
        data[date][symbol]['ENTRIES'] = entries

    with open('time_counts/orb_xian.json', 'w') as outfile:
        json.dump(data, outfile)

    print('TRADE LOG UPDATED')

def calculate_lot_size(symbol, sl_diff):

    risk = 2

    balance = get_balance()

    pip_multiplier = {
        'GBPUSD': 10000,
        'USDCHF': 10000,
        'USDJPY': 100,
        'US30': 1,
        'EURGBP': 10000,
        'AUDUSD': 10000,
        'XAUUSD': 100,
        'EURUSD': 10000
    }

    sl_pip = round(sl_diff * pip_multiplier[symbol])

    pip_value = {
        'GBPUSD': 10,
        'USDCHF': 10.97,
        'USDJPY': 6.48,
        'US30': 1,
        'EURGBP': 12.48,
        'AUDUSD': 10,
        'XAUUSD': 1,
        'EURUSD': 10
    }

    lot_size = round(balance * (risk / 100) / (pip_value[symbol] * sl_pip), 2)

    return lot_size

initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']

while True:

    for symbol in SYMBOL_LIST:
        time.sleep(1)
        
        ready_trade = check_status(symbol)

        if ready_trade:
            data_df = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=20)

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

                entry_price_2 = (orb_high + orb_low) / 2 # PROBLEM
                entry_price_3 = orb_low

                sl_1 = current_price - orb_diff
                sl_2 = entry_price_2 - orb_diff
                sl_3 = entry_price_3 - orb_diff

                tp_1 = current_price + orb_diff*1.5
                tp_2 = entry_price_2 + orb_diff*1.5
                tp_3 = entry_price_3 + orb_diff*2.5
            elif data_df['close'].iloc[-2] < orb_low:
                print(symbol+' PRICE BROKE  >>> DOWN')
                # ORB Break SELL
                current_price = data_df['close'].iloc[-1]
                ORB_Action = 'sell'

                entry_price_2 = (orb_high + orb_low) / 2
                entry_price_3 = orb_high

                sl_1 = current_price + orb_diff
                sl_2 = entry_price_2 + orb_diff
                sl_3 = entry_price_3 + orb_diff

                tp_1 = current_price - orb_diff*1.5
                tp_2 = entry_price_2 - orb_diff*1.5
                tp_3 = entry_price_3 - orb_diff*2.5
            #else:
            #    print(symbol+' PRICE NOT BROKEN ORB')

            if ORB_Action:

                lot_1 = calculate_lot_size(symbol=symbol, sl_diff=abs(current_price-sl_1))
                lot_2 = calculate_lot_size(symbol=symbol, sl_diff=abs(entry_price_2-sl_2))
                lot_3 = calculate_lot_size(symbol=symbol, sl_diff=abs(entry_price_3-sl_3))

                # Trade 1 ORB Top
                trade_with_price(action=ORB_Action, symbol=symbol,
                                 lot=lot_1, tp_price=tp_1, sl_price=sl_1)

                # Trade 2 ORB Middle (Pullback)
                trade_limit_with_price(action=ORB_Action, symbol=symbol,
                                       lot=lot_2, entry_price=entry_price_2,
                                       tp_price=tp_2, sl_price=sl_2)

                # Trade 3 ORB Bottom (Pullback)
                trade_limit_with_price(action=ORB_Action, symbol=symbol,
                                       lot=lot_3, entry_price=entry_price_3,
                                       tp_price=tp_3, sl_price=sl_3)

                # Update trade log
                entries = {
                    'entry_1': {
                        'price': current_price,
                        'sl':sl_1,
                        'tp': tp_1,
                        'lot': lot_1
                    },
                    'entry_2': {
                        'price': entry_price_2,
                        'sl': sl_2,
                        'tp': tp_2,
                        'lot': lot_2
                    },
                    'entry_3': {
                        'price': entry_price_3,
                        'sl': sl_3,
                        'tp': tp_3,
                        'lot': lot_3
                    }
                }
                update_trade_log(symbol, entries)
