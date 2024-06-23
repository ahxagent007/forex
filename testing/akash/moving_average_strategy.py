# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime
# from mt5_utils import get_data
#
#
# # Define symbol and timeframe
# symbol = "EURUSD"
#
# df = get_data(symbol)
#
# # Calculate the 25-candle and 50-candle moving averages
# df['MA_25'] = df['close'].rolling(window=25).mean()
# df['MA_50'] = df['close'].rolling(window=50).mean()
#
# # Plot the close price and the moving averages
# plt.figure(figsize=(14, 7))
# plt.plot(df['close'], label='Close Price', color='blue')
# plt.plot(df['MA_25'], label='48-Candle Moving Average', color='orange')
# plt.plot(df['MA_50'], label='50-Candle Moving Average', color='red')
#
# plt.title(f'{symbol} Close Price with 25-Candle and 50-Candle Moving Averages')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.legend()
# plt.show()

