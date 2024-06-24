# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import MinMaxScaler
# import tensorflow as tf
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense, Dropout
# from mt5_utils import get_live_data
#
#
# def lstm_signal(symbol):
#     # Load historical forex data
#     df = get_live_data(symbol=symbol, time_frame='D1', prev_n_candles=3000)
#     if df.shape[0] == 0:
#         return None
#
#     # Assume 'Close' prices are used
#     data = df[['close']].values
#
#     # Scale data
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     scaled_data = scaler.fit_transform(data)
#
#     # Prepare the data for the LSTM model
#     lookback = 15
#     X, y = [], []
#     for i in range(lookback, len(scaled_data)):
#         X.append(scaled_data[i - lookback:i, 0])
#         y.append(scaled_data[i, 0])
#     X, y = np.array(X), np.array(y)
#
#     # Reshape data for LSTM
#     X = X.reshape(X.shape[0], X.shape[1], 1)
#
#     # Train-test split
#     train_size = int(len(X) * 0.8)
#     X_train, X_test = X[:train_size], X[train_size:]
#     y_train, y_test = y[:train_size], y[train_size:]
#
#     # Build the LSTM model
#     model = Sequential()
#     model.add(LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)))
#     model.add(LSTM(units=50))
#     model.add(Dense(1))
#     model.compile(optimizer='adam', loss='mean_squared_error')
#
#     # Train the model
#     model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))
#
#     # Make predictions
#     predictions = model.predict(X_test)
#
#     # Inverse transform the predictions and actual values
#     predictions_original = scaler.inverse_transform(predictions)
#     y_test_original = scaler.inverse_transform(y_test.reshape(-1, 1))
#
#     # Generate trading signals using a simple rule
#     signals = []
#     for i in range(1, len(predictions_original)):
#         if predictions_original[i] > y_test_original[i - 1]:
#             signals.append('buy')
#         elif predictions_original[i] < y_test_original[i - 1]:
#             signals.append('sell')
#         else:
#             signals.append(None)
#
#     # Add 'Hold' signal for the first entry
#     signals.insert(0, None)
#
#     return signals[-1]
