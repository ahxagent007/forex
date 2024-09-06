# This is a sample Python script.
import time
from datetime import datetime
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
# from hmmlearn import hmm
# import matplotlib.pyplot as plt
import time

from mt5_utils import get_live_data, trade_order_wo_tp_sl

'''import time
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.




import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters




register_matplotlib_converters()
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from candlestick import candlestick




'''


# def bot_patterns(sym, lot, transition_matrix):
#     rates = mt5.copy_rates_range(sym, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=200),
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
#
#     next_state_sequence = predict_next_state_sequence(seq, transition_matrix)
#     # print(next_state_sequence[0], '   ', next_state_sequence[1])
#     if next_state_sequence == None:
#         print('kiccu korar nai')
#     elif (next_state_sequence[0] == 'Bullish'):
#         print('Buy')
#         point = mt5.symbol_info(symbol).point
#         price = mt5.symbol_info_tick(symbol).ask
#         sl = price - 30 * point
#         tp = price + 10 * point
#         '''if sl>price:
#             sl = price - 50 * point'''
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
#     elif (next_state_sequence[0] == 'Bearish'):
#         print('sell')
#         point = mt5.symbol_info(symbol).point
#         price = mt5.symbol_info_tick(symbol).bid
#
#         sl = price + 30 * point
#         tp = price - 10 * point
#
#         '''if sl<price:
#             sl = price + 50 * point'''
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


def getSpike(prices):
    df = prices

    # Calculate the rolling mean and standard deviation
    rolling_window = 3
    df['Rolling_Mean'] = df['close'].rolling(window=rolling_window).mean()
    df['Rolling_Std'] = df['close'].rolling(window=rolling_window).std()

    # Calculate the z-score for each data point
    df['Z_Score'] = (df['close'] - df['Rolling_Mean']) / df['Rolling_Std']

    # Define a threshold for the z-score to detect spikes
    spike_threshold = 0.80  # Adjust as needed

    # Identify spike points based on the z-score threshold
    df['Spike'] = np.where(np.abs(df['Z_Score']) > spike_threshold, True, False)

    print(df)


def line_from_points(P, Q):
    # Calculate the coefficients A, B, C for the line equation Ax + By = C
    A = Q[1] - P[1]  # y2 - y1
    B = P[0] - Q[0]  # x1 - x2
    C = A * P[0] + B * P[1]  # A*x1 + B*y1
    return A, B, C


def find_intersection(P1, Q1, P2, Q2, lim):
    # Get the line equations Ax + By = C for both lines
    A1, B1, C1 = line_from_points(P1, Q1)
    A2, B2, C2 = line_from_points(P2, Q2)

    # Calculate the determinant
    determinant = A1 * B2 - A2 * B1
    #print(determinant)
    if determinant == 0:
        return "not cross"
    else:
        # Using Cramer's rule to find the intersection point (x, y)
        x = (C1 * B2 - C2 * B1) / determinant
        y = (A1 * C2 - A2 * C1) / determinant
        if (x <= lim):
            return "not cross"
        else:
            return x, y


def Ma(prices):
    a = prices['close'].rolling(window=200).mean()
    return a


def Ema(prices):
    a = prices['close'].ewm(span=50, adjust=False).mean()
    return a


def crossover(a, b):
    c = (a > b).astype(int) - (a < b).astype(int)
    d = c.shift(1)
    lst=[]
    if c.iloc[-2] != d.iloc[-2]:
        print("hurrah")
        if c.iloc[-2] == 1:

            return 'bull'
        elif c.iloc[-2] == -1:
            return 'bear'
        else:
            return "none"




    return 'none'


def bot_1(symbol, lot):
    #print("hello")

    positions = mt5.positions_get(symbol=symbol)
    # rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1,
    #                              datetime.now() - timedelta(minutes=300),
    #                              datetime.now())
    time_frame = 'M1'
    rates = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

    ticks_frame1 = pd.DataFrame(rates)
    #print(positions)
    if len(positions) == 0:
        #print("No positions ")

        a = Ma(ticks_frame1)
        b = Ema(ticks_frame1)

        lst = crossover(b, a)
        #print(len(lst))
        #print(lst)

        if (lst=='bull' ):
            print(symbol, 'buy')
            trade_order_wo_tp_sl(symbol=symbol, lot=0.1, action='buy', magic=True)
            # point = mt5.symbol_info(symbol).point
            # price = mt5.symbol_info_tick(symbol).ask
            #
            # '''if sl>price:
            #     sl = price - 50 * point'''
            #
            # deviation = 20
            # request = {
            #     "action": mt5.TRADE_ACTION_DEAL,
            #     "symbol": symbol,
            #     "volume": lot,
            #     "type": mt5.ORDER_TYPE_BUY,
            #     "price": price,
            #     "deviation": deviation,
            #     "magic": 234000,
            #     "comment": "python script open",
            #     "type_time": mt5.ORDER_TIME_GTC,
            #     "type_filling": mt5.ORDER_FILLING_IOC,
            # }
            #
            # # send a trading request
            # result = mt5.order_send(request)
            # print(result)
            #

        elif(lst=='bear' ):
            print(symbol, 'sell')
            trade_order_wo_tp_sl(symbol=symbol, lot=0.1, action='sell', magic=True)
            # point = mt5.symbol_info(symbol).point
            # price = mt5.symbol_info_tick(symbol).bid
            #
            # deviation = 20
            # request = {
            #     "action": mt5.TRADE_ACTION_DEAL,
            #     "symbol": symbol,
            #     "volume": lot,
            #     "type": mt5.ORDER_TYPE_SELL,
            #     "price": price,
            #     "deviation": deviation,
            #     "magic": 234000,
            #     "comment": "python script close",
            #     "type_time": mt5.ORDER_TIME_GTC,
            #     "type_filling": mt5.ORDER_FILLING_IOC,
            # }
            #
            # # send a trading request
            # result = mt5.order_send(request)
            # print(result)

            #print(f"The intersection point is: {intersection_point}")
    elif len(positions) > 0:
        #print("Total positions on USDCHF =", len(positions))
        a = Ma(ticks_frame1)
        b = Ema(ticks_frame1)
        P1 = (0, b.iloc[-7])
        Q1 = (7, b.iloc[-1])
        #print(P1, " ", Q1)
        P2 = (0, a.iloc[-7])
        Q2 = (7, a.iloc[-1])
        #print(P2, " ", Q2)
        intersection_point = find_intersection(P1, Q1, P2, Q2, 7)
        #print(intersection_point)
        if intersection_point!='not cross':
            print('Forced off')

            for position in positions:
                print(position.profit)
                mt5.Close(symbol, ticket=position.ticket)

        # display all open positions
        #for position in positions:
        #    print(position.profit)


def Mt5_backTest(muldhon, Current_time, window, totalTime):
    capital = muldhon
    pt = Current_time
    # if not mt5.initialize(path="C:\Program Files\MetaTrader 5\\terminal64.exe", login=176154099,
    #                       server="Exness-MT5Trial7", password="FUCKnibirr2023#"):

    login = 181244000
    password = 'ABCabc123!@#'
    server = 'Exness-MT5Trial6'
    path = "C:\Program Files\MetaTrader 5\\terminal64.exe"
    timeout = 10000
    portable = False

    if not mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
        print("initialize() failed, error code =", mt5.last_error())
        quit()
    print(mt5.terminal_info())
    print(mt5.version())

    while True:
        bot_1('EURUSD', 0.01)
        time.sleep(5)
        bot_1('USDJPY', 0.01)
        time.sleep(5)
        bot_1('EURJPY', 0.01)
        time.sleep(5)
        bot_1('XAUUSD', 0.01)
        time.sleep(5)
    '''
    plt.figure(figsize=(10, 6))
    # plt.plot(df.index, df['Close'], label='Close Price', marker='o')

    for i in range(1, len(d)):
        if d.iloc[i] == 1:
            print("crossed",i)
        elif d.iloc[i] == -1:
            print("crossed",i)


    plt.plot(b.index, b, label=f'{window}-Day SMA', color='orange', marker='o')
    plt.plot(a.index, a, label='Close Price', marker='o')

    # Add labels and title
    plt.title(f'Close Price and {window}-Day Simple Moving Average')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

    if positions == None:
        print("No positions on USDCHF, error code={}".format(mt5.last_error()))
    elif len(positions) > 0:
        print("Total positions on USDCHF =", len(positions))
        # display all open positions
        for position in positions:
            print(position.profit)


    point = mt5.symbol_info('EURUSDm').point
    price = mt5.symbol_info_tick('EURUSDm').bid

    sl = price + 30 * point
    tp = price - 10 * point



    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": 'EURUSDm',
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "ticket": 1,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)

    ticks_frame1 = pd.DataFrame(rates)
    ticks_frame1['State'] = ticks_frame1.apply(lambda row: identify_state(row['open'], row['close']), axis=1)
    #print(ticks_frame1)
    transition_matrix = calculate_transition_matrix_multiple_to_multiple(states, ticks_frame1, prev_length=10, future_length=1)
    print("Transition Matrix:")
    for key, value in transition_matrix.items():
        print(f"{key}: {value}")
    while True:
        # print(prev_time,'    ',cur_time)
        cur_time = datetime.now().minute
        if prev_time == cur_time:
            isOneCandle = False
        else:
            isOneCandle = True
        if (cur_time % 10) == 0 and isOneCandle:
            print()
            bot_patterns('EURUSDm', 0.03,transition_matrix)
            print('------------------------------------------')
            prev_time = cur_time

      '''

    mt5.shutdown()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Mt5()
    Mt5_backTest(5000, datetime.now() - timedelta(days=0.5), 60, timedelta(minutes=120))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/