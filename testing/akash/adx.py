import pandas as pd
import numpy as np
from mt5_utils import get_data


# def calculate_adx(data, period=14):
#     data['TR'] = np.maximum((data['high'] - data['low']),
#                             np.maximum(abs(data['high'] - data['close'].shift(1)),
#                                        abs(data['low'] - data['close'].shift(1))))
#
#     data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
#                            np.maximum((data['high'] - data['high'].shift(1)), 0), 0)
#     data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
#                            np.maximum((data['low'].shift(1) - data['low']), 0), 0)
#
#     data['TR_smooth'] = data['TR'].rolling(window=period).sum()
#     data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
#     data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()
#
#     data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
#     data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])
#
#     data['DX'] = 100 * abs((data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI']))
#
#     data['ADX'] = data['DX'].rolling(window=period).mean()
#
#     return data


# def get_adx(high, low, close, lookback):
#     plus_dm = high.diff()
#     minus_dm = low.diff()
#     plus_dm[plus_dm < 0] = 0
#     minus_dm[minus_dm > 0] = 0
#
#     tr1 = pd.DataFrame(high - low)
#     tr2 = pd.DataFrame(abs(high - close.shift(1)))
#     tr3 = pd.DataFrame(abs(low - close.shift(1)))
#     frames = [tr1, tr2, tr3]
#     tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
#     atr = tr.rolling(lookback).mean()
#
#     plus_di = 100 * (plus_dm.ewm(alpha=1 / lookback).mean() / atr)
#     minus_di = abs(100 * (minus_dm.ewm(alpha=1 / lookback).mean() / atr))
#     dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
#     adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
#     adx_smooth = adx.ewm(alpha=1 / lookback).mean()
#     return plus_di, minus_di, adx_smooth
#
#
#
# data = get_data('GBPUSD')
#
# data['plus_di'] = pd.DataFrame(get_adx(data['high'], data['low'], data['close'], 14)[0]).rename(columns={0: 'plus_di'})
# data['minus_di'] = pd.DataFrame(get_adx(data['high'], data['low'], data['close'], 14)[1]).rename(
#     columns={0: 'minus_di'})
# data['adx'] = pd.DataFrame(get_adx(data['high'], data['low'], data['close'], 14)[2]).rename(columns={0: 'adx'})


def calculate_adx(data, period=14):
    # Calculate the True Range (TR)
    data['TR'] = np.maximum((data['high'] - data['low']), np.maximum(abs(data['high'] - data['close'].shift(1)),
                                                                     abs(data['low'] - data['close'].shift(1))))

    # Calculate +DM and -DM
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           np.maximum(data['high'] - data['high'].shift(1), 0), 0)
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           np.maximum(data['low'].shift(1) - data['low'], 0), 0)

    # Calculate smoothed TR, +DM, and -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])

    # Calculate the DI Difference and DI Sum
    data['DI_diff'] = abs(data['+DI'] - data['-DI'])
    data['DI_sum'] = data['+DI'] + data['-DI']

    # Calculate the DX
    data['DX'] = 100 * (data['DI_diff'] / data['DI_sum'])

    # Calculate the ADX
    data['ADX'] = data['DX'].rolling(window=period).mean()

    return data

# Example usage
# Create a DataFrame with your data


data = get_data('EURUSD')

adx_data = calculate_adx(data, period=14)

print(adx_data.tail(50))

