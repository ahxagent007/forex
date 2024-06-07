#pip install pandas numpy matplotlib MetaTrader5 scikit-learn

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from mt5_utils import get_live_data

from sklearn.ensemble import RandomForestRegressor

def random_forest_signal(symbol):
    df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=1000)

    # Preprocess data
    data = df[['close']].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Create features for the Random Forest model
    lookback = 60
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)

    # Split data into training and test sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]


    # Build the Random Forest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Inverse transform the predictions and actual values
    predictions_original = scaler.inverse_transform(predictions.reshape(-1, 1))
    y_test_original = scaler.inverse_transform(y_test.reshape(-1, 1))


    # Generate trading signals using a simple rule
    signals = []
    for i in range(1, len(predictions_original)):
        if predictions_original[i] > y_test_original[i - 1]:
            signals.append('buy')
        elif predictions_original[i] < y_test_original[i - 1]:
            signals.append('sell')
        else:
            signals.append(None)

    # Add 'Hold' signal for the first entry
    signals.insert(0, None)

    return signals[-1]


