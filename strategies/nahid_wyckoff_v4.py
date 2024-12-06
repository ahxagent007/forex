import math
from datetime import datetime, timedelta

from common_functions import write_json
from xian import get_max_profit, get_max_loss
from xian import check_duplicate_orders
from mt5_utils import get_live_data, get_all_positions, trade_order_wo_tp_sl, clsoe_position


import pandas as pd
import numpy as np


def detect_phase_a(data, rolling_window=20, volume_multiplier=2, debug=False):
    # Calculate rolling statistics for price and volume
    data['rolling_low'] = data['low'].rolling(window=rolling_window).min()
    data['rolling_high'] = data['high'].rolling(window=rolling_window).max()
    data['rolling_mean_volume'] = data['tick_volume'].rolling(window=rolling_window).mean()

    # Detect Preliminary Support (PS): Increased volume near rolling low
    data['ps'] = (data['low'] <= data['rolling_low'] * 1.05) & \
                 (data['tick_volume'] > volume_multiplier * data['rolling_mean_volume'])

    # Detect Selling Climax (SC): Lowest point with very high volume
    data['sc'] = (data['low'] == data['rolling_low']) & \
                 (data['tick_volume'] > volume_multiplier * data['rolling_mean_volume'])

    # Detect Automatic Rally (AR): Significant rebound from SC
    data['ar'] = (data['close'] > data['rolling_low'] + (data['rolling_high'] - data['rolling_low']) * 0.5) & \
                 (data['sc'].shift(1))

    # Detect Secondary Test (ST): Retest of SC area
    data['st'] = (data['low'] <= data['rolling_low'] * 1.05) & \
                 (data['sc'].shift(1) | data['ar'].shift(1))

    if debug:
        print(data[['low', 'tick_volume', 'rolling_low', 'ps', 'sc', 'ar', 'st']].tail(20))

    return data


def generate_wyckoff_data(start_date, end_date, interval='D', seed=42):
    """
    Generate synthetic market data (OHLCV) based on Wyckoff-like phases.
    """
    np.random.seed(seed)

    # Generate a time range
    time_range = pd.date_range(start=start_date, end=end_date, freq=interval)
    n = len(time_range)

    # Simulate price movements (Accumulate, Markup, Distribution, and Markdown Phases)
    price = 100  # Starting price

    # Create lists to hold data
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []
    volumes = []

    # Define phases
    phases = ['accumulation', 'markup', 'distribution', 'markdown']

    # Duration of each phase in terms of data points
    phase_duration = n // len(phases)

    for phase in phases:
        for i in range(phase_duration):
            # Create phase-specific behavior
            if phase == 'accumulation':
                # Simulate a range-bound (sideways) movement
                price += np.random.uniform(-0.5, 0.5)  # Small random fluctuations
            elif phase == 'markup':
                # Simulate an uptrend with increasing prices
                price += np.random.uniform(0.5, 1.5)  # Positive trend
            elif phase == 'distribution':
                # Simulate a range-bound (sideways) movement (distribution phase)
                price += np.random.uniform(-0.5, 0.5)  # Small fluctuations
            elif phase == 'markdown':
                # Simulate a downtrend with decreasing prices
                price -= np.random.uniform(0.5, 1.5)  # Negative trend

            # Ensure price stays within reasonable bounds
            price = max(50, min(price, 200))  # Clamped price between 50 and 200

            # Simulate OHLCV values
            open_price = price + np.random.uniform(-0.5, 0.5)
            high_price = open_price + np.random.uniform(0, 2)
            low_price = open_price - np.random.uniform(0, 2)
            close_price = open_price + np.random.uniform(-0.5, 0.5)
            volume = np.random.randint(50000, 1000000)

            # Append values to the lists
            open_prices.append(open_price)
            high_prices.append(high_price)
            low_prices.append(low_price)
            close_prices.append(close_price)
            volumes.append(volume)

    # If there are any remaining time steps, fill them with the last phase (to cover the whole time range)
    remaining_steps = n - len(open_prices)
    for i in range(remaining_steps):
        open_prices.append(close_prices[-1])  # Keep the last close price as the new open
        high_prices.append(high_prices[-1])  # Use the last high as the new high
        low_prices.append(low_prices[-1])  # Use the last low as the new low
        close_prices.append(close_prices[-1])  # Keep the last close as the new close
        volumes.append(np.random.randint(50000, 1000000))  # New random volume

    # Create a DataFrame from the simulated data
    data = pd.DataFrame({
        'time': time_range,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })

    return data


def Ma(prices):
    a = prices['close'].rolling(window=100).mean()
    return a


def Ema(prices):
    a = prices['close'].ewm(span=20, adjust=False).mean()
    return a


def line_from_points(P, Q):
    # Calculate the coefficients A, B, C for the line equation Ax + By = C
    A = Q[1] - P[1]  # y2 - y1
    B = P[0] - Q[0]  # x1 - x2
    C = A * P[0] + B * P[1]  # A*x1 + B*y1
    return A, B, C


def find_intersection(P1, Q1, P2, Q2, lim):
    # Get the line equations Ax + By = C for both lines


    delta_x = P2 - P1
    delta_y = Q2 - Q1


        # Compute the slope
    slope = delta_y / delta_x

    # Calculate the angle in radians using arctangent
    angle_rad = math.atan(slope)

    # Adjust based on quadrant
    angle=angle_rad*(180/math.pi)*100

    if angle>30:
        #print(angle)
        return True
    else:
        return False

def find_intersection2(P1, Q1, P2, Q2, lim):
    # Get the line equations Ax + By = C for both lines


    delta_x = P2 - P1
    delta_y = Q2 - Q1


        # Compute the slope
    slope = delta_y / delta_x

    # Calculate the angle in radians using arctangent
    angle_rad = math.atan(slope)

    # Adjust based on quadrant
    angle=angle_rad*(180/math.pi)*100

    if angle<-30:
        #print(angle)
        return True
    else:
        return False


def all_deg(ema):
    deg=[]
    for i in range(len(ema)):
        #P1 = (0, b.iloc[-7])
        #Q1 = (7, b.iloc[-1])
        if(i>=20):
            a=find_intersection(0 ,ema[i-20], 0.1, ema[i], 1)
            deg.append(a)
        else:
            deg.append(False)
    return deg

def all_deg2(ema):
    deg=[]
    for i in range(len(ema)):
        #P1 = (0, b.iloc[-7])
        #Q1 = (7, b.iloc[-1])
        if(i>=20):
            a=find_intersection2(0 ,ema[i-20], 0.1, ema[i], 1)
            deg.append(a)
        else:
            deg.append(False)
    return deg

def crossover(a, b, accum):
    c = (a > b).astype(int) - (a < b).astype(int)
    d = c.shift(1)
    lst = []
    dec = []
    print('hurra')

    for i in range(len(a)):
        if c.iloc[i] != d.iloc[i] and accum.iloc[i] == False:

            if c.iloc[i] == 1:

                # return 'bull'
                lst.append(True)
                dec.append('buy')
            elif c.iloc[i] == -1:
                # return 'bear'
                dec.append('sell')
                lst.append(True)
        else:
            lst.append(False)
            dec.append('none')

    return lst, dec


def crossover_exit(a, b):
    c = (a > b).astype(int) - (a < b).astype(int)
    d = c.shift(1)

    dec = []

    for i in range(len(a)):
        if c.iloc[i] != d.iloc[i]:

            dec.append(True)
        else:

            dec.append(False)

    return dec


def detect_accumulation_and_markup(
        data,
        base_accumulation=0.0005,
        acc_multiplier=1,
        base_markup=0.0008,
        markup_multiplier=2.0,
        base_distribution=0.0001,
        dist_multiplier=2,
        base_markdown=0.0008,
        markdown_multiplier=2,
        debug=False
):

    # Calculate rolling mean and standard deviation
    data['mean_price'] = data['close'].rolling(100, min_periods=1).mean()
    data['std_dev'] = data['close'].rolling(100, min_periods=1).std()

    # Calculate ATR for volatility-based thresholds
    data['high_low'] = data['high'] - data['low']
    data['high_close'] = abs(data['high'] - data['close'].shift(1))
    data['low_close'] = abs(data['low'] - data['close'].shift(1))
    data['true_range'] = data[['high_low', 'high_close', 'low_close']].max(axis=1)
    data['atr'] = data['true_range'].rolling(window=21, min_periods=1).mean()

    # Dynamic accumulation threshold
    data['dynamic_accumulation_threshold'] = (
            base_accumulation + acc_multiplier * (data['atr'] / data['close'].mean())
    )
    data['price_dev'] = abs(data['close'] - data['mean_price']) / data['mean_price']
    data['accumulation'] = data['price_dev'] <= data['dynamic_accumulation_threshold']

    # Dynamic markup threshold based on returns volatility
    data['returns'] = data['close'].pct_change()
    data['returns_std'] = data['returns'].rolling(window=100, min_periods=1).std()
    data['dynamic_markup_threshold'] = base_markup + markup_multiplier * data['returns_std']
    data['markup'] = data['returns'] >= data['dynamic_markup_threshold']

    data['dynamic_distribution_threshold'] = (
            base_distribution + dist_multiplier * (data['atr'] / data['close'].mean())
    )
    data['price_dev'] = abs(data['close'] - data['mean_price']) / data['mean_price']
    data['distribution'] = data['price_dev'] <= data['dynamic_distribution_threshold']

    # Dynamic markdown threshold based on returns volatility
    data['returns'] = data['close'].pct_change()
    data['returns_std'] = data['returns'].rolling(window=100, min_periods=1).std()
    data['dynamic_markdown_threshold'] = base_markdown + markdown_multiplier * data['returns_std']
    data['markdown'] = data['returns'] <= -data['dynamic_markdown_threshold']

    data['buy_signal'] = data['accumulation'] & data['markup']
    data['sell_signal'] = data['distribution'] | data['markdown']

    if debug:
        print(data[[
            'close', 'mean_price', 'std_dev', 'atr',
            'dynamic_accumulation_threshold', 'price_dev',
            'dynamic_markup_threshold', 'returns', 'accumulation', 'markup'
        ]])

    return data


def bot_wyckoff_v4(symbol, lot):
    skip_min = 11
    time_frame = 'M5'

    # Actions: 0 = Hold, 1 = Buy, 2 = Sell
    positions = get_all_positions(symbol)
    ticks_frame1 = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    phase_a_data = detect_accumulation_and_markup(ticks_frame1)
    b = Ma(ticks_frame1)
    a = Ema(ticks_frame1)
    # Visualize Phase A events
    deg=all_deg(a)
    deg2=all_deg2(a)
    # print(P1, " ", Q1)
    if len(positions) == 0:
        json_file_name = 'Nahid_wyckoff_scalping'
        running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                                   json_file_name=json_file_name)
        if running_trade_status:
            # print(symbol, 'MULTIPLE TRADE SKIPPED by TIME >>>>')
            return None

        i = -1
        if (deg[i]==True):
            print('buy')
            trade_order_wo_tp_sl(symbol, lot, 'buy', magic=False)
            write_json(json_dict=orders_json, json_file_name=json_file_name)

        elif (deg2[i]==True):
            print('sell')
            trade_order_wo_tp_sl(symbol, lot, 'sell', magic=False)
            write_json(json_dict=orders_json, json_file_name=json_file_name)


        # Visualize Accumulation and Markup
        # for i in range(len(wyckoff_data)):
    elif len(positions) > 0:
        for position in positions:
            #print(position.comment, 'buy' and deg[-1] == False)
            if (position.comment == 'buy' and deg[-1] == False):
                clsoe_position(symbol, position.ticket)
                print('buy_exit')
            elif (position.comment == 'sell' and deg2[-1] == False):
                clsoe_position(symbol, position.ticket)
                print('sell_exit')
            else:
                if position.profit > get_max_profit(symbol, lot) or position.profit < get_max_loss(symbol, lot):
                    clsoe_position(symbol, position.ticket)
                    print('Profit or Loss Taken: ', position.profit)


