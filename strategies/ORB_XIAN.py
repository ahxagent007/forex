import json
from datetime import datetime
import datetime as dt
import time

from mt5_utils import get_live_data, trade_with_price, trade_limit_with_price, initialize_mt5, \
    cancel_all_pending_orders, get_balance, close_all_positions, trade_order, trade_limit_with_point
from common_functions import isNowInTimePeriod

## TOKYO 6:00 - 9:00
## LONDON 13:00 - 16:00
## NEW YORK 19:00 - 22:00
## ORB 2:45 - 3:00

# ORB_START_HOUR = 19 #19
# ORB_START_MIN = 45 #45
# ORB_END_HOUR = 22 #22
# ORB_END_MIN = 00 #00

TOKYO_ORB_START_HOUR = 0 #6
TOKYO_ORB_START_MIN = 15 #15
TOKYO_ORB_END_HOUR = 3 #9
TOKYO_ORB_END_MIN = 00 #00

LONDON_ORB_START_HOUR = 7 #13
LONDON_ORB_START_MIN = 15 #15
LONDON_ORB_END_HOUR = 10 #16
LONDON_ORB_END_MIN = 00 #00

NY_ORB_START_HOUR = 13 #19
NY_ORB_START_MIN = 45 #45
NY_ORB_END_HOUR = 16 #22
NY_ORB_END_MIN = 00 #00

ALL_TRADE_CLOSE_HOUR = 16

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
            #close all running orders
            close_all_positions(symbol)
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
            orb_high, orb_low, candle_at = get_high_low(symbol=symbol, hour=TOKYO_ORB_START_HOUR, min=TOKYO_ORB_START_MIN)
            if orb_high is None:
               return
            symbol_data = {
                "ORB_HIGH": orb_high,
                "ORB_LOW": orb_low,
                "CREATED": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "TRADED": False, 
                "candle_at": candle_at.strftime("%d-%m-%Y %H:%M:%S")
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
            #close all running orders
            close_all_positions(symbol)
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

            orb_high, orb_low, candle_at = get_high_low(symbol=symbol, hour=LONDON_ORB_START_HOUR, min=LONDON_ORB_START_MIN)
            if orb_high is None:
               return
            symbol_data = {
                "ORB_HIGH": orb_high,
                "ORB_LOW": orb_low,
                "CREATED": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "TRADED": False, 
                "candle_at": candle_at.strftime("%d-%m-%Y %H:%M:%S")
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
            #close all running orders
            close_all_positions(symbol)

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

            orb_high, orb_low, candle_at = get_high_low(symbol=symbol, hour=NY_ORB_START_HOUR, min=NY_ORB_START_MIN)
            if orb_high is None:
               return
            symbol_data = {
                "ORB_HIGH": orb_high,
                "ORB_LOW": orb_low,
                "CREATED": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "TRADED": False, 
                "candle_at": candle_at.strftime("%d-%m-%Y %H:%M:%S")
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

    elif isNowInTimePeriod(dt.time(ALL_TRADE_CLOSE_HOUR, 0), dt.time(ALL_TRADE_CLOSE_HOUR, 10),
                           dt.datetime.now().time()):
        print('ALL RUNNING POSITIONS CLOSED!!')
        close_all_positions(symbol)
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

def get_year_month_day():
    # Current date and time
    now = datetime.now()

    # Extract year, month, and day
    year = now.year
    month = now.month
    day = now.day

    return year, month, day


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

    # timeframe = mt5.TIMEFRAME_M15
    # year, day, month = get_year_month_day()
    #
    #
    # date_time = datetime(year, day, month, hour, min)  # June 13, 2025, at 15:30
    #
    # # Get 1 candle at this datetime
    # rates = mt5.copy_rates_from(symbol, timeframe, date_time, 1)
    #
    # if rates is None or len(rates) == 0:
    #     print("❌ Candle not found or error:", mt5.last_error())
    #     return None, None
    # else:
    #     candle = rates[0]
    #     print("✅ Candle at", date_time)
    #     print(f"Time: {datetime.fromtimestamp(candle['time'])}")
    #     print(
    #         f"Open: {candle['open']}, High: {candle['high']}, Low: {candle['low']}, Close: {candle['close']}, Volume: {candle['tick_volume']}")
    #
    #     return candle['high'], candle['low']

def get_high_low(symbol, hour, min):
    global mt5

    timeframe = mt5.TIMEFRAME_M15
    year, day, month = get_year_month_day()

    min = min - 15
    if min < 0:
        min = min + 60
        hour = hour - 1

    date_time = datetime(year, day, month, hour, min)  # June 13, 2025, at 15:30

    # Get 1 candle at this datetime
    rates = mt5.copy_rates_from(symbol, timeframe, date_time, 1)

    if rates is None or len(rates) == 0:
        print("❌ Candle not found or error:", mt5.last_error())
        return None, None, None
    else:
        candle = rates[0]
        print("✅ Candle at", date_time)
        print(f"Time: {datetime.fromtimestamp(candle['time'])}")
        if date_time == datetime.fromtimestamp(candle['time']):
            
            print(
                f"Open: {candle['open']}, High: {candle['high']}, Low: {candle['low']}, Close: {candle['close']}, Volume: {candle['tick_volume']}, Spread: {candle['spread']}")

            return candle['high'], candle['low'], datetime.fromtimestamp(candle['time'])
        else:
            print('Candle data not generated correctly')
            return None, None, None

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
        'EURUSD': 10
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
        }
    }
    return fixed_sl_tp[symbol]['sl'] * RR, fixed_sl_tp[symbol]['sl']

# ----------- Detect Supports and Resistances -----------
def find_swing_levels(df, window=10):
    supports = []
    resistances = []
    for i in range(window, len(df) - window):
        low = df['low'].iloc[i]
        high = df['high'].iloc[i]
        # Support
        if all(low < df['low'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            supports.append(low)
        # Resistance
        if all(high > df['high'].iloc[j] for j in range(i - window, i + window + 1) if j != i):
            resistances.append(high)
    return supports, resistances


# ----------- Group into Zones -----------
def group_zones(levels, threshold=2.0):
    zones = []
    levels.sort()
    zone = [levels[0]]
    for level in levels[1:]:
        if abs(level - zone[-1]) <= threshold:
            zone.append(level)
        else:
            zones.append((min(zone), max(zone)))
            zone = [level]
    if zone:
        zones.append((min(zone), max(zone)))
    return zones

def support_resistance_ema(df):

    supports_raw, resistances_raw = find_swing_levels(df)
    support_zones = group_zones(supports_raw, threshold=2.0)
    resistance_zones = group_zones(resistances_raw, threshold=2.0)

    df['EMA'] = df['close'].ewm(span=200).mean()

    closest_support_percent = 99999
    closest_resistance_percent = 99999

    for low, high in support_zones[-3:]:  # Limit to last 5 zones for clarity
        percent_change = ((low - df.iloc[-1].close) / df.iloc[-1].close) * 100

        if abs(percent_change) < abs(closest_support_percent):
            closest_support_percent = percent_change

        print(f'Price is {round(percent_change * 100, 2)} % far from Support')

    for low, high in resistance_zones[-3:]:
        percent_change = ((high - df.iloc[-1].close) / df.iloc[-1].close) * 100

        if abs(percent_change) < abs(closest_resistance_percent):
            closest_resistance_percent = percent_change
        print(f'Price is {round(percent_change * 100, 2)} % far from Resistance')


    ema_diff_percent = round(((df.iloc[-1].EMA - df.iloc[-1].close) / df.iloc[-1].close) * 100 * 100, 2)

    return closest_support_percent, closest_resistance_percent, ema_diff_percent



mt5 = initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']

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


                sl_1 = entry_price_1 - orb_diff
                #sl_1 = current_price - orb_diff
                sl_2 = entry_price_2 - orb_diff
                sl_3 = entry_price_3 - orb_diff

                tp_1 = entry_price_1 + orb_diff*1.5
                #tp_1 = current_price + orb_diff*1.5
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

                sl_1 = current_price + orb_diff
                #sl_1 = entry_price_1 + orb_diff
                sl_2 = entry_price_2 + orb_diff
                sl_3 = entry_price_3 + orb_diff

                tp_1 = current_price - orb_diff*1.5
                #tp_1 = entry_price_1 - orb_diff*1.5
                tp_2 = entry_price_2 - orb_diff*1.5
                tp_3 = entry_price_3 - orb_diff*2.5



            if ORB_Action:

                # lot_1 = calculate_lot_size(symbol=symbol, sl_diff=abs(current_price-sl_1))
                # #lot_1 = calculate_lot_size(symbol=symbol, sl_diff=abs(entry_price_1-sl_1))
                # lot_2 = calculate_lot_size(symbol=symbol, sl_diff=abs(entry_price_2-sl_2))
                # lot_3 = calculate_lot_size(symbol=symbol, sl_diff=abs(entry_price_3-sl_3))



                # # Trade 1 ORB Top
                # trade_with_price(action=ORB_Action, symbol=symbol,
                #                  lot=lot_1, tp_price=tp_1, sl_price=sl_1)
                #
                # # # Trade 1 ORB Middle (Pullback)
                # # trade_limit_with_price(action=ORB_Action, symbol=symbol,
                # #                        lot=lot_1, entry_price=entry_price_1,
                # #                        tp_price=tp_1, sl_price=sl_1)
                #
                # # Trade 2 ORB Middle (Pullback)
                # # trade_limit_with_price(action=ORB_Action, symbol=symbol,
                # #                        lot=lot_2, entry_price=entry_price_2,
                # #                        tp_price=tp_2, sl_price=sl_2)
                #
                # # Trade 3 ORB Bottom (Pullback)
                # trade_limit_with_price(action=ORB_Action, symbol=symbol,
                #                        lot=lot_3, entry_price=entry_price_3,
                #                        tp_price=tp_3, sl_price=sl_3)


                ## FIXED TP SL
                # tp_point, sl_point = get_fixed_sl_tp_point(symbol)
                #
                # lot = calculate_lot_size_point(symbol, sl_point)
                # trade_order(symbol, tp_point, sl_point, lot, ORB_Action, magic=False)

                # Update trade log
                # entries = {
                #     'action': ORB_Action,
                #     'entry_1': {
                #         'price': current_price,
                #         'sl':sl_1,
                #         'tp': tp_1,
                #         'lot': lot_1
                #     },
                #     'entry_2': {
                #         'price': entry_price_2,
                #         'sl': sl_2,
                #         'tp': tp_2,
                #         'lot': lot_2
                #     },
                #     'entry_3': {
                #         'price': entry_price_3,
                #         'sl': sl_3,
                #         'tp': tp_3,
                #         'lot': lot_3
                #     },
                #     'fixed_entry': {
                #         'price': current_price,
                #         'sl':sl_point,
                #         'tp': tp_point,
                #         'lot': lot
                #     }
                # }
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

                    # FIXED TP SL
                    tp_point, sl_point = get_fixed_sl_tp_point(symbol=symbol, RR=2)

                    lot = calculate_lot_size_point(symbol, sl_point)

                    if trade_type == 'now':
                        entry_price = current_price
                        #Trade now
                        trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=ORB_Action, magic=False)
                    elif trade_type == 'top':
                        entry_price = entry_price_1
                        # Range Top
                        trade_limit_with_point(action=ORB_Action, symbol=symbol, lot=lot, entry_price=entry_price_1, tp_point=tp_point, sl_point=sl_point)
                    elif trade_type == 'middle':
                        entry_price = entry_price_2
                        # Range Middle
                        trade_limit_with_point(action=ORB_Action, symbol=symbol, lot=lot, entry_price=entry_price_2, tp_point=tp_point, sl_point=sl_point)
                    elif trade_type == 'bottom':
                        entry_price = entry_price_3
                        # Range bottom
                        trade_limit_with_point(action=ORB_Action, symbol=symbol, lot=lot, entry_price=entry_price_3, tp_point=tp_point, sl_point=sl_point)

                    entries = {
                        'action': ORB_Action,
                        'trade_type': trade_type,
                        'entry': {
                            'price': entry_price,
                            'sl': sl_point,
                            'tp': tp_point
                        },
                        'data':{
                            'support': closest_support_percent,
                            'resistance': closest_resistance_percent,
                            'ema': ema_diff_percent
                        }
                    }
                    update_trade_log(symbol, entries)
