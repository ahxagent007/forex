import json
from datetime import datetime
import datetime as dt
import time

from mt5_utils import get_live_data, trade_with_price, trade_limit_with_price, initialize_mt5, cancel_all_pending_orders
from common_functions import isNowInTimePeriod

## TOKYO 6:00 - 9:00
## LONDON 13:00 - 16:00
## NEW YORK 19:00 - 22:00
## ORB 2:45 - 3:00

ORB_START_HOUR = 19 #19
ORB_START_MIN = 45 #45
ORB_END_HOUR = 22 #22
ORB_END_MIN = 00 #00

TOKYO_ORB_START_HOUR = 6 #19
TOKYO_ORB_START_MIN = 15 #45
TOKYO_ORB_END_HOUR = 9 #22
TOKYO_ORB_END_MIN = 00 #00


LONDON_ORB_START_HOUR = 13 #19
LONDON_ORB_START_MIN = 15 #45
LONDON_ORB_END_HOUR = 16 #22
LONDON_ORB_END_MIN = 00 #00


NY_ORB_START_HOUR = 19 #19
NY_ORB_START_MIN = 45 #45
NY_ORB_END_HOUR = 22 #22
NY_ORB_END_MIN = 00 #00

TOKYO_PENDING = False
LONDON_PENDING = False
NY_PENDING = False

SESSION = "_"
def check_status(symbol):
    global TOKYO_ORB_START_HOUR, TOKYO_ORB_START_MIN, TOKYO_ORB_END_HOUR, TOKYO_ORB_END_MIN

    global LONDON_ORB_START_HOUR, LONDON_ORB_START_MIN, LONDON_ORB_END_HOUR, LONDON_ORB_END_MIN

    global NY_ORB_START_HOUR, NY_ORB_START_MIN, NY_ORB_END_HOUR, NY_ORB_END_MIN

    global TOKYO_PENDING, LONDON_PENDING, NY_PENDING

    global SESSION

    date = get_date()
    #check if ORB complete with date and no trade

    ##TOKYO
    if isNowInTimePeriod(dt.time(TOKYO_ORB_START_HOUR, TOKYO_ORB_START_MIN), dt.time(TOKYO_ORB_END_HOUR, TOKYO_ORB_END_MIN),
                         dt.datetime.now().time()):
        TOKYO_PENDING = True
        if NY_PENDING:
            cancel_all_pending_orders()
            NY_PENDING = False

        SESSION = "TOKYO"
        try:
            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)
                symbol_data = data[date][symbol]

                print(symbol, 'ORB STATUS CHECK >> TRADED >> ' + str(symbol_data['TRADED']))

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
                print(data)
            with open('time_counts/orb_xian.json', 'w') as outfile:
                json.dump(data, outfile)

            return True

    ## LONDON
    if isNowInTimePeriod(dt.time(LONDON_ORB_START_HOUR, LONDON_ORB_START_MIN), dt.time(LONDON_ORB_END_HOUR, LONDON_ORB_END_MIN), dt.datetime.now().time()):
        SESSION = "LONDON"

        LONDON_PENDING = True
        if TOKYO_PENDING:
            cancel_all_pending_orders()
            TOKYO_PENDING = False

        try:
            with open('time_counts/orb_xian.json') as json_file:
                data = json.load(json_file)
                symbol_data = data[date][symbol]

                print(symbol, 'ORB STATUS CHECK >> TRADED >> '+str(symbol_data['TRADED']))

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
                print(data)
            with open('time_counts/orb_xian.json', 'w') as outfile:
                json.dump(data, outfile)

            return True

    ## NEW YORK
    if isNowInTimePeriod(dt.time(NY_ORB_START_HOUR, NY_ORB_START_MIN), dt.time(NY_ORB_END_HOUR, NY_ORB_END_MIN), dt.datetime.now().time()):
        SESSION = "NY"

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
                print(data)
            with open('time_counts/orb_xian.json', 'w') as outfile:
                json.dump(data, outfile)

            return True


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


def update_trade_log(symbol):
    #Update Json file
    date = get_date()
    with open('time_counts/orb_xian.json') as json_file:
        data = json.load(json_file)
        data[date][symbol]['TRADED'] = True

    with open('time_counts/orb_xian.json', 'w') as outfile:
        json.dump(data, outfile)

    print('TRADE LOG UPDATED')
initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']

while True:

    for symbol in SYMBOL_LIST:
        time.sleep(1)
        ready_trade = check_status(symbol)

        if ready_trade:
            data_df = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=20)

            orb_high, orb_low = get_orb_high_low(symbol)

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

                entry_price_2 = (orb_high + orb_low) / 2
                entry_price_3 = orb_low

                sl_1 = orb_low
                sl_2 = entry_price_2 - orb_diff
                sl_3 = entry_price_3 - orb_diff

                tp_1 = current_price + orb_diff*2
                tp_2 = entry_price_2 + orb_diff*1.5
                tp_3 = entry_price_3 + orb_diff*1.5
            elif data_df['close'].iloc[-2] < orb_low:
                print(symbol+' PRICE BROKE  >>> DOWN')
                # ORB Break SELL
                current_price = data_df['close'].iloc[-1]
                ORB_Action = 'sell'

                entry_price_2 = (orb_high + orb_low) / 2
                entry_price_3 = orb_high

                sl_1 = orb_high
                sl_2 = entry_price_2 + orb_diff
                sl_3 = entry_price_3 + orb_diff

                tp_1 = current_price - orb_diff*2
                tp_2 = entry_price_2 - orb_diff*1.5
                tp_3 = entry_price_3 - orb_diff*1.5
            else:
                print(symbol+' PRICE NOT BROKEN ORB')

            if ORB_Action:
                # Trade 1 ORB Top
                trade_with_price(action=ORB_Action, symbol=symbol,
                                 lot=1.0, tp_price=tp_1, sl_price=sl_1)

                # Trade 2 ORB Middle (Pullback)
                trade_limit_with_price(action=ORB_Action, symbol=symbol,
                                       lot=1.0, entry_price=entry_price_2,
                                       tp_price=tp_2, sl_price=sl_2)

                # Trade 3 ORB Bottom (Pullback)
                trade_limit_with_price(action=ORB_Action, symbol=symbol,
                                       lot=1.0, entry_price=entry_price_3,
                                       tp_price=tp_3, sl_price=sl_3)

                # Update trade log
                update_trade_log(symbol)
