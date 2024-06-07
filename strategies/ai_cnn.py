## pip install pandas numpy matplotlib tensorflow


import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from mt5_utils import get_live_data

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout


def cnn_model_signal(symbol):
    # Get historical data
    df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=5000)

    # Preprocess data
    data = df[['close']].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Prepare the data for the CNN model
    lookback = 60
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)

    # Reshape data for CNN
    X = X.reshape(X.shape[0], X.shape[1], 1)


    # Build the CNN model
    model = Sequential([
        Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(lookback, 1)),
        MaxPooling1D(pool_size=2),
        Flatten(),
        Dense(50, activation='relu'),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Split data into training and test sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Train the model
    history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

    # Make predictions
    predictions = model.predict(X_test)

    # Inverse transform the predictions and actual values
    predictions_original = scaler.inverse_transform(predictions)
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



