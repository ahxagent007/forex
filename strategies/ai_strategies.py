# from mt5_utils import trade_order
# from ai_hmm import hmm_model_signal
# from ai_cnn import cnn_model_signal
# from ai_random_forests import random_forest_signal
# from common_functions import get_sl_tp_pips, check_duplicate_orders, check_duplicate_orders_magic, write_json
# from mt5_utils import get_live_data, get_order_positions_count
# from ai_lstm import lstm_signal
#
# def ai_trade(symbol):
#     symbol_list = ['EURUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'EURJPY']
#
#     if not symbol in symbol_list:
#         return None
#
#     # json_file_name ='ai_strategies'
#     # running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=30,
#     #                                                            json_file_name=json_file_name)
#     # if running_trade_status:
#     #     print(symbol, 'MULTIPLE TRADE >>>>')
#     #     return None
#
#     order_count = get_order_positions_count(symbol)
#     if order_count>0:
#         print(symbol, 'AI MULTIPLE TRADE >>>>', order_count)
#         return None
#
#     # if_duplicate = check_duplicate_orders_magic(symbol)
#     #
#     # if if_duplicate:
#     #     print('DUPLICATE AI FOR >> ',symbol)
#     #     return None
#
#     all_signals = []
#
#     hmm = hmm_model_signal(symbol)
#     if hmm:
#         print('Hidden Markov Model', hmm)
#         all_signals.append(hmm)
#
#     #TUNE
#     cnn = cnn_model_signal(symbol)
#     if cnn:
#         print('CNN ', cnn)
#         all_signals.append(cnn)
#
#     #TUNE
#     rf = random_forest_signal(symbol)
#     if rf:
#         print('Random Forest ', rf)
#         all_signals.append(rf)
#
#
#     lstm = lstm_signal(symbol)
#     if lstm:
#         print('Long Short Trm Memory ', lstm)
#         all_signals.append(lstm)
#
#
#     buy_signals = 0
#     sell_signals = 0
#
#     for signal in all_signals:
#         if signal == 'buy':
#             buy_signals += 1
#         elif signal == 'sell':
#             sell_signals += 1
#
#     # Set SL TP
#     # df = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=20)
#     # sl_tp = get_sl_tp_pips(df=df, sl=5, tp=10)
#     # tp_point = sl_tp['TP']
#     # sl_point = sl_tp['SL']
#
#     tp_point = 200
#     sl_point = 600
#
#     lot = 0.01
#
#     print('SL TP -->> ',sl_point, tp_point)
#
#
#     if buy_signals > sell_signals:
#         action = 'buy'
#         trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=action, magic=True)
#     elif sell_signals > buy_signals:
#         action = 'sell'
#         trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=action, magic=True)
#
#     # for signal in all_signals:
#     #     trade_order(symbol=symbol, tp_point=tp_point, sl_point=sl_point, lot=lot, action=signal, magic=True)
#
#     #write_json(json_dict=orders_json, json_file_name=json_file_name)
