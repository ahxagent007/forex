# # This is a sample Python script.
# import time
# from datetime import datetime
# from datetime import datetime, timedelta
# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# from hmmlearn import hmm
# import matplotlib.pyplot as plt
#
# '''import time
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
#
# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
# from pandas.plotting import register_matplotlib_converters
#
#
# register_matplotlib_converters()
# import MetaTrader5 as mt5
# from datetime import datetime, timedelta
# from candlestick import candlestick
#
#
# '''
#
#
# def identify_state(open_price, close_price, threshold=0.02):
#     change = (close_price - open_price) / open_price
#     if change > 0:
#         return 'Bullish'
#     else:
#         return 'Bearish'
#
#
# # data['State'] = data.apply(lambda row: identify_state(row['Open'], row['Close']), axis=1)
# # print(data)
# def calculate_transition_matrix_multiple_to_multiple(states, data, prev_length=3, future_length=2):
#     n_states = len(states)
#     prev_state_sequences = [tuple(states) for states in zip(*[data['State'][i:] for i in range(prev_length)])]
#     future_state_sequences = [tuple(states) for states in
#                               zip(*[data['State'][i:] for i in range(prev_length, prev_length + future_length)])]
#
#     transition_counts = {}
#
#     for prev_states, future_states in zip(prev_state_sequences, future_state_sequences):
#         if prev_states not in transition_counts:
#             transition_counts[prev_states] = {state_seq: 0 for state_seq in future_state_sequences}
#         transition_counts[prev_states][future_states] += 1
#
#     transition_matrix = {}
#     for prev_states, future_states_counts in transition_counts.items():
#         total_counts = sum(future_states_counts.values())
#         transition_matrix[prev_states] = {state_seq: count / total_counts for state_seq, count in
#                                           future_states_counts.items()}
#
#     return transition_matrix
#
#
# def predict_next_state_sequence(current_sequence, transition_matrix):
#     if tuple(current_sequence) in transition_matrix:
#         state_sequence_probabilities = transition_matrix[tuple(current_sequence)]
#         next_state_sequence = max(state_sequence_probabilities, key=state_sequence_probabilities.get)
#     else:
#         next_state_sequence = None
#     return next_state_sequence
#
#
# def calculate_transition_matrix_multiple_to_multiple(states, data, prev_length=3, future_length=2):
#     n_states = len(states)
#     prev_state_sequences = [tuple(states) for states in zip(*[data['State'][i:] for i in range(prev_length)])]
#     future_state_sequences = [tuple(states) for states in
#                               zip(*[data['State'][i:] for i in range(prev_length, prev_length + future_length)])]
#
#     transition_counts = {}
#
#     for prev_states, future_states in zip(prev_state_sequences, future_state_sequences):
#         if prev_states not in transition_counts:
#             transition_counts[prev_states] = {state_seq: 0 for state_seq in future_state_sequences}
#         transition_counts[prev_states][future_states] += 1
#
#     transition_matrix = {}
#     for prev_states, future_states_counts in transition_counts.items():
#         total_counts = sum(future_states_counts.values())
#         transition_matrix[prev_states] = {state_seq: count / total_counts for state_seq, count in
#                                           future_states_counts.items()}
#
#     return transition_matrix
#
#
# def predict_next_state_sequence(current_sequence, transition_matrix):
#     if tuple(current_sequence) in transition_matrix:
#         state_sequence_probabilities = transition_matrix[tuple(current_sequence)]
#         next_state_sequence = max(state_sequence_probabilities, key=state_sequence_probabilities.get)
#     else:
#         next_state_sequence = None
#     return next_state_sequence
#
#
# def bot_patterns(sym, lot, transition_matrix):
#     rates = mt5.copy_rates_range(sym, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=500),
#                                  datetime.now())
#
#     ticks_frame1 = pd.DataFrame(rates)
#
#     symbol = sym
#     # ticks_frame1.drop(ticks_frame1.tail(1).index, inplace=True)
#     ticks_frame1 = ticks_frame1.tail(10)
#     ticks_frame1['State'] = ticks_frame1.apply(lambda row: identify_state(row['open'], row['close']), axis=1)
#     seq = list(ticks_frame1['State'])
#     print(seq)
#     print(len(seq))
#     next_state_sequence = predict_next_state_sequence(seq, transition_matrix)
#     print(next_state_sequence)
#     bu_count = 0
#     be_count = 0
#     for t in next_state_sequence:
#         if t == 'Bullish':
#             bu_count += 1
#         elif t == 'Bearish':
#             be_count += 1
#
#     if next_state_sequence == None:
#         print('kiccu korar nai')
#     elif (next_state_sequence[0] == 'Bullish' and bu_count > be_count):
#         print('Buy')
#         point = mt5.symbol_info(symbol).point
#         price = mt5.symbol_info_tick(symbol).ask
#         sl = price - 40 * point
#         tp = price + 20 * point
#
#         deviation = 20
#         request = {
#             "action": mt5.TRADE_ACTION_DEAL,
#             "symbol": symbol,
#             "volume": lot,
#             "type": mt5.ORDER_TYPE_BUY,
#             "price": price,
#             "sl": sl,
#             "tp": tp,
#             "deviation": deviation,
#             "magic": 234000,
#             "comment": "python script open",
#             "type_time": mt5.ORDER_TIME_GTC,
#             "type_filling": mt5.ORDER_FILLING_IOC,
#         }
#
#         # send a trading request
#         result = mt5.order_send(request)
#
#         if result.retcode != mt5.TRADE_RETCODE_DONE:
#             print('not done')
#         else:
#             print('buy done with bot 1')
#     elif (next_state_sequence[0] == 'Bearish' and be_count > bu_count):
#         print('sell')
#         point = mt5.symbol_info(symbol).point
#         price = mt5.symbol_info_tick(symbol).bid
#
#         sl = price + 40 * point
#         tp = price - 20 * point
#
#         deviation = 20
#         request = {
#             "action": mt5.TRADE_ACTION_DEAL,
#             "symbol": symbol,
#             "volume": lot,
#             "type": mt5.ORDER_TYPE_SELL,
#             "price": price,
#             "sl": sl,
#             "tp": tp,
#             "deviation": deviation,
#             "magic": 234000,
#             "comment": "python script close",
#             "type_time": mt5.ORDER_TIME_GTC,
#             "type_filling": mt5.ORDER_FILLING_IOC,
#         }
#
#         # send a trading request
#         result = mt5.order_send(request)
#
#         if result.retcode != mt5.TRADE_RETCODE_DONE:
#             print('not done')
#         else:
#             print('sell done with bot 1')
#     else:
#         print('kiccu korar nai')
#
#
# def Mt5_backTest(muldhon, Current_time, window, totalTime):
#     capital = muldhon
#     pt = Current_time
#     if not mt5.initialize(path="C:\Program Files\MetaTrader 5\\terminal64.exe", login=175066481,
#                           server="Exness-MT5Trial7", password="FUCKnibirr2023#"):
#         print("initialize() failed, error code =", mt5.last_error())
#         quit()
#     print(mt5.terminal_info())
#     print(mt5.version())
#     states = ['Bullish', 'Bearish']
#     state_index = {state: idx for idx, state in enumerate(states)}
#     print(state_index)
#     prev_time = datetime.now().minute
#     cur_time = prev_time
#     isOneCandle = True
#     rates = mt5.copy_rates_range('EURUSDm', mt5.TIMEFRAME_M10, datetime.now() - timedelta(days=360),
#                                  datetime.now())
#
#     ticks_frame1 = pd.DataFrame(rates)
#     ticks_frame1['State'] = ticks_frame1.apply(lambda row: identify_state(row['open'], row['close']), axis=1)
#     # print(ticks_frame1)
#     transition_matrix = calculate_transition_matrix_multiple_to_multiple(states, ticks_frame1, prev_length=10,
#                                                                          future_length=5)
#     print("Transition Matrix:")
#     for key, value in transition_matrix.items():
#         print(f"{key}: {value}")
#     while True:
#         # print(prev_time,'    ',cur_time)
#         cur_time = datetime.now().minute
#         if prev_time == cur_time:
#             isOneCandle = False
#         else:
#             isOneCandle = True
#         if (cur_time % 10) == 0 and isOneCandle:
#             print()
#             bot_patterns('EURUSDm', 0.03, transition_matrix)
#             print('------------------------------------------')
#             prev_time = cur_time
#
#     mt5.shutdown()
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     # Mt5()
#     Mt5_backTest(5000, datetime.now() - timedelta(days=0.5), 60, timedelta(minutes=120))
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
#
