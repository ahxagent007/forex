import pandas as pd


# Function to calculate FVG size
from akash import get_avg_candle_size
from common_functions import check_duplicate_orders_time, check_duplicate_orders_magic, write_json, add_csv
from mt5_utils import get_magic_number, trade_order_magic, get_live_data



def is_valid_fvg(high1, low1, high2, low2, threshold):
    fvg_size = abs(high1 - low2)  # Size of the gap
    avg_candle_size = (high1 - low1 + high2 - low2) / 2  # Average candle size
    return fvg_size >= threshold * avg_candle_size  # Check if the gap meets the threshold

# Function to identify FVGs
def identify_fvg(data, threshold):
    for i in range(2, len(data)):
        # Previous two candles
        prev_candle_1 = data.iloc[i - 2]
        prev_candle_2 = data.iloc[i - 1]
        curr_candle = data.iloc[i]

        # FVG conditions with threshold
        if prev_candle_2['low'] > prev_candle_1['high'] and curr_candle['low'] > prev_candle_2['high']:
            # Bullish FVG
            if is_valid_fvg(prev_candle_1['high'], prev_candle_1['low'], prev_candle_2['high'], prev_candle_2['low'], threshold):
                data.loc[i, 'FVG_Upper'] = prev_candle_1['high']
                data.loc[i, 'FVG_Lower'] = prev_candle_2['low']
        elif prev_candle_2['high'] < prev_candle_1['low'] and curr_candle['high'] < prev_candle_2['low']:
            # Bearish FVG
            if is_valid_fvg(prev_candle_1['low'], prev_candle_1['high'], prev_candle_2['low'], prev_candle_2['high'], threshold):
                data.loc[i, 'FVG_Upper'] = prev_candle_2['high']
                data.loc[i, 'FVG_Lower'] = prev_candle_1['low']
    return data



# Function to generate signals based on FVG
def generate_signals(data):
    for i in range(len(data)):
        # If price re-enters the FVG zone
        if pd.notna(data.loc[i, 'FVG_Upper']) and pd.notna(data.loc[i, 'FVG_Lower']):
            current_price = data.loc[i, 'close']

            # Buy Signal: Price enters a bullish FVG
            if data.loc[i, 'FVG_Upper'] >= current_price >= data.loc[i, 'FVG_Lower']:
                data.loc[i, 'Signal'] = 'buy'

            # Sell Signal: Price enters a bearish FVG
            elif data.loc[i, 'FVG_Upper'] <= current_price <= data.loc[i, 'FVG_Lower']:
                data.loc[i, 'Signal'] = 'sell'
            else:
                data.loc[i, 'Signal'] = None

    return data


def FVG_signal(data):

    # Ensure data has the correct format
    if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
        raise ValueError("Data must contain 'Open', 'High', 'Low', 'Close' columns.")

    # Create empty columns for signals and FVG zones
    data['FVG_Upper'] = None
    data['FVG_Lower'] = None
    data['Signal'] = None

    # Threshold for FVG size as a percentage of the candle range (e.g., 0.5 = 50%)
    FVG_THRESHOLD = 0.5

    # Apply FVG identification
    data = identify_fvg(data, FVG_THRESHOLD)

    # Generate signals
    data = generate_signals(data)

    return data['Signal'].iloc[-1]

def FVG_trade(symbol):
    time_frame = 'M1'       # VARIALBE
    skip_min = 2            # VARIALBE
    json_file_name = 'FVG_trade'
    code = 79

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                                         json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=code)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=500)

    action = FVG_signal(df)

    if action:
        print(symbol, 'FVG_trade')
        avg_candle_size, sl, tp = get_avg_candle_size(symbol, df, 10, 1)

        lot = 0.01

        MAGIC_NUMBER = get_magic_number()
        trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True, code=code,
                          MAGIC_NUMBER=MAGIC_NUMBER)
        write_json(json_dict=orders_json, json_file_name=json_file_name)

        data = ' '
        data_lst = [symbol, time_frame, MAGIC_NUMBER, avg_candle_size, action, tp, sl, 'FVG_trade', data]
        add_csv(data_lst)
