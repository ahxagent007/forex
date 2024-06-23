from mt5_utils import get_live_data, trade_order
from common_functions import check_duplicate_orders, write_json


## DOUBEL DOJI BREAK
# Function to identify Doji candles
def is_doji(row, threshold=0.1):
    body_size = abs(row['open'] - row['close'])
    total_range = row['high'] - row['low']
    return body_size <= threshold * total_range

# Function to identify Double Doji patterns and generate signals
def double_doji_break_signal(df, threshold=0.1):
    df['doji'] = df.apply(lambda row: is_doji(row, threshold), axis=1)
    df['double_doji'] = (df['doji'] & df['doji'].shift(1))

    df['signal'] = 0
    i = -1
    if df['double_doji'].iloc[i]:
        if df['high'].iloc[i] > df['high'].iloc[i - 1]:
            return 'buy'
        elif df['low'].iloc[i] < df['low'].iloc[i - 1]:
            return 'sell'
        else:
            return None

    return None

## FIRST BREAK

def first_break_signal(df):
    window = 20
    threshold = 0.01

    df['range'] = df['high'] - df['low']
    df['rolling_range'] = df['range'].rolling(window=window).mean()
    df['consolidation'] = df['rolling_range'] < threshold

    df['signal'] = 0
    consolidation = False

    i = -1

    if df['consolidation'].iloc[i] and not consolidation:
        consolidation = True
    elif not df['consolidation'].iloc[i] and consolidation:
        if df['close'].iloc[i] > df['high'].iloc[i - 1]:
            return 'buy'
            consolidation = False
        elif df['close'].iloc[i] < df['low'].iloc[i - 1]:
            return 'sell'
            consolidation = False

    return None


### SECOND BREAK
def second_break_signal(df, breakout_window=40, pullback_window=5, threshold=0.01):
    df['high_breakout'] = df['high'].rolling(window=breakout_window).max()
    df['low_breakout'] = df['low'].rolling(window=breakout_window).min()

    df['signal'] = 0

    i = -1

    if df['close'].iloc[i] > df['high_breakout'].iloc[i - 1]:
        # Look for a pullback
        pullback_high = df['high'].iloc[i - pullback_window:i].max()
        if df['close'].iloc[i] < pullback_high - threshold:
            # Look for the second breakout
            for j in range(i + 1, len(df)):
                if df['close'].iloc[j] > pullback_high:
                    return 'buy'
                    break

    elif df['close'].iloc[i] < df['low_breakout'].iloc[i - 1]:
        # Look for a pullback
        pullback_low = df['low'].iloc[i - pullback_window:i].min()
        if df['close'].iloc[i] > pullback_low + threshold:
            # Look for the second breakout
            for j in range(i + 1, len(df)):
                if df['close'].iloc[j] < pullback_low:
                    return 'sell'
                    break

    return None

# Function to identify the Block Break signal
def block_break_signal(df, consolidation_window=40, breakout_window=60):
    df['signal'] = 0

    j = -1
    consolidation_high = max(df['high'].iloc[consolidation_window:len(df)])
    consolidation_low = min(df['low'].iloc[consolidation_window:len(df)])

    if df['close'].iloc[j] > consolidation_high:
        return 'buy'
    elif df['close'].iloc[j] < consolidation_low:
        return 'sell'
    else:
        return None

## RANGE BREAK

def range_break_signal(df, range_window=40, breakout_window=5):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()

    df['signal'] = 0

    i = range_window + breakout_window

    range_high = df['high_range'].iloc[-i]
    range_low = df['low_range'].iloc[-i]

    # Look for breakout after range
    j = -1

    if df['close'].iloc[j] > range_high:
        return 'buy'
    elif df['close'].iloc[j] < range_low:
        return 'sell'
    return None

### INSIDE RANGE BREAK

def inside_range_break_signal(df):
    df['inside_bar'] = (df['high'] < df['high'].shift(1)) & (df['low'] > df['low'].shift(1))

    df['signal'] = 0
    i = -1
    if df['inside_bar'].iloc[i]:
        high_range = df['high'].iloc[i-1]
        low_range = df['low'].iloc[i-1]
        # Check for breakout
        if df['close'].iloc[i] > high_range:
            return 'buy'
        elif df['close'].iloc[i] < low_range:
            return 'sell'
    return None


## ADVANCE RANGE BREAK
def advance_range_break_signal(df, range_window=20, breakout_window=5, confirmation_window=3):
    df['high_range'] = df['high'].rolling(window=range_window).max()
    df['low_range'] = df['low'].rolling(window=range_window).min()

    df['signal'] = 0

    i = range_window + breakout_window
    range_high = df['high_range'].iloc[i]
    range_low = df['low_range'].iloc[i]

    # Look for breakout after range
    j = -1
    if df['close'].iloc[j] > range_high:
        # Confirmation criteria: Check if price stays above the range high for a few candles
        if df['close'].iloc[j + 1:j + 1 + confirmation_window] > range_high:
            return 'buy'
    elif df['close'].iloc[j] < range_low:
        # Confirmation criteria: Check if price stays below the range low for a few candles
        if df['close'].iloc[j + 1:j + 1 + confirmation_window] < range_low:
            return 'sell'
    return None

def bob_volman_signal(tick_frames):

    try:
        ddb = double_doji_break_signal(tick_frames)
        if ddb:
            print('Double Doji', ddb)
            return ddb

        fb = first_break_signal(tick_frames)
        if fb:
            print('First Break', fb)
            return fb

        sb = second_break_signal(tick_frames)
        if sb:
            print('Second Break', sb)
            return sb

        bb = block_break_signal(tick_frames)
        if bb:
            print('Block Break', bb)
            return bb

        rb = range_break_signal(tick_frames)
        if rb:
            print('Range Break', rb)
            return rb

        irb = inside_range_break_signal(tick_frames)
        if irb:
            print('Inside Range Break', irb)
            return irb

        arb = advance_range_break_signal(tick_frames)
        if arb:
            print('Advance Range Break', arb)
            return arb
    except:
        return None

    return None




def volman_strategies(symbol):
    json_file_name = 'volman'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=1,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        print('VOLMAN MULTIPLE TRADE >>>', symbol)
        return None

    accepted_symbol_list = ['EURUSD']
    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    tick_df = get_live_data(symbol=symbol, time_frame='M1', prev_n_candles=70)

    signal = bob_volman_signal(tick_df)

    tp_point = 80
    sl_point = 40
    lot = 0.05

    if signal:
        trade_order(symbol, tp_point, sl_point, lot, signal)
        write_json(json_dict=orders_json, json_file_name=json_file_name)



