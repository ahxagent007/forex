import pandas as pd
import numpy as np

from mt5_utils import get_live_data, get_all_positions, trade_order_wo_tp_sl, close_position, trade_order_wo_tp, \
    print_time, trade_order_wo_tp_price, initialize_mt5


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
    a = prices['close'].ewm(span=1, adjust=False).mean()
    return a


def line_from_points(P, Q):
    # Calculate the coefficients A, B, C for the line equation Ax + By = C
    A = Q[1] - P[1]  # y2 - y1
    B = P[0] - Q[0]  # x1 - x2
    C = A * P[0] + B * P[1]  # A*x1 + B*y1
    return A, B, C


def find_intersection(P1, Q1, P2, Q2, lim):
    # Get the line equations Ax + By = C for both lines
    A1, B1, C1 = line_from_points(P1, Q1)
    A2, B2, C2 = line_from_points(P2, Q2)

    # Calculate the determinant
    determinant = A1 * B2 - A2 * B1
    # print(determinant)
    if determinant == 0:
        return "not cross"
    else:
        # Using Cramer's rule to find the intersection point (x, y)
        x = (C1 * B2 - C2 * B1) / determinant
        y = (A1 * C2 - A2 * C1) / determinant
        if (x <= lim):
            return "not cross"
        else:
            return x, y


def crossover(a, b, accum):
    c = (a > b).astype(int) - (a < b).astype(int)
    d = c.shift(1)
    lst = []
    dec = []

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
    """
    Detect accumulation and markup phases using dynamic thresholds.

    Args:
        data (pd.DataFrame): A DataFrame containing 'close', 'high', 'low', and 'volume'.
        base_accumulation (float): Base threshold for accumulation detection.
        acc_multiplier (float): Multiplier for dynamic accumulation threshold adjustment.
        base_markup (float): Base threshold for markup detection.
        markup_multiplier (float): Multiplier for dynamic markup threshold adjustment.
        debug (bool): If True, print debug information.

    Returns:
        pd.DataFrame: Original data with additional 'accumulation' and 'markup' columns.
    """

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



def convert_minutes_to_days(total_minutes):
    # Constants for conversion
    minutes_per_hour = 60
    hours_per_day = 24
    minutes_per_day = minutes_per_hour * hours_per_day

    # Calculate days, hours, and minutes
    days = total_minutes // minutes_per_day
    remaining_minutes = total_minutes % minutes_per_day
    hours = remaining_minutes // minutes_per_hour
    minutes = remaining_minutes % minutes_per_hour

    return days, hours, minutes

def backtest_wyckoff_bot_v2(symbol):

    time_frame = 'M5'
    prev_n_candle= 50000
    data_df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=prev_n_candle)

    window = 100
    future_window = 20

    profit = 0
    loss = 0
    buy_trade = 0
    sell_tade = 0

    buy_lose = 0
    sell_lose = 0

    buy_win = 0
    sell_win = 0

    if symbol == 'XAUUSD':
        symbol_multi = 1000
    elif symbol == 'EURUSD':
        symbol_multi = 100000
    elif symbol == 'USDJPY':
        symbol_multi = 10000
    elif symbol == 'GBPUSD':
        symbol_multi = 100000
    elif symbol == 'EURJPY':
        symbol_multi = 10000

    n = 0
    while n < (data_df.shape[0]-window):
        ticks_frame1 = data_df.iloc[n : n+window]

        phase_a_data = detect_accumulation_and_markup(ticks_frame1)
        b = Ma(ticks_frame1)
        a = Ema(ticks_frame1)
        # Visualize Phase A events
        lst, d = crossover(a, b, phase_a_data['accumulation'])

        i = -1
        price_future = data_df.iloc[n+window:n+window+future_window]
        max_high = price_future['high'].max()
        max_low = price_future['low'].max()

        current_price = ticks_frame1.iloc[-1]['close']

        high_diff = (max_high - current_price) * symbol_multi
        low_diff = (current_price - max_low) * symbol_multi

        sl_diff = abs((current_price - max(ticks_frame1.iloc[-2]['close'], ticks_frame1.iloc[-3]['close'], ticks_frame1.iloc[-4]['close'])) * symbol_multi)

        if (lst[-1] == True and d[-1] == 'buy'):
            n += future_window
            #print(symbol, 'buy')
            buy_trade += 1
            #sl = get_prev_sl(ticks_frame1, 'buy')

            if low_diff > sl_diff:
                buy_lose += 1
                loss += sl_diff
            else:
                buy_win += 1
                profit += high_diff

        elif (lst[-1] == True and d[-1] == 'sell'):
            n += future_window
            #print(symbol, 'sell')
            sell_tade += 1
            #sl = get_prev_sl(ticks_frame1, 'sell')

            if high_diff > sl_diff:
                sell_lose += 1
                loss += sl_diff
            else:
                sell_win += 1
                profit += low_diff
        else:
            n += 1

    days, hours, mins = convert_minutes_to_days(data_df.shape[0]*5)
    print('--------------------------------------------------------------------------')
    print('Backtest on symbol -> ', symbol)
    print('Total Trade ##', buy_trade+sell_tade)
    print('Buy ## Win', buy_win, ' : Lose', buy_lose)
    print('Sell ## Win', sell_win, ' : Lose', sell_lose)
    print('Profit: ', profit, 'pips')
    print('Loss: ', loss, 'pips')
    print('Net Profit over {0} days {1} hours {2} min is {3} pips'.format(days,hours, mins, profit-loss))
    print('--------------------------------------------------------------------------')



import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

initialize_mt5()

symbol_list = ['EURUSD', 'USDJPY', 'GBPUSD', 'EURJPY']

for symbol in symbol_list:
    backtest_wyckoff_bot_v2(symbol)