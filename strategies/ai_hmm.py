# #pip install pandas numpy hmmlearn matplotlib
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from hmmlearn.hmm import GaussianHMM
# from sklearn.preprocessing import MinMaxScaler
# from mt5_utils import get_live_data
# import joblib
#
#
# def hmm_model_signal(symbol):
#     time_frame = 'M5'
#     df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)
#     if df.shape[0] == 0:
#         return None
#     # Preprocess data: Assume 'close' prices are used
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     df['close'] = scaler.fit_transform(df['close'].values.reshape(-1, 1))
#
#     # Feature engineering: Calculate returns
#     df['Returns'] = df['close'].pct_change().dropna()
#
#     # Remove NaN and infinite values
#     df.replace([np.inf, -np.inf], np.nan, inplace=True)
#     df.dropna(inplace=True)
#
#     # Prepare data for HMM
#     returns = df['Returns'].values.reshape(-1, 1)
#     try:
#         model = joblib.load('ai_models/hmm.joblib')
#     except:
#         print('MODEL NOT FOUND')
#         # Initialize and fit HMM
#         model = GaussianHMM(n_components=4, covariance_type="full", n_iter=2000)
#
#     model.fit(returns)
#
#     joblib.dump(model, 'ai_models/hmm.joblib')
#
#     # Predict hidden states
#     hidden_states = model.predict(returns)
#
#     # Add hidden states to the dataframe
#     df['Hidden State'] = hidden_states
#
#     # Generate trading signals
#     signals = []
#     for i in range(1, len(hidden_states)):
#         if hidden_states[i] == 0:
#             signals.append('buy')
#         elif hidden_states[i] == 1:
#             signals.append('sell')
#         else:
#             signals.append(None)
#
#     # Add 'Hold' signal for the first entry
#     signals.insert(0, 'Hold')
#
#     # Add signals to the dataframe
#     df['Signal'] = signals
#
#     return signals[-1]
