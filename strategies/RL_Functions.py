import talib
import numpy as np
import pandas as pd

def calculate_ADX(df, period=14):
    # Calculate ADX, +DI, and -DI
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=period)
    df['+DI'] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=period)
    df['-DI'] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=period)

    return df

def boilinger_bands(df, window=20, num_std=2):

    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])

    return df



def calculate_rsi(data, period=14):
    delta = data['close'].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    data['rsi'] = rsi
    return data

def create_MA(df, window=50):
    df = df['close'].rolling(window=window).mean()
    return df


def get_features(df):
    df = create_MA(df)
    df = calculate_ADX(df)
    df = calculate_rsi(df)
    df = boilinger_bands(df)

    return df